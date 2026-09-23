"""Create resumes + parsed_resume_data tables (Phase 1 Prompt 1).

Revision ID: 0001_resumes
Revises: None (first migration)
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_resumes"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "resumes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("org_id", sa.String(128), nullable=False, server_default=""),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("storage_path", sa.String(1024), nullable=False),
        sa.Column("mime_type", sa.String(128), nullable=False, server_default=""),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(16), nullable=False, server_default="uploaded"),
        sa.Column("error", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])
    op.create_index("ix_resumes_status", "resumes", ["status"])
    op.create_table(
        "parsed_resume_data",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "resume_id",
            sa.String(36),
            sa.ForeignKey("resumes.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("raw_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("contact", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("skills", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("experience", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("education", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("projects", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("certifications", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("languages", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("parsed_resume_data")
    op.drop_index("ix_resumes_status", table_name="resumes")
    op.drop_index("ix_resumes_user_id", table_name="resumes")
    op.drop_table("resumes")
