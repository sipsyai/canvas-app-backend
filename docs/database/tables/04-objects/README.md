# objects Table

## Genel Bakış

**Amaç:** Object tanımları (Contact, Company, Opportunity, vb.)

**Tip:** Metadata Table
**ID Format:** obj_xxxxxxxx (8 hex chars)
**Entities:** Contact, Company, Opportunity, Ticket, Asset, vb.
**Flexible:** JSONB for views & permissions

---

## Tablo Özellikleri

| Özellik | Değer |
|---------|-------|
| **Primary Key** | id (VARCHAR) |
| **Unique Constraints** | None (but name should be unique per user) |
| **Foreign Keys** | None (root metadata table) |
| **Referenced By** | object_fields, records, relationships (CASCADE) |
| **Cascade Deletes** | YES (deletes all dependent data) |
| **Indexes** | 2 indexes (id) |
| **Row Estimate** | Hundreds |

---

## Kolonlar

### id (varchar) - Primary Key
- **Tip:** VARCHAR
- **Nullable:** NO
- **Default:** -
- **Format:** `obj_` + 8 hex chars
- **Generasyon:** Python `uuid.uuid4().hex[:8]`
- **Örnek:** `obj_contact`, `obj_company`

### name (varchar)
- **Tip:** VARCHAR
- **Nullable:** NO
- **Default:** -
- **Açıklama:** Object internal name (identifier)
- **Örnek:** `contact`, `company`, `opportunity`
- **Convention:** Singular, lowercase

### label (varchar)
- **Tip:** VARCHAR
- **Nullable:** NO
- **Default:** -
- **Açıklama:** Display label (shown in UI)
- **Örnek:** `Contact`, `Company`, `Opportunity`

### plural_name (varchar)
- **Tip:** VARCHAR
- **Nullable:** NO
- **Default:** -
- **Açıklama:** Plural form (for lists, navigation)
- **Örnek:** `Contacts`, `Companies`, `Opportunities`

### description (text)
- **Tip:** TEXT
- **Nullable:** YES
- **Default:** NULL
- **Açıklama:** Object description
- **Örnek:** `Person or individual you do business with`

### icon (varchar)
- **Tip:** VARCHAR
- **Nullable:** YES
- **Default:** NULL
- **Açıklama:** Icon (emoji or CSS class name)
- **Örnekler:**
  - Emoji: `👤`, `🏢`, `💼`, `🎫`
  - CSS: `fa-user`, `mdi-office-building`

### is_custom (boolean)
- **Tip:** BOOLEAN
- **Nullable:** NO
- **Default:** true
- **Açıklama:** Custom object (created by user)
- **Values:**
  - `true` - User-created object
  - `false` - System-defined object

### is_global (boolean)
- **Tip:** BOOLEAN
- **Nullable:** NO
- **Default:** false
- **Açıklama:** Global object (shared across tenants)
- **Use Case:** System objects available to all users

### views (jsonb)
- **Tip:** JSONB
- **Nullable:** NO
- **Default:**
```json
{
  "forms": [],
  "tables": [],
  "kanbans": [],
  "calendars": []
}
```
- **Açıklama:** View configurations for this object
- **Schema:**

```json
{
  "forms": [
    {
      "id": "form_default",
      "name": "Default Form",
      "layout": [
        {
          "section": "Basic Info",
          "fields": ["fld_name", "fld_email"]
        }
      ],
      "isDefault": true
    }
  ],
  "tables": [
    {
      "id": "table_all",
      "name": "All Contacts",
      "columns": ["fld_name", "fld_email", "fld_phone"],
      "filters": [],
      "sortBy": "created_at",
      "sortOrder": "desc"
    }
  ],
  "kanbans": [
    {
      "id": "kanban_status",
      "name": "By Status",
      "groupByField": "fld_status",
      "cardFields": ["fld_name", "fld_priority"]
    }
  ],
  "calendars": [
    {
      "id": "calendar_meetings",
      "name": "Meetings",
      "dateField": "fld_meeting_date",
      "titleField": "fld_name"
    }
  ]
}
```

### permissions (jsonb)
- **Tip:** JSONB
- **Nullable:** NO
- **Default:**
```json
{
  "read": ["all"],
  "create": ["all"],
  "update": ["all"],
  "delete": ["all"]
}
```
- **Açıklama:** RBAC permissions for this object
- **Schema:**

```json
{
  "read": ["all"],  // Who can view records
  "create": ["all", "role_admin", "user_uuid"],  // Who can create
  "update": ["owner", "role_admin"],  // Who can update
  "delete": ["role_admin"]  // Who can delete
}
```

**Permission Values:**
- `"all"` - Everyone
- `"owner"` - Record creator only
- `"user_<uuid>"` - Specific user
- `"role_<name>"` - Specific role (admin, manager, etc.)

### created_at (timestamptz)
- **Tip:** TIMESTAMP WITH TIME ZONE
- **Nullable:** NO
- **Default:** NOW()
- **Açıklama:** Object creation timestamp

### updated_at (timestamptz)
- **Tip:** TIMESTAMP WITH TIME ZONE
- **Nullable:** NO
- **Default:** NOW()
- **Açıklama:** Last update timestamp
- **Maintenance:** Manually updated

### created_by (uuid)
- **Tip:** UUID
- **Nullable:** YES
- **Default:** NULL
- **References:** users.id (not enforced)
- **Açıklama:** Object creator

---

## İlişkiler

### Referenced By (Outbound)

#### 1. object_fields.object_id → objects.id
- **Type:** CASCADE
- **Behavior:** Delete object → delete all field attachments
- **Query Pattern:** Get fields for object

```sql
SELECT * FROM object_fields
WHERE object_id = 'obj_contact';
```

#### 2. records.object_id → objects.id
- **Type:** CASCADE
- **Behavior:** Delete object → delete all records ⚠️
- **Critical:** Deleting object deletes ALL data!
- **Query Pattern:** Get records for object

```sql
SELECT * FROM records
WHERE object_id = 'obj_contact';
```

#### 3. relationships.from_object_id → objects.id
#### 4. relationships.to_object_id → objects.id
- **Type:** CASCADE
- **Behavior:** Delete object → delete all relationships
- **Query Pattern:** Get relationships for object

```sql
SELECT * FROM relationships
WHERE from_object_id = 'obj_contact'
   OR to_object_id = 'obj_contact';
```

---

## Index'ler

### 1. objects_pkey (UNIQUE)
```sql
CREATE UNIQUE INDEX objects_pkey ON objects USING btree (id);
```
**Amaç:** Primary key
**Query:** `WHERE id = 'obj_xxx'`

### 2. ix_objects_id
```sql
CREATE INDEX ix_objects_id ON objects USING btree (id);
```
**Amaç:** Additional id lookup (SQLAlchemy)

---

## JSONB Schemas

### views.forms

```json
{
  "id": "form_default",
  "name": "Default Form",
  "description": "Default contact form",
  "layout": [
    {
      "section": "Basic Information",
      "fields": ["fld_name", "fld_email", "fld_phone"]
    },
    {
      "section": "Additional Details",
      "fields": ["fld_company", "fld_position"],
      "collapsible": true
    }
  ],
  "isDefault": true,
  "submitButtonText": "Save Contact"
}
```

### views.tables

```json
{
  "id": "table_all",
  "name": "All Contacts",
  "description": "Complete list of all contacts",
  "columns": [
    "fld_name",
    "fld_email",
    "fld_phone",
    "fld_company"
  ],
  "filters": [
    {
      "field": "fld_status",
      "operator": "equals",
      "value": "active"
    }
  ],
  "sortBy": "created_at",
  "sortOrder": "desc",
  "pageSize": 50
}
```

### views.kanbans

```json
{
  "id": "kanban_status",
  "name": "Opportunities by Status",
  "groupByField": "fld_status",
  "cardFields": ["fld_name", "fld_value", "fld_close_date"],
  "cardTitleField": "fld_name",
  "cardSubtitleField": "fld_company",
  "allowDragDrop": true
}
```

### views.calendars

```json
{
  "id": "calendar_meetings",
  "name": "Meeting Calendar",
  "dateField": "fld_meeting_date",
  "titleField": "fld_name",
  "descriptionField": "fld_notes",
  "colorField": "fld_status",
  "defaultView": "month"
}
```

### permissions

```json
{
  "read": [
    "all"  // Everyone can view
  ],
  "create": [
    "all",  // Everyone can create
    "role_sales",
    "role_admin"
  ],
  "update": [
    "owner",  // Record creator
    "role_manager",
    "role_admin",
    "user_550e8400-e29b-41d4-a716-446655440000"  // Specific user
  ],
  "delete": [
    "role_admin"  // Only admins can delete
  ]
}
```

---

## Örnek Kullanımlar

### 1. Create Object (System Admin)

```python
from app.services.object_service import ObjectService

object_service = ObjectService()

# Create Contact object
contact_object = await object_service.create_object(
    db=db,
    object_in=ObjectCreate(
        name="contact",
        label="Contact",
        plural_name="Contacts",
        description="Person or individual you do business with",
        icon="👤",
        is_custom=False,  # System object
        is_global=True,  # Available to all
        views={
            "forms": [{
                "id": "form_default",
                "name": "Default Form",
                "layout": [{
                    "section": "Basic Info",
                    "fields": ["fld_name", "fld_email", "fld_phone"]
                }],
                "isDefault": True
            }],
            "tables": [{
                "id": "table_all",
                "name": "All Contacts",
                "columns": ["fld_name", "fld_email", "fld_phone"],
                "sortBy": "created_at",
                "sortOrder": "desc"
            }],
            "kanbans": [],
            "calendars": []
        },
        permissions={
            "read": ["all"],
            "create": ["all"],
            "update": ["owner", "role_admin"],
            "delete": ["role_admin"]
        }
    ),
    user_id=admin_user_id
)
```

### 2. Create Custom Object (User)

```python
# Create custom Product object
product_object = await object_service.create_object(
    db=db,
    object_in=ObjectCreate(
        name="product",
        label="Product",
        plural_name="Products",
        description="Product catalog item",
        icon="📦",
        is_custom=True,  # Custom object
        is_global=False  # User-specific
    ),
    user_id=user_id
)
```

### 3. Update Object Views

```python
# Add kanban view
await object_service.update_object(
    db=db,
    object_id="obj_opportunity",
    object_in=ObjectUpdate(
        views={
            **existing_views,
            "kanbans": [{
                "id": "kanban_stage",
                "name": "By Stage",
                "groupByField": "fld_stage",
                "cardFields": ["fld_name", "fld_value"]
            }]
        }
    )
)
```

### 4. Update Permissions

```python
# Restrict delete to admins only
await object_service.update_object(
    db=db,
    object_id="obj_contact",
    object_in=ObjectUpdate(
        permissions={
            "read": ["all"],
            "create": ["all"],
            "update": ["owner", "role_admin"],
            "delete": ["role_admin"]  # Changed
        }
    )
)
```

---

## Örnek Sorgular

### 1. Get All Global Objects

```sql
SELECT
    id,
    name,
    label,
    plural_name,
    icon,
    is_custom
FROM objects
WHERE is_global = true
ORDER BY name;
```

### 2. Get User's Custom Objects

```sql
SELECT
    id,
    name,
    label,
    plural_name,
    description,
    created_at
FROM objects
WHERE created_by = '550e8400-e29b-41d4-a716-446655440000'
  AND is_custom = true
ORDER BY created_at DESC;
```

### 3. Get Object with Field Count

```sql
SELECT
    o.id,
    o.name,
    o.label,
    o.plural_name,
    COUNT(of.id) AS field_count
FROM objects o
LEFT JOIN object_fields of ON o.id = of.object_id
GROUP BY o.id, o.name, o.label, o.plural_name
ORDER BY field_count DESC;
```

### 4. Get Object with Record Count

```sql
SELECT
    o.id,
    o.name,
    o.label,
    COUNT(r.id) AS record_count,
    COUNT(r.id) FILTER (WHERE r.created_at > NOW() - INTERVAL '7 days') AS recent_records
FROM objects o
LEFT JOIN records r ON o.id = r.object_id
GROUP BY o.id, o.name, o.label
ORDER BY record_count DESC;
```

### 5. Get Object with Views

```sql
SELECT
    id,
    name,
    label,
    jsonb_array_length(views->'forms') AS form_count,
    jsonb_array_length(views->'tables') AS table_count,
    jsonb_array_length(views->'kanbans') AS kanban_count,
    jsonb_array_length(views->'calendars') AS calendar_count
FROM objects
WHERE jsonb_array_length(views->'forms') > 0;
```

### 6. Find Objects with Specific Permission

```sql
-- Find objects where "all" can create
SELECT
    id,
    name,
    label,
    permissions
FROM objects
WHERE permissions->'create' @> '["all"]'::jsonb;
```

### 7. Get Complete Object Schema

```sql
-- Object with all fields
SELECT
    o.id,
    o.name,
    o.label,
    o.plural_name,
    o.icon,
    json_agg(
        json_build_object(
            'field_id', f.id,
            'field_name', f.name,
            'field_label', f.label,
            'field_type', f.type,
            'display_order', of.display_order,
            'is_required', of.is_required
        ) ORDER BY of.display_order
    ) AS fields
FROM objects o
LEFT JOIN object_fields of ON o.id = of.object_id
LEFT JOIN fields f ON of.field_id = f.id
WHERE o.id = 'obj_contact'
GROUP BY o.id, o.name, o.label, o.plural_name, o.icon;
```

---

## Permissions System

### Permission Check Logic

```python
def check_permission(
    user_id: str,
    user_roles: list[str],
    object_permissions: dict,
    action: str,  # "read", "create", "update", "delete"
    record_owner_id: str | None = None
) -> bool:
    """Check if user has permission for action"""

    allowed = object_permissions.get(action, [])

    # Check "all"
    if "all" in allowed:
        return True

    # Check specific user
    if f"user_{user_id}" in allowed:
        return True

    # Check roles
    for role in user_roles:
        if f"role_{role}" in allowed:
            return True

    # Check owner (for update/delete)
    if "owner" in allowed and record_owner_id == user_id:
        return True

    return False
```

### Example Usage

```python
# Check if user can create contact
can_create = check_permission(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    user_roles=["sales", "user"],
    object_permissions={
        "read": ["all"],
        "create": ["all"],
        "update": ["owner", "role_admin"],
        "delete": ["role_admin"]
    },
    action="create"
)
# Result: True (because "all" can create)

# Check if user can delete
can_delete = check_permission(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    user_roles=["sales", "user"],
    object_permissions=...,
    action="delete"
)
# Result: False (only role_admin can delete)
```

---

## Views System

### Default View Creation

```python
def create_default_views(object_id: str, field_ids: list[str]) -> dict:
    """Create default views for new object"""

    return {
        "forms": [
            {
                "id": f"form_default_{uuid.uuid4().hex[:8]}",
                "name": "Default Form",
                "layout": [
                    {
                        "section": "Details",
                        "fields": field_ids[:10]  # First 10 fields
                    }
                ],
                "isDefault": True
            }
        ],
        "tables": [
            {
                "id": f"table_all_{uuid.uuid4().hex[:8]}",
                "name": "All Records",
                "columns": field_ids[:5],  # First 5 fields as columns
                "sortBy": "created_at",
                "sortOrder": "desc",
                "pageSize": 50
            }
        ],
        "kanbans": [],
        "calendars": []
    }
```

---

## Best Practices

### 1. Object Naming Convention

**✅ GOOD:**
- `contact` (singular, lowercase)
- `company`
- `opportunity`

**❌ BAD:**
- `contacts` (plural)
- `Contact` (uppercase)
- `my_contact` (unnecessary prefix)

### 2. Plural Names

```python
# Simple pluralization
"contact" → "Contacts"
"company" → "Companies"  # Irregular

# Use proper plural forms
"opportunity" → "Opportunities"  # NOT "Opportunitys"
```

### 3. Icon Selection

**Emoji (Recommended):**
```python
{
    "contact": "👤",
    "company": "🏢",
    "opportunity": "💼",
    "ticket": "🎫",
    "task": "✅"
}
```

**CSS Classes:**
```python
{
    "contact": "fa-user",
    "company": "mdi-office-building"
}
```

### 4. Permission Granularity

```python
# ✅ GOOD - Granular permissions
{
    "read": ["all"],
    "create": ["role_sales", "role_admin"],
    "update": ["owner", "role_manager", "role_admin"],
    "delete": ["role_admin"]
}

# ❌ BAD - Too open
{
    "read": ["all"],
    "create": ["all"],
    "update": ["all"],
    "delete": ["all"]  # Everyone can delete!
}
```

### 5. Object Deletion Safety

```python
# ALWAYS warn before deleting object
async def safe_delete_object(db: AsyncSession, object_id: str):
    # 1. Count records
    record_count = await db.scalar(
        select(func.count(Record.id))
        .where(Record.object_id == object_id)
    )

    if record_count > 0:
        raise ValueError(
            f"Cannot delete: object has {record_count} records. "
            "This will delete ALL data!"
        )

    # 2. Count relationships
    rel_count = await db.scalar(
        select(func.count(Relationship.id))
        .where(
            (Relationship.from_object_id == object_id) |
            (Relationship.to_object_id == object_id)
        )
    )

    if rel_count > 0:
        raise ValueError(
            f"Cannot delete: object has {rel_count} relationships"
        )

    # 3. Safe to delete
    await db.delete(object)
    await db.commit()
```

---

## Migration History

**Created:** Initial migration
**File:** `alembic/versions/003_objects.py`

**Changes:**
- 2026-01-15: Initial table creation
- 2026-01-16: Added views column (JSONB)
- 2026-01-17: Added permissions column (JSONB)
- 2026-01-18: Added updated_at column

---

## İlgili Dosyalar

- **Model:** `app/models/object.py`
- **Schema:** `app/schemas/object.py`
- **Router:** `app/routers/objects.py`
- **Service:** `app/services/object_service.py`
- **API Docs:** `docs/api/03-objects/`

---

**Last Updated:** 2026-01-18
**Status:** ✅ Production Ready
**View Types:** 4 (forms, tables, kanbans, calendars)
**Permission Actions:** 4 (read, create, update, delete)
