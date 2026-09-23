import os
os.environ.setdefault("SUPABASE_BYPASS_AUTH", "true")
os.environ.setdefault("GEMINI_TIER", "free")

from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_me_rejects_missing_token():
    # Bypass is ON, but a missing token must still 401: HTTPBearer(auto_error=False)
    # yields None creds, and get_current_user rejects before any bypass logic.
    r = client.get("/me")
    assert r.status_code in (401, 403)


def test_me_accepts_dev_candidate():
    r = client.get("/me", headers={"Authorization": "Bearer dev-candidate"})
    assert r.status_code == 200
    assert r.json()["role"] == "candidate"


def test_me_rejects_bad_token():
    r = client.get("/me", headers={"Authorization": "Bearer dev-superuser"})
    assert r.status_code == 401
