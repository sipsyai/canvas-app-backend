# 🤖 CLAUDE PROMPT - Task 02: Object Model Schema Update

```
I need you to update the Object model to add missing JSONB columns for views and permissions. This enables the frontend to define custom TableViews, FormViews, KanbanViews, and CRUD permissions.

WHAT TO DO:
1. Update app/models/object.py to add: views JSONB, permissions JSONB columns
2. Rename plural_label to plural_name (for consistency with spec)
3. Update datetime.utcnow to datetime.now(UTC)
4. Create Alembic migration for schema changes
5. Update Pydantic schemas (app/schemas/object.py)
6. Verify with test data (create object with views config)

IMPORTANT:
- views JSONB default: {"forms": [], "tables": [], "kanbans": [], "calendars": []}
- permissions JSONB default: {"create": ["all"], "read": ["all"], "update": ["all"], "delete": ["all"]}
- Use GIN index on views JSONB for performance

VERIFICATION:
- Run: alembic upgrade head
- Test: Create object with custom TableView configuration
- Verify: psql -c "\d objects" shows views and permissions columns

FOLLOW THE DETAILED STEPS BELOW:
```

---

## 📋 Objective

Add `views` and `permissions` JSONB columns to the Object model to enable frontend customization of TableView, FormView, KanbanView, and CRUD permissions.

---

## 🎯 Problem

Current Object model is missing:

| Missing Column | Purpose |
|----------------|---------|
| `views` | Store custom view configurations (TableView, FormView, Kanban, Calendar) |
| `permissions` | Store CRUD permissions (create, read, update, delete roles) |
| **Naming inconsistency** | `plural_label` should be `plural_name` per specification |

**Example Use Case:**
```json
{
  "views": {
    "tables": [
      {
        "id": "view_contact_all",
        "name": "All Contacts",
        "columns": ["fld_name", "fld_email", "fld_phone"],
        "filters": [],
        "sortBy": "fld_name"
      }
    ],
    "forms": [...],
    "kanbans": [...],
    "calendars": [...]
  },
  "permissions": {
    "create": ["all"],
    "read": ["all"],
    "update": ["owner", "admin"],
    "delete": ["admin"]
  }
}
```

---

## 📝 Implementation Steps

### Step 1: Update Object Model

**File:** `app/models/object.py`

```python
# BEFORE (current code)
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship as db_relationship
from app.database import Base

class Object(Base):
    __tablename__ = "objects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    label = Column(String, nullable=False)
    plural_label = Column(String, nullable=False)  # ❌ Should be plural_name
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    is_custom = Column(Boolean, nullable=False, default=True)
    is_global = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)  # ❌ Deprecated
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)  # ❌ Deprecated
    created_by = Column(UUID(as_uuid=True), nullable=True)

# AFTER (updated code)
from datetime import UTC, datetime  # ✅ Import UTC
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship as db_relationship
from app.database import Base

class Object(Base):
    __tablename__ = "objects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    label = Column(String, nullable=False)
    plural_name = Column(String, nullable=False)  # ✅ RENAMED from plural_label
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    is_custom = Column(Boolean, nullable=False, default=True)
    is_global = Column(Boolean, nullable=False, default=False)

    # ✅ NEW: Views configuration (TableView, FormView, Kanban, Calendar)
    views = Column(JSONB, nullable=False, server_default='{"forms": [], "tables": [], "kanbans": [], "calendars": []}')

    # ✅ NEW: Permissions configuration (CRUD roles)
    permissions = Column(JSONB, nullable=False, server_default='{"create": ["all"], "read": ["all"], "update": ["all"], "delete": ["all"]}')

    # ✅ UPDATED: Modern datetime
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships (unchanged)
    object_fields = db_relationship("ObjectField", back_populates="object", cascade="all, delete-orphan")
    records = db_relationship("Record", back_populates="object", cascade="all, delete-orphan")
    relationships_from = db_relationship(
        "Relationship",
        foreign_keys="Relationship.from_object_id",
        back_populates="from_object",
        cascade="all, delete-orphan"
    )
    relationships_to = db_relationship(
        "Relationship",
        foreign_keys="Relationship.to_object_id",
        back_populates="to_object",
        cascade="all, delete-orphan"
    )
```

---

### Step 2: Create Alembic Migration

**Command:**
```bash
source venv/bin/activate
alembic revision -m "Add views and permissions to objects, rename plural_label"
```

**File:** `alembic/versions/XXXX_add_views_permissions.py`

```python
"""Add views and permissions to objects, rename plural_label

Revision ID: XXXX
Revises: [previous migration ID]
Create Date: 2026-01-18 XX:XX:XX
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = 'XXXX'
down_revision = '[previous]'
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
```

---

### Step 3: Run Migration

```bash
# Apply migration
alembic upgrade head

# Verify changes
psql $DATABASE_URL -c "\d objects"
```

**Expected Output:**
```sql
                       Table "public.objects"
     Column      |           Type           | Nullable |   Default
-----------------+--------------------------+----------+-------------
 id              | text                     | not null |
 name            | text                     | not null |
 label           | text                     | not null |
 plural_name     | text                     | not null |              ← RENAMED
 description     | text                     |          |
 icon            | text                     |          |
 is_custom       | boolean                  | not null | true
 is_global       | boolean                  | not null | false
 views           | jsonb                    | not null | {...}        ← NEW
 permissions     | jsonb                    | not null | {...}        ← NEW
 created_at      | timestamp with time zone | not null | now()
 updated_at      | timestamp with time zone | not null | now()
 created_by      | uuid                     |          |

Indexes:
    "objects_pkey" PRIMARY KEY, btree (id)
    "idx_objects_views" gin (views)                                ← NEW
    "idx_objects_permissions" gin (permissions)                    ← NEW
```

---

### Step 4: Update Pydantic Schemas

**File:** `app/schemas/object.py`

```python
from datetime import datetime
from pydantic import BaseModel, Field

class ObjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    label: str = Field(..., min_length=1, max_length=255)
    plural_name: str = Field(..., min_length=1, max_length=255)  # ✅ RENAMED
    description: str | None = None
    icon: str | None = None

class ObjectCreate(ObjectBase):
    """Schema for creating a new object"""
    views: dict = Field(default_factory=lambda: {  # ✅ NEW
        "forms": [],
        "tables": [],
        "kanbans": [],
        "calendars": []
    })
    permissions: dict = Field(default_factory=lambda: {  # ✅ NEW
        "create": ["all"],
        "read": ["all"],
        "update": ["all"],
        "delete": ["all"]
    })

class ObjectUpdate(BaseModel):
    """Schema for updating an object"""
    name: str | None = None
    label: str | None = None
    plural_name: str | None = None  # ✅ RENAMED
    description: str | None = None
    icon: str | None = None
    views: dict | None = None  # ✅ NEW
    permissions: dict | None = None  # ✅ NEW

class ObjectResponse(ObjectBase):
    """Schema for object response"""
    id: str
    is_custom: bool
    is_global: bool
    views: dict  # ✅ NEW
    permissions: dict  # ✅ NEW
    created_at: datetime
    updated_at: datetime
    created_by: str | None

    model_config = {"from_attributes": True}
```

---

### Step 5: Update Service Logic (if needed)

**File:** `app/services/object_service.py`

```python
# ✅ Ensure views and permissions are handled in create/update
async def create_object(
    self,
    db: AsyncSession,
    object_data: ObjectCreate,
    user_id: str
) -> Object:
    """Create object with default views and permissions"""
    new_object = Object(
        id=f"obj_{uuid.uuid4().hex[:8]}",
        name=object_data.name,
        label=object_data.label,
        plural_name=object_data.plural_name,  # ✅ Use plural_name
        description=object_data.description,
        icon=object_data.icon,
        views=object_data.views,  # ✅ Include views
        permissions=object_data.permissions,  # ✅ Include permissions
        created_by=user_id
    )
    db.add(new_object)
    await db.commit()
    await db.refresh(new_object)
    return new_object
```

---

## ✅ Acceptance Criteria

- [ ] `views` JSONB column exists in `objects` table
- [ ] `permissions` JSONB column exists in `objects` table
- [ ] Column renamed: `plural_label` → `plural_name`
- [ ] GIN indexes created on `views` and `permissions`
- [ ] Migration runs successfully without errors
- [ ] Object model uses `datetime.now(UTC)` instead of `datetime.utcnow()`
- [ ] Pydantic schemas updated with new fields
- [ ] API endpoint `/api/objects` returns objects with views and permissions
- [ ] Tests pass

---

## 🧪 Testing

**Manual Test:**
```bash
# 1. Create object with custom TableView
curl -X POST http://localhost:8000/api/objects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "contact",
    "label": "Contact",
    "plural_name": "Contacts",
    "icon": "users",
    "views": {
      "tables": [
        {
          "id": "view_all_contacts",
          "name": "All Contacts",
          "columns": ["fld_name", "fld_email", "fld_phone"],
          "sortBy": "fld_name"
        }
      ],
      "forms": [],
      "kanbans": [],
      "calendars": []
    },
    "permissions": {
      "create": ["all"],
      "read": ["all"],
      "update": ["owner", "admin"],
      "delete": ["admin"]
    }
  }'

# 2. Verify object has views
curl -X GET http://localhost:8000/api/objects/{object_id} \
  -H "Authorization: Bearer $TOKEN"
```

**Unit Test:**
```python
# tests/test_services/test_object_service.py
async def test_object_with_custom_views(db_session, user_id):
    object_data = ObjectCreate(
        name="contact",
        label="Contact",
        plural_name="Contacts",
        views={
            "tables": [{
                "id": "view_all",
                "name": "All Contacts",
                "columns": ["fld_name", "fld_email"]
            }]
        }
    )

    obj = await object_service.create_object(db_session, object_data, user_id)

    assert obj.plural_name == "Contacts"  # Test rename
    assert "tables" in obj.views
    assert len(obj.views["tables"]) == 1
    assert obj.views["tables"][0]["name"] == "All Contacts"
```

---

## 🚨 Rollback Plan

```bash
alembic downgrade -1
```

This will:
1. Drop `views` and `permissions` columns
2. Drop GIN indexes
3. Rename `plural_name` back to `plural_label`

---

## 📚 Related Tasks

- **Task 01:** Field Model Schema Update (prerequisite)
- **Task 03:** Test Coverage Expansion (depends on this)

---

**Priority:** 🔴 CRITICAL
**Estimated Time:** 1-2 hours
**Assignee:** Backend Developer
**Due Date:** Day 1
