"""Add views and permissions to objects, rename plural_label

Revision ID: b901639974d8
Revises: e599c4a67d06
Create Date: 2026-01-18 16:49:49.820192

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'b901639974d8'
down_revision = 'e599c4a67d06'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Rename column: plural_label → plural_name
    op.execute("""
        ALTER TABLE objects
        RENAME COLUMN plural_label TO plural_name;
    """)

    # 2. Add views JSONB column with default structure
    op.execute("""
        ALTER TABLE objects
        ADD COLUMN views JSONB NOT NULL DEFAULT '{"forms": [], "tables": [], "kanbans": [], "calendars": []}'::jsonb;
    """)

    # 3. Add permissions JSONB column with default structure
    op.execute("""
        ALTER TABLE objects
        ADD COLUMN permissions JSONB NOT NULL DEFAULT '{"create": ["all"], "read": ["all"], "update": ["all"], "delete": ["all"]}'::jsonb;
    """)

    # 4. Create GIN index on views for fast JSONB queries
    op.execute("""
        CREATE INDEX idx_objects_views ON objects USING GIN(views);
    """)

    # 5. Create GIN index on permissions
    op.execute("""
        CREATE INDEX idx_objects_permissions ON objects USING GIN(permissions);
    """)


def downgrade() -> None:
    # Reverse all changes
    op.execute("DROP INDEX IF EXISTS idx_objects_permissions;")
    op.execute("DROP INDEX IF EXISTS idx_objects_views;")
    op.execute("ALTER TABLE objects DROP COLUMN IF EXISTS permissions;")
    op.execute("ALTER TABLE objects DROP COLUMN IF EXISTS views;")
    op.execute("""
        ALTER TABLE objects
        RENAME COLUMN plural_name TO plural_label;
    """)
