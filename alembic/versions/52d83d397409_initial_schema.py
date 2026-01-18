"""initial_schema

Revision ID: 52d83d397409
Revises: 
Create Date: 2026-01-18 15:15:12.245182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52d83d397409'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ========================================================================
    # CREATE TABLES (7 tables)
    # ========================================================================

    # 1. FIELDS TABLE - Master Field Library
    op.execute("""
        CREATE TABLE fields (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            label TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            config JSONB DEFAULT '{}',
            is_global BOOLEAN DEFAULT false,
            is_custom BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            created_by UUID REFERENCES auth.users(id),
            CONSTRAINT fields_name_unique UNIQUE (name)
        );
    """)

    # 2. OBJECTS TABLE - Object Definitions
    op.execute("""
        CREATE TABLE objects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            label TEXT NOT NULL,
            plural_label TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            is_custom BOOLEAN DEFAULT true,
            is_global BOOLEAN DEFAULT false,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            created_by UUID REFERENCES auth.users(id),
            CONSTRAINT objects_name_unique UNIQUE (name, created_by)
        );
    """)

    # 3. OBJECT_FIELDS TABLE - N:N Mapping
    op.execute("""
        CREATE TABLE object_fields (
            id TEXT PRIMARY KEY,
            object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
            field_id TEXT NOT NULL REFERENCES fields(id) ON DELETE RESTRICT,
            display_order INTEGER NOT NULL DEFAULT 0,
            is_required BOOLEAN DEFAULT false,
            is_visible BOOLEAN DEFAULT true,
            is_readonly BOOLEAN DEFAULT false,
            field_overrides JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT object_fields_unique UNIQUE (object_id, field_id)
        );
    """)

    # 4. RECORDS TABLE - Dynamic Data Storage (JSONB Hybrid Model)
    op.execute("""
        CREATE TABLE records (
            id TEXT PRIMARY KEY,
            object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
            data JSONB NOT NULL DEFAULT '{}',
            primary_value TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            created_by UUID REFERENCES auth.users(id),
            updated_by UUID REFERENCES auth.users(id),
            tenant_id TEXT
        );
    """)

    # 5. RELATIONSHIPS TABLE - Relationship Definitions
    op.execute("""
        CREATE TABLE relationships (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            from_object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
            to_object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
            type TEXT NOT NULL,
            from_label TEXT,
            to_label TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            created_by UUID REFERENCES auth.users(id),
            CONSTRAINT relationships_unique UNIQUE (from_object_id, to_object_id, name)
        );
    """)

    # 6. RELATIONSHIP_RECORDS TABLE - N:N Junction Table
    op.execute("""
        CREATE TABLE relationship_records (
            id TEXT PRIMARY KEY,
            relationship_id TEXT NOT NULL REFERENCES relationships(id) ON DELETE CASCADE,
            from_record_id TEXT NOT NULL REFERENCES records(id) ON DELETE CASCADE,
            to_record_id TEXT NOT NULL REFERENCES records(id) ON DELETE CASCADE,
            relationship_metadata JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            created_by UUID REFERENCES auth.users(id),
            CONSTRAINT relationship_records_unique UNIQUE (relationship_id, from_record_id, to_record_id)
        );
    """)

    # 7. APPLICATIONS TABLE - Application Containers
    op.execute("""
        CREATE TABLE applications (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            config JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            created_by UUID REFERENCES auth.users(id),
            published_at TIMESTAMPTZ
        );
    """)

    # ========================================================================
    # INDEXES (Performance Optimization)
    # ========================================================================

    # Fields indexes
    op.execute("CREATE INDEX idx_fields_type ON fields(type);")
    op.execute("CREATE INDEX idx_fields_is_global ON fields(is_global);")

    # Objects indexes
    op.execute("CREATE INDEX idx_objects_created_by ON objects(created_by);")
    op.execute("CREATE INDEX idx_objects_is_custom ON objects(is_custom);")

    # Object Fields indexes
    op.execute("CREATE INDEX idx_object_fields_object_id ON object_fields(object_id);")
    op.execute("CREATE INDEX idx_object_fields_field_id ON object_fields(field_id);")

    # Records indexes (CRITICAL for JSONB performance)
    op.execute("CREATE INDEX idx_records_object_id ON records(object_id);")
    op.execute("CREATE INDEX idx_records_created_by ON records(created_by);")
    op.execute("CREATE INDEX idx_records_data_gin ON records USING GIN (data);")
    op.execute("CREATE INDEX idx_records_primary_value ON records(primary_value);")

    # Relationship Records indexes
    op.execute("CREATE INDEX idx_relationship_records_from ON relationship_records(from_record_id);")
    op.execute("CREATE INDEX idx_relationship_records_to ON relationship_records(to_record_id);")
    op.execute("CREATE INDEX idx_relationship_records_relationship_id ON relationship_records(relationship_id);")

    # Applications indexes
    op.execute("CREATE INDEX idx_applications_created_by ON applications(created_by);")

    # ========================================================================
    # TRIGGERS (Auto-update updated_at timestamp)
    # ========================================================================

    # Create trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Apply triggers to tables with updated_at
    op.execute("""
        CREATE TRIGGER objects_updated_at
        BEFORE UPDATE ON objects
        FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)

    op.execute("""
        CREATE TRIGGER records_updated_at
        BEFORE UPDATE ON records
        FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)

    op.execute("""
        CREATE TRIGGER applications_updated_at
        BEFORE UPDATE ON applications
        FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)

    # ========================================================================
    # ROW LEVEL SECURITY (RLS)
    # ========================================================================

    # Enable RLS on all tables
    op.execute("ALTER TABLE fields ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE objects ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE object_fields ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE records ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE relationships ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE relationship_records ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE applications ENABLE ROW LEVEL SECURITY;")

    # Fields Policies
    op.execute("""
        CREATE POLICY fields_select_policy ON fields
        FOR SELECT USING (
            is_global = true OR created_by = auth.uid()
        );
    """)

    op.execute("""
        CREATE POLICY fields_insert_policy ON fields
        FOR INSERT WITH CHECK (
            created_by = auth.uid() AND is_custom = true
        );
    """)

    op.execute("""
        CREATE POLICY fields_update_policy ON fields
        FOR UPDATE USING (
            created_by = auth.uid() AND is_custom = true
        );
    """)

    op.execute("""
        CREATE POLICY fields_delete_policy ON fields
        FOR DELETE USING (
            created_by = auth.uid() AND is_custom = true
        );
    """)

    # Objects Policies
    op.execute("""
        CREATE POLICY objects_select_policy ON objects
        FOR SELECT USING (
            is_global = true OR created_by = auth.uid()
        );
    """)

    op.execute("""
        CREATE POLICY objects_insert_policy ON objects
        FOR INSERT WITH CHECK (
            created_by = auth.uid()
        );
    """)

    op.execute("""
        CREATE POLICY objects_update_policy ON objects
        FOR UPDATE USING (
            created_by = auth.uid()
        );
    """)

    op.execute("""
        CREATE POLICY objects_delete_policy ON objects
        FOR DELETE USING (
            created_by = auth.uid()
        );
    """)

    # Records Policies
    op.execute("""
        CREATE POLICY records_select_policy ON records
        FOR SELECT USING (
            EXISTS (
                SELECT 1 FROM objects
                WHERE objects.id = records.object_id
                AND objects.created_by = auth.uid()
            )
        );
    """)

    op.execute("""
        CREATE POLICY records_insert_policy ON records
        FOR INSERT WITH CHECK (
            created_by = auth.uid() AND
            EXISTS (
                SELECT 1 FROM objects
                WHERE objects.id = records.object_id
                AND objects.created_by = auth.uid()
            )
        );
    """)

    op.execute("""
        CREATE POLICY records_update_policy ON records
        FOR UPDATE USING (
            EXISTS (
                SELECT 1 FROM objects
                WHERE objects.id = records.object_id
                AND objects.created_by = auth.uid()
            )
        );
    """)

    op.execute("""
        CREATE POLICY records_delete_policy ON records
        FOR DELETE USING (
            EXISTS (
                SELECT 1 FROM objects
                WHERE objects.id = records.object_id
                AND objects.created_by = auth.uid()
            )
        );
    """)


def downgrade() -> None:
    # Drop tables in reverse order (due to foreign keys)
    op.execute("DROP TABLE IF EXISTS relationship_records CASCADE;")
    op.execute("DROP TABLE IF EXISTS relationships CASCADE;")
    op.execute("DROP TABLE IF EXISTS records CASCADE;")
    op.execute("DROP TABLE IF EXISTS object_fields CASCADE;")
    op.execute("DROP TABLE IF EXISTS applications CASCADE;")
    op.execute("DROP TABLE IF EXISTS objects CASCADE;")
    op.execute("DROP TABLE IF EXISTS fields CASCADE;")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at() CASCADE;")
