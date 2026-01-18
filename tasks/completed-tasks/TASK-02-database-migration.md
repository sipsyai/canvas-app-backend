# TASK-02: Database Migration

**Phase:** 2/8
**Tahmini Süre:** 1 saat
**Bağımlılık:** Phase 1 (Project Setup) ✅
**Durum:** 🔜 Sonraki

---

## 🎯 Görev Açıklaması

Alembic kullanarak PostgreSQL database'inde **7 tablolu** initial migration oluştur. Bu migration, platform'un tüm core tablolarını (fields, objects, records, relationships, applications) ve RLS (Row Level Security) policy'lerini içermeli.

---

## 📋 Ön Gereksinimler

- [] PostgreSQL 16 kurulu veya Supabase projesi hazır
- [] `.env` dosyası `DATABASE_URL` ile yapılandırılmış
- [] Alembic initialized (`alembic/` klasörü mevcut)
- [] `app/database.py` ve `app/config.py` hazır

---

## 🗄️ Oluşturulacak Tablolar (7 Adet)

### 1. `fields` - Master Field Library
```sql
CREATE TABLE fields (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    label TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'text', 'number', 'email', 'date', 'select', etc.
    description TEXT,

    -- Configuration (JSONB)
    config JSONB DEFAULT '{}',  -- validation, options, default_value, etc.

    -- System/Custom distinction
    is_global BOOLEAN DEFAULT false,  -- System fields (Created By, Owner, etc.)
    is_custom BOOLEAN DEFAULT true,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT REFERENCES auth.users(id),

    CONSTRAINT fields_name_unique UNIQUE (name)
);
```

### 2. `objects` - Object Definitions (Contact, Company, etc.)
```sql
CREATE TABLE objects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    label TEXT NOT NULL,
    plural_label TEXT NOT NULL,
    description TEXT,
    icon TEXT,

    -- System/Custom distinction
    is_custom BOOLEAN DEFAULT true,
    is_global BOOLEAN DEFAULT false,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT REFERENCES auth.users(id),

    CONSTRAINT objects_name_unique UNIQUE (name, created_by)
);
```

### 3. `object_fields` - N:N Mapping (Which fields in which objects)
```sql
CREATE TABLE object_fields (
    id TEXT PRIMARY KEY,
    object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
    field_id TEXT NOT NULL REFERENCES fields(id) ON DELETE RESTRICT,

    -- Field positioning and display
    display_order INTEGER NOT NULL DEFAULT 0,
    is_required BOOLEAN DEFAULT false,
    is_visible BOOLEAN DEFAULT true,
    is_readonly BOOLEAN DEFAULT false,

    -- Field-specific overrides (JSONB)
    field_overrides JSONB DEFAULT '{}',  -- Override field config per object

    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT object_fields_unique UNIQUE (object_id, field_id)
);
```

### 4. `records` - Dynamic Data Storage (JSONB Hybrid Model)
```sql
CREATE TABLE records (
    id TEXT PRIMARY KEY,
    object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,

    -- Dynamic data (JSONB)
    data JSONB NOT NULL DEFAULT '{}',  -- { "fld_001": "John Doe", "fld_002": "john@example.com" }

    -- Denormalized primary value (for performance)
    primary_value TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT REFERENCES auth.users(id),
    updated_by TEXT REFERENCES auth.users(id),

    -- Multi-tenancy
    tenant_id TEXT  -- Redundant check with created_by
);
```

### 5. `relationships` - Relationship Definitions
```sql
CREATE TABLE relationships (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,

    -- From/To objects
    from_object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
    to_object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,

    -- Relationship type
    type TEXT NOT NULL,  -- '1:N' or 'N:N'

    -- Display configuration
    from_label TEXT,  -- e.g., "Opportunities" on Contact
    to_label TEXT,    -- e.g., "Contact" on Opportunity

    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT REFERENCES auth.users(id),

    CONSTRAINT relationships_unique UNIQUE (from_object_id, to_object_id, name)
);
```

### 6. `relationship_records` - N:N Junction Table
```sql
CREATE TABLE relationship_records (
    id TEXT PRIMARY KEY,
    relationship_id TEXT NOT NULL REFERENCES relationships(id) ON DELETE CASCADE,

    from_record_id TEXT NOT NULL REFERENCES records(id) ON DELETE CASCADE,
    to_record_id TEXT NOT NULL REFERENCES records(id) ON DELETE CASCADE,

    -- Optional metadata
    metadata JSONB DEFAULT '{}',  -- e.g., role, start_date, etc.

    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT REFERENCES auth.users(id),

    CONSTRAINT relationship_records_unique UNIQUE (relationship_id, from_record_id, to_record_id)
);
```

### 7. `applications` - Application Containers (CRM, ITSM, etc.)
```sql
CREATE TABLE applications (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,

    -- Application structure (JSONB)
    config JSONB DEFAULT '{}',  -- navigation, layout, permissions

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT REFERENCES auth.users(id),
    published_at TIMESTAMPTZ
);
```

---

## 🔐 Row Level Security (RLS) Policies

**Tüm tablolarda RLS aktif et:**
```sql
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE objects ENABLE ROW LEVEL SECURITY;
ALTER TABLE object_fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE records ENABLE ROW LEVEL SECURITY;
ALTER TABLE relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE relationship_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
```

### Fields Policies
```sql
-- Users can see global fields + their own custom fields
CREATE POLICY fields_select_policy ON fields
    FOR SELECT USING (
        is_global = true OR created_by = auth.uid()
    );

-- Users can only create custom fields
CREATE POLICY fields_insert_policy ON fields
    FOR INSERT WITH CHECK (
        created_by = auth.uid() AND is_custom = true
    );

-- Users can only update their own custom fields
CREATE POLICY fields_update_policy ON fields
    FOR UPDATE USING (
        created_by = auth.uid() AND is_custom = true
    );

-- Users can only delete their own custom fields
CREATE POLICY fields_delete_policy ON fields
    FOR DELETE USING (
        created_by = auth.uid() AND is_custom = true
    );
```

### Objects Policies
```sql
-- Users can see global objects + their own objects
CREATE POLICY objects_select_policy ON objects
    FOR SELECT USING (
        is_global = true OR created_by = auth.uid()
    );

-- Users can create objects
CREATE POLICY objects_insert_policy ON objects
    FOR INSERT WITH CHECK (
        created_by = auth.uid()
    );

-- Users can only update their own objects
CREATE POLICY objects_update_policy ON objects
    FOR UPDATE USING (
        created_by = auth.uid()
    );

-- Users can only delete their own objects
CREATE POLICY objects_delete_policy ON objects
    FOR DELETE USING (
        created_by = auth.uid()
    );
```

### Records Policies
```sql
-- Users can only see records from their own objects
CREATE POLICY records_select_policy ON records
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM objects
            WHERE objects.id = records.object_id
            AND objects.created_by = auth.uid()
        )
    );

-- Users can create records for their objects
CREATE POLICY records_insert_policy ON records
    FOR INSERT WITH CHECK (
        created_by = auth.uid() AND
        EXISTS (
            SELECT 1 FROM objects
            WHERE objects.id = records.object_id
            AND objects.created_by = auth.uid()
        )
    );

-- Similar UPDATE and DELETE policies
CREATE POLICY records_update_policy ON records
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM objects
            WHERE objects.id = records.object_id
            AND objects.created_by = auth.uid()
        )
    );

CREATE POLICY records_delete_policy ON records
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM objects
            WHERE objects.id = records.object_id
            AND objects.created_by = auth.uid()
        )
    );
```

---

## 🚀 Indexes (Performance Optimization)

```sql
-- Fields
CREATE INDEX idx_fields_type ON fields(type);
CREATE INDEX idx_fields_is_global ON fields(is_global);

-- Objects
CREATE INDEX idx_objects_created_by ON objects(created_by);
CREATE INDEX idx_objects_is_custom ON objects(is_custom);

-- Object Fields
CREATE INDEX idx_object_fields_object_id ON object_fields(object_id);
CREATE INDEX idx_object_fields_field_id ON object_fields(field_id);

-- Records (CRITICAL for JSONB performance)
CREATE INDEX idx_records_object_id ON records(object_id);
CREATE INDEX idx_records_created_by ON records(created_by);
CREATE INDEX idx_records_data_gin ON records USING GIN (data);  -- GIN index for JSONB
CREATE INDEX idx_records_primary_value ON records(primary_value);

-- Relationship Records
CREATE INDEX idx_relationship_records_from ON relationship_records(from_record_id);
CREATE INDEX idx_relationship_records_to ON relationship_records(to_record_id);
CREATE INDEX idx_relationship_records_relationship_id ON relationship_records(relationship_id);

-- Applications
CREATE INDEX idx_applications_created_by ON applications(created_by);
```

---

## 🔧 Auto-Update Triggers

```sql
-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables with updated_at
CREATE TRIGGER objects_updated_at BEFORE UPDATE ON objects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER records_updated_at BEFORE UPDATE ON records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER applications_updated_at BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

---

## 📝 Implementation Steps

### Step 1: Create Migration File
```bash
# Generate empty migration
alembic revision -m "initial_schema"

# This creates: alembic/versions/xxxxx_initial_schema.py
```

### Step 2: Edit Migration File

Open `alembic/versions/xxxxx_initial_schema.py` and populate:

```python
"""initial_schema

Revision ID: xxxxx
Revises:
Create Date: 2026-01-18
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers
revision = 'xxxxx'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create fields table
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
            created_by TEXT REFERENCES auth.users(id),
            CONSTRAINT fields_name_unique UNIQUE (name)
        );
    """)

    # (Tüm diğer CREATE TABLE statements buraya...)
    # (Tüm RLS policies buraya...)
    # (Tüm indexes buraya...)
    # (Tüm triggers buraya...)

def downgrade() -> None:
    # Drop tables in reverse order (due to foreign keys)
    op.execute("DROP TABLE IF EXISTS relationship_records CASCADE;")
    op.execute("DROP TABLE IF EXISTS relationships CASCADE;")
    op.execute("DROP TABLE IF EXISTS records CASCADE;")
    op.execute("DROP TABLE IF EXISTS object_fields CASCADE;")
    op.execute("DROP TABLE IF EXISTS applications CASCADE;")
    op.execute("DROP TABLE IF EXISTS objects CASCADE;")
    op.execute("DROP TABLE IF EXISTS fields CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at() CASCADE;")
```

### Step 3: Run Migration
```bash
# Apply migration
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"

# Expected output:
# - fields
# - objects
# - object_fields
# - records
# - relationships
# - relationship_records
# - applications
```

### Step 4: Verify RLS
```sql
-- Check RLS enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('fields', 'objects', 'records');

-- Expected: rowsecurity = true for all
```

---

## ✅ Başarı Kriterleri

Tamamlandığında şunlar olmalı:

- [ ] `alembic/versions/xxxxx_initial_schema.py` dosyası oluşturulmuş
- [ ] 7 tablo PostgreSQL'de oluşmuş (fields, objects, object_fields, records, relationships, relationship_records, applications)
- [ ] RLS tüm tablolarda aktif (rowsecurity = true)
- [ ] 15+ index oluşmuş (özellikle GIN index records.data üzerinde)
- [ ] Trigger fonksiyonları çalışıyor (updated_at auto-update)
- [ ] `alembic current` komutu migration ID'yi gösteriyor
- [ ] Foreign key constraints çalışıyor (CASCADE/RESTRICT doğru)
- [ ] `\d fields` gibi komutlarla tablo yapısı görülebiliyor

---

## 🐛 Troubleshooting

**Problem: Migration fails with "relation auth.users does not exist"**
- **Çözüm**: Supabase kullanıyorsan auth schema zaten var. Local PostgreSQL'de ise auth.users tablosunu manuel oluştur:
  ```sql
  CREATE SCHEMA IF NOT EXISTS auth;
  CREATE TABLE IF NOT EXISTS auth.users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL
  );
  ```

**Problem: RLS policies not working**
- **Çözüm**: `auth.uid()` fonksiyonu Supabase'e özel. Local PostgreSQL'de mock fonksiyon oluştur:
  ```sql
  CREATE OR REPLACE FUNCTION auth.uid() RETURNS TEXT AS $$
  BEGIN
      RETURN current_setting('request.jwt.claim.sub', TRUE);
  END;
  $$ LANGUAGE plpgsql STABLE;
  ```

**Problem: GIN index fails on JSONB column**
- **Çözüm**: PostgreSQL 16'da varsayılan. Eğer daha eski versiyonsa:
  ```sql
  CREATE EXTENSION IF NOT EXISTS btree_gin;
  ```

---

## 📚 İlgili Dökümanlar

- `DATABASE_VISUAL_SCHEMA.md` - Tablo ilişkileri ve CRM örneği
- `BACKEND_ARCHITECTURE_ANALYSIS.md` - JSONB Hybrid Model kararı
- `CLAUDE.md` - Alembic migration best practices

---

**Sonraki Task:** `TASK-03-orm-models.md` (SQLAlchemy ORM modelleri)
