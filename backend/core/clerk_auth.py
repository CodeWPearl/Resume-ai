"""Clerk JWT auth with three roles: candidate | recruiter | admin.

If CLERK_BYPASS_AUTH=true (local dev only), accepts `Authorization: Bearer dev-<role>`
e.g. `Bearer dev-candidate`. In prod it verifies the JWT via Clerk JWKS and
rejects missing/invalid tokens with 401.
Role is read from claims: public_metadata.role > metadata.role > role > org_role.
"""
from dataclasses import dataclass
import logging
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from .config import get_settings

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)

ALLOWED_ROLES = {"candidate", "recruiter", "admin"}
_JWKS_CACHE: dict | None = None


@dataclass
class CurrentUser:
    user_id: str
    role: str
    email: str = ""
    org_id: str = ""


def _get_jwks() -> dict:
    global _JWKS_CACHE
    if _JWKS_CACHE is not None:
        return _JWKS_CACHE
    settings = get_settings()
    if not settings.CLERK_JWKS_URL:
        raise HTTPException(status_code=500, detail="CLERK_JWKS_URL not configured")
    resp = httpx.get(settings.CLERK_JWKS_URL, timeout=10.0)
    resp.raise_for_status()
    _JWKS_CACHE = resp.json()
    return _JWKS_CACHE


def _role_from_claims(claims: dict) -> str:
    for path in (("public_metadata", "role"), ("metadata", "role"),):
        node = claims
        try:
            for key in path:
                node = node.get(key, {})
            if isinstance(node, str) and node in ALLOWED_ROLES:
                return node
        except Exception:
            continue
    for key in ("role", "org_role"):
        if claims.get(key) in ALLOWED_ROLES:
            return claims[key]
    return "candidate"


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    settings = get_settings()
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth token")
    token = creds.credentials

    # Local-dev bypass (never in production — guarded in config).
    if settings.CLERK_BYPASS_AUTH:
        if token.startswith("dev-"):
            role = token.removeprefix("dev-")
            if role not in ALLOWED_ROLES:
                raise HTTPException(status_code=401, detail="Invalid dev role")
            return CurrentUser(user_id=f"dev-{role}", role=role, email=f"{role}@test.local")
        raise HTTPException(status_code=401, detail="Invalid dev token")

    # Production path: verify via Clerk JWKS.
    try:
        jwks = _get_jwks()
        # jose needs the key set; verify signature + expiry. Audience/issuer checks
        # are intentionally lenient here — tighten to your Clerk issuer in prod.
        claims = jwt.decode(token, jwks, options={"verify_aud": False})
    except Exception as e:
        logger.warning("Clerk token rejected: %s", e)
        raise HTTPException(status_code=401, detail="Invalid auth token")
    user_id = claims.get("sub", "")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    return CurrentUser(
        user_id=user_id,
        role=_role_from_claims(claims),
        email=claims.get("email", ""),
        org_id=claims.get("org_id", "") or claims.get("org", ""),
    )


def require_role(*roles: str):
    def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles and user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden for role " + user.role)
        return user

    return checker
