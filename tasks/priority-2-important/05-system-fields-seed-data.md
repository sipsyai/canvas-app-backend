# 🤖 CLAUDE PROMPT - Task 05: System Fields Seed Data

```
I need you to create seed data for global system fields that should be available to all users. These fields (created_at, created_by, updated_at, updated_by, owner) are essential for every object.

WHAT TO DO:
1. Create Alembic migration to insert system fields
2. Set is_system_field=true, is_global=true for these fields
3. created_by should be NULL (global system fields)
4. Add these 5 system fields: created_at, created_by, updated_at, updated_by, owner
5. Verify fields are created with correct types and categories

SYSTEM FIELDS TO CREATE:
- fld_system_created_at (datetime) - When record was created
- fld_system_created_by (lookup → User) - Who created the record
- fld_system_updated_at (datetime) - When record was last modified
- fld_system_updated_by (lookup → User) - Who last modified
- fld_system_owner (lookup → User) - Record owner

VERIFICATION:
- Run: alembic upgrade head
- Test: curl -X GET "http://localhost:8000/api/fields?is_system=true"
- Should return 5 system fields

FOLLOW THE DETAILED STEPS BELOW:
```

---

## 📋 Objective

Create global system fields that are automatically available to all objects (similar to Salesforce standard fields).

---

## 🎯 System Fields List

| Field ID | Name | Label | Type | Description |
|----------|------|-------|------|-------------|
| `fld_system_created_at` | created_at | Created Date | datetime | When record was created |
| `fld_system_created_by` | created_by | Created By | lookup | User who created record |
| `fld_system_updated_at` | updated_at | Modified Date | datetime | When record was last modified |
| `fld_system_updated_by` | updated_by | Modified By | lookup | User who last modified record |
| `fld_system_owner` | owner | Owner | lookup | Record owner (can reassign) |

---

## 📝 Implementation Steps

### Step 1: Create Alembic Migration

**Command:**
```bash
source venv/bin/activate
alembic revision -m "Add system fields seed data"
```

**File:** `alembic/versions/XXXX_add_system_fields.py`

```python
"""Add system fields seed data

Revision ID: XXXX
Revises: [previous migration ID]
Create Date: 2026-01-18 XX:XX:XX
"""
from alembic import op
import sqlalchemy as sa

revision = 'XXXX'
down_revision = '[previous]'
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
```

---

### Step 2: Run Migration

```bash
# Apply migration
alembic upgrade head

# Verify system fields created
psql $DATABASE_URL -c "SELECT id, name, label, type, is_system_field, is_global FROM fields WHERE is_system_field = true;"
```

**Expected Output:**
```
           id            |    name     |     label      |   type   | is_system_field | is_global
-------------------------+-------------+----------------+----------+-----------------+-----------
 fld_system_created_at   | created_at  | Created Date   | datetime | t               | t
 fld_system_created_by   | created_by  | Created By     | lookup   | t               | t
 fld_system_updated_at   | updated_at  | Modified Date  | datetime | t               | t
 fld_system_updated_by   | updated_by  | Modified By    | lookup   | t               | t
 fld_system_owner        | owner       | Owner          | lookup   | t               | t
```

---

### Step 3: Test API Endpoint

```bash
# Get all system fields
curl -X GET "http://localhost:8000/api/fields?is_system=true" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
[
  {
    "id": "fld_system_created_at",
    "name": "created_at",
    "label": "Created Date",
    "type": "datetime",
    "category": "System",
    "is_global": true,
    "is_system_field": true,
    "is_custom": false
  },
  {
    "id": "fld_system_created_by",
    "name": "created_by",
    "label": "Created By",
    "type": "lookup",
    "category": "System",
    "is_global": true,
    "is_system_field": true,
    "is_custom": false,
    "config": {
      "lookupObject": "user"
    }
  },
  ...
]
```

---

### Step 4: Auto-Add System Fields to New Objects (Optional Service Logic)

**File:** `app/services/object_service.py`

```python
async def create_object(
    self,
    db: AsyncSession,
    object_data: ObjectCreate,
    user_id: str
) -> Object:
    """Create object and auto-add system fields"""

    # 1. Create object
    new_object = Object(...)
    db.add(new_object)
    await db.commit()

    # 2. Get all system fields
    system_fields_query = select(Field).where(Field.is_system_field == True)
    system_fields_result = await db.execute(system_fields_query)
    system_fields = system_fields_result.scalars().all()

    # 3. Auto-add system fields to object
    for idx, system_field in enumerate(system_fields):
        object_field = ObjectField(
            id=f"objfld_{uuid.uuid4().hex[:8]}",
            object_id=new_object.id,
            field_id=system_field.id,
            display_order=1000 + idx,  # Append at end
            is_required=False,
            is_visible=True,
            is_readonly=True  # System fields are readonly
        )
        db.add(object_field)

    await db.commit()
    await db.refresh(new_object)
    return new_object
```

---

## ✅ Acceptance Criteria

- [ ] 5 system fields created in database
- [ ] All system fields have `is_system_field = true`
- [ ] All system fields have `is_global = true`
- [ ] All system fields have `created_by = NULL` (global)
- [ ] All system fields have `category = 'System'`
- [ ] Lookup fields have correct config: `{"lookupObject": "user"}`
- [ ] API endpoint `/api/fields?is_system=true` returns 5 fields
- [ ] New objects automatically include system fields (if auto-add implemented)
- [ ] Migration is reversible (downgrade works)

---

## 🧪 Testing

**Unit Test:**
```python
# tests/test_services/test_field_service.py
async def test_system_fields_exist(db_session):
    """Test that system fields are created"""
    fields = await field_service.get_fields(
        db_session,
        user_id=None,  # No user needed for global fields
        is_system=True
    )

    assert len(fields) == 5

    field_names = {f.name for f in fields}
    assert field_names == {
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "owner"
    }

    # Verify all are global and system
    for field in fields:
        assert field.is_global is True
        assert field.is_system_field is True
        assert field.is_custom is False
        assert field.category == "System"
```

---

## 🚨 Rollback Plan

```bash
alembic downgrade -1
```

This will delete all system fields from the database.

---

## 📚 Related Tasks

- **Task 01:** Field Model Schema Update (prerequisite - adds is_system_field column)
- **Task 06:** User Object Implementation (these fields reference User object)

---

**Priority:** 🟡 IMPORTANT
**Estimated Time:** 1 hour
**Assignee:** Backend Developer
**Due Date:** Day 2
