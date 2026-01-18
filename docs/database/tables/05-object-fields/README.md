# object_fields Table

## Genel Bakış

**Amaç:** Object ve Field arasında Many-to-Many mapping

**Tip:** Mapping/Junction Table
**ID Format:** ofd_xxxxxxxx (8 hex chars)
**Pattern:** Object ↔ Field (N:N relationship)
**Purpose:** Define which fields belong to which objects

---

## Tablo Özellikleri

| Özellik | Değer |
|---------|-------|
| **Primary Key** | id (VARCHAR) |
| **Foreign Keys** | object_id → objects.id (CASCADE)<br>field_id → fields.id (RESTRICT) |
| **Referenced By** | None (junction table) |
| **Cascade Deletes** | YES (when object deleted)<br>RESTRICT (when field deleted) |
| **Indexes** | 2 indexes (id) |
| **Row Estimate** | Thousands |

---

## Kolonlar

### id (varchar) - Primary Key
- **Tip:** VARCHAR
- **Nullable:** NO
- **Format:** `ofd_` + 8 hex chars
- **Generasyon:** Python `uuid.uuid4().hex[:8]`
- **Örnek:** `ofd_a1b2c3d4`

### object_id (varchar) - Foreign Key
- **Tip:** VARCHAR
- **Nullable:** NO
- **References:** objects.id (CASCADE)
- **Açıklama:** Object ID
- **Örnek:** `obj_contact`

### field_id (varchar) - Foreign Key
- **Tip:** VARCHAR
- **Nullable:** NO
- **References:** fields.id (RESTRICT)
- **Açıklama:** Field ID
- **Örnek:** `fld_name`

### display_order (integer)
- **Tip:** INTEGER
- **Nullable:** NO
- **Default:** 0
- **Açıklama:** Field display order in UI (0, 1, 2, ...)
- **Sortable:** YES

### is_required (boolean)
- **Tip:** BOOLEAN
- **Nullable:** NO
- **Default:** false
- **Açıklama:** Is this field required?
- **Validation:** Enforced during record create/update

### is_visible (boolean)
- **Tip:** BOOLEAN
- **Nullable:** NO
- **Default:** true
- **Açıklama:** Is this field visible in UI?
- **Use Case:** Hide fields conditionally

### is_readonly (boolean)
- **Tip:** BOOLEAN
- **Nullable:** NO
- **Default:** false
- **Açıklama:** Is this field read-only?
- **Use Case:** System fields, calculated fields

### field_overrides (jsonb)
- **Tip:** JSONB
- **Nullable:** NO
- **Default:** `{}`
- **Açıklama:** Object-specific field config overrides
- **Use Case:** Override field label, placeholder, validation per object

**Example Overrides:**
```json
{
  "label": "Customer Name",  // Override field label
  "placeholder": "Enter customer full name",
  "required": true,  // Can override is_required
  "minLength": 5,  // Override validation
  "helpText": "Customer's legal name"
}
```

### created_at (timestamptz)
- **Tip:** TIMESTAMP WITH TIME ZONE
- **Nullable:** NO
- **Default:** NOW()
- **Açıklama:** Attachment creation timestamp

---

## İlişkiler

### Foreign Keys (Inbound)

#### object_id → objects.id
- **Type:** CASCADE
- **Behavior:** Delete object → delete all object_fields
- **Index:** Implicit (foreign key)

#### field_id → fields.id
- **Type:** RESTRICT
- **Behavior:** Delete field → BLOCKED if attached to any object
- **Must:** Detach from all objects before deleting field
- **Index:** Implicit (foreign key)

**Critical Difference:**
- **objects.id CASCADE:** Object owns the attachment
- **fields.id RESTRICT:** Field is shared resource, cannot delete if in use

---

## Index'ler

### 1. object_fields_pkey (UNIQUE)
```sql
CREATE UNIQUE INDEX object_fields_pkey ON object_fields USING btree (id);
```

### 2. ix_object_fields_id
```sql
CREATE INDEX ix_object_fields_id ON object_fields USING btree (id);
```

**Missing Index Recommendation:**
```sql
-- Add composite index for common query
CREATE INDEX ix_object_fields_object_id_display_order
ON object_fields (object_id, display_order);
```

---

## Örnek Kullanımlar

### 1. Attach Field to Object

```python
from app.services.object_field_service import ObjectFieldService

object_field_service = ObjectFieldService()

# Attach "name" field to "contact" object
await object_field_service.create_object_field(
    db=db,
    object_field_in=ObjectFieldCreate(
        object_id="obj_contact",
        field_id="fld_name",
        display_order=0,  # First field
        is_required=True,
        is_visible=True,
        is_readonly=False,
        field_overrides={
            "placeholder": "Enter full name"
        }
    ),
    user_id=user_id
)
```

### 2. Get Fields for Object (Ordered)

```python
# Get all fields for object, ordered by display_order
fields = await db.execute(
    select(ObjectField)
    .where(ObjectField.object_id == "obj_contact")
    .order_by(ObjectField.display_order)
)
```

### 3. Update Display Order

```python
# Reorder fields
await object_field_service.update_object_field(
    db=db,
    object_field_id="ofd_name",
    object_field_in=ObjectFieldUpdate(
        display_order=5  # Move to position 5
    )
)
```

### 4. Detach Field from Object

```python
# Remove field from object (field itself is NOT deleted)
await object_field_service.delete_object_field(
    db=db,
    object_field_id="ofd_old_field"
)
```

---

## Örnek Sorgular

### 1. Get Fields for Object (with Field Details)

```sql
SELECT
    of.id AS object_field_id,
    of.display_order,
    of.is_required,
    of.is_visible,
    of.is_readonly,
    f.id AS field_id,
    f.name AS field_name,
    f.label AS field_label,
    f.type AS field_type,
    COALESCE(
        of.field_overrides->>'label',
        f.label
    ) AS final_label
FROM object_fields of
JOIN fields f ON of.field_id = f.id
WHERE of.object_id = 'obj_contact'
ORDER BY of.display_order;
```

### 2. Count Fields per Object

```sql
SELECT
    o.name AS object_name,
    o.label AS object_label,
    COUNT(of.id) AS field_count,
    COUNT(of.id) FILTER (WHERE of.is_required = true) AS required_count
FROM objects o
LEFT JOIN object_fields of ON o.id = of.object_id
GROUP BY o.id, o.name, o.label
ORDER BY field_count DESC;
```

### 3. Find Objects Using Specific Field

```sql
SELECT DISTINCT
    o.id,
    o.name,
    o.label,
    of.is_required,
    of.display_order
FROM object_fields of
JOIN objects o ON of.object_id = o.id
WHERE of.field_id = 'fld_email'
ORDER BY o.name;
```

### 4. Find Required Fields

```sql
SELECT
    of.id,
    o.name AS object_name,
    f.name AS field_name,
    f.label AS field_label,
    of.display_order
FROM object_fields of
JOIN objects o ON of.object_id = o.id
JOIN fields f ON of.field_id = f.id
WHERE of.is_required = true
ORDER BY o.name, of.display_order;
```

### 5. Validate Object has Required Fields

```sql
-- Check if object has at least one required field
SELECT
    o.id,
    o.name,
    COUNT(of.id) FILTER (WHERE of.is_required = true) AS required_field_count
FROM objects o
LEFT JOIN object_fields of ON o.id = of.object_id
GROUP BY o.id, o.name
HAVING COUNT(of.id) FILTER (WHERE of.is_required = true) = 0;
```

---

## Field Overrides

### Override Examples

**1. Override Label:**
```json
{
  "label": "Customer Name"  // Instead of "Full Name"
}
```

**2. Override Placeholder:**
```json
{
  "placeholder": "Enter customer full legal name"
}
```

**3. Override Validation:**
```json
{
  "minLength": 5,
  "maxLength": 100,
  "pattern": "^[A-Z].*"  // Must start with capital
}
```

**4. Add Help Text:**
```json
{
  "helpText": "Enter the customer's legal name as it appears on documents"
}
```

**5. Conditional Visibility:**
```json
{
  "visibleWhen": {
    "field": "fld_customer_type",
    "operator": "equals",
    "value": "individual"
  }
}
```

### Override Application Logic

```python
def get_final_field_config(field: Field, object_field: ObjectField) -> dict:
    """Merge field config with object-specific overrides"""

    # Start with field's default config
    final_config = field.config.copy()

    # Apply overrides
    if object_field.field_overrides:
        final_config.update(object_field.field_overrides)

    # Override label if specified
    final_label = object_field.field_overrides.get("label", field.label)

    return {
        "id": field.id,
        "name": field.name,
        "label": final_label,
        "type": field.type,
        "config": final_config,
        "is_required": object_field.is_required,
        "is_visible": object_field.is_visible,
        "is_readonly": object_field.is_readonly,
        "display_order": object_field.display_order
    }
```

---

## Display Order Management

### Reorder Fields

```python
async def reorder_fields(
    db: AsyncSession,
    object_id: str,
    field_order: list[str]  # List of object_field IDs in new order
):
    """Reorder fields for an object"""

    for index, object_field_id in enumerate(field_order):
        await db.execute(
            update(ObjectField)
            .where(ObjectField.id == object_field_id)
            .values(display_order=index)
        )

    await db.commit()
```

**Example Usage:**
```python
# Reorder: name, email, phone → email, name, phone
await reorder_fields(
    db=db,
    object_id="obj_contact",
    field_order=[
        "ofd_email",  # 0 (was 1)
        "ofd_name",   # 1 (was 0)
        "ofd_phone"   # 2 (same)
    ]
)
```

---

## Validation

### Required Field Validation

```python
async def validate_record_data(
    db: AsyncSession,
    object_id: str,
    data: dict
) -> list[str]:
    """Validate record data against object field requirements"""

    errors = []

    # Get all required fields for object
    result = await db.execute(
        select(ObjectField, Field)
        .join(Field, ObjectField.field_id == Field.id)
        .where(
            ObjectField.object_id == object_id,
            ObjectField.is_required == True
        )
    )

    for object_field, field in result.all():
        # Check if required field has value
        value = data.get(field.id)

        if value is None or value == "":
            errors.append(
                f"Field '{field.label}' is required"
            )

    return errors
```

---

## Best Practices

### 1. Display Order Convention

```python
# Use increments of 10 for flexibility
display_orders = [0, 10, 20, 30, 40]

# Easy to insert between fields later
# Insert between 10 and 20? Use 15
```

### 2. Required Field Strategy

```python
# ✅ GOOD - Make key fields required
{
    "fld_name": is_required=True,
    "fld_email": is_required=True,
    "fld_phone": is_required=False  # Optional
}

# ❌ BAD - Too many required fields
# (Makes data entry difficult)
```

### 3. Field Override Scope

```python
# ✅ GOOD - Override only what's necessary
field_overrides = {
    "label": "Customer Name"  # Just change label
}

# ❌ BAD - Duplicate entire config
field_overrides = {
    "label": "Customer Name",
    "minLength": 1,  # Already in field.config
    "maxLength": 255,  # Already in field.config
    ...
}
```

### 4. Detach vs Delete

```python
# Detach field from object (safe)
DELETE FROM object_fields WHERE id = 'ofd_xxx';
# Field still exists, can be reused

# Delete field (dangerous)
DELETE FROM fields WHERE id = 'fld_xxx';
# Blocked if attached to any object (RESTRICT)
```

---

## Migration History

**Created:** Initial migration
**File:** `alembic/versions/004_object_fields.py`

**Changes:**
- 2026-01-15: Initial table creation
- 2026-01-16: Added field_overrides column (JSONB)
- 2026-01-17: Added is_visible, is_readonly columns

---

## İlgili Dosyalar

- **Model:** `app/models/object_field.py`
- **Schema:** `app/schemas/object_field.py`
- **Router:** `app/routers/object_fields.py`
- **Service:** `app/services/object_field_service.py`
- **API Docs:** `docs/api/07-object-fields/`

---

**Last Updated:** 2026-01-18
**Status:** ✅ Production Ready
**Pattern:** N:N Junction Table
**Critical Constraint:** RESTRICT on field_id (cannot delete field if in use)
