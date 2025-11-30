"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255)),
        sa.Column("plan", sa.Enum("free", "pro", "admin", name="userplan"), default="free"),
        sa.Column("usage_seconds", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "voice_personas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.Enum("pending", "training", "ready", "failed", name="personastatus"), default="pending"),
        sa.Column("sample_paths", postgresql.ARRAY(sa.String)),
        sa.Column("model_path", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("voice_persona_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("voice_personas.id")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.Enum("created", "uploading", "processing_stems", "stems_ready", "generating_vocals", "vocals_ready", "mixing", "completed", "failed", name="projectstatus"), default="created"),
        sa.Column("vocal_mode", sa.Enum("remove", "replace", "blend", name="vocalmode"), default="replace"),
        sa.Column("original_path", sa.String(500)),
        sa.Column("stems_path", sa.String(500)),
        sa.Column("vocals_path", sa.String(500)),
        sa.Column("output_path", sa.String(500)),
        sa.Column("duration_seconds", sa.Float),
        sa.Column("mix_settings", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id")),
        sa.Column("voice_persona_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("voice_personas.id")),
        sa.Column("task_type", sa.Enum("stem_separation", "voice_training", "vocal_generation", "mixing", name="tasktype"), nullable=False),
        sa.Column("status", sa.Enum("pending", "running", "completed", "failed", name="taskstatus"), default="pending"),
        sa.Column("progress", sa.Integer, default=0),
        sa.Column("error_message", sa.Text),
        sa.Column("celery_task_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("tasks")
    op.drop_table("projects")
    op.drop_table("voice_personas")
    op.drop_table("users")
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS taskstatus")
    op.execute("DROP TYPE IF EXISTS tasktype")
    op.execute("DROP TYPE IF EXISTS vocalmode")
    op.execute("DROP TYPE IF EXISTS projectstatus")
    op.execute("DROP TYPE IF EXISTS personastatus")
    op.execute("DROP TYPE IF EXISTS userplan")
