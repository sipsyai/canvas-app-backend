"""Add system fields seed data

Revision ID: 818919cb752e
Revises: b901639974d8
Create Date: 2026-01-18 16:55:16.906833

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '818919cb752e'
down_revision = 'b901639974d8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Insert 5 global system fields
    op.execute("""
        INSERT INTO fields (id, name, label, type, description, category, is_global, is_system_field, is_custom, created_by, config)
        VALUES
        (
            'fld_system_created_at',
            'created_at',
            'Created Date',
            'datetime',
            'Date and time when the record was created',
            'System',
            true,
            true,
            false,
            NULL,
            '{}'::jsonb
        ),
        (
            'fld_system_created_by',
            'created_by',
            'Created By',
            'lookup',
            'User who created this record',
            'System',
            true,
            true,
            false,
            NULL,
            '{"lookupObject": "user"}'::jsonb
        ),
        (
            'fld_system_updated_at',
            'updated_at',
            'Modified Date',
            'datetime',
            'Date and time when the record was last modified',
            'System',
            true,
            true,
            false,
            NULL,
            '{}'::jsonb
        ),
        (
            'fld_system_updated_by',
            'updated_by',
            'Modified By',
            'lookup',
            'User who last modified this record',
            'System',
            true,
            true,
            false,
            NULL,
            '{"lookupObject": "user"}'::jsonb
        ),
        (
            'fld_system_owner',
            'owner',
            'Owner',
            'lookup',
            'User who owns this record',
            'System',
            true,
            true,
            false,
            NULL,
            '{"lookupObject": "user"}'::jsonb
        )
        ON CONFLICT (id) DO NOTHING;
    """)


def downgrade() -> None:
    # Remove system fields
    op.execute("""
        DELETE FROM fields
        WHERE id IN (
            'fld_system_created_at',
            'fld_system_created_by',
            'fld_system_updated_at',
            'fld_system_updated_by',
            'fld_system_owner'
        );
    """)
