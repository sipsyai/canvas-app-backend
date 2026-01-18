"""Fix datetime timezone and add application label

Revision ID: 517f0ef4cd0b
Revises: 818919cb752e
Create Date: 2026-01-18 17:05:31.740911

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '517f0ef4cd0b'
down_revision = '818919cb752e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add label column to applications table
    op.execute("""
        ALTER TABLE applications
        ADD COLUMN IF NOT EXISTS label TEXT;
    """)


def downgrade() -> None:
    # Remove label column from applications table
    op.execute("""
        ALTER TABLE applications
        DROP COLUMN IF EXISTS label;
    """)
