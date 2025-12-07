"""Add indexes for query performance

Revision ID: b5c8d3e2f1a6
Revises: a3b7c9d2e1f4
Create Date: 2024-02-01
"""
from alembic import op

revision = "b5c8d3e2f1a6"
down_revision = "a3b7c9d2e1f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add indexes for foreign keys and frequently queried columns."""

    # Users table - email index for login lookups
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # Voice personas - user lookup and status filtering
    op.create_index("ix_voice_personas_user_id", "voice_personas", ["user_id"])
    op.create_index("ix_voice_personas_status", "voice_personas", ["status"])

    # Projects - user lookup, status filtering, and created_at for sorting
    op.create_index("ix_projects_user_id", "projects", ["user_id"])
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_index("ix_projects_created_at", "projects", ["created_at"])
    # Composite index for common query pattern: user's projects sorted by date
    op.create_index(
        "ix_projects_user_created",
        "projects",
        ["user_id", "created_at"],
    )

    # Tasks - project/persona lookup and status filtering
    op.create_index("ix_tasks_project_id", "tasks", ["project_id"])
    op.create_index("ix_tasks_voice_persona_id", "tasks", ["voice_persona_id"])
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_celery_task_id", "tasks", ["celery_task_id"])


def downgrade() -> None:
    """Remove all added indexes."""

    # Tasks indexes
    op.drop_index("ix_tasks_celery_task_id", table_name="tasks")
    op.drop_index("ix_tasks_status", table_name="tasks")
    op.drop_index("ix_tasks_voice_persona_id", table_name="tasks")
    op.drop_index("ix_tasks_project_id", table_name="tasks")

    # Projects indexes
    op.drop_index("ix_projects_user_created", table_name="projects")
    op.drop_index("ix_projects_created_at", table_name="projects")
    op.drop_index("ix_projects_status", table_name="projects")
    op.drop_index("ix_projects_user_id", table_name="projects")

    # Voice personas indexes
    op.drop_index("ix_voice_personas_status", table_name="voice_personas")
    op.drop_index("ix_voice_personas_user_id", table_name="voice_personas")

    # Users indexes
    op.drop_index("ix_users_email", table_name="users")
