"""FastAPI entrypoint."""
import logging
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.resumes import router as resumes_router
from backend.core.config import get_settings
from backend.core.supabase_auth import get_current_user, CurrentUser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title="ResumeIQ API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(resumes_router)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV, "gemini_tier": settings.GEMINI_TIER}


@app.get("/me")
def me(user: CurrentUser = Depends(get_current_user)):
    """Auth probe: proves the role middleware works. Frontend uses /health unauthenticated."""
    return {"user_id": user.user_id, "role": user.role, "org_id": user.org_id}
