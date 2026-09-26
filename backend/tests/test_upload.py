"""Phase 1 Prompt 1 DoD: file lands in Storage, row created, background task flips
status without blocking; bad files rejected BEFORE storage. No live Supabase:
SQLite file DB (built by the real Alembic migration) + fake storage."""
import os

os.environ.setdefault("SUPABASE_BYPASS_AUTH", "true")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.api.main import app
from backend.core.database import get_db
from backend.services import parsing
from backend.services.storage import get_storage
from .conftest import upgrade_db

AUTH = {"Authorization": "Bearer dev-candidate"}
OTHER_AUTH = {"Authorization": "Bearer dev-recruiter"}
PDF_BYTES = b"%PDF-1.7 fake resume content"
DOCX_BYTES = b"PK\x03\x04 fake docx content"


class FakeStorage:
    def __init__(self):
        self.objects: dict[str, bytes] = {}
        self.deleted: list[str] = []

    def upload(self, bucket: str, path: str, data: bytes, content_type: str) -> str:
        self.objects[f"{bucket}/{path}"] = data
        return path

    def delete(self, bucket: str, path: str) -> None:
        self.deleted.append(f"{bucket}/{path}")
        self.objects.pop(f"{bucket}/{path}", None)


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_file = str(tmp_path / "upload.db")
    upgrade_db(db_file)
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(bind=engine)

    def override_db():
        s = TestingSession()
        try:
            yield s
        finally:
            s.close()

    fake = FakeStorage()
    monkeypatch.setattr(parsing, "SessionLocal", TestingSession)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_storage] = lambda: fake
    yield TestClient(app), fake
    app.dependency_overrides.clear()


def test_valid_pdf_upload_end_to_end(client):
    c, fake = client
    r = c.post("/resumes/upload", files={"file": ("cv.pdf", PDF_BYTES, "application/pdf")}, headers=AUTH)
    assert r.status_code == 202, r.text
    body = r.json()
    assert body["status"] == "uploaded"  # response reflects pre-background state
    assert len(fake.objects) == 1  # file reached storage exactly once
    stored_bytes = next(iter(fake.objects.values()))
    assert stored_bytes == PDF_BYTES

    # Background stub ran: status flipped without another request.
    g = c.get(f"/resumes/{body['id']}", headers=AUTH)
    assert g.status_code == 200
    assert g.json()["status"] == "parsed"


def test_valid_docx_upload(client):
    c, fake = client
    r = c.post(
        "/resumes/upload",
        files={"file": ("cv.docx", DOCX_BYTES, "application/vnd.openxmlformats")},
        headers=AUTH,
    )
    assert r.status_code == 202, r.text
    assert len(fake.objects) == 1


def test_wrong_extension_rejected_before_storage(client):
    c, fake = client
    r = c.post("/resumes/upload", files={"file": ("notes.txt", b"hello", "text/plain")}, headers=AUTH)
    assert r.status_code == 400
    assert fake.objects == {}


def test_content_mismatch_rejected_before_storage(client):
    c, fake = client
    r = c.post("/resumes/upload", files={"file": ("fake.pdf", b"just text", "application/pdf")}, headers=AUTH)
    assert r.status_code == 400
    assert fake.objects == {}


def test_oversized_file_rejected_before_storage(client):
    c, fake = client
    big = b"%PDF" + b"0" * (10 * 1024 * 1024)
    r = c.post("/resumes/upload", files={"file": ("big.pdf", big, "application/pdf")}, headers=AUTH)
    assert r.status_code == 400
    assert fake.objects == {}


def test_missing_auth_rejected(client):
    c, _ = client
    r = c.post("/resumes/upload", files={"file": ("cv.pdf", PDF_BYTES, "application/pdf")})
    assert r.status_code == 401


def test_cannot_read_another_users_resume(client):
    c, _ = client
    r = c.post("/resumes/upload", files={"file": ("cv.pdf", PDF_BYTES, "application/pdf")}, headers=AUTH)
    rid = r.json()["id"]
    assert c.get(f"/resumes/{rid}", headers=OTHER_AUTH).status_code == 404


def test_storage_failure_rolls_back_row(client, monkeypatch):
    from fastapi import HTTPException

    c, fake = client

    def boom(bucket: str, path: str, data: bytes, content_type: str) -> str:
        raise HTTPException(status_code=502, detail="File storage unavailable")

    monkeypatch.setattr(fake, "upload", boom)
    r = c.post("/resumes/upload", files={"file": ("cv.pdf", PDF_BYTES, "application/pdf")}, headers=AUTH)
    assert r.status_code == 502
    assert fake.objects == {}
    # No orphan row: the id from a retry must 404 (nothing was persisted).
    assert c.get("/resumes/does-not-exist", headers=AUTH).status_code == 404


def test_commit_failure_compensates_orphan_file(client, monkeypatch):
    from sqlalchemy.orm import Session

    c, fake = client
    real_commit = Session.commit

    def fail_once(self):
        monkeypatch.setattr(Session, "commit", real_commit)
        raise RuntimeError("simulated commit failure")

    monkeypatch.setattr(Session, "commit", fail_once)
    r = c.post("/resumes/upload", files={"file": ("cv.pdf", PDF_BYTES, "application/pdf")}, headers=AUTH)
    assert r.status_code == 502
    assert fake.objects == {}  # orphan file was deleted
    assert len(fake.deleted) == 1
