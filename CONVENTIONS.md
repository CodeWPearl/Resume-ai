# CONVENTIONS — ResumeIQ final stack (do not change without updating this file)

Frontend: Next.js + TypeScript + Tailwind CSS + shadcn/ui, deployed on Vercel (Hobby).
  Design system: Impeccable (`/impeccable` skill in .opencode) — PRODUCT.md + DESIGN.md
  are the source of truth for UX copy, colors, type, components. Run
  `npx impeccable detect <dir>` before shipping UI.
Backend: Python + FastAPI on Render Free Web Service (upgrade to $7/mo only demo week).
Async: FastAPI BackgroundTasks ONLY — no Celery, no separate worker (750 instance-hrs budget).
DB: Supabase PostgreSQL + pgvector (enable extension in dashboard). 500MB, pauses after 7d idle.
Storage: Supabase Storage (private bucket `resumes-private`), never commit resumes to git.
Auth: Clerk (free, 50k MAU) with roles candidate|recruiter|admin. Local dev may use
  CLERK_BYPASS_AUTH=true + `Bearer dev-<role>` tokens. Never true in prod.
Cache: Upstash Redis (free, 500k cmds/mo), optional/best-effort only.
Embeddings: Gemini text-embedding-004 via internal wrapper ONLY (services/llm_client.py).
LLM: Gemini via wrapper generate()/embed(). GEMINI_TIER=free => synthetic/test data ONLY.
  Flip to paid before real resumes (see README switch procedure).
Extraction: PyMuPDF, python-docx, pytesseract OCR fallback, spaCy NER.
PDF reports: ReportLab ONLY — never WeasyPrint (needs Pango/Cairo missing on Render).
ORM: SQLAlchemy + Alembic. Tests: pytest (backend), Jest+RTL (frontend).
CI: GitHub Actions lint/test only — no Docker build (Render/Vercel build from repo).
Monitoring: Render logs + free UptimeRobot on /health.

FORBIDDEN without updating this block: Docker, Celery, Railway, self-hosted embeddings, WeasyPrint.
Prompts live in backend/prompts/<version>/*.txt and are loaded via load_prompt() — never inline.
Guardrail (Phase 3+): every generation = generate + fact-check calls; flagged rows stored with flag, never silently dropped.
