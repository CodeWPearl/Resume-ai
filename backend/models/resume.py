"""Phase 1 tables. (No /docs schema file exists in repo — designed from the table
names in 12_FINAL_STACK_AGENT_PROMPTS.md: resumes, parsed_resume_data.)

Status flow: uploaded -> parsing -> parsed | failed. Prompt 2 fills the JSON
columns and adds the pgvector embedding column + real parsing logic.
"""
import uuid
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

RESUME_STATUSES = ("uploaded", "parsing", "parsed", "failed")


def new_id() -> str:
    return str(uuid.uuid4())


class ResumeRecord(Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    org_id: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    size_bytes: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="uploaded", index=True)
    error: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    parsed: Mapped["ParsedResumeData | None"] = relationship(
        back_populates="resume", uselist=False, cascade="all, delete-orphan"
    )


class ParsedResumeData(Base):
    __tablename__ = "parsed_resume_data"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    resume_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    contact: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    experience: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    education: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    projects: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    certifications: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    languages: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    resume: Mapped[ResumeRecord] = relationship(back_populates="parsed")
