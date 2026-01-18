# fields Table

## Genel Bakış

**Amaç:** Yeniden kullanılabilir field tanımları (text, number, email, vb.)

**Tip:** Metadata Table
**ID Format:** fld_xxxxxxxx (8 hex chars)
**Reusable:** YES (bir field birden fazla object'de kullanılabilir)
**Global Support:** YES (is_global flag ile tenant'lar arası paylaşım)

---

## Tablo Özellikleri

| Özellik | Değer |
|---------|-------|
| **Primary Key** | id (VARCHAR) |
| **Unique Constraints** | (name, created_by) |
| **Foreign Keys** | None (root metadata table) |
| **Referenced By** | object_fields (RESTRICT) |
| **Cascade Deletes** | RESTRICT (cannot delete if in use) |
| **Indexes** | 4 indexes (id, name+created_by, category) |
| **Row Estimate** | Hundreds to thousands |

---

## Kolonlar

### id (varchar) - Primary Key
- **Tip:** VARCHAR
- **Nullable:** NO
- **Default:** -
- **Format:** `fld_` + 8 hex chars
- **Generasyon:** Python `uuid.uuid4().hex[:8]`
- **Örnek:** `fld_a1b2c3d4`

### name (varchar)
- **Tip:** VARCHAR
- **Nullable:** NO
- **Default:** -
- **Unique:** YES (with created_by)
- **Açıklama:** Field internal name (identifier)
- **Örnek:** `full_name`, `email_address`, `product_price`
- **Constraint:** Unique per user

### label (varchar)
- **Tip:** VARCHAR
- **Nullable:** NO
- **Default:** -
- **Açıklama:** Display label (shown in UI)
- **Örnek:** `Full Name`, `Email`, `Price`

### type (varchar)
- **Tip:** VARCHAR
- **Nullable:** NO
- **Default:** -
- **Açıklama:** Field type
- **Allowed Values:**
  - `text` - Single line text
  - `textarea` - Multi-line text
  - `number` - Numeric value
  - `email` - Email address
  - `phone` - Phone number
  - `url` - URL
  - `date` - Date
  - `datetime` - Date and time
  - `boolean` - Yes/No, True/False
  - `select` - Dropdown (single choice)
  - `multiselect` - Multiple choice
  - `currency` - Money value
  - `percentage` - Percentage value
  - `file` - File upload
  - `image` - Image upload
  - `reference` - Reference to another record

### description (text)
- **Tip:** TEXT
- **Nullable:** YES
- **Default:** NULL
- **Açıklama:** Field description (help text)
- **Örnek:** `Person's full legal name`

### config (jsonb)
- **Tip:** JSONB
- **Nullable:** NO
- **Default:** `{}`
- **Açıklama:** Type-specific configuration
- **Örnekler:**

**Text field:**
```json
{
  "minLength": 1,
  "maxLength": 255,
  "placeholder": "Enter text..."
}
```

**Number field:**
```json
{
  "min": 0,
  "max": 1000000,
  "decimals": 2,
  "step": 0.01
}
```

**Email field:**
```json
{
  "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
  "allowMultiple": false
}
```

**Select field:**
```json
{
  "options": [
    {"value": "new", "label": "New"},
    {"value": "active", "label": "Active"},
    {"value": "closed", "label": "Closed"}
  ],
  "allowCustom": false
}
```

**Currency field:**
```json
{
  "currency": "USD",
  "decimals": 2,
  "min": 0
}
```

**Reference field:**
```json
{
  "targetObjectId": "obj_contact",
  "displayField": "fld_name"
}
```

### category (varchar)
- **Tip:** VARCHAR
- **Nullable:** YES
- **Default:** NULL
- **Açıklama:** Field category (grouping)
- **Index:** YES
- **Örnekler:** `contact`, `product`, `system`, `custom`

### is_global (boolean)
- **Tip:** BOOLEAN
- **Nullable:** NO
- **Default:** false
- **Açıklama:** Global field (shared across tenants)
- **Use Case:** System-defined fields available to all users

### is_custom (boolean)
- **Tip:** BOOLEAN
- **Nullable:** NO
- **Default:** true
- **Açıklama:** Custom field (created by user)
- **Values:**
  - `true` - User-created field
  - `false` - System-defined field

### is_system_field (boolean)
- **Tip:** BOOLEAN
- **Nullable:** NO
- **Default:** false
- **Açıklama:** System field (cannot be deleted/modified)
- **Use Case:** Built-in fields (created_at, updated_at, etc.)

### created_at (timestamptz)
- **Tip:** TIMESTAMP WITH TIME ZONE
- **Nullable:** NO
- **Default:** NOW()
- **Açıklama:** Field creation timestamp

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
- **Açıklama:** Field creator
- **Unique:** With name (composite unique constraint)

---

## İlişkiler

### Referenced By (Outbound)

#### object_fields.field_id → fields.id
- **Type:** RESTRICT
- **Behavior:** Cannot delete field if attached to any object
- **Must:** Detach from all objects first
- **Query Pattern:** Find objects using this field

```sql
-- Check if field is in use
SELECT COUNT(*) FROM object_fields
WHERE field_id = 'fld_email';
```

**Delete Workflow:**
1. Check if field is attached to any object
2. If YES → Return error "Cannot delete field, it is in use"
3. If NO → Delete field

---

## Index'ler

### 1. fields_pkey (UNIQUE)
```sql
CREATE UNIQUE INDEX fields_pkey ON fields USING btree (id);
```
**Amaç:** Primary key
**Query:** `WHERE id = 'fld_xxx'`

### 2. uq_field_name_created_by (UNIQUE)
```sql
CREATE UNIQUE INDEX uq_field_name_created_by ON fields USING btree (name, created_by);
```
**Amaç:** Prevent duplicate field names per user
**Query:** `WHERE name = 'email_address' AND created_by = ?`
**Criticality:** ⚠️ CRITICAL - Business rule enforcement

### 3. ix_fields_id
```sql
CREATE INDEX ix_fields_id ON fields USING btree (id);
```
**Amaç:** Additional id lookup (SQLAlchemy)

### 4. ix_fields_category
```sql
CREATE INDEX ix_fields_category ON fields USING btree (category);
```
**Amaç:** Filter by category
**Query:** `WHERE category = 'contact'`
**Use Case:** Group fields by type

---

## Field Types ve Validation

### Text Types

#### text
- **Purpose:** Single line text
- **Config:**
```json
{
  "minLength": 1,
  "maxLength": 255,
  "placeholder": "Enter text",
  "pattern": null
}
```

#### textarea
- **Purpose:** Multi-line text
- **Config:**
```json
{
  "minLength": 0,
  "maxLength": 5000,
  "rows": 5
}
```

#### email
- **Purpose:** Email address
- **Config:**
```json
{
  "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
  "allowMultiple": false
}
```
- **Validation:** Email format check

#### phone
- **Purpose:** Phone number
- **Config:**
```json
{
  "format": "international",
  "allowExtension": true
}
```

#### url
- **Purpose:** Website URL
- **Config:**
```json
{
  "allowedProtocols": ["http", "https"],
  "requireProtocol": true
}
```

### Numeric Types

#### number
- **Purpose:** General numeric value
- **Config:**
```json
{
  "min": null,
  "max": null,
  "decimals": 0,
  "step": 1
}
```

#### currency
- **Purpose:** Money value
- **Config:**
```json
{
  "currency": "USD",
  "decimals": 2,
  "min": 0,
  "symbol": "$"
}
```

#### percentage
- **Purpose:** Percentage value
- **Config:**
```json
{
  "min": 0,
  "max": 100,
  "decimals": 2,
  "symbol": "%"
}
```

### Date/Time Types

#### date
- **Purpose:** Date only
- **Config:**
```json
{
  "format": "YYYY-MM-DD",
  "minDate": null,
  "maxDate": null
}
```

#### datetime
- **Purpose:** Date and time
- **Config:**
```json
{
  "format": "YYYY-MM-DD HH:mm:ss",
  "timezone": "UTC",
  "includeTime": true
}
```

### Selection Types

#### select
- **Purpose:** Single choice dropdown
- **Config:**
```json
{
  "options": [
    {"value": "option1", "label": "Option 1", "color": "#1E40AF"},
    {"value": "option2", "label": "Option 2", "color": "#059669"}
  ],
  "allowCustom": false
}
```

#### multiselect
- **Purpose:** Multiple choice
- **Config:**
```json
{
  "options": [...],
  "maxSelections": null,
  "minSelections": 0
}
```

#### boolean
- **Purpose:** Yes/No, True/False
- **Config:**
```json
{
  "trueLabel": "Yes",
  "falseLabel": "No",
  "defaultValue": false
}
```

### File Types

#### file
- **Purpose:** File upload
- **Config:**
```json
{
  "allowedExtensions": [".pdf", ".doc", ".docx"],
  "maxSize": 10485760,
  "multiple": false
}
```

#### image
- **Purpose:** Image upload
- **Config:**
```json
{
  "allowedFormats": ["jpg", "png", "gif"],
  "maxSize": 5242880,
  "maxWidth": 1920,
  "maxHeight": 1080
}
```

### Relationship Types

#### reference
- **Purpose:** Link to another record
- **Config:**
```json
{
  "targetObjectId": "obj_contact",
  "displayField": "fld_name",
  "allowMultiple": false
}
```

---

## Örnek Kullanımlar

### 1. Create Field (System Admin)

```python
from app.services.field_service import FieldService

field_service = FieldService()

# Create email field
email_field = await field_service.create_field(
    db=db,
    field_in=FieldCreate(
        name="email_address",
        label="Email",
        type="email",
        description="Email address",
        config={
            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
            "allowMultiple": False
        },
        category="contact",
        is_global=True,  # Available to all users
        is_custom=False,  # System field
        is_system_field=True  # Cannot be deleted
    ),
    user_id=admin_user_id
)
```

### 2. Create Custom Field (User)

```python
# Create custom product price field
price_field = await field_service.create_field(
    db=db,
    field_in=FieldCreate(
        name="product_price",
        label="Price",
        type="currency",
        description="Product price in USD",
        config={
            "currency": "USD",
            "decimals": 2,
            "min": 0,
            "symbol": "$"
        },
        category="product",
        is_global=False,  # User-specific
        is_custom=True,  # Custom field
        is_system_field=False  # Can be deleted
    ),
    user_id=user_id
)
```

### 3. Update Field

```python
await field_service.update_field(
    db=db,
    field_id="fld_price",
    field_in=FieldUpdate(
        label="Product Price (USD)",
        config={
            "currency": "USD",
            "decimals": 2,
            "min": 0.01,  # Updated minimum
            "symbol": "$"
        }
    )
)
```

### 4. Delete Field (with safety check)

```python
# Check if field is in use
in_use = await db.execute(
    select(ObjectField).where(ObjectField.field_id == "fld_old_field")
)

if in_use.scalar_one_or_none():
    raise HTTPException(
        status_code=400,
        detail="Cannot delete field: it is attached to objects"
    )

# Safe to delete
await field_service.delete_field(db=db, field_id="fld_old_field")
```

---

## Örnek Sorgular

### 1. Get All Global Fields

```sql
SELECT
    id,
    name,
    label,
    type,
    category
FROM fields
WHERE is_global = true
ORDER BY category, name;
```

### 2. Get User's Custom Fields

```sql
SELECT
    id,
    name,
    label,
    type,
    config,
    created_at
FROM fields
WHERE created_by = '550e8400-e29b-41d4-a716-446655440000'
  AND is_custom = true
ORDER BY created_at DESC;
```

### 3. Find Fields by Category

```sql
SELECT
    id,
    name,
    label,
    type,
    is_system_field
FROM fields
WHERE category = 'contact'
ORDER BY is_system_field DESC, name;
```

### 4. Search Fields by Name or Label

```sql
SELECT
    id,
    name,
    label,
    type,
    category
FROM fields
WHERE name ILIKE '%email%'
   OR label ILIKE '%email%'
ORDER BY is_global DESC, name;
```

### 5. Count Fields by Type

```sql
SELECT
    type,
    COUNT(*) AS field_count,
    COUNT(*) FILTER (WHERE is_global = true) AS global_count,
    COUNT(*) FILTER (WHERE is_custom = true) AS custom_count
FROM fields
GROUP BY type
ORDER BY field_count DESC;
```

### 6. Find Fields in Use

```sql
-- Fields with usage count
SELECT
    f.id,
    f.name,
    f.label,
    f.type,
    COUNT(of.id) AS usage_count,
    json_agg(DISTINCT o.name) AS used_in_objects
FROM fields f
LEFT JOIN object_fields of ON f.id = of.field_id
LEFT JOIN objects o ON of.object_id = o.id
GROUP BY f.id, f.name, f.label, f.type
HAVING COUNT(of.id) > 0
ORDER BY usage_count DESC;
```

### 7. Find Unused Fields (Safe to Delete)

```sql
-- Fields not attached to any object
SELECT
    f.id,
    f.name,
    f.label,
    f.type,
    f.created_at
FROM fields f
LEFT JOIN object_fields of ON f.id = of.field_id
WHERE of.id IS NULL
  AND f.is_system_field = false
ORDER BY f.created_at DESC;
```

---

## Validation Rules

### Field Name Rules

```python
from pydantic import field_validator

class FieldCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

    @field_validator('name')
    def validate_name(cls, v):
        # Must be lowercase alphanumeric + underscore
        if not re.match(r'^[a-z0-9_]+$', v):
            raise ValueError('Name must be lowercase alphanumeric with underscores')

        # Cannot start with number
        if v[0].isdigit():
            raise ValueError('Name cannot start with number')

        # Reserved keywords
        reserved = ['id', 'created_at', 'updated_at', 'deleted_at']
        if v in reserved:
            raise ValueError(f'Name "{v}" is reserved')

        return v
```

### Type-Specific Validation

```python
def validate_field_config(field_type: str, config: dict):
    """Validate config based on field type"""

    if field_type == "number":
        if "min" in config and "max" in config:
            if config["min"] > config["max"]:
                raise ValueError("min cannot be greater than max")

    elif field_type == "select":
        if "options" not in config or len(config["options"]) == 0:
            raise ValueError("select field requires options")

    elif field_type == "reference":
        if "targetObjectId" not in config:
            raise ValueError("reference field requires targetObjectId")

    # Add more validations...
    return True
```

---

## Best Practices

### 1. Field Naming Convention

**✅ GOOD:**
- `full_name` (lowercase, underscores)
- `email_address`
- `product_price`

**❌ BAD:**
- `FullName` (uppercase)
- `email-address` (hyphens)
- `Product Price` (spaces)

### 2. Use Categories

```python
# Group related fields
contact_fields = {
    "category": "contact",
    "fields": ["full_name", "email_address", "phone_number"]
}

product_fields = {
    "category": "product",
    "fields": ["product_name", "product_price", "stock_quantity"]
}
```

### 3. Global vs Custom Fields

**Global Fields (is_global=true):**
- System-defined
- Shared across all users
- Cannot be modified by users
- Examples: `created_at`, `updated_at`, `id`

**Custom Fields (is_global=false):**
- User-created
- Private to user
- Can be modified/deleted
- Examples: Custom product attributes

### 4. Field Deletion Safety

```python
# ALWAYS check before deleting
async def safe_delete_field(db: AsyncSession, field_id: str):
    # 1. Check if field is in use
    usage_count = await db.scalar(
        select(func.count(ObjectField.id))
        .where(ObjectField.field_id == field_id)
    )

    if usage_count > 0:
        raise ValueError(f"Cannot delete: field is used in {usage_count} objects")

    # 2. Check if system field
    field = await db.get(Field, field_id)
    if field.is_system_field:
        raise ValueError("Cannot delete system field")

    # 3. Safe to delete
    await db.delete(field)
    await db.commit()
```

### 5. Config Schema Evolution

```python
# Always provide defaults for new config keys
def migrate_field_config(field: Field) -> dict:
    """Add new config keys with defaults"""
    config = field.config.copy()

    if field.type == "text":
        config.setdefault("placeholder", "")
        config.setdefault("minLength", 0)
        config.setdefault("maxLength", 255)

    return config
```

---

## Migration History

**Created:** Initial migration
**File:** `alembic/versions/002_fields.py`

**Changes:**
- 2026-01-15: Initial table creation
- 2026-01-16: Added category column + index
- 2026-01-17: Added is_system_field column
- 2026-01-18: Added updated_at column

---

## İlgili Dosyalar

- **Model:** `app/models/field.py`
- **Schema:** `app/schemas/field.py`
- **Router:** `app/routers/fields.py`
- **Service:** `app/services/field_service.py`
- **API Docs:** `docs/api/02-fields/`

---

**Last Updated:** 2026-01-18
**Status:** ✅ Production Ready
**Total Field Types:** 16 supported types
