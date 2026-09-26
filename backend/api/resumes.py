"""Resume upload (Phase 1 Prompt 1): validate -> Supabase Storage -> resumes row
(status "uploaded") -> BackgroundTasks stub parsing. No Celery anywhere."""
import os
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.database import get_db
from backend.core.supabase_auth import CurrentUser, get_current_user
from backend.models.resume import ResumeRecord
from backend.schemas.resume import ResumeStatusResponse, ResumeUploadResponse
from backend.services import parsing
from backend.services.storage import get_storage

router = APIRouter(prefix="/resumes", tags=["resumes"])

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAGIC_BYTES = {".pdf": b"%PDF", ".docx": b"PK\x03\x04"}


def _validate(filename: str | None, data: bytes, limit_bytes: int) -> str:
    """Returns the lowercase extension. Raises 400 before anything touches storage."""
    if not filename or "." not in os.path.basename(filename):
        raise HTTPException(status_code=400, detail="A PDF or DOCX filename is required")
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are accepted")
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    if len(data) > limit_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {limit_bytes // (1024 * 1024)}MB limit",
        )
    if not data.startswith(MAGIC_BYTES[ext]):
        raise HTTPException(status_code=400, detail="File content does not match its extension")
    return ext


def _safe_filename(filename: str) -> str:
    base = os.path.basename(filename).strip().replace(" ", "_")
    return "".join(c for c in base if c.isalnum() or c in ("-", "_", "."))


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_resume(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage=Depends(get_storage),
):
    settings = get_settings()
    limit_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    # Bounded read: never buffer more than limit+1 bytes (Render Free has 512MB).
    data = await file.read(limit_bytes + 1)
    _validate(file.filename, data, limit_bytes)

    resume = ResumeRecord(
        user_id=user.user_id,
        org_id=user.org_id,
        filename=_safe_filename(file.filename or "resume"),
        storage_path="",  # filled after we know the id
        mime_type=file.content_type or "",
        size_bytes=len(data),
        status="uploaded",
    )
    db.add(resume)
    db.flush()  # assign id before building the storage path
    assert resume.id is not None
    resume.storage_path = f"{user.user_id}/{resume.id}/{resume.filename}"
    try:
        storage.upload(settings.SUPABASE_STORAGE_BUCKET, resume.storage_path, data, resume.mime_type)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:  # noqa: BLE001
        # Storage succeeded but the row did not persist (or vice versa) — roll back
        # and remove any orphan file so no phantom objects accumulate.
        db.rollback()
        storage.delete(settings.SUPABASE_STORAGE_BUCKET, resume.storage_path)
        raise HTTPException(status_code=502, detail="Could not save upload") from e

    background.add_task(parsing.parse_resume_stub, resume.id)
    return ResumeUploadResponse(id=resume.id, status="uploaded", filename=resume.filename)


@router.get("/{resume_id}", response_model=ResumeStatusResponse)
def get_resume(
    resume_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.get(ResumeRecord, resume_id)
    if resume is None or (resume.user_id != user.user_id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Resume not found")
    return ResumeStatusResponse(
        id=resume.id,
        filename=resume.filename,
        status=resume.status,
        error=resume.error,
        size_bytes=resume.size_bytes,
        created_at=resume.created_at,
    )
