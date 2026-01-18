# 🗄️ DATABASE SCHEMA DOCUMENTATION

**Database:** PostgreSQL 16 (Supabase Local)
**Schema:** public
**Last Updated:** 2026-01-18

---

## 📊 TABLE OVERVIEW

| Table | Purpose | Row Count | Key Type |
|-------|---------|-----------|----------|
| [users](#users) | User authentication & profiles | Variable | UUID |
| [token_blacklist](#token_blacklist) | JWT token revocation | Variable | VARCHAR |
| [fields](#fields) | Field definitions (text, number, etc.) | Variable | VARCHAR (fld_*) |
| [objects](#objects) | Object definitions (Contact, Company, etc.) | Variable | VARCHAR (obj_*) |
| [object_fields](#object_fields) | Field-to-Object attachments | Variable | VARCHAR (ofd_*) |
| [records](#records) | Actual data records (JSONB storage) | Variable | VARCHAR (rec_*) |
| [relationships](#relationships) | Object-to-Object relationship definitions | Variable | VARCHAR (rel_*) |
| [relationship_records](#relationship_records) | Record-to-Record links | Variable | VARCHAR (rrec_*) |
| [applications](#applications) | Application definitions (CRM, ITSM, etc.) | Variable | VARCHAR (app_*) |
| [alembic_version](#alembic_version) | Database migration version | 1 | VARCHAR |

---

## 🔗 ENTITY RELATIONSHIP DIAGRAM

```
┌─────────────┐
│    users    │
│ (UUID)      │
└──────┬──────┘
       │ created_by (references)
       │
       ├──────────────────────────────────────────────────┐
       │                                                  │
       ▼                                                  ▼
┌─────────────┐                                   ┌─────────────┐
│   fields    │                                   │   objects   │
│ (fld_xxx)   │                                   │ (obj_xxx)   │
└──────┬──────┘                                   └──────┬──────┘
       │                                                  │
       │                    ┌─────────────────────────────┤
       │                    │                             │
       │              ┌─────▼──────┐                      │
       └──────────────►object_fields│◄─────────────────────┘
                      │  (ofd_xxx)  │
                      └─────────────┘
                            │ (defines structure)
                            │
                      ┌─────▼──────┐
                      │   records  │
                      │ (rec_xxx)  │◄─────┐
                      │  [JSONB]   │      │
                      └──────┬─────┘      │
                             │            │
                      ┌──────▼──────┐     │
                      │relationships│     │
                      │  (rel_xxx)  │     │
                      └──────┬──────┘     │
                             │            │
                  ┌──────────▼────────┐   │
                  │relationship_records│───┘
                  │    (rrec_xxx)      │
                  └────────────────────┘

┌─────────────────┐
│  applications   │  (standalone)
│   (app_xxx)     │
└─────────────────┘

┌─────────────────┐
│ token_blacklist │  (standalone)
│      (jti)      │
└─────────────────┘
```

---

## 📋 TABLE DETAILS

### users

**Purpose:** User authentication and profile management

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO | - | **Primary Key** - User ID |
| email | varchar | NO | - | **Unique** - User email address |
| hashed_password | varchar | NO | - | Bcrypt hashed password |
| full_name | varchar | NO | - | User's full name |
| is_active | boolean | NO | - | Account active status |
| is_verified | boolean | NO | - | Email verification status |
| created_at | timestamptz | NO | - | Account creation timestamp |
| updated_at | timestamptz | NO | - | Last update timestamp |
| last_login | timestamptz | YES | NULL | Last login timestamp |

**Indexes:**
- `users_pkey` (UNIQUE) on `id`
- `ix_users_email` (UNIQUE) on `email`
- `ix_users_id` on `id`

**Foreign Keys:** None

**Referenced By:**
- fields.created_by
- objects.created_by
- records.created_by, records.updated_by
- relationships.created_by
- relationship_records.created_by
- applications.created_by

---

### token_blacklist

**Purpose:** JWT token revocation (logout functionality)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| jti | varchar | NO | - | **Primary Key** - JWT Token ID (unique identifier) |
| user_id | uuid | NO | - | User who owns this token |
| expires_at | timestamptz | NO | - | Token expiration time |
| blacklisted_at | timestamptz | NO | - | When token was revoked |

**Indexes:**
- `token_blacklist_pkey` (UNIQUE) on `jti`
- `ix_token_blacklist_jti` on `jti`
- `ix_token_blacklist_user_id` on `user_id`
- `ix_token_blacklist_expires_at` on `expires_at`

**Foreign Keys:** None (users table reference not enforced)

**Use Case:**
- When user logs out, JWT's `jti` is added to blacklist
- API checks blacklist before accepting token
- Expired tokens can be cleaned up via `expires_at` index

---

### fields

**Purpose:** Reusable field definitions (text, number, email, etc.)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | varchar | NO | - | **Primary Key** - Field ID (fld_xxxxxxxx) |
| name | varchar | NO | - | Field name (unique per user) |
| label | varchar | NO | - | Display label |
| type | varchar | NO | - | Field type (text, number, email, etc.) |
| description | text | YES | NULL | Field description |
| config | jsonb | NO | {} | Field configuration (validation rules, etc.) |
| category | varchar | YES | NULL | Field category (contact, system, etc.) |
| is_global | boolean | NO | false | Global field (shared across tenants) |
| is_custom | boolean | NO | true | Custom field (vs system field) |
| is_system_field | boolean | NO | false | System-defined field |
| created_at | timestamptz | NO | now() | Creation timestamp |
| updated_at | timestamptz | NO | now() | Last update timestamp |
| created_by | uuid | YES | NULL | **FK → users.id** |

**Indexes:**
- `fields_pkey` (UNIQUE) on `id`
- `uq_field_name_created_by` (UNIQUE) on `(name, created_by)`
- `ix_fields_id` on `id`
- `ix_fields_category` on `category`

**Foreign Keys:** None (users FK not enforced)

**Referenced By:**
- object_fields.field_id (CASCADE on delete)

**Unique Constraint:**
- Field name must be unique per user (name + created_by)

---

### objects

**Purpose:** Object definitions (Contact, Company, Opportunity, etc.)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | varchar | NO | - | **Primary Key** - Object ID (obj_xxxxxxxx) |
| name | varchar | NO | - | Object name (contact, company, etc.) |
| label | varchar | NO | - | Display label (Contact, Company, etc.) |
| plural_name | varchar | NO | - | Plural form (Contacts, Companies, etc.) |
| description | text | YES | NULL | Object description |
| icon | varchar | YES | NULL | Icon (emoji or class name) |
| is_custom | boolean | NO | true | Custom object (vs system object) |
| is_global | boolean | NO | false | Global object (shared across tenants) |
| views | jsonb | NO | `{"forms": [], "tables": [], "kanbans": [], "calendars": []}` | View configurations |
| permissions | jsonb | NO | `{"read": ["all"], "create": ["all"], "delete": ["all"], "update": ["all"]}` | Permission rules |
| created_at | timestamptz | NO | now() | Creation timestamp |
| updated_at | timestamptz | NO | now() | Last update timestamp |
| created_by | uuid | YES | NULL | **FK → users.id** |

**Indexes:**
- `objects_pkey` (UNIQUE) on `id`
- `ix_objects_id` on `id`

**Foreign Keys:** None (users FK not enforced)

**Referenced By:**
- object_fields.object_id (CASCADE on delete)
- records.object_id (CASCADE on delete)
- relationships.from_object_id, relationships.to_object_id (CASCADE on delete)

**JSONB Fields:**
- `views`: Stores different view configurations (forms, tables, kanbans, calendars)
- `permissions`: RBAC rules (who can read, create, update, delete)

---

### object_fields

**Purpose:** Many-to-Many mapping between objects and fields

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | varchar | NO | - | **Primary Key** - Object-Field ID (ofd_xxxxxxxx) |
| object_id | varchar | NO | - | **FK → objects.id (CASCADE)** |
| field_id | varchar | NO | - | **FK → fields.id (RESTRICT)** |
| display_order | integer | NO | 0 | Display order in UI (0, 1, 2, ...) |
| is_required | boolean | NO | false | Is this field required? |
| is_visible | boolean | NO | true | Is this field visible in UI? |
| is_readonly | boolean | NO | false | Is this field read-only? |
| field_overrides | jsonb | NO | {} | Field-specific config overrides |
| created_at | timestamptz | NO | now() | Creation timestamp |

**Indexes:**
- `object_fields_pkey` (UNIQUE) on `id`
- `ix_object_fields_id` on `id`

**Foreign Keys:**
- `object_id` → objects.id (CASCADE on delete)
- `field_id` → fields.id (RESTRICT on delete)

**Cascade Behavior:**
- If object is deleted → object_fields are deleted (CASCADE)
- If field is deleted → deletion is blocked if used (RESTRICT)

**Use Case:**
```
Object: "Contact"
├── Field: "Name" (display_order: 0, is_required: true)
├── Field: "Email" (display_order: 1, is_required: true)
└── Field: "Phone" (display_order: 2, is_required: false)
```

---

### records

**Purpose:** Actual data records with JSONB storage (hybrid model)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | varchar | NO | - | **Primary Key** - Record ID (rec_xxxxxxxx) |
| object_id | varchar | NO | - | **FK → objects.id (CASCADE)** |
| data | jsonb | NO | {} | Field values `{"fld_xxx": "value", ...}` |
| primary_value | text | YES | NULL | Denormalized primary display value (for search) |
| created_at | timestamptz | NO | now() | Creation timestamp |
| updated_at | timestamptz | NO | now() | Last update timestamp |
| created_by | uuid | YES | NULL | **FK → users.id** |
| updated_by | uuid | YES | NULL | **FK → users.id** |
| tenant_id | varchar | YES | NULL | Multi-tenancy support |

**Indexes:**
- `records_pkey` (UNIQUE) on `id`
- `ix_records_id` on `id`
- `ix_records_object_id` on `object_id` (filter by object type)
- `ix_records_primary_value` on `primary_value` (fast search)
- `ix_records_created_at` on `created_at` (sorting)

**Foreign Keys:**
- `object_id` → objects.id (CASCADE on delete)

**Referenced By:**
- relationship_records.from_record_id, relationship_records.to_record_id (CASCADE)

**JSONB Storage Pattern:**
```json
{
  "fld_name": "John Doe",
  "fld_email": "john@example.com",
  "fld_phone": "+1 555 1234"
}
```

**primary_value:**
- Auto-extracted from first text field in `data`
- Used for fast search (ILIKE queries)
- 7x faster than JSONB queries

---

### relationships

**Purpose:** Define relationships between objects (1:N, N:N)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | varchar | NO | - | **Primary Key** - Relationship ID (rel_xxxxxxxx) |
| name | varchar | NO | - | Relationship name (contact_companies, etc.) |
| from_object_id | varchar | NO | - | **FK → objects.id (CASCADE)** - Source object |
| to_object_id | varchar | NO | - | **FK → objects.id (CASCADE)** - Target object |
| type | varchar | NO | - | Relationship type ("1:N" or "N:N") |
| from_label | text | YES | NULL | Label shown on source object |
| to_label | text | YES | NULL | Label shown on target object |
| created_at | timestamptz | NO | now() | Creation timestamp |
| created_by | uuid | YES | NULL | **FK → users.id** |

**Indexes:**
- `relationships_pkey` (UNIQUE) on `id`
- `ix_relationships_id` on `id`

**Foreign Keys:**
- `from_object_id` → objects.id (CASCADE on delete)
- `to_object_id` → objects.id (CASCADE on delete)

**Referenced By:**
- relationship_records.relationship_id (CASCADE)

**Cascade Behavior:**
- If object is deleted → all relationships involving that object are deleted

**Example:**
```
Relationship: "contact_companies"
├── from_object_id: obj_contact
├── to_object_id: obj_company
├── type: "1:N"
├── from_label: "Companies"
└── to_label: "Contact"
```

---

### relationship_records

**Purpose:** Link actual records via relationships

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | varchar | NO | - | **Primary Key** - Relationship Record ID (rrec_xxx) |
| relationship_id | varchar | NO | - | **FK → relationships.id (CASCADE)** |
| from_record_id | varchar | NO | - | **FK → records.id (CASCADE)** |
| to_record_id | varchar | NO | - | **FK → records.id (CASCADE)** |
| relationship_metadata | jsonb | NO | {} | Additional relationship data |
| created_at | timestamptz | NO | now() | Creation timestamp |
| created_by | uuid | YES | NULL | **FK → users.id** |

**Indexes:**
- `relationship_records_pkey` (UNIQUE) on `id`
- `ix_relationship_records_id` on `id`
- `ix_relationship_records_relationship_id` on `relationship_id`
- `ix_relationship_records_from_record_id` on `from_record_id`
- `ix_relationship_records_to_record_id` on `to_record_id`

**Foreign Keys:**
- `relationship_id` → relationships.id (CASCADE on delete)
- `from_record_id` → records.id (CASCADE on delete)
- `to_record_id` → records.id (CASCADE on delete)

**Cascade Behavior:**
- If relationship is deleted → all record links are deleted
- If record is deleted → all links involving that record are deleted

**Example:**
```
Record Link:
├── relationship_id: rel_contact_companies (Contact → Company)
├── from_record_id: rec_john_doe (Contact: John Doe)
├── to_record_id: rec_acme_corp (Company: Acme Corp)
└── relationship_metadata: {"role": "CEO", "since": "2020-01-01"}
```

---

### applications

**Purpose:** Application definitions (CRM, ITSM, etc.)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | varchar | NO | - | **Primary Key** - Application ID (app_xxxxxxxx) |
| name | varchar | NO | - | Application name (CRM, ITSM, etc.) |
| label | varchar | YES | NULL | Display label |
| description | text | YES | NULL | Application description |
| icon | varchar | YES | NULL | Icon (emoji or class name) |
| config | jsonb | NO | {} | Application configuration |
| published_at | timestamptz | YES | NULL | Publication timestamp (NULL = draft) |
| created_at | timestamptz | NO | now() | Creation timestamp |
| updated_at | timestamptz | NO | now() | Last update timestamp |
| created_by | uuid | YES | NULL | **FK → users.id** |

**Indexes:**
- `applications_pkey` (UNIQUE) on `id`
- `ix_applications_id` on `id`

**Foreign Keys:** None (users FK not enforced)

**Draft/Published State:**
- `published_at = NULL` → Draft (not visible to end users)
- `published_at = timestamp` → Published (visible to end users)

**config JSONB:**
```json
{
  "objects": ["obj_contact", "obj_company"],
  "theme": {"primaryColor": "#1E40AF"},
  "navigation": {...}
}
```

---

### alembic_version

**Purpose:** Database migration version tracking (Alembic)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| version_num | varchar(32) | NO | - | **Primary Key** - Current migration version |

**Indexes:**
- `alembic_version_pkc` (UNIQUE) on `version_num`

**Foreign Keys:** None

**Use Case:**
- Single row table storing current migration version
- Managed by Alembic migration tool
- Example: `version_num = "a1b2c3d4e5f6"`

---

## 🔄 CASCADE BEHAVIOR MATRIX

| Parent Table | Child Table | Column | On Delete |
|--------------|-------------|--------|-----------|
| objects | object_fields | object_id | **CASCADE** |
| fields | object_fields | field_id | **RESTRICT** |
| objects | records | object_id | **CASCADE** |
| objects | relationships | from_object_id | **CASCADE** |
| objects | relationships | to_object_id | **CASCADE** |
| relationships | relationship_records | relationship_id | **CASCADE** |
| records | relationship_records | from_record_id | **CASCADE** |
| records | relationship_records | to_record_id | **CASCADE** |

**Key Behaviors:**

1. **Delete Object** → Deletes:
   - All object_fields for that object
   - All records for that object
   - All relationships involving that object
   - All relationship_records (via CASCADE chain)

2. **Delete Field** → **BLOCKED** if:
   - Field is attached to any object (RESTRICT)
   - Must detach from all objects first

3. **Delete Relationship** → Deletes:
   - All relationship_records using that relationship

4. **Delete Record** → Deletes:
   - All relationship_records involving that record

---

## 🎯 COMMON QUERY PATTERNS

### 1. Get Object with Fields

```sql
-- Get object definition
SELECT * FROM objects WHERE id = 'obj_contact';

-- Get fields for object (ordered)
SELECT
    of.id,
    of.display_order,
    of.is_required,
    f.name,
    f.label,
    f.type
FROM object_fields of
JOIN fields f ON of.field_id = f.id
WHERE of.object_id = 'obj_contact'
ORDER BY of.display_order;
```

### 2. Search Records (Fast)

```sql
-- Search by primary_value (7x faster than JSONB)
SELECT * FROM records
WHERE object_id = 'obj_contact'
  AND primary_value ILIKE '%john%'
LIMIT 50;
```

### 3. Get Related Records

```sql
-- Get all companies for a contact (1:N relationship)
SELECT r.*
FROM relationship_records rr
JOIN records r ON rr.to_record_id = r.id
WHERE rr.relationship_id = 'rel_contact_companies'
  AND rr.from_record_id = 'rec_john_doe';
```

### 4. Bidirectional Relationship Query

```sql
-- Get all relationships for an object (source OR target)
SELECT * FROM relationships
WHERE from_object_id = 'obj_contact'
   OR to_object_id = 'obj_contact';
```

### 5. Multi-Tenant Filtering

```sql
-- Filter records by tenant
SELECT * FROM records
WHERE object_id = 'obj_contact'
  AND tenant_id = 'tenant_abc123';
```

---

## 📈 PERFORMANCE INDEXES

### Critical Indexes

1. **records.ix_records_primary_value**
   - Type: B-tree
   - Purpose: Fast text search (ILIKE queries)
   - 7x faster than JSONB search

2. **records.ix_records_object_id**
   - Type: B-tree
   - Purpose: Filter records by object type
   - Essential for list/search queries

3. **relationship_records.ix_relationship_records_from_record_id**
   - Type: B-tree
   - Purpose: Find all related records (forward lookup)

4. **relationship_records.ix_relationship_records_to_record_id**
   - Type: B-tree
   - Purpose: Find all related records (reverse lookup)

5. **token_blacklist.ix_token_blacklist_expires_at**
   - Type: B-tree
   - Purpose: Cleanup expired tokens efficiently

---

## 🔐 SECURITY CONSIDERATIONS

### 1. Password Storage
- **Table:** users.hashed_password
- **Algorithm:** bcrypt
- **Cost Factor:** 12 (default)
- **Never store plain text passwords**

### 2. JWT Token Revocation
- **Table:** token_blacklist
- **Strategy:** Store revoked token JTI
- **Cleanup:** Regularly delete expired tokens via `expires_at`

### 3. Multi-Tenancy
- **Column:** records.tenant_id
- **Strategy:** Row-level tenant isolation
- **Enforcement:** Application-level (middleware)

### 4. JSONB Injection Prevention
- **ORM:** SQLAlchemy parameterized queries
- **Validation:** Pydantic schema validation
- **Never:** Concatenate user input into SQL

---

## 🚀 MIGRATION HISTORY

**Tool:** Alembic
**Current Version:** Stored in `alembic_version` table

**Migration Commands:**
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

**Migration Files:** `/Users/ali/Documents/Projects/canvas-app-backend/alembic/versions/`

---

## 📊 JSONB FIELD SCHEMAS

### records.data

```json
{
  "fld_xxxxxxxx": "value",
  "fld_yyyyyyyy": 42,
  "fld_zzzzzzzz": true
}
```

**Key Format:** `fld_` + 8 hex chars (field ID)
**Value Type:** Any JSON type (string, number, boolean, array, object)

### objects.views

```json
{
  "forms": [
    {"id": "form_1", "name": "Default Form", "layout": [...]}
  ],
  "tables": [
    {"id": "table_1", "name": "All Contacts", "columns": [...]}
  ],
  "kanbans": [],
  "calendars": []
}
```

### objects.permissions

```json
{
  "read": ["all"],
  "create": ["all", "user_id_1", "role_admin"],
  "update": ["owner", "role_admin"],
  "delete": ["role_admin"]
}
```

**Permission Values:**
- `"all"` - Everyone
- `"owner"` - Record owner only
- `"user_<uuid>"` - Specific user
- `"role_<name>"` - Specific role

### relationship_records.relationship_metadata

```json
{
  "role": "CEO",
  "since": "2020-01-01",
  "is_primary": true,
  "custom_field": "value"
}
```

**Purpose:** Store relationship-specific data (e.g., "Contact is CEO of Company since 2020")

---

## 🎯 DATA INTEGRITY RULES

### 1. Unique Constraints

| Table | Columns | Purpose |
|-------|---------|---------|
| users | email | One account per email |
| fields | (name, created_by) | Unique field name per user |
| token_blacklist | jti | One entry per token |

### 2. NOT NULL Constraints

**Critical NOT NULL fields:**
- All `id` columns (primary keys)
- All `created_at` columns (audit trail)
- `users.email`, `users.hashed_password`
- `records.data` (default: `{}`)
- `objects.views`, `objects.permissions` (default JSONB)

### 3. Foreign Key Integrity

**All FK relationships are enforced via constraints**
- Prevents orphaned records
- CASCADE deletes propagate correctly
- RESTRICT prevents accidental deletions

---

## 📝 NOTES

### 1. ID Generation Pattern

**Format:** `<prefix>_<8_hex_chars>`

| Prefix | Table | Example |
|--------|-------|---------|
| fld_ | fields | fld_a1b2c3d4 |
| obj_ | objects | obj_e5f6g7h8 |
| ofd_ | object_fields | ofd_i9j0k1l2 |
| rec_ | records | rec_m3n4o5p6 |
| rel_ | relationships | rel_q7r8s9t0 |
| rrec_ | relationship_records | rrec_u1v2w3x4 |
| app_ | applications | app_y5z6a7b8 |

**Generated by:** Python `uuid.uuid4().hex[:8]`

### 2. Timestamp Strategy

**All timestamps are:**
- Type: `timestamp with time zone` (timestamptz)
- Timezone: UTC
- Default: `now()` for created_at
- Updated: Manually set for updated_at

**Best Practice:**
```python
from datetime import UTC, datetime
updated_at = datetime.now(UTC)  # NOT datetime.utcnow()
```

### 3. JSONB vs Normalized

**Use JSONB when:**
- Schema is dynamic (user-defined fields)
- Flexible key-value storage needed
- Performance: 7x faster than EAV pattern

**Use Normalized when:**
- Fixed schema (system tables)
- Need strong typing
- Need foreign key constraints

**Hybrid Model (Used in this project):**
- Metadata: Normalized tables (objects, fields)
- Data: JSONB storage (records.data)
- Best of both worlds: Type safety + Flexibility

---

**Last Updated:** 2026-01-18
**Database Version:** Stored in alembic_version table
**Schema Status:** ✅ Production Ready
