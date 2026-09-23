# ResumeIQ — AI resume-intelligence platform

Three portals (candidate / recruiter / admin) sharing one scoring/matching
engine, so the score a candidate sees and the score a recruiter sees are
computed identically. Full build order lives in
`12_FINAL_STACK_AGENT_PROMPTS.md`; agent operating rules in `AGENTS.md`;
per-change diary in `WORK_LOG.md`; design system in `PRODUCT.md` + `DESIGN.md`.

## Quickstart (local dev)
```powershell
# Backend (repo root) — needs Python 3.12+
pip install -r backend/requirements.txt
$env:SUPABASE_BYPASS_AUTH="true"       # local dev only, NEVER prod
python -m pytest backend/tests/ -v
uvicorn backend.api.main:app --reload  # :8000, /health

# Frontend (frontend/) — needs Node 20+
npm ci
npx tsc --noEmit; npm run lint
npm run dev                            # :3000
```
Copy `backend/.env.example` → `backend/.env` and `frontend/.env.example` →
`frontend/.env.local` and fill real keys (never commit them).

## Service plans + limits (don't forget these in 3 phases)
| Service | Plan | Limits that bite |
|---|---|---|
| Render (API) | Free Web Service | Cold start ~60s after idle; 0.1 CPU / 512MB RAM; 750 instance-hours/month shared across ALL services (no separate worker — BackgroundTasks in-process only). Upgrade to $7/mo only for demo week. |
| Vercel (UI) | Hobby | Builds from repo; env vars in dashboard. |
| Supabase (DB+Storage) | Free | 500MB Postgres; pauses after 7 days idle; enable `pgvector` in dashboard. Resumes in PRIVATE bucket, never git. |
| Supabase Auth | Free | Roles candidate\|recruiter\|admin via `user_metadata.role` (set at sign-up; admins in dashboard). |
| Upstash Redis | Free (500k cmds/mo) | Optional/best-effort cache only; misses must degrade, never error. |
| Gemini | FREE tier in dev | Tight RPM/day caps (expect 429s — client backs off); **free tier may train on prompts/responses → synthetic/test resumes ONLY**. Flip `GEMINI_TIER` to `paid` + pin model version before any real resume. |

Secrets live in Render/Vercel dashboards, never in code (audited: no keys in repo).
