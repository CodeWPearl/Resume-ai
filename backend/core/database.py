"""SQLAlchemy engine + session. Supabase Postgres with pgvector (enable pgvector in Supabase dashboard, not code)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import get_settings

settings = get_settings()

# pool_pre_ping protects against Supabase pooler dropping idle connections (7-day pause / free tier).
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
