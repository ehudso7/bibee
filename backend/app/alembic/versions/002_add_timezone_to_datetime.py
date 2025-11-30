"""Add timezone support to datetime columns

Revision ID: a3b7c9d2e1f4
Revises: 001
Create Date: 2024-01-15
"""
from alembic import op

revision = "a3b7c9d2e1f4"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert all datetime columns to timezone-aware timestamps
    # Using AT TIME ZONE 'UTC' to interpret existing naive timestamps as UTC

    # Users table
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING created_at AT TIME ZONE 'UTC'
    """)
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING updated_at AT TIME ZONE 'UTC'
    """)

    # Voice personas table
    op.execute("""
        ALTER TABLE voice_personas
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING created_at AT TIME ZONE 'UTC'
    """)
    op.execute("""
        ALTER TABLE voice_personas
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING updated_at AT TIME ZONE 'UTC'
    """)

    # Projects table
    op.execute("""
        ALTER TABLE projects
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING created_at AT TIME ZONE 'UTC'
    """)
    op.execute("""
        ALTER TABLE projects
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING updated_at AT TIME ZONE 'UTC'
    """)

    # Tasks table
    op.execute("""
        ALTER TABLE tasks
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING created_at AT TIME ZONE 'UTC'
    """)
    op.execute("""
        ALTER TABLE tasks
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING updated_at AT TIME ZONE 'UTC'
    """)


def downgrade() -> None:
    # Revert to naive datetime columns
    # Note: This will lose timezone information

    # Users table
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
    """)
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
    """)

    # Voice personas table
    op.execute("""
        ALTER TABLE voice_personas
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
    """)
    op.execute("""
        ALTER TABLE voice_personas
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
    """)

    # Projects table
    op.execute("""
        ALTER TABLE projects
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
    """)
    op.execute("""
        ALTER TABLE projects
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
    """)

    # Tasks table
    op.execute("""
        ALTER TABLE tasks
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
    """)
    op.execute("""
        ALTER TABLE tasks
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
    """)
