# 🤖 CLAUDE PROMPT - Task 01: Field Model Schema Update

```
I need you to update the Field model and database schema to match the architecture specification. This is a CRITICAL task.

WHAT TO DO:
1. Update app/models/field.py to add: category, is_system_field, updated_at columns
2. Fix unique constraint from UNIQUE(name) to UNIQUE(name, created_by)
3. Change datetime.utcnow to datetime.now(UTC)
4. Create Alembic migration with all schema changes
5. Update Pydantic schemas (app/schemas/field.py)
6. Update service to support category and is_system filtering
7. Update router to add query parameters for filtering
8. Run migration and verify with psql

IMPORTANT:
- Use modern Python 3.11+ datetime: from datetime import UTC, datetime
- Migration must be reversible (downgrade function)
- Add indexes on category and is_system_field
- Create trigger for auto-updating updated_at

VERIFICATION:
- Run: alembic upgrade head
- Test: curl -X GET "http://localhost:8000/api/fields?category=Contact%20Info"
- Verify: psql -c "\d fields" shows all new columns

FOLLOW THE DETAILED STEPS BELOW:
```

---

## 📋 Objective

Update the `Field` model and database schema to match the architecture specification. Add missing columns: `category`, `is_system_field`, `updated_at`, and fix the unique constraint.

---

## 🎯 Problem

Current `Field` model is missing critical columns from the specification:

| Missing Column | Purpose |
|----------------|---------|
| `category` | Group fields by category (Contact Info, Business, System, etc.) |
| `is_system_field` | Distinguish system fields (created_at, owner) from custom fields |
| `updated_at` | Track when field definition was last modified |
| **Bug:** `UNIQUE(name)` | Should be `UNIQUE(name, created_by)` - users can have same field names |

---

## 📝 Implementation Steps

### Step 1: Update Field Model

**File:** `app/models/field.py`

```python
# BEFORE (current code)
class Field(Base):
    __tablename__ = "fields"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # ❌ Wrong constraint
    label = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    config = Column(JSONB, nullable=False, server_default='{}')
    is_global = Column(Boolean, nullable=False, default=False)
    is_custom = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)  # ❌ Deprecated
    created_by = Column(UUID(as_uuid=True), nullable=True)

# AFTER (updated code)
from datetime import UTC, datetime  # ✅ Import UTC
from sqlalchemy import UniqueConstraint  # ✅ Import for composite unique

class Field(Base):
    __tablename__ = "fields"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)  # ✅ Remove unique=True
    label = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    config = Column(JSONB, nullable=False, server_default='{}')

    # ✅ NEW: Add category
    category = Column(String, nullable=True, index=True)

    # ✅ UPDATED: Distinguish system vs custom fields
    is_global = Column(Boolean, nullable=False, default=False)
    is_system_field = Column(Boolean, nullable=False, default=False)  # ✅ NEW
    is_custom = Column(Boolean, nullable=False, default=True)

    # ✅ UPDATED: Modern datetime
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))  # ✅ NEW
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # ✅ NEW: Composite unique constraint
    __table_args__ = (
        UniqueConstraint('name', 'created_by', name='uq_field_name_created_by'),
    )
```

---

### Step 2: Create Alembic Migration

**Command:**
```bash
source venv/bin/activate
alembic revision -m "Add category, is_system_field, updated_at to fields table"
```

**File:** `alembic/versions/XXXX_add_field_columns.py`

```python
"""Add category, is_system_field, updated_at to fields table

Revision ID: XXXX
Revises: 000f38f3d771
Create Date: 2026-01-18 XX:XX:XX
"""
from alembic import op
import sqlalchemy as sa

revision = 'XXXX'
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
```

---

### Step 3: Run Migration

```bash
# Apply migration
alembic upgrade head

# Verify changes
psql $DATABASE_URL -c "\d fields"
```

**Expected Output:**
```
                       Table "public.fields"
     Column      |           Type           | Nullable |   Default
-----------------+--------------------------+----------+-------------
 id              | text                     | not null |
 name            | text                     | not null |
 label           | text                     | not null |
 type            | text                     | not null |
 description     | text                     |          |
 config          | jsonb                    | not null | '{}'::jsonb
 category        | text                     |          |              ← NEW
 is_global       | boolean                  | not null | false
 is_system_field | boolean                  | not null | false        ← NEW
 is_custom       | boolean                  | not null | true
 created_at      | timestamp with time zone | not null | now()
 updated_at      | timestamp with time zone | not null | now()        ← NEW
 created_by      | uuid                     |          |

Indexes:
    "fields_pkey" PRIMARY KEY, btree (id)
    "idx_fields_category" btree (category)                          ← NEW
    "idx_fields_system" btree (is_system_field) WHERE is_system_field = true  ← NEW
    "uq_field_name_created_by" UNIQUE CONSTRAINT, btree (name, created_by)   ← NEW

Triggers:
    trigger_field_updated_at BEFORE UPDATE ON fields                ← NEW
```

---

### Step 4: Update Pydantic Schemas

**File:** `app/schemas/field.py`

```python
# ✅ Add new fields to schemas
from datetime import datetime
from pydantic import BaseModel, Field

class FieldBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    label: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(text|number|email|phone|date|datetime|select|lookup|formula)$")
    description: str | None = None
    config: dict = Field(default_factory=dict)
    category: str | None = None  # ✅ NEW

class FieldCreate(FieldBase):
    """Schema for creating a new field"""
    pass

class FieldUpdate(BaseModel):
    """Schema for updating a field"""
    name: str | None = None
    label: str | None = None
    type: str | None = None
    description: str | None = None
    config: dict | None = None
    category: str | None = None  # ✅ NEW

class FieldResponse(FieldBase):
    """Schema for field response"""
    id: str
    is_global: bool
    is_system_field: bool  # ✅ NEW
    is_custom: bool
    created_at: datetime
    updated_at: datetime  # ✅ NEW
    created_by: str | None

    model_config = {"from_attributes": True}
```

---

### Step 5: Update Service Logic

**File:** `app/services/field_service.py`

```python
# ✅ Update query to filter by category
async def get_fields(
    self,
    db: AsyncSession,
    user_id: str,
    category: str | None = None,  # ✅ NEW parameter
    is_system: bool | None = None,
) -> list[Field]:
    """Get fields (global + user's own), optionally filter by category"""
    query = select(Field).where(
        or_(
            Field.is_global == True,
            Field.created_by == user_id
        )
    )

    # ✅ Filter by category if provided
    if category:
        query = query.where(Field.category == category)

    # ✅ Filter by system fields if provided
    if is_system is not None:
        query = query.where(Field.is_system_field == is_system)

    result = await db.execute(query)
    return result.scalars().all()
```

---

### Step 6: Update Router

**File:** `app/routers/fields.py`

```python
# ✅ Add query parameters for filtering
@router.get("/", response_model=list[FieldResponse])
async def list_fields(
    category: str | None = Query(None, description="Filter by category"),  # ✅ NEW
    is_system: bool | None = Query(None, description="Filter system fields"),  # ✅ NEW
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List all fields (global + user's own) with optional filters"""
    fields = await field_service.get_fields(db, user_id, category, is_system)
    return fields
```

---

## ✅ Acceptance Criteria

- [ ] `category` column exists in `fields` table
- [ ] `is_system_field` column exists in `fields` table
- [ ] `updated_at` column exists and auto-updates on row change
- [ ] Unique constraint is `(name, created_by)` not just `(name)`
- [ ] Migration runs successfully without errors
- [ ] All indexes are created (category, is_system_field)
- [ ] Trigger `trigger_field_updated_at` exists and works
- [ ] Field model uses `datetime.now(UTC)` instead of `datetime.utcnow()`
- [ ] Pydantic schemas include new fields
- [ ] API endpoint `/api/fields?category=Contact Info` works
- [ ] API endpoint `/api/fields?is_system=true` works
- [ ] Tests pass

---

## 🧪 Testing

**Manual Test:**
```bash
# 1. Create a field with category
curl -X POST http://localhost:8000/api/fields \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "email",
    "label": "Email Address",
    "type": "email",
    "category": "Contact Info"
  }'

# 2. Get fields by category
curl -X GET "http://localhost:8000/api/fields?category=Contact%20Info" \
  -H "Authorization: Bearer $TOKEN"

# 3. Verify updated_at changes on update
curl -X PATCH http://localhost:8000/api/fields/fld_001 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"label": "Email (Updated)"}'

# Check updated_at changed
```

**Unit Test:**
```python
# tests/test_services/test_field_service.py
async def test_field_category_filter(db_session, user_id):
    # Create fields in different categories
    await field_service.create_field(db_session, FieldCreate(
        name="email", label="Email", type="email", category="Contact Info"
    ), user_id)

    await field_service.create_field(db_session, FieldCreate(
        name="amount", label="Amount", type="number", category="Sales"
    ), user_id)

    # Filter by category
    contact_fields = await field_service.get_fields(db_session, user_id, category="Contact Info")
    assert len(contact_fields) == 1
    assert contact_fields[0].name == "email"
```

---

## 🚨 Rollback Plan

If migration fails:
```bash
alembic downgrade -1
```

This will:
1. Drop new columns
2. Drop new indexes
3. Drop trigger
4. Restore old unique constraint

---

## 📚 Related Tasks

- **Task 02:** Object Model Schema Update (depends on this)
- **Task 05:** System Fields Seed Data (depends on this)

---

**Priority:** 🔴 CRITICAL
**Estimated Time:** 2-3 hours
**Assignee:** Backend Developer
**Due Date:** Day 1
