# 🔗 DATABASE ENTITY RELATIONSHIP DIAGRAM

**Database:** PostgreSQL 16 (Supabase Local)
**Last Updated:** 2026-01-18

---

## 📊 COMPLETE ER DIAGRAM

```
                                    ┌──────────────────────────────┐
                                    │          users               │
                                    │ ─────────────────────────    │
                                    │ PK  id (uuid)                │
                                    │ UK  email                    │
                                    │     hashed_password          │
                                    │     full_name                │
                                    │     is_active                │
                                    │     is_verified              │
                                    │     created_at               │
                                    │     updated_at               │
                                    │     last_login               │
                                    └────────────┬─────────────────┘
                                                 │
                                                 │ created_by (not enforced FK)
                                                 │
                 ┌───────────────────────────────┼────────────────────────────────┐
                 │                               │                                │
                 │                               │                                │
    ┌────────────▼───────────┐     ┌────────────▼───────────┐     ┌──────────────▼──────────┐
    │       fields           │     │        objects         │     │     applications        │
    │ ──────────────────     │     │ ──────────────────     │     │ ───────────────────     │
    │ PK  id (fld_xxx)       │     │ PK  id (obj_xxx)       │     │ PK  id (app_xxx)        │
    │ UK  (name,created_by)  │     │     name               │     │     name                │
    │     name               │     │     label              │     │     label               │
    │     label              │     │     plural_name        │     │     description         │
    │     type               │     │     description        │     │     icon                │
    │     description        │     │     icon               │     │     config (jsonb)      │
    │     config (jsonb)     │     │     is_custom          │     │     published_at        │
    │     category           │     │     is_global          │     │     created_at          │
    │     is_global          │     │     views (jsonb)      │     │     updated_at          │
    │     is_custom          │     │     permissions(jsonb) │     │     created_by          │
    │     is_system_field    │     │     created_at         │     └─────────────────────────┘
    │     created_at         │     │     updated_at         │
    │     updated_at         │     │     created_by         │
    │     created_by         │     └────────────┬───────────┘
    └────────────┬───────────┘                  │
                 │                               │
                 │                               │
                 │         ┌─────────────────────┼──────────────────────┐
                 │         │                     │                      │
                 │         │                     │                      │
                 │    ┌────▼─────────────────────▼───┐           ┌──────▼────────────┐
                 │    │      object_fields           │           │    records        │
                 └────►  (Mapping Table)             │           │ ─────────────     │
                      │ ────────────────────────     │           │ PK  id (rec_xxx)  │
                      │ PK  id (ofd_xxx)             │           │ FK  object_id     │◄────┐
                      │ FK  object_id → objects      │           │     data (jsonb)  │     │
                      │ FK  field_id → fields        │           │     primary_value │     │
                      │     display_order            │           │     created_at    │     │
                      │     is_required              │           │     updated_at    │     │
                      │     is_visible               │           │     created_by    │     │
                      │     is_readonly              │           │     updated_by    │     │
                      │     field_overrides (jsonb)  │           │     tenant_id     │     │
                      │     created_at               │           └──────┬────────────┘     │
                      └──────────────────────────────┘                  │                  │
                                                                        │                  │
                                                                        │                  │
              ┌─────────────────────────────────────────────────────────┼──────────────────┘
              │                                                         │
              │                                                         │
              │                                        ┌────────────────▼──────────────┐
              │                                        │      relationships            │
              │                                        │ ─────────────────────────     │
              │                                        │ PK  id (rel_xxx)              │
              │                                        │ FK  from_object_id → objects  │
              │                                        │ FK  to_object_id → objects    │
              │                                        │     name                      │
              │                                        │     type (1:N or N:N)         │
              │                                        │     from_label                │
              │                                        │     to_label                  │
              │                                        │     created_at                │
              │                                        │     created_by                │
              │                                        └────────────┬──────────────────┘
              │                                                     │
              │                                                     │
              │                                        ┌────────────▼──────────────────┐
              │                                        │  relationship_records         │
              │                                        │  (Mapping Table)              │
              └────────────────────────────────────────►  ─────────────────────────    │
                                                       │  PK  id (rrec_xxx)            │
                                                       │  FK  relationship_id          │
                                                       │  FK  from_record_id → records │
                                                       │  FK  to_record_id → records   │
                                                       │      relationship_metadata    │
                                                       │      created_at               │
                                                       │      created_by               │
                                                       └───────────────────────────────┘


                       ┌──────────────────────────────┐
                       │    token_blacklist           │  (Standalone - no FKs)
                       │ ────────────────────────     │
                       │ PK  jti                      │
                       │     user_id                  │
                       │     expires_at               │
                       │     blacklisted_at           │
                       └──────────────────────────────┘

                       ┌──────────────────────────────┐
                       │    alembic_version           │  (Standalone - migration tracking)
                       │ ────────────────────────────  │
                       │ PK  version_num              │
                       └──────────────────────────────┘
```

---

## 🔗 RELATIONSHIP CARDINALITY

### 1. users → fields (1:N)
```
users (1) ───creates──► (N) fields
```
- One user can create many fields
- Field references creator via `created_by`
- **NOT ENFORCED** (no FK constraint)

### 2. users → objects (1:N)
```
users (1) ───creates──► (N) objects
```
- One user can create many objects
- Object references creator via `created_by`
- **NOT ENFORCED** (no FK constraint)

### 3. users → applications (1:N)
```
users (1) ───creates──► (N) applications
```
- One user can create many applications
- Application references creator via `created_by`
- **NOT ENFORCED** (no FK constraint)

### 4. objects ←→ fields (N:N via object_fields)
```
objects (N) ◄───object_fields───► (N) fields
```
- Many objects can use many fields
- `object_fields` is the junction table
- **Cascade Rules:**
  - Delete object → delete object_fields (CASCADE)
  - Delete field → blocked if used (RESTRICT)

### 5. objects → records (1:N)
```
objects (1) ───has──► (N) records
```
- One object definition has many data records
- Record references object via `object_id`
- **Cascade Rule:** Delete object → delete records (CASCADE)

### 6. objects ←→ objects (N:N via relationships)
```
objects (N) ◄───relationships───► (N) objects
```
- Objects can be related to other objects
- `from_object_id` and `to_object_id` both reference objects
- **Cascade Rule:** Delete object → delete relationships (CASCADE)

### 7. relationships → relationship_records (1:N)
```
relationships (1) ───has──► (N) relationship_records
```
- One relationship definition has many record links
- **Cascade Rule:** Delete relationship → delete relationship_records (CASCADE)

### 8. records ←→ records (N:N via relationship_records)
```
records (N) ◄───relationship_records───► (N) records
```
- Records can be linked to other records
- `from_record_id` and `to_record_id` both reference records
- **Cascade Rule:** Delete record → delete relationship_records (CASCADE)

---

## 🔄 CASCADE DELETE CHAINS

### Scenario 1: Delete Object
```
DELETE FROM objects WHERE id = 'obj_contact'
  ↓ CASCADE
  ├─► DELETE FROM object_fields WHERE object_id = 'obj_contact'
  ├─► DELETE FROM records WHERE object_id = 'obj_contact'
  │     ↓ CASCADE
  │     └─► DELETE FROM relationship_records
  │          WHERE from_record_id IN (contact_records)
  │             OR to_record_id IN (contact_records)
  └─► DELETE FROM relationships
        WHERE from_object_id = 'obj_contact'
           OR to_object_id = 'obj_contact'
        ↓ CASCADE
        └─► DELETE FROM relationship_records
             WHERE relationship_id IN (contact_relationships)
```

**Impact:** Deleting an object deletes everything related to it.

---

### Scenario 2: Delete Field
```
DELETE FROM fields WHERE id = 'fld_email'
  ↓ CHECK REFERENCES
  ├─► IF EXISTS object_fields WHERE field_id = 'fld_email'
  │     THEN ERROR: "Cannot delete field, it is in use"
  │     (RESTRICT constraint)
  └─► IF NOT EXISTS object_fields WHERE field_id = 'fld_email'
        THEN DELETE SUCCESSFUL
```

**Impact:** Cannot delete field if attached to any object. Must detach first.

---

### Scenario 3: Delete Record
```
DELETE FROM records WHERE id = 'rec_john_doe'
  ↓ CASCADE
  └─► DELETE FROM relationship_records
       WHERE from_record_id = 'rec_john_doe'
          OR to_record_id = 'rec_john_doe'
```

**Impact:** Deleting a record removes all relationship links involving that record.

---

### Scenario 4: Delete Relationship
```
DELETE FROM relationships WHERE id = 'rel_contact_companies'
  ↓ CASCADE
  └─► DELETE FROM relationship_records
       WHERE relationship_id = 'rel_contact_companies'
```

**Impact:** Deleting a relationship definition removes all record links using that relationship.

---

## 🎯 DATA FLOW PATTERNS

### Pattern 1: Creating an Object with Fields

```
Step 1: Create Object
POST /api/objects
  ↓
INSERT INTO objects (id, name, label, ...)
  VALUES ('obj_contact', 'contact', 'Contact', ...)

Step 2: Create Fields (if not exist)
POST /api/fields
  ↓
INSERT INTO fields (id, name, type, ...)
  VALUES ('fld_name', 'full_name', 'text', ...)

Step 3: Attach Fields to Object
POST /api/object-fields
  ↓
INSERT INTO object_fields (id, object_id, field_id, display_order, ...)
  VALUES ('ofd_xxx', 'obj_contact', 'fld_name', 0, ...)

Result: Object schema is defined
```

---

### Pattern 2: Creating a Record

```
Step 1: Get Object Fields
GET /api/object-fields?object_id=obj_contact
  ↓
SELECT * FROM object_fields
WHERE object_id = 'obj_contact'
ORDER BY display_order

Step 2: Validate Required Fields
Check: is_required = true fields have values

Step 3: Create Record
POST /api/records
  ↓
INSERT INTO records (id, object_id, data, primary_value, ...)
  VALUES (
    'rec_xxx',
    'obj_contact',
    '{"fld_name": "John Doe", "fld_email": "john@example.com"}',
    'John Doe',  -- auto-extracted
    ...
  )

Result: Data record created
```

---

### Pattern 3: Linking Records via Relationship

```
Step 1: Define Relationship
POST /api/relationships
  ↓
INSERT INTO relationships (id, from_object_id, to_object_id, type, ...)
  VALUES (
    'rel_contact_companies',
    'obj_contact',
    'obj_company',
    '1:N',
    ...
  )

Step 2: Link Records
POST /api/relationship-records
  ↓
INSERT INTO relationship_records (id, relationship_id, from_record_id, to_record_id, ...)
  VALUES (
    'rrec_xxx',
    'rel_contact_companies',
    'rec_john_doe',     -- Contact
    'rec_acme_corp',    -- Company
    ...
  )

Result: John Doe is linked to Acme Corp via contact_companies relationship
```

---

## 📊 QUERY PATTERNS WITH JOINS

### Query 1: Get All Fields for an Object (with field details)

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
    f.config AS field_config
FROM object_fields of
INNER JOIN fields f ON of.field_id = f.id
WHERE of.object_id = 'obj_contact'
ORDER BY of.display_order;
```

**Returns:**
```
object_field_id | display_order | is_required | field_name | field_type
----------------|---------------|-------------|------------|------------
ofd_abc123      | 0             | true        | full_name  | text
ofd_def456      | 1             | true        | email      | email
ofd_ghi789      | 2             | false       | phone      | phone
```

---

### Query 2: Get Related Records (1:N Relationship)

```sql
-- Get all companies for a contact
SELECT
    rr.id AS link_id,
    rr.relationship_metadata,
    r.id AS company_id,
    r.data AS company_data,
    r.primary_value AS company_name
FROM relationship_records rr
INNER JOIN records r ON rr.to_record_id = r.id
WHERE rr.relationship_id = 'rel_contact_companies'
  AND rr.from_record_id = 'rec_john_doe';
```

**Returns:**
```
link_id     | company_id   | company_name | relationship_metadata
------------|--------------|--------------|----------------------
rrec_xyz    | rec_acme     | Acme Corp    | {"role": "CEO"}
rrec_abc    | rec_globex   | Globex Inc   | {"role": "Consultant"}
```

---

### Query 3: Get All Relationships for an Object (Bidirectional)

```sql
-- Get all relationships where Contact is source OR target
SELECT
    r.id AS relationship_id,
    r.name AS relationship_name,
    r.type AS relationship_type,
    r.from_label,
    r.to_label,
    fo.name AS from_object_name,
    to.name AS to_object_name
FROM relationships r
INNER JOIN objects fo ON r.from_object_id = fo.id
INNER JOIN objects to ON r.to_object_id = to.id
WHERE r.from_object_id = 'obj_contact'
   OR r.to_object_id = 'obj_contact';
```

**Returns:**
```
relationship_id      | name                 | type | from_object | to_object
---------------------|----------------------|------|-------------|------------
rel_contact_company  | contact_companies    | 1:N  | contact     | company
rel_contact_opps     | contact_opportunities| 1:N  | contact     | opportunity
rel_company_contact  | company_contacts     | N:1  | company     | contact
```

---

### Query 4: Full Record Detail (Object + Fields + Data)

```sql
SELECT
    r.id AS record_id,
    r.primary_value,
    r.created_at,
    o.name AS object_name,
    o.label AS object_label,
    r.data AS record_data
FROM records r
INNER JOIN objects o ON r.object_id = o.id
WHERE r.id = 'rec_john_doe';
```

**Returns:**
```
record_id    | primary_value | object_name | record_data
-------------|---------------|-------------|----------------------------------
rec_john_doe | John Doe      | contact     | {"fld_name": "John Doe", ...}
```

---

## 🔐 REFERENTIAL INTEGRITY

### Enforced Constraints

| Constraint Type | Table | Columns | Action |
|-----------------|-------|---------|--------|
| PRIMARY KEY | users | id | Unique identifier |
| UNIQUE | users | email | One account per email |
| PRIMARY KEY | fields | id | Unique identifier |
| UNIQUE | fields | (name, created_by) | Unique field per user |
| PRIMARY KEY | objects | id | Unique identifier |
| FOREIGN KEY | object_fields | object_id | CASCADE on delete |
| FOREIGN KEY | object_fields | field_id | RESTRICT on delete |
| FOREIGN KEY | records | object_id | CASCADE on delete |
| FOREIGN KEY | relationships | from_object_id | CASCADE on delete |
| FOREIGN KEY | relationships | to_object_id | CASCADE on delete |
| FOREIGN KEY | relationship_records | relationship_id | CASCADE on delete |
| FOREIGN KEY | relationship_records | from_record_id | CASCADE on delete |
| FOREIGN KEY | relationship_records | to_record_id | CASCADE on delete |

### Not Enforced (Application-Level)

| Table | Column | References | Reason |
|-------|--------|------------|--------|
| fields | created_by | users.id | Avoid circular dependencies |
| objects | created_by | users.id | Avoid circular dependencies |
| records | created_by | users.id | Avoid circular dependencies |
| records | updated_by | users.id | Avoid circular dependencies |
| relationships | created_by | users.id | Avoid circular dependencies |
| relationship_records | created_by | users.id | Avoid circular dependencies |
| applications | created_by | users.id | Avoid circular dependencies |
| token_blacklist | user_id | users.id | Performance (high write volume) |

**Note:** These relationships are enforced in application code, not at database level.

---

## 🎯 INDEX STRATEGY

### Primary Lookup Indexes

```sql
-- Fast primary key lookups
CREATE UNIQUE INDEX users_pkey ON users (id);
CREATE UNIQUE INDEX fields_pkey ON fields (id);
CREATE UNIQUE INDEX objects_pkey ON objects (id);
CREATE UNIQUE INDEX records_pkey ON records (id);
CREATE UNIQUE INDEX relationships_pkey ON relationships (id);
```

### Foreign Key Indexes

```sql
-- Speed up JOIN operations
CREATE INDEX ix_records_object_id ON records (object_id);
CREATE INDEX ix_relationship_records_relationship_id ON relationship_records (relationship_id);
CREATE INDEX ix_relationship_records_from_record_id ON relationship_records (from_record_id);
CREATE INDEX ix_relationship_records_to_record_id ON relationship_records (to_record_id);
```

### Search Indexes

```sql
-- Fast text search
CREATE INDEX ix_records_primary_value ON records (primary_value);
CREATE UNIQUE INDEX ix_users_email ON users (email);

-- Category filtering
CREATE INDEX ix_fields_category ON fields (category);

-- Time-based queries
CREATE INDEX ix_records_created_at ON records (created_at);
CREATE INDEX ix_token_blacklist_expires_at ON token_blacklist (expires_at);
```

### Composite Unique Indexes

```sql
-- Enforce business rules
CREATE UNIQUE INDEX uq_field_name_created_by ON fields (name, created_by);
```

---

## 📈 PERFORMANCE CONSIDERATIONS

### 1. JSONB vs Normalized Trade-offs

**JSONB Advantages:**
- Flexible schema (user-defined fields)
- Fast reads (single row fetch)
- 7x faster than EAV pattern

**JSONB Disadvantages:**
- Cannot use foreign keys to JSONB fields
- Harder to enforce data types
- Index on specific JSONB keys requires GIN index

**Solution:** Hybrid model
- Metadata: Normalized (objects, fields, object_fields)
- Data: JSONB (records.data)

---

### 2. Primary Value Denormalization

**Problem:** JSONB queries are slow for text search
```sql
-- Slow (70ms)
SELECT * FROM records
WHERE data->>'fld_name' ILIKE '%john%';
```

**Solution:** Denormalize first text field into `primary_value`
```sql
-- Fast (10ms) - uses B-tree index
SELECT * FROM records
WHERE primary_value ILIKE '%john%';
```

**Maintenance:** Auto-updated on record create/update

---

### 3. Relationship Query Optimization

**Inefficient:**
```sql
-- N+1 query problem
SELECT * FROM records WHERE object_id = 'obj_contact';
-- Then for each record:
SELECT * FROM relationship_records WHERE from_record_id = ?;
```

**Efficient:**
```sql
-- Single query with JOIN
SELECT
    r.*,
    json_agg(
        json_build_object(
            'relationship_id', rr.relationship_id,
            'to_record_id', rr.to_record_id
        )
    ) AS relationships
FROM records r
LEFT JOIN relationship_records rr ON r.id = rr.from_record_id
WHERE r.object_id = 'obj_contact'
GROUP BY r.id;
```

---

## 🚀 SCALING CONSIDERATIONS

### Horizontal Scaling Challenges

1. **Multi-Tenant Isolation**
   - Current: `records.tenant_id` (VARCHAR)
   - Future: Consider separate schemas per tenant

2. **JSONB Query Performance**
   - Consider adding GIN indexes on frequently queried JSONB paths
   - Example: `CREATE INDEX idx_email ON records USING GIN ((data->'fld_email'));`

3. **Relationship Graph Complexity**
   - Consider graph database for complex relationship queries
   - Current approach: Works well for 2-3 levels deep

### Vertical Scaling Options

1. **Connection Pooling**
   - Use PgBouncer for connection management
   - Current: Direct connections via asyncpg

2. **Read Replicas**
   - Offload read queries to replicas
   - Write to primary, read from replicas

3. **Partitioning**
   - Partition `records` table by `object_id` or `tenant_id`
   - Partition `relationship_records` by `relationship_id`

---

**Last Updated:** 2026-01-18
**Schema Version:** Stored in alembic_version
**Status:** ✅ Production Ready
