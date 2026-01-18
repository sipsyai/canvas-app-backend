"""Add category, is_system_field, updated_at to fields table

Revision ID: e599c4a67d06
Revises: 000f38f3d771
Create Date: 2026-01-18 16:41:57.806981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e599c4a67d06'
down_revision = '000f38f3d771'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add new columns
    op.execute("""
        ALTER TABLE fields
        ADD COLUMN category TEXT,
        ADD COLUMN is_system_field BOOLEAN NOT NULL DEFAULT false,
        ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
    """)

    # 2. Create index on category
    op.execute("""
        CREATE INDEX idx_fields_category ON fields(category);
    """)

    # 3. Create index on is_system_field
    op.execute("""
        CREATE INDEX idx_fields_system ON fields(is_system_field) WHERE is_system_field = true;
    """)

    # 4. Drop old unique constraint
    op.execute("""
        ALTER TABLE fields DROP CONSTRAINT IF EXISTS fields_name_key;
    """)
    op.execute("""
        ALTER TABLE fields DROP CONSTRAINT IF EXISTS fields_name_unique;
    """)

    # 5. Add new composite unique constraint
    op.execute("""
        ALTER TABLE fields
        ADD CONSTRAINT uq_field_name_created_by UNIQUE (name, created_by);
    """)

    # 6. Create trigger for auto-update updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_field_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trigger_field_updated_at
        BEFORE UPDATE ON fields
        FOR EACH ROW
        EXECUTE FUNCTION update_field_updated_at();
    """)


def downgrade() -> None:
    # Reverse all changes
    op.execute("DROP TRIGGER IF EXISTS trigger_field_updated_at ON fields;")
    op.execute("DROP FUNCTION IF EXISTS update_field_updated_at();")
    op.execute("ALTER TABLE fields DROP CONSTRAINT IF EXISTS uq_field_name_created_by;")
    op.execute("ALTER TABLE fields ADD CONSTRAINT fields_name_unique UNIQUE (name);")
    op.execute("DROP INDEX IF EXISTS idx_fields_system;")
    op.execute("DROP INDEX IF EXISTS idx_fields_category;")
    op.execute("""
        ALTER TABLE fields
        DROP COLUMN IF EXISTS updated_at,
        DROP COLUMN IF EXISTS is_system_field,
        DROP COLUMN IF EXISTS category;
    """)
