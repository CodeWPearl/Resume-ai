"""Phase 1 Prompt 1: migration executes and produces the expected tables."""
import os
from sqlalchemy import create_engine, inspect

from .conftest import upgrade_db

os.environ.setdefault("SUPABASE_BYPASS_AUTH", "true")


def test_upgrade_creates_resume_tables(tmp_path):
    db = str(tmp_path / "mig.db")
    upgrade_db(db)
    insp = inspect(create_engine(f"sqlite:///{db}"))
    tables = set(insp.get_table_names())
    assert {"resumes", "parsed_resume_data", "alembic_version"} <= tables

    cols = {c["name"] for c in insp.get_columns("resumes")}
    assert {"id", "user_id", "org_id", "filename", "storage_path", "status"} <= cols
    pcols = {c["name"] for c in insp.get_columns("parsed_resume_data")}
    assert {"id", "resume_id", "skills", "experience", "contact"} <= pcols


def test_downgrade_reverses_upgrade(tmp_path):
    db = str(tmp_path / "mig-down.db")
    upgrade_db(db)
    os.environ["DATABASE_URL"] = f"sqlite:///{db}"
    from alembic.config import Config
    from alembic import command
    from .conftest import BACKEND_ROOT

    cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    command.downgrade(cfg, "base")
    insp = inspect(create_engine(f"sqlite:///{db}"))
    assert "resumes" not in set(insp.get_table_names())
