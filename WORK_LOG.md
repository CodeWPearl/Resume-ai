# WORK_LOG.md — ResumeIQ build diary (one entry per change)

Rule (see AGENTS.md): every change updates this file in the SAME commit as the
change it describes. Each entry records WHAT, HOW, exact COMMANDS, VERIFICATION,
and the COMMIT hash. Commits are pushed individually, never batched.

Format:
`## <date> — <title>` + What / How / Commands / Verification / Commit.

---

## 2026-09-22 — Phase 0-1: backend scaffold (FastAPI + Supabase + Clerk + /health)
- What: FastAPI project (`api/`, `core/`, `models/`, `schemas/`), SQLAlchemy engine
  for Supabase Postgres+pgvector, Alembic, Clerk JWT middleware with
  candidate|recruiter|admin roles, `/health` + `/me` endpoints, `render.yaml`.
- How: wrote `backend/core/{config,database,clerk_auth}.py`, `backend/api/main.py`,
  `backend/alembic/{env.py,script.py.mako}`, `render.yaml`; `.env.example` only.
- Commands:
  `pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary pydantic pydantic-settings python-jose httpx pytest pytest-asyncio python-dotenv`
  `python -m pytest backend/tests/test_health.py -v` → 4 passed.
- Verification: `/health` 200; `/me` 401 without token, 200 with `dev-candidate`,
  401 with bad dev role.
- Commit: `3c63d70 feat(backend): FastAPI scaffold, Supabase wiring, Clerk roles, /health`

## 2026-09-22 — Phase 0-2: provider-agnostic Gemini client + versioned prompts
- What: `backend/services/llm_client.py` exposing `generate()`/`embed()` (nothing
  else touches the Gemini SDK), 429 exponential backoff → `LLMRateLimitExhausted`,
  `GEMINI_TIER=free` startup warning, `load_prompt()` over `backend/prompts/v1/*.txt`.
- How: lazy `google-genai` client; backoff in `_with_backoff()`; templates
  `structured_extraction.txt`, `ats_explanation.txt`, `factcheck.txt` (+ README).
- Commands:
  `python -m pytest backend/tests/test_llm_client.py::test_load_prompt_versions backend/tests/test_llm_client.py::test_backoff_retries_then_raises -v` → 2 passed.
  Live API test skipped (no `GEMINI_API_KEY`); re-run with key for DoD.
- Commit: `7e74d28 feat(backend): provider-agnostic Gemini client with backoff plus versioned prompts`

## 2026-09-22 — Phase 0-3: frontend scaffold (Next.js + Clerk + shadcn shells)
- What: Next.js 16 + TS + Tailwind app, Clerk auth (sign-in/up, middleware-protected
  `/candidate|/recruiter|/admin` placeholders), shared `ui/` (button/input/label/
  table/card), visual-only `UploadDropzone`, `NEXT_PUBLIC_API_URL` wiring.
- How: `npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir`,
  then `npm install @clerk/nextjs clsx tailwind-merge class-variance-authority lucide-react @radix-ui/react-slot @radix-ui/react-label`;
  hand-wrote shadcn-style components (no interactive init).
- Commands: `npm install ...` (385 packages, 0 vulns); `npx tsc --noEmit` → 3 Clerk
  v7 prop errors (fixed next entry).
- Commit: `62fda82 feat(frontend): Next.js plus Clerk plus shadcn shells plus role portals (Impeccable)`

## 2026-09-22 — Impeccable design system install + PRODUCT.md/DESIGN.md
- What: installed Impeccable skill for OpenCode; wrote `PRODUCT.md` (users/goals/
  voice) and `DESIGN.md` (tokens, components, cold-start/empty/error states).
- How: `npx impeccable install --providers=opencode --scope=project -y`; engine
  binaries gitignored (reinstall command in AGENTS.md §3).
- Commands: `npx -y impeccable install --providers=opencode --scope=project -y`
- Commit: `4165172 chore(tools): install Impeccable skill for OpenCode (binaries excluded, reinstall via npx)`

## 2026-09-23 — Repo hygiene: .gitignore + remote + 8 one-by-one pushes
- What: root `.gitignore` (envs, node_modules, `.next`, `*.pdf/*.docx`, engine
  `scripts/bin/`), `git remote add origin https://github.com/CodeWPearl/Resume-ai.git`,
  pushed prior work as 8 separate commits (`9c50430`, `a3ab3c2`, `46cca80`,
  `cb1b2f3`, `3c63d70`, `7e74d28`, `62fda82`, `4165172`), each `git push origin main`.
- How: `git add <paths>` per logical unit; `git commit`; `git push origin main` × 8.
  `frontend/.gitignore` gained `!.env.example` so the env template is tracked.
- Verification: `git status --short` clean; `git log --oneline` shows 8 commits.
- Commits: `9c50430`, `a3ab3c2`, `46cca80`, `cb1b2f3` (+ the four above).

## 2026-09-23 — docs: AGENTS.md operating rules for coding agents
- What: repo-root `AGENTS.md` — stack summary, everyday commands, phase workflow,
  verification + git rules (incl. this WORK_LOG rule).
- How: single-file write, no code touched.
- Commands: `git add AGENTS.md` → commit → `git push origin main`.
- Verification: committed `AGENTS.md` only (1 file, 58 insertions).
- Commit: `ceffa72 docs: add AGENTS.md operating rules for coding agents`

## 2026-09-23 — docs: WORK_LOG.md build diary (this file)
- What: this file — full history of every change with what/how/commands/
  verification/commit, plus the standing rule to keep it updated per change.
- How: reconstructed from prior session commands and `git log --oneline`.
- Commands: `git add WORK_LOG.md` → commit → `git push origin main`.
- Verification: this commit touches `WORK_LOG.md` only.
- Commit: `3ed1d6f docs: add WORK_LOG.md build diary with per-change history`

## 2026-09-23 — fix(frontend): Clerk v7 redirect props (`fallbackRedirectUrl`)
- What: `npx tsc --noEmit` failed with 3 errors — Clerk v7 removed
  `afterSignInUrl`/`afterSignUpUrl` (SignIn/SignUp) and `afterSignOutUrl`
  (UserButton). Replaced with `fallbackRedirectUrl="/?auto=1"`; dropped the
  unsupported UserButton prop (sign-out redirect now provider-default).
- How: verified prop names against installed `@clerk/shared` types
  (`UserButtonProps` has no redirect prop; SignIn/SignUp accept
  `fallbackRedirectUrl`/`forceRedirectUrl`).
- Commands (from `frontend/`): `npx tsc --noEmit` → clean; `npm run lint` → clean.
  From root: `python -m pytest backend/tests/ -v` → 6 passed, 1 skipped (live
  Gemini test needs `GEMINI_API_KEY`).
- Commit: `6e6962f fix(frontend): Clerk v7 redirect props (fallbackRedirectUrl)`

## 2026-09-23 — Phase 0-5a: GitHub Actions CI (lint + test, no Docker)
- What: `.github/workflows/ci.yml` — backend job (pip install + pytest with
  `CLERK_BYPASS_AUTH=true`) and frontend job (`npm ci`, `tsc`, `lint`, `build`
  with placeholder Clerk keys). No Docker build step: Render/Vercel build from
  the repo. Jest runs will be added with the first frontend tests.
- How: single workflow file; backend env uses dummy `DATABASE_URL` (tests never
  open a DB connection); frontend build uses non-secret placeholder keys.
- Commands: validated locally — `python -m pytest backend/tests/ -v` (6 passed,
  1 skipped), `npx tsc --noEmit` + `npm run lint` clean. (Full `npm run build`
  runs in CI.)
- Commit: `d49860f ci: add GitHub Actions lint plus test workflow (no Docker)`

## 2026-09-23 — Phase 0-5b: root README (plans/limits) + secrets audit
- What: root `README.md` — quickstart, service-plan/limits table (Render cold
  starts + 750 instance-hours, Supabase 500MB/7-day pause, Gemini free-tier data
  rule), secrets-in-dashboards note.
- How: transcribed from `12_FINAL_STACK_AGENT_PROMPTS.md` Phase 0 Prompt 5 +
  `CONVENTIONS.md`; audited repo for hardcoded keys.
- Commands: `git grep -n -i -E "sk-(live|test)-...|AIza...|postgres://...|service_role"`
  → no hits (only `change-me` / `ci-placeholder` templates remain).
- Commit: `01e8f0a docs: add root README with service plans, limits, and quickstart`

## 2026-09-23 — verify: Phase 0 DoD sweep (tests/typecheck/lint/design)
- What: full local verification pass after all Phase 0 changes.
- Commands + results:
  `python -m pytest backend/tests/ -v` → 6 passed, 1 skipped (live Gemini, no key).
  `npx tsc --noEmit` (frontend/) → clean.
  `npm run lint` (frontend/) → clean.
  `npx impeccable detect frontend/src` → clean, no findings.
  `npm run build` → left to CI (first run visible under repo Actions tab).
- Commit: `77b711c docs: log Phase 0 verification sweep in WORK_LOG`

## 2026-09-23 — fix(ci): Clerk Core 3 removed SignedIn/SignedOut → Show
- What: CI frontend `npm run build` failed prerendering `/` with
  `Clerk: <SignedOut> is not available in @clerk/nextjs Core 3`
  (removed 2026-03-03; single `<Show when=...>` replaces SignedIn/SignedOut/Protect).
  `SiteHeader` now uses `<Show when="signed-out">` / `<Show when="signed-in">`.
  Grep confirms no remaining SignedIn/SignedOut/Protect component usages.
- How: per https://clerk.com/err/signedout-is-not-available-in-clerk-nextjs;
  reproduced locally with CI's exact placeholder-key env, verified fixed.
- Commands (from `frontend/`): `npx tsc --noEmit` → clean; `npm run lint` →
  clean; `npm run build` (CI env) → 7/7 static pages generated, all routes OK.
- Commit: `6079c81 fix(ci): Clerk Core 3 removed SignedIn/SignedOut, use Show component`

## 2026-09-23 — fix(ci): backend pip install — 3 bad pins in requirements.txt
- What: CI `backend` job failed at `pip install` (frontend job: SUCCESS after the
  Show fix). Diagnosed via GitHub API (`.../runs/35807007975/jobs`): step
  `pip install -r backend/requirements.txt` → failure. Root causes, all
  mistyped/yanked versions in `backend/requirements.txt` (never installed from
  file locally before):
  `tenacity==9.0.2` → `9.1.4` (9.0.2 was never released — THE breaker, pip
  errors instantly, matches the ~40s runs);
  `PyMuPDF==1.24.10` → `1.25.5` (1.24.10 yanked from PyPI);
  `spacy==3.7.6` → `3.8.16` (3.7.6 yanked; 3.8.16 has cp312 manylinux_2_28
  wheels for ubuntu-24.04 runners and cp314 wheels for local dev);
  `psycopg2-binary==2.9.10` → `2.9.11` (adds cp314 wheels; cp312 manylinux
  wheels kept for CI).
- How: reproduced with `pip install --dry-run` (+ `--python-version 3.12
  --platform manylinux... --only-binary=:all:` to mirror the runner) and PyPI
  JSON wheel checks; full file resolves with zero errors after the fix.
- Commands: `pip install --dry-run -r backend/requirements.txt`;
  PyPI checks for psycopg2-binary/spacy wheels; `git push origin main` re-runs CI.
- Commit: `f09f70d fix(ci): correct 4 uninstallable pins in backend requirements`

## 2026-09-23 — milestone: CI fully green (run #5, both jobs)
- What: run #5 (`f09f70d`) conclusion `success` — `backend` success,
  `frontend` success (verified via public API
  `repos/CodeWPearl/Resume-ai/actions/runs?per_page=1` + jobs endpoint).
  This closes Phase 0 Prompts 1–3 + 5 on the automation side. Remaining:
  Prompt 4 dataset (needs Supabase private bucket — user action) and the
  deliberately-broken-test check below.
- Commit: `eb60281 docs: log CI-green milestone (run 5, both jobs) in WORK_LOG`

## 2026-09-23 — DoD: deliberately broken test to prove CI fails (TEMPORARY)
- What: added `backend/tests/test_ci_canary.py` with one `assert False` per
  Phase 0 Prompt 5 DoD ("fails on a deliberately broken test, verify once,
  then revert"). Local check first: `python -m pytest backend/tests/test_ci_canary.py`
  → 1 failed as intended. Revert commit follows once CI run #6 goes red.
- Commit: `b0f25d5 test(ci): TEMPORARY canary to prove CI fails on broken test`

## 2026-09-23 — DoD complete: canary reverted, CI green again
- What: deleted `backend/tests/test_ci_canary.py`. Proof recorded: run #6
  (`eb60281`, clean) → success; run #7 (`b0f25d5`, canary) → failure with
  `backend` failed / `frontend` success — exactly the red/green behavior Phase 0
  Prompt 5 demands. Local `python -m pytest backend/tests/ -v` re-verified after
  removal (expect 6 passed, 1 skipped).
- Commit: `6d82341 test(ci): revert TEMPORARY canary, CI red-green proven`

## 2026-09-23 — fix(backend): root-relative imports so uvicorn boots from repo root
- What: `uvicorn backend.api.main:app` crashed with `No module named 'core'` —
  `api/main.py` and `services/llm_client.py` used bare `from core...` imports
  that only resolved under pytest's sys.path. Switched 3 imports to
  `backend.`-prefixed absolute imports (matches alembic env.py + tests).
- How: reproduced the crash via foreground uvicorn, fixed, re-verified.
- Commands: `uvicorn backend.api.main:app --port 8000` (+ `CLERK_BYPASS_AUTH=true`)
  → `curl localhost:8000/health` → `{"status":"ok",...}`;
  `curl /me -H "Bearer dev-candidate"` → role candidate;
  `python -m pytest backend/tests/` → 6 passed, 1 skipped.
- Commit: `5c666b9 fix(backend): root-relative imports so uvicorn boots from repo root`

## 2026-09-24 — feat(auth): backend Clerk → Supabase Auth
- What: deleted `backend/core/clerk_auth.py` (Clerk JWKS verify); new
  `backend/core/supabase_auth.py` with the SAME interface (`CurrentUser`,
  `get_current_user`, `require_role`, `dev-<role>` bypass tokens) — tokens now
  validated via `supabase.auth.get_user()` against the Auth server, roles read
  from `user_metadata.role`. `config.py`: CLERK_* → SUPABASE_URL/ANON_KEY/
  SERVICE_KEY + SUPABASE_BYPASS_AUTH (prod guard kept). `requirements.txt`:
  dropped `python-jose`, added `supabase==2.31.0`, bumped `pydantic 2.10.4` →
  `2.11.10` (supabase tree conflicts with 2.10.4 — proven by resolver error,
  fixed, full-file dry-run resolves clean). `test_health.py` uses new bypass var.
- How: interface-preserving swap so `api/main.py` changes one import line.
- Commands: `python -m pytest backend/tests/` → 6 passed, 1 skipped;
  `pip install --dry-run -r backend/requirements.txt` → zero conflicts.
- Commit: `bd0cf32 feat(auth): backend Clerk to Supabase Auth, same role interface`

## 2026-09-24 — feat(auth): frontend Clerk → Supabase Auth
- What: removed `@clerk/nextjs`; added `@supabase/supabase-js` + `@supabase/ssr`.
  New `lib/supabase/{client,server}.ts` (+ shared `roleOf()` from user_metadata),
  `middleware.ts` does session refresh + redirects logged-out users from the 3
  portals, `SiteHeader` is a session-aware client component (email + sign out),
  custom sign-in (email/password) and sign-up (email/password + role select
  writing `user_metadata.role`) forms in our design-system components, home keeps
  `?auto=1` role redirect via server `getUser()`, `/admin` redirects non-admins
  server-side. Deleted Clerk `[[...sign-in]]`/`[[...sign-up]]` routes.
- How: no Auth-UI dep (custom forms = full DESIGN.md control); every server
  `getUser()` wrapped so CI placeholder env renders logged-out views.
- Commands (from `frontend/`): `npm uninstall @clerk/nextjs`,
  `npm install @supabase/supabase-js @supabase/ssr`, cleared stale `.next`
  (it referenced deleted routes), `npx tsc --noEmit` → clean, `npm run lint` →
  clean, `npm run build` with placeholder Supabase env → 7/7 routes OK.
- Commit: `33a2cc9 feat(auth): frontend Clerk to Supabase Auth with custom forms`

## 2026-09-24 — chore(auth): configs + docs sweep, Clerk fully out
- What: `render.yaml` CLERK_* → SUPABASE_ANON_KEY; CI backend env
  `SUPABASE_BYPASS_AUTH`, frontend build env → placeholder Supabase URL/anon key;
  AGENTS.md, CONVENTIONS.md, README.md, DESIGN.md auth lines → Supabase Auth.
  Verified via repo grep: live code/configs contain zero Clerk references
  (remaining hits are WORK_LOG history + the original plan doc, both intentionally kept).
- Commit: `6bf9ee8 chore(auth): configs and docs sweep, Clerk fully out`

## 2026-09-24 — Phase 1 Prompt 1a: resumes + parsed_resume_data models + migration
- What: `backend/models/resume.py` (`ResumeRecord`: user/org/file/status flow
  uploaded→parsing→parsed|failed; `ParsedResumeData`: raw_text + 7 JSON fields;
  no embedding column yet — Prompt 2 adds pgvector), Alembic revision
  `0001_resumes` with reversible upgrade/downgrade, `tests/conftest.upgrade_db`
  + `test_migrations.py` running upgrade AND downgrade for real against throwaway
  SQLite (same migration runs on Supabase via DATABASE_URL). Note: the plan's
  `/docs/project-plan/05_database_schema.md` doesn't exist in repo — schema
  designed from the plan's table names + conventional columns.
- Commands: `python -m pytest backend/tests/test_migrations.py -v` → 2 passed.
- Commit: `a237f87 feat(db): resumes and parsed_resume_data models plus migration`

## 2026-09-24 — Phase 1 Prompt 1b: upload endpoint + Storage + BackgroundTasks stub
- What: `POST /resumes/upload` (202): extension allowlist (.pdf/.docx) + magic-byte
  sniff + 10MB limit (`MAX_UPLOAD_MB` in config) validated BEFORE storage → upload
  to private Supabase Storage bucket (`{user}/{id}/{file}` via service-role) →
  `resumes` row `uploaded` → BackgroundTasks `parse_resume_stub` flips to `parsed`
  (Prompt 2 replaces the body). `GET /resumes/{id}` for polling, owner-or-admin
  gated. New `services/storage.py` (DI-overridable), `services/parsing.py`,
  `schemas/resume.py`; router registered in `main.py`.
- How: no live Supabase yet — endpoint proven via TestClient + real Alembic-built
  SQLite + fake storage + dev tokens.
- Commands: `python -m pytest backend/tests/test_upload.py -v` → 7 passed
  (e2e stored-bytes match, 3 rejection-before-storage cases, 401, cross-user 404);
  full suite `python -m pytest backend/tests/` → 15 passed, 1 skipped.
- Commit: `bc3131a feat(upload): validated upload endpoint with Storage and stub parsing task`

## Backfilled: two small commits that shipped without diary entries (rule fix)
- `ad46dcd test: fix misleading bypass comment in health tests` — corrected the
  `test_me_rejects_missing_token` comment (bypass is ON; None creds reject before
  bypass logic). Verified: `test_health.py` 4 passed.
- `60619bf chore: drop duplicated .next entry in gitignore` — removed the repeated
  `.next/` line. No behavior change.

## 2026-09-26 — harden(upload): orphan compensation + bounded read + tests
- What (3 one-file commits): `927e141` added best-effort `delete()` to
  `StorageService`/Supabase impl; `975dc3e` wrapped upload+commit in try/except
  (rollback + orphan delete + 502) and capped body reads at limit+1 bytes;
  `dcc1420` added `FakeStorage.delete` + 2 tests (storage-failure rollback,
  commit-failure compensation). Found by a two-agent sweep (storage verified live:
  project reachable, both buckets private, Auth healthy; backend audited green).
- Commands: `python -m pytest backend/tests/test_upload.py -v` → 9 passed;
  full suite → 17 passed, 1 skipped (15 old + 2 new).
- Commits: `927e141`, `975dc3e`, `dcc1420`

## 2026-09-26 — fix(llm): retired default models → live-verified IDs (backfill)
- What: the user's Gemini key worked, but `gemini-2.0-flash` is retired (live 404)
  and `text-embedding-004` is gone from the models list. Queried
  `v1beta/models` live: generation default → `gemini-3.8-flash` (first tried
  `gemini-2.5-flash`, rejected for new free-tier accounts; one transient 503 on
  3.8-flash cleared after 70s), embedding → `gemini-embedding-001` (3072-dim —
  NOTE for Prompt 2: pgvector column width must fit 3072, not 768).
- Commands: live `generate('Reply with exactly: ok')` → `ok`;
  `embed('hello world')` → 3072 floats; `test_llm_client.py` → 3 passed.
- Commits (one file each): `7d23f33` config.py, `9a586a7` .env.example,
  `41dc53a` render.yaml.

## 2026-09-26 — Phase 0 Prompt 4 DONE: 50 synthetic resumes + 20 JDs in bucket
- What: `backend/scripts/generate_test_dataset.py` (seeded RNG, zero network/LLM
  calls): 50 resumes 10 roles×5 (35 PDF in 3 layouts, 10 DOCX incl. tables,
  5 scanned image-only PDFs), 20 JDs (junior+senior per family), manifest +
  bucket README. Identities obviously fake (Demo/Testerson/TestCorp/@example.com).
  Verified: 72 files, none empty, DOCX opens (20 paras), scanned PDF has 0 text
  chars (correct — exercises OCR path), multi-page resume present. Uploaded 72/72
  to private bucket `test-dataset` via storage API; bucket listing confirms 72
  incl. manifest + README. Local `test-data/` gitignored; generator committed.
- Commands: `python backend/scripts/generate_test_dataset.py --out test-data
  --resumes 50 --jds 20 --seed 42`; bucket list check → 72 objects.
- Commits (one file each): `06ebf0f` requirements (docx 1.2.0 + pillow 12.2.0),
  `458b606` generator, `0157022` gitignore test-data/.
