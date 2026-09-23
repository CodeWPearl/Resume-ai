"""Shared test helpers. No live Supabase needed: migrations + endpoints run
against throwaway SQLite files; Supabase Storage is replaced by a fake."""
import os
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent


def upgrade_db(sqlite_path: str) -> None:
    """Run `alembic upgrade head` against a SQLite file. Proves the migration
    executes for real (SQLite stands in for Postgres here; the same migration
    runs via `alembic upgrade head` with DATABASE_URL on Supabase)."""
    os.environ["DATABASE_URL"] = f"sqlite:///{sqlite_path}"
    from alembic.config import Config
    from alembic import command

    cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    command.upgrade(cfg, "head")
