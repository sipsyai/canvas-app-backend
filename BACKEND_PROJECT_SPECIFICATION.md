# Backend Project Specification - Canvas App API

**Project Name:** canvas-app-backend
**Purpose:** REST API for Object-Centric No-Code Platform
**Tech Stack:** FastAPI + PostgreSQL (Supabase) + Python 3.11+
**Status:** 🚀 Ready for Development with Claude Code

---

## Executive Summary

Bu backend, Salesforce/ServiceNow/Airtable tarzı bir **no-code platform** için RESTful API sağlar. Kullanıcılar:
- **Object** (Contact, Company, Opportunity) tanımlayabilir
- **Field** (Email, Phone, Amount) library'den seçip object'lere ekleyebilir
- **Record** (Ali Yılmaz, Acme Corp) oluşturabilir
- **Relationship** (Contact → Company, Opportunity ↔ Contact) kurabilir
- **Application** (CRM, ITSM) oluşturup object'leri gruplandırabilir

**Core Pattern:** JSONB Hybrid Model (metadata normalized, data in JSONB)

---

## 1. Technology Stack

### Backend Framework
```yaml
Language: Python 3.11+
Framework: FastAPI 0.115+
ASGI Server: Uvicorn
Validation: Pydantic v2
```

### Database
```yaml
Database: PostgreSQL 16
Provider: Supabase (managed)
ORM: SQLAlchemy 2.0+ (async)
Migration: Alembic
Storage Pattern: JSONB for dynamic data
```

### Authentication
```yaml
Method: Supabase Auth (JWT)
Provider: @supabase/supabase-py
Token Type: Bearer token
Expiry: 1 hour (refresh token support)
```

### Additional Tools
```yaml
CORS: FastAPI middleware
Logging: Python logging + structlog
Testing: pytest + pytest-asyncio
Code Quality: ruff (linter + formatter)
Type Checking: mypy
```

---

## 2. Project Structure

```
canvas-app-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Environment variables
│   ├── database.py                # SQLAlchemy engine setup
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── field.py               # Field model
│   │   ├── object.py              # Object model
│   │   ├── object_field.py        # ObjectField mapping
│   │   ├── record.py              # Record model
│   │   ├── relationship.py        # Relationship model
│   │   ├── relationship_record.py # RelationshipRecord junction
│   │   └── application.py         # Application model
│   │
│   ├── schemas/                   # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── field.py
│   │   ├── object.py
│   │   ├── record.py
│   │   ├── relationship.py
│   │   └── application.py
│   │
│   ├── routers/                   # API route handlers
│   │   ├── __init__.py
│   │   ├── fields.py              # /api/fields
│   │   ├── objects.py             # /api/objects
│   │   ├── records.py             # /api/records
│   │   ├── relationships.py       # /api/relationships
│   │   ├── applications.py        # /api/applications
│   │   └── health.py              # /api/health
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── field_service.py       # Field CRUD
│   │   ├── object_service.py      # Object CRUD
│   │   ├── record_service.py      # Record CRUD (JSONB handling)
│   │   ├── relationship_service.py # Relationship logic
│   │   └── application_service.py # Application logic
│   │
│   ├── middleware/                # Custom middleware
│   │   ├── __init__.py
│   │   ├── auth.py                # JWT verification
│   │   ├── error_handler.py       # Global error handling
│   │   └── logging.py             # Request logging
│   │
│   └── utils/                     # Helper functions
│       ├── __init__.py
│       ├── auth.py                # Auth utilities
│       ├── jsonb.py               # JSONB helpers
│       └── validators.py          # Custom validators
│
├── alembic/                       # Database migrations
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py
│   └── alembic.ini
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_fields.py
│   ├── test_objects.py
│   ├── test_records.py
│   └── test_integration.py
│
├── .env.example                   # Environment template
├── .gitignore
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Ruff/mypy config
├── README.md                      # Project documentation
└── Dockerfile                     # Container definition
```

---

## 3. Database Schema

### 3.1 Complete SQL Schema

```sql
-- ============================================================================
-- CANVAS APP BACKEND - POSTGRESQL SCHEMA
-- ============================================================================
-- Pattern: JSONB Hybrid Model (normalized metadata + JSONB data)
-- Version: 1.0
-- Date: 2026-01-18
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE 1: fields (Master Field Library)
-- ============================================================================
CREATE TABLE fields (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Field definition
  name TEXT NOT NULL,                    -- "email", "full_name"
  label TEXT NOT NULL,                   -- "Email Address", "Full Name"
  type TEXT NOT NULL,                    -- "text", "email", "phone", "number", etc.

  -- Configuration (type-specific settings)
  config JSONB DEFAULT '{}'::jsonb,      -- {"min": 2, "max": 100}, {"currency": "USD"}

  -- Categorization
  is_system_field BOOLEAN DEFAULT false, -- true for Created Date, Owner, etc.
  is_global BOOLEAN DEFAULT false,       -- true if available to all users
  category TEXT,                         -- "Contact Info", "Business", "System"

  -- Sharing
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  UNIQUE(name, created_by)               -- User can't have duplicate field names
);

-- Indexes
CREATE INDEX idx_fields_type ON fields(type);
CREATE INDEX idx_fields_category ON fields(category);
CREATE INDEX idx_fields_global ON fields(is_global) WHERE is_global = true;
CREATE INDEX idx_fields_system ON fields(is_system_field) WHERE is_system_field = true;

-- Comments
COMMENT ON TABLE fields IS 'Master field library - reusable field definitions';
COMMENT ON COLUMN fields.config IS 'Type-specific configuration as JSONB';

-- ============================================================================
-- TABLE 2: objects (Object Definitions)
-- ============================================================================
CREATE TABLE objects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Basic info
  name TEXT NOT NULL,                    -- "Contact", "Company"
  plural_name TEXT NOT NULL,             -- "Contacts", "Companies"
  description TEXT,
  icon TEXT,                             -- "users", "building"
  is_custom BOOLEAN DEFAULT true,        -- false for system objects (User)

  -- Views (JSONB for flexibility)
  views JSONB DEFAULT '{
    "forms": [],
    "tables": [],
    "kanbans": [],
    "calendars": []
  }'::jsonb,

  -- Permissions (JSONB)
  permissions JSONB DEFAULT '{
    "create": ["all"],
    "read": ["all"],
    "update": ["all"],
    "delete": ["all"]
  }'::jsonb,

  -- Metadata
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  UNIQUE(name, created_by)
);

-- Indexes
CREATE INDEX idx_objects_created_by ON objects(created_by);
CREATE INDEX idx_objects_custom ON objects(is_custom);
CREATE INDEX idx_objects_views ON objects USING GIN(views);

-- Comments
COMMENT ON TABLE objects IS 'Object definitions (Contact, Company, Opportunity, etc.)';

-- ============================================================================
-- TABLE 3: object_fields (N:N Mapping)
-- ============================================================================
CREATE TABLE object_fields (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Relationship
  object_id UUID NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
  field_id UUID NOT NULL REFERENCES fields(id) ON DELETE RESTRICT,

  -- Object-specific configuration
  required BOOLEAN DEFAULT false,
  default_value TEXT,
  sort_order INTEGER DEFAULT 0,

  -- Permissions (object-level override)
  visible_to_roles TEXT[] DEFAULT ARRAY['all'],
  editable_by_roles TEXT[] DEFAULT ARRAY['all'],

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  UNIQUE(object_id, field_id)
);

-- Indexes
CREATE INDEX idx_object_fields_object ON object_fields(object_id);
CREATE INDEX idx_object_fields_field ON object_fields(field_id);
CREATE INDEX idx_object_fields_order ON object_fields(object_id, sort_order);

-- Comments
COMMENT ON TABLE object_fields IS 'Mapping between objects and fields (N:N relationship)';

-- ============================================================================
-- TABLE 4: records (Dynamic Data Storage)
-- ============================================================================
CREATE TABLE records (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Object reference
  object_id UUID NOT NULL REFERENCES objects(id) ON DELETE CASCADE,

  -- Dynamic data (JSONB)
  data JSONB NOT NULL DEFAULT '{}'::jsonb,
  -- Example: {"fld_001": "Ali Yılmaz", "fld_002": "ali@example.com"}

  -- Performance optimization (denormalized)
  primary_value TEXT,                    -- Cached from data (for list views)

  -- Metadata
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes (CRITICAL for performance!)
CREATE INDEX idx_records_object ON records(object_id);
CREATE INDEX idx_records_primary_value ON records(object_id, primary_value);
CREATE INDEX idx_records_data_gin ON records USING GIN(data);
CREATE INDEX idx_records_created_at ON records(created_at DESC);
CREATE INDEX idx_records_created_by ON records(created_by);

-- Comments
COMMENT ON TABLE records IS 'Dynamic record storage using JSONB pattern';
COMMENT ON COLUMN records.data IS 'Field values stored as JSONB: {field_id: value}';
COMMENT ON COLUMN records.primary_value IS 'Denormalized primary field for performance';

-- ============================================================================
-- TABLE 5: relationships (Relationship Definitions)
-- ============================================================================
CREATE TABLE relationships (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Relationship definition
  name TEXT NOT NULL,                    -- "contact_company", "opportunity_contact"
  from_object_id UUID NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
  to_object_id UUID NOT NULL REFERENCES objects(id) ON DELETE CASCADE,

  -- Type
  type TEXT NOT NULL,                    -- "lookup" (N:1), "manyToMany" (N:N)

  -- Labels (bidirectional)
  label TEXT,                            -- "Company" (from Contact's perspective)
  inverse_label TEXT,                    -- "Contacts" (from Company's perspective)

  -- Behavior
  required BOOLEAN DEFAULT false,
  cascade_delete BOOLEAN DEFAULT false,

  -- Metadata
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  UNIQUE(from_object_id, to_object_id, name),
  CONSTRAINT chk_relationship_type CHECK (type IN ('lookup', 'manyToMany'))
);

-- Indexes
CREATE INDEX idx_relationships_from ON relationships(from_object_id);
CREATE INDEX idx_relationships_to ON relationships(to_object_id);
CREATE INDEX idx_relationships_type ON relationships(type);

-- Comments
COMMENT ON TABLE relationships IS 'Relationship definitions between objects';

-- ============================================================================
-- TABLE 6: relationship_records (Junction Table for N:N)
-- ============================================================================
CREATE TABLE relationship_records (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Relationship reference
  relationship_id UUID NOT NULL REFERENCES relationships(id) ON DELETE CASCADE,

  -- Record references
  from_record_id UUID NOT NULL REFERENCES records(id) ON DELETE CASCADE,
  to_record_id UUID NOT NULL REFERENCES records(id) ON DELETE CASCADE,

  -- Additional metadata (e.g., role in opportunity)
  metadata JSONB DEFAULT '{}'::jsonb,    -- {"role": "Champion", "startDate": "2026-01-18"}

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  UNIQUE(relationship_id, from_record_id, to_record_id)
);

-- Indexes
CREATE INDEX idx_relationship_records_from ON relationship_records(from_record_id);
CREATE INDEX idx_relationship_records_to ON relationship_records(to_record_id);
CREATE INDEX idx_relationship_records_rel ON relationship_records(relationship_id);
CREATE INDEX idx_relationship_records_metadata ON relationship_records USING GIN(metadata);

-- Comments
COMMENT ON TABLE relationship_records IS 'Junction table for many-to-many relationships';

-- ============================================================================
-- TABLE 7: applications (Application Collections)
-- ============================================================================
CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Basic info
  name TEXT NOT NULL,                    -- "CRM", "ITSM"
  description TEXT,
  icon TEXT,

  -- Objects (JSONB array of object IDs)
  objects JSONB DEFAULT '[]'::jsonb,     -- ["obj_001", "obj_002", ...]

  -- Navigation menu (JSONB)
  navigation JSONB DEFAULT '{
    "menu": []
  }'::jsonb,

  -- Permissions
  permissions JSONB DEFAULT '{
    "viewApp": ["all"],
    "editApp": ["owner"]
  }'::jsonb,

  -- Metadata
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  published_at TIMESTAMPTZ,

  -- Constraints
  UNIQUE(name, created_by)
);

-- Indexes
CREATE INDEX idx_applications_created_by ON applications(created_by);
CREATE INDEX idx_applications_objects ON applications USING GIN(objects);

-- Comments
COMMENT ON TABLE applications IS 'Application collections (CRM, ITSM, etc.)';

-- ============================================================================
-- TRIGGERS: Auto-update updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_fields_updated_at
  BEFORE UPDATE ON fields
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_objects_updated_at
  BEFORE UPDATE ON objects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_records_updated_at
  BEFORE UPDATE ON records
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_relationships_updated_at
  BEFORE UPDATE ON relationships
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_applications_updated_at
  BEFORE UPDATE ON applications
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE objects ENABLE ROW LEVEL SECURITY;
ALTER TABLE object_fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE records ENABLE ROW LEVEL SECURITY;
ALTER TABLE relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE relationship_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- Fields: Users see global fields + their own
CREATE POLICY fields_select_policy ON fields
  FOR SELECT
  USING (is_global = true OR created_by = auth.uid());

CREATE POLICY fields_insert_policy ON fields
  FOR INSERT
  WITH CHECK (created_by = auth.uid());

CREATE POLICY fields_update_policy ON fields
  FOR UPDATE
  USING (created_by = auth.uid());

CREATE POLICY fields_delete_policy ON fields
  FOR DELETE
  USING (created_by = auth.uid() AND is_system_field = false);

-- Objects: Users see only their own
CREATE POLICY objects_select_policy ON objects
  FOR SELECT
  USING (created_by = auth.uid());

CREATE POLICY objects_insert_policy ON objects
  FOR INSERT
  WITH CHECK (created_by = auth.uid());

CREATE POLICY objects_update_policy ON objects
  FOR UPDATE
  USING (created_by = auth.uid());

CREATE POLICY objects_delete_policy ON objects
  FOR DELETE
  USING (created_by = auth.uid());

-- Object Fields: Cascade from objects
CREATE POLICY object_fields_select_policy ON object_fields
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM objects o
      WHERE o.id = object_fields.object_id
        AND o.created_by = auth.uid()
    )
  );

CREATE POLICY object_fields_insert_policy ON object_fields
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM objects o
      WHERE o.id = object_fields.object_id
        AND o.created_by = auth.uid()
    )
  );

-- Records: Cascade from objects
CREATE POLICY records_select_policy ON records
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM objects o
      WHERE o.id = records.object_id
        AND o.created_by = auth.uid()
    )
  );

CREATE POLICY records_insert_policy ON records
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM objects o
      WHERE o.id = records.object_id
        AND o.created_by = auth.uid()
    )
  );

CREATE POLICY records_update_policy ON records
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM objects o
      WHERE o.id = records.object_id
        AND o.created_by = auth.uid()
    )
  );

CREATE POLICY records_delete_policy ON records
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM objects o
      WHERE o.id = records.object_id
        AND o.created_by = auth.uid()
    )
  );

-- Similar RLS policies for relationships, relationship_records, applications...
-- (Omitted for brevity, follow same pattern)

-- ============================================================================
-- SEED DATA: System Fields
-- ============================================================================
INSERT INTO fields (id, name, label, type, is_system_field, is_global, category, created_by)
VALUES
  ('00000000-0000-0000-0000-000000000001', 'created_at', 'Created Date', 'datetime', true, true, 'System', NULL),
  ('00000000-0000-0000-0000-000000000002', 'created_by', 'Created By', 'lookup', true, true, 'System', NULL),
  ('00000000-0000-0000-0000-000000000003', 'updated_at', 'Modified Date', 'datetime', true, true, 'System', NULL),
  ('00000000-0000-0000-0000-000000000004', 'updated_by', 'Modified By', 'lookup', true, true, 'System', NULL),
  ('00000000-0000-0000-0000-000000000005', 'owner', 'Owner', 'lookup', true, true, 'System', NULL)
ON CONFLICT (id) DO NOTHING;
```

---

## 4. API Endpoints Specification

### Base URL
```
Development: http://localhost:8000
Production: https://api.canvasapp.com
```

### Authentication
All endpoints require Bearer token (except `/health` and `/auth/*`)

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 4.1 Health Check

#### GET /api/health
Check API status

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "database": "connected"
}
```

---

### 4.2 Fields API

#### GET /api/fields
List all fields (global + user's own)

**Query Parameters:**
- `category` (optional): Filter by category
- `is_system` (optional): Filter system fields
- `search` (optional): Search by name/label

**Response:**
```json
{
  "fields": [
    {
      "id": "uuid",
      "name": "email",
      "label": "Email Address",
      "type": "email",
      "config": {"pattern": "email"},
      "is_system_field": false,
      "is_global": false,
      "category": "Contact Info",
      "created_by": "user_id",
      "created_at": "2026-01-18T10:00:00Z"
    }
  ],
  "total": 25
}
```

#### POST /api/fields
Create a new field

**Request:**
```json
{
  "name": "email",
  "label": "Email Address",
  "type": "email",
  "config": {
    "pattern": "email"
  },
  "category": "Contact Info"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "email",
  "label": "Email Address",
  ...
}
```

#### GET /api/fields/{field_id}
Get field details

#### PATCH /api/fields/{field_id}
Update field (only own fields)

#### DELETE /api/fields/{field_id}
Delete field (only if not system and not in use)

---

### 4.3 Objects API

#### GET /api/objects
List all user's objects

**Query Parameters:**
- `is_custom` (optional): Filter custom/system objects
- `search` (optional): Search by name

**Response:**
```json
{
  "objects": [
    {
      "id": "uuid",
      "name": "Contact",
      "plural_name": "Contacts",
      "description": "Customer contacts",
      "icon": "users",
      "is_custom": true,
      "fields": [
        {
          "field_id": "uuid",
          "name": "email",
          "label": "Email Address",
          "type": "email",
          "required": true,
          "sort_order": 0
        }
      ],
      "relationships": [],
      "views": {},
      "created_at": "2026-01-18T10:00:00Z"
    }
  ],
  "total": 5
}
```

#### POST /api/objects
Create a new object

**Request:**
```json
{
  "name": "Contact",
  "plural_name": "Contacts",
  "description": "Customer contacts",
  "icon": "users",
  "field_ids": ["field_uuid_1", "field_uuid_2"],
  "field_configs": [
    {
      "field_id": "field_uuid_1",
      "required": true,
      "sort_order": 0
    }
  ]
}
```

**Response:** `201 Created`

#### GET /api/objects/{object_id}
Get object details with all fields

#### PATCH /api/objects/{object_id}
Update object metadata

#### DELETE /api/objects/{object_id}
Delete object (cascade deletes all records)

#### POST /api/objects/{object_id}/fields
Add field to object

**Request:**
```json
{
  "field_id": "uuid",
  "required": false,
  "default_value": "New",
  "sort_order": 10
}
```

#### DELETE /api/objects/{object_id}/fields/{field_id}
Remove field from object

---

### 4.4 Records API

#### GET /api/records
List records for an object

**Query Parameters:**
- `object_id` (required): Object ID
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 50)
- `sort_by` (optional): Field ID to sort by
- `sort_order` (optional): `asc` or `desc`
- `filters` (optional): JSON filter conditions

**Response:**
```json
{
  "records": [
    {
      "id": "uuid",
      "object_id": "uuid",
      "data": {
        "fld_001": "Ali Yılmaz",
        "fld_002": "ali@example.com",
        "fld_003": "+90 555 123 4567"
      },
      "primary_value": "Ali Yılmaz",
      "created_at": "2026-01-18T10:00:00Z",
      "created_by": "user_id"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 50,
  "total_pages": 3
}
```

#### POST /api/records
Create a new record

**Request:**
```json
{
  "object_id": "uuid",
  "data": {
    "fld_001": "Ali Yılmaz",
    "fld_002": "ali@example.com",
    "fld_003": "+90 555 123 4567"
  }
}
```

**Response:** `201 Created`

#### GET /api/records/{record_id}
Get record details with typed values

**Response:**
```json
{
  "id": "uuid",
  "object_id": "uuid",
  "data": {...},
  "typed_values": [
    {
      "field_id": "fld_001",
      "field_name": "full_name",
      "field_label": "Full Name",
      "field_type": "text",
      "value": "Ali Yılmaz",
      "display_value": "Ali Yılmaz"
    }
  ],
  "created_at": "2026-01-18T10:00:00Z"
}
```

#### PATCH /api/records/{record_id}
Update record fields

**Request:**
```json
{
  "data": {
    "fld_002": "newemail@example.com"
  }
}
```

#### DELETE /api/records/{record_id}
Delete record

#### POST /api/records/bulk
Bulk create records

**Request:**
```json
{
  "object_id": "uuid",
  "records": [
    {"data": {"fld_001": "Record 1"}},
    {"data": {"fld_001": "Record 2"}}
  ]
}
```

**Response:**
```json
{
  "created": 2,
  "failed": 0,
  "errors": [],
  "record_ids": ["uuid1", "uuid2"]
}
```

#### DELETE /api/records/bulk
Bulk delete records

---

### 4.5 Relationships API

#### GET /api/relationships
List all relationships for user's objects

#### POST /api/relationships
Create a relationship

**Request:**
```json
{
  "name": "contact_company",
  "from_object_id": "contact_uuid",
  "to_object_id": "company_uuid",
  "type": "lookup",
  "label": "Company",
  "inverse_label": "Contacts",
  "required": false,
  "cascade_delete": false
}
```

#### GET /api/relationships/{relationship_id}
Get relationship details

#### DELETE /api/relationships/{relationship_id}
Delete relationship

#### POST /api/relationships/{relationship_id}/link
Link two records (N:N only)

**Request:**
```json
{
  "from_record_id": "contact_uuid",
  "to_record_id": "opportunity_uuid",
  "metadata": {
    "role": "Champion"
  }
}
```

#### DELETE /api/relationships/{relationship_id}/link/{link_id}
Unlink records

#### GET /api/records/{record_id}/related/{relationship_id}
Get related records via relationship

**Response:**
```json
{
  "records": [
    {
      "id": "uuid",
      "data": {...},
      "relationship_metadata": {
        "role": "Champion"
      }
    }
  ]
}
```

---

### 4.6 Applications API

#### GET /api/applications
List user's applications

#### POST /api/applications
Create application

**Request:**
```json
{
  "name": "CRM",
  "description": "Customer Relationship Management",
  "icon": "briefcase",
  "object_ids": ["contact_uuid", "company_uuid"],
  "navigation": {
    "menu": [
      {
        "label": "Contacts",
        "objectId": "contact_uuid",
        "icon": "users"
      }
    ]
  }
}
```

#### GET /api/applications/{app_id}
Get application details

#### PATCH /api/applications/{app_id}
Update application

#### DELETE /api/applications/{app_id}
Delete application

---

## 5. Service Layer Architecture

### 5.1 Field Service (`app/services/field_service.py`)

```python
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.field import Field
from app.schemas.field import FieldCreate, FieldUpdate

class FieldService:
    async def create_field(
        self,
        db: AsyncSession,
        field: FieldCreate,
        user_id: UUID
    ) -> Field:
        """Create a new field"""
        pass

    async def get_fields(
        self,
        db: AsyncSession,
        user_id: UUID,
        category: Optional[str] = None,
        is_system: Optional[bool] = None
    ) -> List[Field]:
        """Get fields (global + user's own)"""
        pass

    async def get_field(
        self,
        db: AsyncSession,
        field_id: UUID
    ) -> Optional[Field]:
        """Get single field"""
        pass

    async def update_field(
        self,
        db: AsyncSession,
        field_id: UUID,
        updates: FieldUpdate,
        user_id: UUID
    ) -> Field:
        """Update field (only own fields)"""
        pass

    async def delete_field(
        self,
        db: AsyncSession,
        field_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete field (check if in use first)"""
        pass
```

### 5.2 Object Service (`app/services/object_service.py`)

```python
class ObjectService:
    async def create_object(
        self,
        db: AsyncSession,
        object_data: ObjectCreate,
        user_id: UUID
    ) -> Object:
        """
        Create object and link fields
        1. Create object record
        2. Create object_fields mappings
        3. Auto-add system fields
        """
        pass

    async def get_object_with_fields(
        self,
        db: AsyncSession,
        object_id: UUID
    ) -> ObjectWithFields:
        """Get object with all field definitions"""
        pass

    async def add_field_to_object(
        self,
        db: AsyncSession,
        object_id: UUID,
        field_id: UUID,
        config: ObjectFieldConfig
    ) -> ObjectField:
        """Add field to object"""
        pass
```

### 5.3 Record Service (`app/services/record_service.py`)

```python
class RecordService:
    async def create_record(
        self,
        db: AsyncSession,
        object_id: UUID,
        data: Dict[str, Any],
        user_id: UUID
    ) -> Record:
        """
        Create record with JSONB data
        1. Validate field IDs exist in object
        2. Validate field types (text, number, etc.)
        3. Store in data JSONB column
        4. Update primary_value
        """
        pass

    async def validate_record_data(
        self,
        db: AsyncSession,
        object_id: UUID,
        data: Dict[str, Any]
    ) -> bool:
        """Validate data against object's field definitions"""
        pass

    async def get_typed_values(
        self,
        db: AsyncSession,
        record: Record
    ) -> List[TypedFieldValue]:
        """Convert JSONB data to typed field values"""
        pass

    async def query_records(
        self,
        db: AsyncSession,
        object_id: UUID,
        filters: Optional[List[FilterCondition]] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> RecordQueryResult:
        """Query records with filters, sorting, pagination"""
        pass
```

---

## 6. Authentication & Authorization

### 6.1 Supabase Auth Integration

```python
# app/middleware/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify JWT token with Supabase
    Returns user info if valid
    """
    token = credentials.credentials

    try:
        # Verify with Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        user = supabase.auth.get_user(token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
```

### 6.2 RLS Integration

All queries use `created_by = auth.uid()` automatically via RLS policies.

---

## 7. Error Handling

### 7.1 Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Field 'email' is required",
    "details": {
      "field": "email",
      "constraint": "required"
    }
  }
}
```

### 7.2 Error Codes

```python
class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
```

---

## 8. Environment Variables

```bash
# .env.example

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/canvasapp
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# App
APP_NAME=Canvas App API
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Security
SECRET_KEY=your-secret-key-here
```

---

## 9. Testing Strategy

### 9.1 Unit Tests
```python
# tests/test_field_service.py
async def test_create_field():
    field = await field_service.create_field(
        db,
        FieldCreate(name="email", label="Email", type="email"),
        user_id
    )
    assert field.name == "email"
```

### 9.2 Integration Tests
```python
# tests/test_integration.py
async def test_create_object_with_fields():
    # Create fields
    # Create object
    # Link fields to object
    # Verify object_fields mapping
    pass
```

### 9.3 API Tests
```python
# tests/test_api.py
async def test_create_record_api(client):
    response = await client.post(
        "/api/records",
        json={"object_id": "uuid", "data": {...}},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
```

---

## 10. Development Workflow

### 10.1 Initial Setup

```bash
# 1. Create project directory
mkdir canvas-app-backend
cd canvas-app-backend

# 2. Initialize Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Create requirements.txt
cat > requirements.txt << EOF
fastapi[all]==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.25
alembic==1.13.1
asyncpg==0.29.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
supabase==2.3.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
ruff==0.1.8
mypy==1.7.1
EOF

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize Alembic
alembic init alembic

# 6. Create .env
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 10.2 Run Development Server

```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 10.3 Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 11. Deployment

### 11.1 Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: canvasapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 12. Claude Code Development Checklist

When developing with Claude Code, follow this order:

### Phase 1: Project Setup (30 min)
- [ ] Create project directory structure
- [ ] Setup virtual environment
- [ ] Install dependencies
- [ ] Configure `.env`

### Phase 2: Database (1 hour)
- [ ] Create Alembic migration with schema
- [ ] Run migration
- [ ] Verify tables created
- [ ] Test RLS policies

### Phase 3: Models (1 hour)
- [ ] Create SQLAlchemy models (Field, Object, Record, etc.)
- [ ] Test model relationships
- [ ] Verify auto-timestamps work

### Phase 4: Schemas (30 min)
- [ ] Create Pydantic schemas for request/response
- [ ] Add validation rules
- [ ] Test schema validation

### Phase 5: Services (2 hours)
- [ ] Implement FieldService
- [ ] Implement ObjectService
- [ ] Implement RecordService
- [ ] Add JSONB validation logic

### Phase 6: Routers (1 hour)
- [ ] Create API routes
- [ ] Add authentication middleware
- [ ] Test endpoints with Swagger UI

### Phase 7: Testing (1 hour)
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Test authentication flow

### Phase 8: Documentation (30 min)
- [ ] Generate OpenAPI docs
- [ ] Update README
- [ ] Add deployment guide

**Total Estimated Time: ~8 hours**

---

## 13. Success Criteria

Backend is ready when:
- ✅ All 7 tables created and RLS working
- ✅ Field Library API working (CRUD)
- ✅ Object API working with field mapping
- ✅ Record API working with JSONB validation
- ✅ Relationship API working (lookup + N:N)
- ✅ Authentication with Supabase working
- ✅ All tests passing (>90% coverage)
- ✅ OpenAPI docs accessible at `/docs`

---

## 14. Next Steps (After Backend Complete)

1. **Frontend Integration**
   - Update `src/services/` to call backend API
   - Remove localStorage fallback
   - Add API error handling

2. **Advanced Features**
   - Audit trail (track all changes)
   - Real-time updates (WebSockets)
   - Bulk operations optimization
   - Export/Import (CSV, JSON)

3. **Production**
   - Deploy to Railway/Render
   - Setup monitoring (Sentry)
   - Configure CI/CD
   - Performance testing

---

**This specification is complete and ready for Claude Code development!** 🚀
