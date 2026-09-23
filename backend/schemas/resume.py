from datetime import datetime
from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    id: str
    status: str
    filename: str


class ResumeStatusResponse(BaseModel):
    id: str
    filename: str
    status: str
    error: str = ""
    size_bytes: int = 0
    created_at: datetime | None = None
