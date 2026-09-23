# AGENTS.md — Operating rules for coding agents on ResumeIQ

Read this file before writing any code. `CONVENTIONS.md` (stack) and
`DESIGN.md` + `PRODUCT.md` (frontend design system) are companion docs.

## 1. Project identity
ResumeIQ: AI resume-intelligence platform, three portals (candidate / recruiter /
admin) sharing one scoring/matching engine. Highest-risk feature: anything that
rewrites or generates resume content — it must NEVER invent facts (guardrail:
constrained prompts + post-generation fact-check, built once, reused everywhere).

## 2. Stack (frozen — see CONVENTIONS.md)
Next.js+TS+Tailwind+shadcn (Vercel) / FastAPI (Render Free, BackgroundTasks ONLY) /
Supabase Postgres+pgvector + Storage + Auth / roles (candidate|recruiter|admin) /
Upstash Redis (optional cache) / Gemini via `backend/services/llm_client.py` ONLY.
FORBIDDEN: Docker, Celery, Railway, self-hosted embeddings, WeasyPrint.
Prompts live in `backend/prompts/<version>/*.txt`, loaded via `load_prompt()` —
never inline in business logic.

## 3. Everyday commands
```powershell
# Backend (from repo root)
python -m pytest backend/tests/ -v
uvicorn backend.api.main:app --reload            # local API on :8000
$env:SUPABASE_BYPASS_AUTH="true"             # local dev auth bypass (NEVER prod)

# Frontend (from frontend/)
npx tsc --noEmit
npm run lint
npm run build
npm run dev                                      # local UI on :3000

# Design quality (from repo root, Impeccable skill in .opencode/)
npx impeccable detect frontend/src
```
Reinstall the Impeccable engine (binaries are gitignored) with:
`npx impeccable install --providers=opencode --scope=project -y`

## 4. Workflow rules
- Work phase by phase per `12_FINAL_STACK_AGENT_PROMPTS.md`: ONE prompt, verify
  its Definition of Done, then the next. Never skip verification.
- Verify with execution: run tests/typecheck/build, don't assert from memory.
- Frontend changes must respect `DESIGN.md` tokens/components and pass
  `npx impeccable detect frontend/src` (no purple gradients, no glow, 40px+
  touch targets, cold-start/empty/error states with honest copy).
- Backend: every generation path routes through the shared guardrail; flagged
  content is stored flagged and shown flagged — never silently dropped/accepted.
- `GEMINI_TIER=free` => synthetic/test resumes ONLY. Never send real resumes.

## 5. Git rules (strict)
- NEVER commit: real `.env` files, `node_modules`, `.next`, `*.pdf`/`*.docx`
  resumes, Impeccable `scripts/bin/` binaries, or any secret.
- One logical change per commit, each pushed individually (`git push origin main`
  after every commit) — never batch unrelated work into one push.
- Every change updates `WORK_LOG.md` (what / how / commands / verification /
  commit hash) in the SAME commit as the change it describes.
- Inspect `git status --short`, `git diff --cached --stat`, `git log --oneline -10`
  before every commit. Stage only intended files.
