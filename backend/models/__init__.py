from .database import Base  # noqa: F401  (Alembic imports this)
# Phase 1+ models (resumes, parsed_resume_data, ...) will be added here.
# Keep this import surface stable so alembic env.py never changes.
