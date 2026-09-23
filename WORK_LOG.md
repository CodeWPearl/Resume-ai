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
- Commit: `75e58b0 docs: add WORK_LOG.md build diary with per-change history`
