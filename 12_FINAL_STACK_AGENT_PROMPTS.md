# ResumeIQ — Final Build Plan (Free-Tier Stack)
*Overall description, tech stack, RAG/LLM explanation, and the full multi-phase
agent-prompt set — all rewritten against the stack we actually landed on:
Render + Vercel + Supabase + Upstash + Clerk + Gemini, no Docker, no Celery.*

---

## 1. Overall Project Description (for context — paste this once, at the top of your agent session)

```
ResumeIQ is an AI resume-intelligence platform with three portals sharing one
scoring/matching engine, so the score a candidate sees and the score a
recruiter sees are computed identically.

Candidate Portal: upload a resume (PDF/DOCX) -> it's parsed into structured
data (skills, experience, education, projects, certifications, contact info)
-> scored against ATS heuristics (formatting, readability, keywords, semantic
relevance, skills, projects, experience, education) with a plain-language
explanation per category -> optionally matched against a pasted job
description (match %, missing skills split into critical/nice-to-have,
suggested certifications/projects) -> candidate can request AI-assisted
rewrites of weak bullets (STAR method, ATS-optimized, NEVER fabricating
achievements), tailored summaries (startup/corporate/FAANG/international
tone), a cover letter, LinkedIn copy, a 30/60/90-day learning roadmap, and
interview practice (personalized questions + rubric-scored answers) -> all
downloadable as one PDF report.

Recruiter Portal: upload a JD -> bulk-upload resumes -> every candidate is
scored and ranked using the SAME engine as the candidate portal -> compare
candidates side-by-side, view a skill-coverage heatmap across the pool, get
an AI shortlist with score-grounded reasoning, export as CSV/PDF.

Admin Portal: usage, storage, and AI token-cost dashboards; user/role
management; system health monitoring.

The single highest-risk feature is anything that rewrites or generates
resume content — it must never invent a fact, number, employer, or
achievement the candidate didn't already state. This is enforced by a
guardrail pattern built once and reused everywhere: constrained prompts +
a post-generation fact-check pass that flags anything new before it's shown
to the user.
```

---

## 2. Final Tech Stack (paste this once — keep it in a repo-level `CONVENTIONS.md`)

```
Frontend: Next.js + TypeScript + Tailwind CSS + shadcn/ui, deployed on Vercel (Hobby tier)
Backend: Python + FastAPI, deployed on Render (Free Web Service tier while
  building; upgrade to Render's $7/mo tier only during a live demo/viva week
  to eliminate cold starts)
Async/background jobs: FastAPI's built-in BackgroundTasks — NOT Celery.
  (Render's free tier shares 750 instance-hours/month across all services in
  the account; running a second always-on worker service alongside the API
  would exceed that budget. BackgroundTasks runs jobs in-process instead.)
Database: Supabase PostgreSQL with the pgvector extension (Free tier: 500MB,
  pauses after 7 days idle — fine while building, upgrade to Supabase Pro
  ($25/mo) only if that becomes a problem near launch)
File storage: Supabase Storage (not S3)
Auth: Clerk (Free tier, up to 50,000 monthly users) — or Supabase Auth if you
  prefer one fewer vendor
Cache / optional queue: Upstash Redis (Free tier, permanent, 500K commands/month)
Embeddings: Gemini `text-embedding-004` via API — NOT self-hosted
  sentence-transformers. (Render's free web service has only 0.1 CPU / 512MB
  RAM; self-hosting an embedding model on that is unreliable and risks
  out-of-memory crashes on bulk uploads.)
LLM (generation): Gemini API, called only through an internal swappable
  client wrapper (so switching to Claude/OpenAI later is a config change,
  not a rewrite). Use the FREE tier only against synthetic/test data during
  development — Gemini's free tier allows prompts/responses to be used for
  product improvement, which is not acceptable for real candidates' resumes.
  Switch to the PAID tier before any real person's resume goes through it.
Resume/JD text extraction: PyMuPDF, python-docx, pytesseract (OCR fallback), spaCy for NER
PDF report generation: ReportLab — NOT WeasyPrint. (WeasyPrint needs system-level
  Pango/Cairo libraries that may not be available in Render's build
  environment; ReportLab is pure Python and has no such dependency.)
ORM/migrations: SQLAlchemy + Alembic
Testing: pytest (backend), Jest + React Testing Library (frontend)
CI: GitHub Actions for lint/test only (no Docker image build needed — Render
  builds directly from your GitHub repo using Nixpacks/buildpacks)
Monitoring: Render's built-in logs + a free UptimeRobot monitor (paid
  monitoring like Sentry/Datadog is optional, not required at this scale)

Do NOT introduce Docker, Celery, Railway, self-hosted embeddings, or
WeasyPrint anywhere in this project without updating this block first.
```

---

## 3. Where the RAG/LLM Portion Actually Lives

There is no separate "RAG service" or special infrastructure box for this —
it's application code inside the FastAPI backend on Render, calling out to
Gemini over HTTPS. Concretely:

| Step | Runs in | Calls |
|---|---|---|
| Text extraction (PyMuPDF, python-docx, Tesseract) | Render (FastAPI) | Local Python libraries only |
| Structured extraction (skills, experience, etc.) | Render (FastAPI) | Gemini generation API (JSON mode) |
| Embedding generation | Render (FastAPI) | Gemini `text-embedding-004` API |
| Storing/searching vectors | — | Supabase Postgres via pgvector |
| ATS scoring (deterministic formula) | Render (FastAPI) | Pure Python, no external call |
| Rewrite / summaries / cover letter / interview Qs (guarded) | Render (FastAPI) | Gemini generation API, twice per call (generate + fact-check) |
| Async jobs (parsing, bulk ranking) | Render (FastAPI), via BackgroundTasks | Same calls as above, non-blocking |

"RAG" specifically = the combination of a pgvector similarity search
(retrieval) immediately followed by a Gemini call that's given that
retrieved context (generation) — both happening inside the same FastAPI
request/background-task handler.

---
---

# THE MULTI-PHASE AGENT PROMPTS

Same rule as before: paste ONE prompt, verify it, then the next. Fixed order
within every phase: **Backend/DB -> RAG/LLM -> Frontend -> Dataset -> Deployment.**

---
---

# PHASE 0 — Foundations

## Phase 0 — Prompt 1 of 5: Backend Scaffold & Render Deploy

```
Use the stack in "Final Tech Stack" above exactly — FastAPI, Supabase
Postgres+pgvector, Clerk auth, deployed on Render's Free Web Service tier.
Do NOT use Docker, Celery, or Railway anywhere.

Build:
1. A FastAPI project scaffold (api/, services/, models/, schemas/, core/config.py).
2. SQLAlchemy connected to a Supabase PostgreSQL instance (pgvector extension
   enabled on that Supabase project — enable it via the Supabase dashboard,
   not code).
3. Alembic configured against that same Supabase connection.
4. Clerk authentication middleware supporting three roles: candidate,
   recruiter, admin. (If using Supabase Auth instead of Clerk, use its JWT
   verification instead — pick one and be consistent.)
5. A `/health` endpoint.
6. A `render.yaml` (or Render dashboard config) so the repo deploys straight
   to a Render Free Web Service on push to main, with environment variables
   read from Render's dashboard (never hardcoded).

Definition of Done:
- Pushing to the connected GitHub branch triggers a live deploy on Render.
- The deployed `/health` endpoint returns 200 at the public Render URL.
- Alembic can run a migration against the live Supabase database.
- A request with an invalid/missing auth token is rejected by the role middleware.

Do not build any resume/JD/candidate features yet — infrastructure only.
```

## Phase 0 — Prompt 2 of 5: RAG/LLM Client Setup (Gemini)

```
Assume Phase 0 Prompt 1 is done and deployed.

Build a provider-agnostic internal LLM client wrapper in Python that:
1. Exposes `generate(prompt, **kwargs)` and `embed(text)` so nothing else in
   the codebase calls the Gemini SDK directly.
2. Defaults to Gemini for both generation and embeddings
   (`text-embedding-004`), configured via environment variables so the
   provider can be swapped later without code changes.
3. Handles Gemini's rate-limit errors (HTTP 429) with exponential backoff and
   a clear, typed exception if retries are exhausted — this matters more
   here than it would on a paid API, since the free tier's daily/per-minute
   caps are tight.
4. Reads a `GEMINI_TIER` environment variable (`free` or `paid`) and logs a
   warning on startup if it's `free`, reminding whoever's running it that
   real user data should not go through the free tier due to Google's
   data-usage terms on that tier.
5. Sets up a versioned `prompts/` directory for prompt templates — never
   hardcode a prompt string inline in business logic.

Definition of Done:
- A test script successfully calls `generate()` and `embed()` against the
  real Gemini API and prints a real response.
- Simulating a 429 (or triggering one for real by looping past the free-tier
  RPM limit) demonstrates the backoff-and-retry logic working, not an
  unhandled crash.
```

## Phase 0 — Prompt 3 of 5: Frontend Scaffold & Vercel Deploy

```
Assume Phase 0 Prompt 1 (backend) is deployed and reachable.

Build:
1. A Next.js + TypeScript project with Tailwind and shadcn/ui.
2. A shared component library: buttons, form inputs, a data table, and a
   drag-and-drop upload widget shell (visual only, no upload logic yet).
3. Login/signup screens using Clerk's prebuilt React components (or
   Supabase Auth's client, matching whatever Phase 0 Prompt 1 used).
4. Role-aware redirect: candidates -> `/candidate`, recruiters ->
   `/recruiter`, admins -> `/admin` (empty placeholder pages for now).
5. Connect this repo to Vercel for auto-deploy on push, with the Render
   backend URL set as an environment variable.

Definition of Done:
- The Vercel-deployed frontend can sign up, log in, and route to the correct
  role-based empty dashboard, talking to the real Render backend, not a mock.
```

## Phase 0 — Prompt 4 of 5: Dataset Preparation

```
This is a data-gathering task, not primarily a coding task.

Assemble an initial test dataset:
1. ~50 real or realistic resumes (PDF text-based, PDF scanned/image-only, DOCX).
2. ~20 sample job descriptions across a few role families.
3. Store all of this in a PRIVATE Supabase Storage bucket (not public, not in
   git) — access-controlled, never committed to source control.
4. Write a short README in that bucket describing provenance (real-anonymized
   vs. synthetic) and format breakdown.

Definition of Done:
- The test set exists in a private Supabase Storage bucket, not in git.
- A README documents what's in it.
```

## Phase 0 — Prompt 5 of 5: CI & Environment Config

```
Assume Prompts 1-3 are deployed.

Build:
1. A GitHub Actions workflow that runs on every PR: lint (frontend + backend)
   and tests (pytest + Jest). No Docker build step is needed — Render and
   Vercel build directly from the repo.
2. Confirm every secret (Gemini API key, Supabase connection string, Clerk
   keys) lives in Render's/Vercel's environment variable dashboards, never
   hardcoded or committed.
3. Document, in a repo README, which services are on which plan (Render
   Free, Vercel Hobby, Supabase Free, Clerk Free, Upstash Free) and the
   specific limits of each (cold starts, 750 shared instance-hours, 500MB DB,
   7-day pause on inactivity) so this isn't forgotten three phases from now.

Definition of Done:
- CI passes on a clean PR and fails on a deliberately broken test (verify
  once, then revert).
- The limits README exists and is accurate.
```

---
---

# PHASE 1 — Candidate MVP: Upload, Parse, ATS Score

## Phase 1 — Prompt 1 of 5: Backend — Upload & Parsing Endpoint

```
Read /docs/project-plan/05_database_schema.md before starting. Assume Phase 0
is complete and deployed.

Build:
1. SQLAlchemy models + Alembic migrations for `resumes` and `parsed_resume_data`.
2. An upload endpoint: validates file type (PDF/DOCX only) and size, stores
   the file in Supabase Storage, creates a `resumes` row with status
   "uploaded", then kicks off parsing via FastAPI `BackgroundTasks` (NOT a
   Celery task — there is no separate worker in this stack).
3. For now, stub the actual parsing logic to just flip status to "parsed" so
   the end-to-end wiring is provably correct before Prompt 2 adds real logic.

Definition of Done:
- A file POSTed to the upload endpoint ends up in Supabase Storage, a
  `resumes` row is created, and the background task updates its status
  without blocking the HTTP response to the client.
- Invalid file types/oversized files are rejected before ever reaching storage.
```

## Phase 1 — Prompt 2 of 5: RAG/LLM — Extraction Pipeline & ATS Scoring

```
Read /docs/project-plan/06_rag_llm_design.md sections 6.1 and 6.3 carefully.
Assume Phase 1 Prompt 1 is done.

Build:
1. Text extraction: PyMuPDF/pdfplumber for PDF, python-docx for DOCX, with a
   pytesseract OCR fallback for near-empty extracted text (scanned PDFs).
2. Deterministic regex extraction for email, phone, GitHub/LinkedIn/portfolio URLs.
3. Structured extraction (skills, experience, projects, education,
   certifications, languages) via the Gemini client from Phase 0 Prompt 2,
   using JSON-mode/structured output. The prompt must extract ONLY what's
   present in the resume, never invent a field. Validate the returned JSON
   against a Pydantic schema; retry once on malformed output, then flag for
   manual review.
4. Wire this into the real background task (replacing the Prompt 1 stub),
   writing to `parsed_resume_data` and generating/storing a `text-embedding-004`
   embedding for the resume in the pgvector column.
5. Implement the ATS scoring formula EXACTLY as specified in section 6.3 — a
   deterministic weighted calculation, not an LLM call. Use one small Gemini
   call only to generate a plain-language explanation per already-computed category.

Definition of Done:
- Uploading a real resume produces correct structured JSON for a sample of
  test resumes.
- The same resume scored twice gives the identical overall_score.
- A scanned PDF triggers OCR rather than failing silently.
- Run this against your FREE Gemini tier using ONLY the synthetic/test
  resumes from Phase 0 Prompt 4 — never a real person's resume, per the data-
  usage note in the tech stack block.
```

## Phase 1 — Prompt 3 of 5: Frontend — Uploader, Confirm Screen, Score Dashboard

```
Assume Phase 1 Prompts 1-2 are deployed.

Build:
1. A drag-and-drop uploader (PDF/DOCX) with progress bar and client-side validation.
2. A screen showing parsed data back to the candidate, with an edit/confirm step.
3. An ATS score dashboard: overall + 8 category scores with explanations.
4. A visible loading state that accounts for Render's cold-start delay (up to
   ~60 seconds on first request after idle) — show a message like "waking up
   the server, this can take up to a minute" rather than a bare spinner that
   looks broken.

Definition of Done:
- A candidate can upload a real resume, see it parsed, edit/confirm, and see
  a real ATS score with explanations.
- The cold-start wait state is visibly communicated, not silent.
```

## Phase 1 — Prompt 4 of 5: Dataset — Parsing Accuracy Regression Suite

```
Assume Phase 1 Prompts 1-2 are done.

Build:
1. Expand the test set to 150+ resumes with edge cases: multi-column
   layouts, tables, unusual fonts, embedded images, non-English names.
2. Manually label ground-truth values for a sample of at least 30.
3. Write a script that runs the parsing pipeline against this sample and
   reports field-level precision/recall.
4. Save it as a re-runnable regression script.

Definition of Done:
- The script runs and outputs precision/recall per field, reproducibly.
```

## Phase 1 — Prompt 5 of 5: Deployment — Verify the Free-Tier Flow End to End

```
Assume Phase 1 Prompts 1-3 are deployed to Render/Vercel/Supabase.

Do:
1. From a cold state (leave the Render service idle 20+ minutes), upload a
   resume through the real deployed frontend and time the full round trip.
2. Confirm the background-task parsing completes and the frontend correctly
   polls or refreshes to show the result (no lost requests during cold start).
3. Document the real, measured cold-start + parse + score latency in the repo
   README, so you know the actual number rather than guessing.

Definition of Done:
- A cold-start upload completes successfully end to end, and the real
  latency number is documented.
```

---
---

# PHASE 2 — Semantic Matching & Missing Skills

## Phase 2 — Prompt 1 of 5: Backend — JD & Matching Endpoints

```
Read /docs/project-plan/05_database_schema.md (job_descriptions,
resume_jd_matches, skill_suggestions). Assume Phase 1 is complete.

Build:
1. SQLAlchemy models + migrations for these three tables.
2. A JD submission endpoint (pasted or uploaded text).
3. A matching endpoint (resume_id + jd_id -> stored match result).

Definition of Done:
- A JD can be submitted and stored; calling the matching endpoint with a
  real resume_id + jd_id creates a row (logic comes in Prompt 2).
```

## Phase 2 — Prompt 2 of 5: RAG/LLM — Embedding Match & Skill Gap Logic

```
Read /docs/project-plan/06_rag_llm_design.md sections 6.2 and 6.4 carefully.
Assume Phase 2 Prompt 1 is done.

Build:
1. JD embedding via the same Gemini `text-embedding-004` pipeline as resumes.
2. Matching logic: cosine similarity for match_percentage; skill-level
   comparison via embedding similarity (catches "Postgres" vs. "PostgreSQL").
3. Missing-skill classification (critical vs. nice-to-have), stored in
   skill_suggestions.
4. For each critical gap, one Gemini call suggesting certifications drawn
   ONLY from a curated allowlist file you create — never let the model
   invent certification names — plus one suggested project idea.
5. Create the skill taxonomy/synonym list as a versioned data file.

Definition of Done:
- Submitting a resume + JD returns real match data, not mocked.
- Certification suggestions never fall outside the allowlist — write an
  automated test asserting this.
- Test against synthetic data only, on the free Gemini tier, per the data-
  usage rule.
```

## Phase 2 — Prompt 3 of 5: Frontend — JD Screen & Match Results

```
Assume Phase 2 Prompts 1-2 are deployed.

Build:
1. A JD paste/upload screen.
2. A match-results view: match %, matching/missing skills split by priority,
   skill importance, experience gap, education match.
3. A missing-skill panel with certification/project suggestions.

Definition of Done:
- A candidate can paste a JD against their resume and see a real match report.
```

## Phase 2 — Prompt 4 of 5: Dataset — Match-Quality Eval

```
Assume Phase 2 Prompts 1-2 are done.

Build a hand-labeled set of ~50 resume/JD pairs with human judgments (good/
partial/poor match), and a script reporting how well match_percentage
correlates with those labels. Review the taxonomy/allowlist files yourself —
this needs real judgment, don't just accept the agent's first draft.

Definition of Done:
- The correlation script runs and reports a number.
- You've personally reviewed and edited the taxonomy/allowlist.
```

## Phase 2 — Prompt 5 of 5: Deployment — Optional Upstash Caching

```
Assume Phase 2 Prompts 1-3 are deployed.

Add Upstash Redis caching for repeat resume+JD lookups, so re-checking the
same pair doesn't re-embed/re-match from scratch. This is the first real use
of Upstash in this project — keep it strictly optional/best-effort (a cache
miss should degrade gracefully to a fresh computation, never error).

Definition of Done:
- A repeated identical match request is measurably faster on the second call.
- Upstash being fully unavailable does not break the matching endpoint.
```

---
---

# PHASE 3 — Generation Suite (Rewrite, Summary, Cover Letter, LinkedIn)

## Phase 3 — Prompt 1 of 5: Backend — Generation Endpoint

```
Read /docs/project-plan/02_requirements.md (C-06 through C-09). Assume Phase 2
is complete.

Build:
1. SQLAlchemy model + migration for `generated_content`.
2. A single generation endpoint that ALL generation features route through
   (rewrite, 4 summary types, cover letter, 4 LinkedIn types) — one shared
   service function, not separate logic per type.

Definition of Done:
- The endpoint accepts a `type` parameter + resume_id (+ optional jd_id),
  stores a row (real generation logic comes in Prompt 2).
```

## Phase 3 — Prompt 2 of 5: RAG/LLM — Guardrail Pattern & Templates (HIGH RISK — READ CAREFULLY)

```
Read /docs/project-plan/06_rag_llm_design.md section 6.5 IN FULL before
writing any code. This is the highest fabrication-risk feature in the
project. Assume Phase 3 Prompt 1 is done.

Build, in this exact order:
1. The guardrail pattern, implemented ONCE and reused everywhere below:
   (a) a system prompt constraining Gemini to use only facts already present
   in the parsed resume, (b) for rewrite, STAR structure where the Result
   comes from the original bullet or stays qualitative if no metric was
   given — never invent a number, (c) a second Gemini call after generation
   that diffs the new text against the source resume and flags any new
   proper noun, number, or tool name not in the original.
2. Resume rewrite, built on the guardrail.
3. The 4 summary templates.
4. Cover letter generation, same guardrail reused.
5. LinkedIn copy generation, same guardrail reused.

Note: every generation call now costs TWO Gemini calls (generate + fact-
check), which matters on the free tier's daily request cap — be mindful of
this while testing, and definitely switch to Gemini's paid tier before any
real user's resume goes through this.

Definition of Done:
- Every generation type routes through the SAME guardrail function — verify
  by code review.
- Flagged content is stored with a flag on the row, never silently dropped
  or silently accepted.
```

## Phase 3 — Prompt 3 of 5: Frontend — Generation UIs

```
Assume Phase 3 Prompts 1-2 are deployed.

Build:
1. Rewrite-suggestion UI with per-bullet accept/edit/reject — never auto-apply.
2. Summary generator with 4 tone options.
3. Cover letter editor with export.
4. LinkedIn optimizer screens.
5. Visibly highlight anything the backend flagged as potentially fabricated
   — don't hide it.
6. Handle Gemini rate-limit errors gracefully in the UI (a clear "AI is busy,
   try again in a moment" message, not a raw error).

Definition of Done:
- A candidate can generate, review, and accept/reject content for all 4
  types end to end.
- Flagged content is visibly distinct in the UI.
```

## Phase 3 — Prompt 4 of 5: Dataset — Fabrication Red-Team Eval

```
Assume Phase 3 Prompts 1-2 are done.

Build a test set of 30+ resumes run through rewrite/cover letter/LinkedIn
generation, manually checked for invented facts. Turn it into a repeatable
eval script.

Definition of Done:
- The eval script runs and reports a fabrication count/rate.
- You've personally read a sample of flagged AND unflagged outputs to
  confirm the automated check is catching what it should.
```

## Phase 3 — Prompt 5 of 5: Deployment — Usage Logging & Gemini Tier Switch Plan

```
Assume Phase 3 Prompts 1-3 are deployed.

Do:
1. Log token usage/estimated cost on every generation call into a
   `usage_events` table.
2. Add a hard per-user request limit in the app itself (in addition to
   whatever Gemini enforces) so one user can't burn through your daily
   Gemini quota alone.
3. Document, clearly, the exact steps to flip `GEMINI_TIER` from `free` to
   `paid` (which env vars change, what it costs) — you'll need this fast
   before a demo, not figured out under pressure.

Definition of Done:
- Every generation call produces a usage_events row.
- The free-to-paid switch is a documented, tested procedure, not theoretical.
```

---
---

# PHASE 4 — Roadmap, Interview Copilot, AI Report

## Phase 4 — Prompt 1 of 5: Backend — Report Endpoint (ReportLab, not WeasyPrint)

```
Assume Phase 3 is complete.

Build:
1. SQLAlchemy models + migrations for `interview_sessions` and `reports`.
2. A report-generation endpoint using ReportLab (pure Python, no system
   dependencies) to produce a PDF from all prior analysis data for a resume
   (ATS score, match report, generated content). Do NOT use WeasyPrint —
   it needs system-level libraries that may not be available in Render's
   build environment.

Definition of Done:
- Calling the report endpoint for a resume with existing data produces a
  real downloadable PDF from the deployed Render service.
```

## Phase 4 — Prompt 2 of 5: RAG/LLM — Roadmap, Interview Questions, Rubric

```
Read /docs/project-plan/06_rag_llm_design.md sections 6.6 and 6.7. Assume
Phase 4 Prompt 1 is done.

Build:
1. Career roadmap generation explicitly GROUNDED in the Phase 2 missing-skill
   output — verify by checking that changing a candidate's gaps changes
   their roadmap.
2. A curated behavioral/HR question bank as structured data.
3. Technical/project questions generated via RAG over the candidate's own
   resume — verify two different candidates get meaningfully different questions.
4. Rubric generation BEFORE the candidate answers.

Definition of Done:
- Roadmap output traces back to specific Phase 2 skill gaps.
- Technical questions differ meaningfully between two test candidates.
```

## Phase 4 — Prompt 3 of 5: Frontend — Roadmap, Interview UI, Report Download

```
Assume Phase 4 Prompts 1-2 are deployed.

Build:
1. A 30/60/90-day roadmap timeline.
2. Interview-practice chat/quiz UI with rubric feedback.
3. A "Generate Report" button with PDF preview/download.

Definition of Done:
- A candidate can complete the roadmap, interview practice, and report
  download, all working end to end.
```

## Phase 4 — Prompt 4 of 5: Dataset — Question Bank Curation

```
Assume Phase 4 Prompt 2 is done. Curate a behavioral/HR interview question
bank as versioned structured data, ideally reviewed by someone with real
hiring/interviewing experience.

Definition of Done:
- The question bank exists, is versioned, and has been humanly reviewed.
```

## Phase 4 — Prompt 5 of 5: Deployment — Full Candidate Journey Soak Test

```
Assume Phase 4 Prompts 1-3 are deployed. This closes the candidate journey.

Do:
1. Run the full flow from a cold Render start: upload -> parse -> score ->
   match -> generate -> roadmap -> interview -> report, as one session.
2. Fix anything that breaks across the full chain.
3. Tag this release as `candidate-portal-v1`.

Definition of Done:
- The full flow completes without manual intervention, including the cold-start case.
```

---
---

# PHASE 5 — Recruiter Portal

## Phase 5 — Prompt 1 of 5: Backend — Ranking & Bulk Upload

```
Read /docs/project-plan/02_requirements.md (R-01 through R-09). Assume
candidate-portal-v1 is stable.

Build:
1. SQLAlchemy model + migration for `recruiter_shortlists`.
2. A ranking endpoint that REUSES the Phase 1-2 scoring/matching logic in
   batch, against a pool of resumes for one JD.
3. A bulk-upload endpoint queuing many resumes through the SAME parsing
   pipeline via BackgroundTasks. Be aware: Render's free tier gives 0.1 CPU,
   so bulk processing will run serially and slowly, not in true parallel —
   design the UI to show per-file progress honestly rather than implying speed.
4. Recruiter authentication with org-scoped access.

Definition of Done:
- Bulk-uploading 20+ resumes results in all of them parsed/scored using the
  exact same code path as Phase 1 (verify by comparing scores against
  single-upload results for the same resume).
```

## Phase 5 — Prompt 2 of 5: RAG/LLM — Shortlist Rationale

```
Assume Phase 5 Prompt 1 is done.

Build recruiter-summary generation reusing the EXACT Phase 3 guardrail
pattern. Build AI shortlisting: rank by existing overall_score/
match_percentage, then generate a "why shortlisted" rationale per candidate
grounded in their actual score breakdown — never stating anything not
present in that candidate's parsed resume.

Definition of Done:
- Shortlist rationale text passes the same fabrication check used in Phase 3.
```

## Phase 5 — Prompt 3 of 5: Frontend — Recruiter Dashboard

```
Assume Phase 5 Prompts 1-2 are deployed.

Build: recruiter auth/dashboard, JD upload, bulk uploader with per-file
status, ranked candidate table, side-by-side comparison, skill heatmap,
shortlist screen, CSV/PDF export.

Definition of Done:
- A recruiter can go from JD upload through export in one working flow.
```

## Phase 5 — Prompt 4 of 5: Dataset — Realistic Bulk Load Test

```
Assume Phase 5 Prompts 1-2 are done. Simulate 50-100 resumes against one JD
(scaled down from a larger number given the free-tier CPU constraint) and
record real throughput. If this is too slow for practical use, document that
finding clearly — it's a legitimate, expected limit of the free tier, not a bug.

Definition of Done:
- Documented real throughput numbers and a clear statement of whether the
  free tier is adequate for your expected demo/grading scale.
```

## Phase 5 — Prompt 5 of 5: Deployment — Tenant Isolation

```
Assume Phase 5 Prompts 1-3 are deployed. Security-critical — review the
output yourself.

Enforce org_id scoping at the query layer for every JD/resume-pool query.
Write an automated test proving one recruiter org cannot see another org's data.

Definition of Done:
- The tenant-isolation test passes, and you've personally reviewed the
  query-layer code, not just the test.
```

---
---

# PHASE 6 — Admin Portal & Hardening

## Phase 6 — Prompt 1 of 4: Backend — Metrics & Rate Limiting

```
Read /docs/project-plan/02_requirements.md (A-01 through A-05). Assume Phase
5 is complete.

Build:
1. An admin metrics pipeline reading `usage_events` and storage data.
2. Rate limiting using Upstash Redis (simple fixed-window or sliding-window
   counter) at the API level, on top of Gemini's own limits.
3. A tenant-isolation audit across every service, not just recruiter-specific ones.

Definition of Done:
- Metrics pipeline produces real numbers from actual usage.
- Rate limiting demonstrably rejects a request that exceeds the configured limit.
```

## Phase 6 — Prompt 2 of 4: RAG/LLM — Cost Review

```
Assume Phase 6 Prompt 1 is done.

Document actual Gemini API spend so far (paid-tier usage, if any) and
confirm embedding/score caching (added in earlier phases) is measurably
reducing redundant calls, with before/after numbers.

Definition of Done:
- Documented real cost numbers, not estimates.
```

## Phase 6 — Prompt 3 of 4: Frontend — Admin Dashboard

```
Assume Phase 6 Prompts 1-2 are deployed.

Build usage, cost, reporting, user/role management, and system-health views,
all pulling real data.

Definition of Done:
- Every number on the dashboard is real, not mocked.
```

## Phase 6 — Prompt 4 of 4: Deployment — Lightweight Hardening

```
Assume Phase 6 Prompts 1-3 are deployed. (Note: enterprise hardening like
blue-green deploys and WAF aren't available/needed at this tier — keep this
proportionate to a student project.)

Do:
1. Confirm Supabase's automated backup behavior for your plan and document
   how to restore from one.
2. Audit that every secret is in Render's/Vercel's env var dashboard, never
   in code.
3. Set up a free UptimeRobot monitor pinging your `/health` endpoint, with
   an email alert on downtime.

Definition of Done:
- You've documented (and ideally tested) the Supabase restore process.
- UptimeRobot is live and you've confirmed you receive its alert once, on purpose.
```

---
---

# PHASE 7 — Demo/Launch Week

## Phase 7 — Prompt 1 of 4: Backend — Final Config Review

```
Assume Phase 6 is complete and every prior Definition of Done has been
personally verified. This phase covers the days around your actual demo,
viva, or submission.

Do a final review of environment variables, timeouts, and error handling —
confirm nothing throws a raw stack trace to the user on failure.

Definition of Done:
- A deliberately triggered error (bad input, Gemini timeout) shows a clean
  user-facing message, not a raw exception.
```

## Phase 7 — Prompt 2 of 4: RAG/LLM — Switch to Paid Tier & Pin Model Version

```
Assume Phase 7 Prompt 1 is done. THIS IS THE STEP WHERE YOU ACTUALLY SPEND
MONEY — do it deliberately, a day or two before you need it, not the morning of.

Do:
1. Switch `GEMINI_TIER` to `paid` using the documented procedure from Phase 3
   Prompt 5. Confirm real resumes can now be processed without the free-tier
   data-usage concern.
2. Pin the exact Gemini model version in production config rather than
   riding "latest."
3. Re-run the Phase 3 fabrication red-team eval one final time against the
   paid tier to confirm nothing changed.

Definition of Done:
- Paid tier is active and confirmed working.
- The red-team eval still passes at the same rate as before.
```

## Phase 7 — Prompt 3 of 4: Backend — Upgrade Render for the Demo Window

```
Assume Phase 7 Prompts 1-2 are done.

Upgrade the Render service to the $7/month tier for the demo/viva/submission
window (a few days), specifically to eliminate cold starts. Set a personal
reminder to downgrade back to Free afterward if you don't need it running
continuously.

Definition of Done:
- The live app responds immediately with no cold-start delay during a fresh test.
```

## Phase 7 — Prompt 4 of 4: Deployment — Final Smoke Test & Go/No-Go

```
Assume Phase 7 Prompts 1-3 are done. Run this yourself, not unattended by an agent.

Do:
1. Run the full candidate + recruiter end-to-end flow against the live,
   paid-tier, warmed-up production deployment.
2. Confirm the admin dashboard shows real data from that session.
3. Make the final call yourself on whether it's ready to demo/submit.

Definition of Done:
- Full flow works live, and you've personally made the go/no-go call.
```
