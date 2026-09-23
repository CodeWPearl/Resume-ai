"""Background parsing tasks (FastAPI BackgroundTasks — no worker service).

Phase 1 Prompt 1 ships the STUB only: flip uploaded -> parsing -> parsed so the
end-to-end wiring is provably correct. Prompt 2 replaces the body with text
extraction + structured extraction + embeddings, writing parsed_resume_data.
"""
import logging

from backend.core.database import SessionLocal
from backend.models.resume import ResumeRecord

logger = logging.getLogger(__name__)


def parse_resume_stub(resume_id: str) -> None:
    db = SessionLocal()
    try:
        resume = db.get(ResumeRecord, resume_id)
        if resume is None:
            logger.error("parse stub: resume %s not found", resume_id)
            return
        resume.status = "parsing"
        db.commit()
        # Real pipeline lands here in Prompt 2.
        resume.status = "parsed"
        db.commit()
    except Exception:  # noqa: BLE001
        logger.exception("parse stub failed for resume %s", resume_id)
        try:
            resume = db.get(ResumeRecord, resume_id)
            if resume is not None:
                resume.status = "failed"
                resume.error = "parsing failed (stub)"
                db.commit()
        except Exception:  # noqa: BLE001
            db.rollback()
    finally:
        db.close()
