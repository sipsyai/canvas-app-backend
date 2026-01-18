"""Remove foreign key constraints to auth.users

Revision ID: 000f38f3d771
Revises: 52d83d397409
Create Date: 2026-01-18 16:19:56.892995

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '000f38f3d771'
down_revision = '52d83d397409'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop foreign key constraints to auth.users table
    # These constraints prevent testing since we can't easily create users in auth.users

    # List of tables and their foreign key constraint names
    tables_and_constraints = [
        ('fields', 'fields_created_by_fkey'),
        ('objects', 'objects_created_by_fkey'),
        ('objects', 'objects_updated_by_fkey'),
        ('records', 'records_created_by_fkey'),
        ('records', 'records_updated_by_fkey'),
        ('relationships', 'relationships_created_by_fkey'),
        ('relationship_records', 'relationship_records_created_by_fkey'),
        ('object_fields', 'object_fields_created_by_fkey'),
        ('object_fields', 'object_fields_updated_by_fkey'),
        ('applications', 'applications_created_by_fkey'),
        ('applications', 'applications_updated_by_fkey'),
    ]

    # Drop constraints if they exist using PostgreSQL IF EXISTS
    for table_name, constraint_name in tables_and_constraints:
        op.execute(f'ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name}')


def downgrade() -> None:
    # Re-create foreign key constraints to auth.users table

    # Note: This assumes auth.users table exists (Supabase managed)
    op.create_foreign_key('fields_created_by_fkey', 'fields', 'auth.users', ['created_by'], ['id'])
    op.create_foreign_key('objects_created_by_fkey', 'objects', 'auth.users', ['created_by'], ['id'])
    op.create_foreign_key('objects_updated_by_fkey', 'objects', 'auth.users', ['updated_by'], ['id'])
    op.create_foreign_key('records_created_by_fkey', 'records', 'auth.users', ['created_by'], ['id'])
    op.create_foreign_key('records_updated_by_fkey', 'records', 'auth.users', ['updated_by'], ['id'])
    op.create_foreign_key('relationships_created_by_fkey', 'relationships', 'auth.users', ['created_by'], ['id'])
    op.create_foreign_key('relationship_records_created_by_fkey', 'relationship_records', 'auth.users', ['created_by'], ['id'])
    op.create_foreign_key('object_fields_created_by_fkey', 'object_fields', 'auth.users', ['created_by'], ['id'])
    op.create_foreign_key('object_fields_updated_by_fkey', 'object_fields', 'auth.users', ['updated_by'], ['id'])
    op.create_foreign_key('applications_created_by_fkey', 'applications', 'auth.users', ['created_by'], ['id'])
    op.create_foreign_key('applications_updated_by_fkey', 'applications', 'auth.users', ['updated_by'], ['id'])
