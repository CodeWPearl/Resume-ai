"""Supabase Storage access. Server-side uploads use the service-role key against
a PRIVATE bucket. Swappable via FastAPI dependency override in tests."""
import logging
from fastapi import HTTPException

from backend.core.config import get_settings

logger = logging.getLogger(__name__)


class StorageService:
    def upload(self, bucket: str, path: str, data: bytes, content_type: str) -> str:
        raise NotImplementedError

    def delete(self, bucket: str, path: str) -> None:
        """Best-effort removal (orphan compensation). Must never raise."""
        raise NotImplementedError


class SupabaseStorageService(StorageService):
    def __init__(self):
        settings = get_settings()
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise HTTPException(status_code=500, detail="Supabase storage not configured")
        from supabase import create_client

        self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    def upload(self, bucket: str, path: str, data: bytes, content_type: str) -> str:
        try:
            self._client.storage.from_(bucket).upload(
                path, data, {"content-type": content_type, "upsert": "false"}
            )
        except Exception as e:  # noqa: BLE001
            logger.exception("Storage upload failed for %s/%s", bucket, path)
            raise HTTPException(status_code=502, detail="File storage unavailable") from e
        return path

    def delete(self, bucket: str, path: str) -> None:
        try:
            self._client.storage.from_(bucket).remove([path])
        except Exception:  # noqa: BLE001
            logger.exception("Storage delete failed for %s/%s (orphan)", bucket, path)


def get_storage() -> StorageService:
    return SupabaseStorageService()
