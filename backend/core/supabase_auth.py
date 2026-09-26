"""Supabase Auth with three roles: candidate | recruiter | admin.

Role lives in the user's `user_metadata.role` (set at sign-up or edited in the
Supabase dashboard under Auth > Users). Tokens are validated against the live
Supabase Auth server via `auth.get_user()`, so no local key/algorithm
assumptions can drift out of date.

If SUPABASE_BYPASS_AUTH=true (local dev only), accepts
`Authorization: Bearer dev-<role>`, e.g. `Bearer dev-candidate`.
In prod, missing/invalid tokens are rejected with 401.
"""
from dataclasses import dataclass
from functools import lru_cache
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import get_settings

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)

ALLOWED_ROLES = {"candidate", "recruiter", "admin"}


@dataclass
class CurrentUser:
    user_id: str
    role: str
    email: str = ""
    org_id: str = ""


@lru_cache
def _get_client():
    settings = get_settings()
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="SUPABASE_URL/ANON_KEY not configured")
    from supabase import create_client

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    settings = get_settings()
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth token")
    token = creds.credentials

    # Local-dev bypass (never in production — guarded in config).
    if settings.SUPABASE_BYPASS_AUTH:
        if token.startswith("dev-"):
            role = token.removeprefix("dev-")
            if role not in ALLOWED_ROLES:
                raise HTTPException(status_code=401, detail="Invalid dev role")
            return CurrentUser(user_id=f"dev-{role}", role=role, email=f"{role}@test.local")
        raise HTTPException(status_code=401, detail="Invalid dev token")

    # Production path: validate against the Supabase Auth server.
    # Client construction stays OUTSIDE the try: a broken server setup must
    # surface as 500, never masquerade as an invalid user token (401).
    client = _get_client()
    try:
        resp = client.auth.get_user(token)
        user = resp.user
    except Exception as e:  # noqa: BLE001
        logger.warning("Supabase token rejected: %s", e)
        raise HTTPException(status_code=401, detail="Invalid auth token")
    if user is None or not user.id:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    meta = user.user_metadata or {}
    role = meta.get("role", "candidate")
    if role not in ALLOWED_ROLES:
        role = "candidate"
    return CurrentUser(
        user_id=user.id,
        role=role,
        email=user.email or "",
        org_id=str(meta.get("org_id", "") or ""),
    )


def require_role(*roles: str):
    def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles and user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden for role " + user.role)
        return user

    return checker
