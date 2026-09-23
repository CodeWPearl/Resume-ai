"""Central app config. All secrets come from environment, never hardcoded."""
from functools import lru_cache
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: str = "development"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/resumeiq"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "resumes-private"

    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_JWKS_URL: str = ""
    CLERK_BYPASS_AUTH: bool = False

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_EMBED_MODEL: str = "text-embedding-004"
    GEMINI_TIER: str = "free"  # free | paid

    UPSTASH_REDIS_URL: str = ""
    UPSTASH_REDIS_TOKEN: str = ""

    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if s.GEMINI_TIER == "free":
        logger.warning(
            "GEMINI_TIER=free: Google may use prompts/responses for product improvement. "
            "Use ONLY synthetic/test resumes. Switch to paid before real user data."
        )
    if s.CLERK_BYPASS_AUTH and s.ENV == "production":
        raise RuntimeError("CLERK_BYPASS_AUTH must never be true in production")
    return s
