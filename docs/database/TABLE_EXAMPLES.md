# 📝 DATABASE TABLE EXAMPLES

**Database:** PostgreSQL 16 (Supabase Local)
**Last Updated:** 2026-01-18

Bu dokümantasyon, her tablonun gerçek kullanım örneklerini gösterir.

---

## 📋 TABLE OF CONTENTS

1. [users](#users-examples)
2. [token_blacklist](#token_blacklist-examples)
3. [fields](#fields-examples)
4. [objects](#objects-examples)
5. [object_fields](#object_fields-examples)
6. [records](#records-examples)
7. [relationships](#relationships-examples)
8. [relationship_records](#relationship_records-examples)
9. [applications](#applications-examples)

---

## users Examples

### Sample Data

```sql
INSERT INTO users (id, email, hashed_password, full_name, is_active, is_verified, created_at, updated_at, last_login)
VALUES
  (
    '550e8400-e29b-41d4-a716-446655440000',
    'john.doe@example.com',
    '$2b$12$KIXxLhGvBZLXN5Zg2hVQYO.Jx4ZqX8YqL2Hn3V4Zg2hVQYO.Jx4Zq',  -- hashed "password123"
    'John Doe',
    true,
    true,
    '2026-01-15 10:00:00+00',
    '2026-01-15 10:00:00+00',
    '2026-01-18 08:30:00+00'
  ),
  (
    '660e8400-e29b-41d4-a716-446655440001',
    'jane.smith@example.com',
    '$2b$12$LJYyMihCWCMYO6Ah3XWRZe.Ky5ArY9ZrM3Io4W5Ah3XWRZe.Ky5Ar',  -- hashed "securepass"
    'Jane Smith',
    true,
    false,  -- Email not verified
    '2026-01-16 14:30:00+00',
    '2026-01-16 14:30:00+00',
    NULL  -- Never logged in
  );
```

### Query Examples

```sql
-- Find user by email (login)
SELECT * FROM users
WHERE email = 'john.doe@example.com';

-- Get active verified users
SELECT id, email, full_name, last_login
FROM users
WHERE is_active = true AND is_verified = true
ORDER BY last_login DESC;

-- Count users by status
SELECT
  COUNT(*) FILTER (WHERE is_verified = true) AS verified_users,
  COUNT(*) FILTER (WHERE is_verified = false) AS unverified_users,
  COUNT(*) FILTER (WHERE is_active = false) AS inactive_users
FROM users;
```

---

## token_blacklist Examples

### Sample Data

```sql
INSERT INTO token_blacklist (jti, user_id, expires_at, blacklisted_at)
VALUES
  (
    'baae b20f-fa3a-4829-9aef-df2b4da7094c',
    '550e8400-e29b-41d4-a716-446655440000',
    '2026-01-19 10:00:00+00',  -- Expires in 24 hours
    '2026-01-18 10:00:00+00'   -- Blacklisted now
  ),
  (
    'ccbf c30g-gb4b-5930-0bfg-eg3c5eb8105d',
    '550e8400-e29b-41d4-a716-446655440000',
    '2026-01-18 08:00:00+00',  -- Already expired
    '2026-01-17 08:00:00+00'
  );
```

### Query Examples

```sql
-- Check if token is blacklisted (called on every API request)
SELECT EXISTS (
  SELECT 1 FROM token_blacklist
  WHERE jti = 'baae b20f-fa3a-4829-9aef-df2b4da7094c'
) AS is_blacklisted;

-- Cleanup expired tokens (run daily via cron)
DELETE FROM token_blacklist
WHERE expires_at < NOW();

-- Count active blacklisted tokens per user
SELECT
  user_id,
  COUNT(*) AS blacklisted_tokens
FROM token_blacklist
WHERE expires_at > NOW()
GROUP BY user_id;
```

---

## fields Examples

### Sample Data

```sql
INSERT INTO fields (id, name, label, type, description, config, category, is_global, is_custom, is_system_field, created_at, updated_at, created_by)
VALUES
  (
    'fld_name',
    'full_name',
    'Full Name',
    'text',
    'Person full name',
    '{"minLength": 1, "maxLength": 255}',
    'contact',
    true,  -- Global field (can be used by anyone)
    false,  -- Not custom (system-defined)
    true,   -- System field
    '2026-01-15 10:00:00+00',
    '2026-01-15 10:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000'
  ),
  (
    'fld_email',
    'email_address',
    'Email',
    'email',
    'Email address',
    '{"pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"}',
    'contact',
    true,
    false,
    true,
    '2026-01-15 10:00:00+00',
    '2026-01-15 10:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000'
  ),
  (
    'fld_phone',
    'phone_number',
    'Phone',
    'phone',
    'Phone number',
    '{"format": "international"}',
    'contact',
    true,
    false,
    true,
    '2026-01-15 10:00:00+00',
    '2026-01-15 10:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000'
  ),
  (
    'fld_price',
    'product_price',
    'Price',
    'number',
    'Product price in USD',
    '{"min": 0, "decimals": 2, "currency": "USD"}',
    'product',
    false,  -- Not global
    true,   -- Custom field
    false,  -- Not system field
    '2026-01-16 11:00:00+00',
    '2026-01-16 11:00:00+00',
    '660e8400-e29b-41d4-a716-446655440001'
  );
```

### Query Examples

```sql
-- Get all global fields (shared across tenants)
SELECT id, name, label, type, category
FROM fields
WHERE is_global = true
ORDER BY category, name;

-- Get custom fields created by user
SELECT id, name, label, type, config
FROM fields
WHERE created_by = '660e8400-e29b-41d4-a716-446655440001'
  AND is_custom = true;

-- Find fields by category
SELECT id, name, label, type
FROM fields
WHERE category = 'contact'
ORDER BY name;

-- Search fields by name or label
SELECT id, name, label, type
FROM fields
WHERE name ILIKE '%email%'
   OR label ILIKE '%email%';
```

---

## objects Examples

### Sample Data

```sql
INSERT INTO objects (id, name, label, plural_name, description, icon, is_custom, is_global, views, permissions, created_at, updated_at, created_by)
VALUES
  (
    'obj_contact',
    'contact',
    'Contact',
    'Contacts',
    'Person or individual',
    '👤',
    false,  -- System object
    true,   -- Global
    '{
      "forms": [{"id": "form_default", "name": "Default Form", "layout": []}],
      "tables": [{"id": "table_all", "name": "All Contacts", "columns": ["fld_name", "fld_email"]}],
      "kanbans": [],
      "calendars": []
    }',
    '{
      "read": ["all"],
      "create": ["all"],
      "update": ["owner", "role_admin"],
      "delete": ["role_admin"]
    }',
    '2026-01-15 10:00:00+00',
    '2026-01-15 10:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000'
  ),
  (
    'obj_company',
    'company',
    'Company',
    'Companies',
    'Business organization',
    '🏢',
    false,
    true,
    '{
      "forms": [],
      "tables": [{"id": "table_all", "name": "All Companies", "columns": ["fld_name", "fld_website"]}],
      "kanbans": [],
      "calendars": []
    }',
    '{
      "read": ["all"],
      "create": ["all"],
      "update": ["all"],
      "delete": ["all"]
    }',
    '2026-01-15 10:00:00+00',
    '2026-01-15 10:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000'
  ),
  (
    'obj_product',
    'product',
    'Product',
    'Products',
    'Product catalog item',
    '📦',
    true,   -- Custom object
    false,  -- Not global (user-specific)
    '{
      "forms": [],
      "tables": [],
      "kanbans": [],
      "calendars": []
    }',
    '{
      "read": ["all"],
      "create": ["all"],
      "delete": ["all"],
      "update": ["all"]
    }',
    '2026-01-16 11:00:00+00',
    '2026-01-16 11:00:00+00',
    '660e8400-e29b-41d4-a716-446655440001'
  );
```

### Query Examples

```sql
-- Get all global objects (system-defined)
SELECT id, name, label, plural_name, icon
FROM objects
WHERE is_global = true
ORDER BY name;

-- Get custom objects created by user
SELECT id, name, label, plural_name, description
FROM objects
WHERE created_by = '660e8400-e29b-41d4-a716-446655440001'
  AND is_custom = true;

-- Get object with permissions
SELECT
  id,
  name,
  label,
  permissions->>'read' AS read_perms,
  permissions->>'create' AS create_perms,
  permissions->>'update' AS update_perms,
  permissions->>'delete' AS delete_perms
FROM objects
WHERE id = 'obj_contact';

-- Count views per object
SELECT
  id,
  name,
  jsonb_array_length(views->'forms') AS form_count,
  jsonb_array_length(views->'tables') AS table_count,
  jsonb_array_length(views->'kanbans') AS kanban_count,
  jsonb_array_length(views->'calendars') AS calendar_count
FROM objects;
```

---

## object_fields Examples

### Sample Data

```sql
-- Contact object with 3 fields
INSERT INTO object_fields (id, object_id, field_id, display_order, is_required, is_visible, is_readonly, field_overrides, created_at)
VALUES
  (
    'ofd_contact_name',
    'obj_contact',
    'fld_name',
    0,  -- First field
    true,  -- Required
    true,
    false,
    '{}',
    '2026-01-15 10:00:00+00'
  ),
  (
    'ofd_contact_email',
    'obj_contact',
    'fld_email',
    1,  -- Second field
    true,  -- Required
    true,
    false,
    '{"placeholder": "Enter email address"}',  -- Override
    '2026-01-15 10:00:00+00'
  ),
  (
    'ofd_contact_phone',
    'obj_contact',
    'fld_phone',
    2,  -- Third field
    false,  -- Optional
    true,
    false,
    '{}',
    '2026-01-15 10:00:00+00'
  );

-- Product object with 2 fields
INSERT INTO object_fields (id, object_id, field_id, display_order, is_required, is_visible, is_readonly, field_overrides, created_at)
VALUES
  (
    'ofd_product_name',
    'obj_product',
    'fld_name',
    0,
    true,
    true,
    false,
    '{"label": "Product Name"}',  -- Override label
    '2026-01-16 11:00:00+00'
  ),
  (
    'ofd_product_price',
    'obj_product',
    'fld_price',
    1,
    true,
    true,
    false,
    '{}',
    '2026-01-16 11:00:00+00'
  );
```

### Query Examples

```sql
-- Get all fields for an object (with field details)
SELECT
    of.id AS object_field_id,
    of.display_order,
    of.is_required,
    of.is_visible,
    of.is_readonly,
    f.id AS field_id,
    f.name,
    f.label,
    f.type,
    COALESCE(of.field_overrides->>'label', f.label) AS final_label
FROM object_fields of
JOIN fields f ON of.field_id = f.id
WHERE of.object_id = 'obj_contact'
ORDER BY of.display_order;

-- Count fields per object
SELECT
    o.id,
    o.name,
    COUNT(of.id) AS field_count
FROM objects o
LEFT JOIN object_fields of ON o.id = of.object_id
GROUP BY o.id, o.name
ORDER BY field_count DESC;

-- Find required fields for object
SELECT
    of.id,
    f.name,
    f.label,
    f.type
FROM object_fields of
JOIN fields f ON of.field_id = f.id
WHERE of.object_id = 'obj_contact'
  AND of.is_required = true
ORDER BY of.display_order;

-- Find objects using a specific field
SELECT DISTINCT
    o.id,
    o.name,
    o.label
FROM object_fields of
JOIN objects o ON of.object_id = o.id
WHERE of.field_id = 'fld_name'
ORDER BY o.name;
```

---

## records Examples

### Sample Data

```sql
-- Contact records
INSERT INTO records (id, object_id, data, primary_value, created_at, updated_at, created_by, updated_by, tenant_id)
VALUES
  (
    'rec_john_doe',
    'obj_contact',
    '{
      "fld_name": "John Doe",
      "fld_email": "john.doe@example.com",
      "fld_phone": "+1 555 1234"
    }',
    'John Doe',  -- Auto-extracted from fld_name
    '2026-01-15 11:00:00+00',
    '2026-01-15 11:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440000',
    'tenant_abc123'
  ),
  (
    'rec_jane_smith',
    'obj_contact',
    '{
      "fld_name": "Jane Smith",
      "fld_email": "jane.smith@example.com",
      "fld_phone": "+1 555 5678"
    }',
    'Jane Smith',
    '2026-01-15 12:00:00+00',
    '2026-01-15 12:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440000',
    'tenant_abc123'
  );

-- Company records
INSERT INTO records (id, object_id, data, primary_value, created_at, updated_at, created_by, updated_by, tenant_id)
VALUES
  (
    'rec_acme_corp',
    'obj_company',
    '{
      "fld_name": "Acme Corporation",
      "fld_website": "https://acme.com"
    }',
    'Acme Corporation',
    '2026-01-15 13:00:00+00',
    '2026-01-15 13:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440000',
    'tenant_abc123'
  );

-- Product records
INSERT INTO records (id, object_id, data, primary_value, created_at, updated_at, created_by, updated_by, tenant_id)
VALUES
  (
    'rec_laptop',
    'obj_product',
    '{
      "fld_name": "Gaming Laptop X1",
      "fld_price": 1299.99
    }',
    'Gaming Laptop X1',
    '2026-01-16 11:30:00+00',
    '2026-01-16 11:30:00+00',
    '660e8400-e29b-41d4-a716-446655440001',
    '660e8400-e29b-41d4-a716-446655440001',
    'tenant_xyz789'
  );
```

### Query Examples

```sql
-- Get all contacts for a tenant
SELECT
    id,
    primary_value,
    data->>'fld_email' AS email,
    data->>'fld_phone' AS phone,
    created_at
FROM records
WHERE object_id = 'obj_contact'
  AND tenant_id = 'tenant_abc123'
ORDER BY created_at DESC;

-- Search contacts by name (fast - uses index)
SELECT
    id,
    primary_value,
    data->>'fld_email' AS email
FROM records
WHERE object_id = 'obj_contact'
  AND primary_value ILIKE '%john%'
LIMIT 50;

-- Get record with specific field value (JSONB query)
SELECT
    id,
    primary_value,
    data
FROM records
WHERE object_id = 'obj_contact'
  AND data->>'fld_email' = 'john.doe@example.com';

-- Update record (partial JSONB merge)
UPDATE records
SET
    data = data || '{"fld_phone": "+1 555 9999"}',  -- Merge new data
    updated_at = NOW(),
    updated_by = '550e8400-e29b-41d4-a716-446655440000'
WHERE id = 'rec_john_doe';

-- Count records per object type
SELECT
    o.name AS object_name,
    o.label AS object_label,
    COUNT(r.id) AS record_count
FROM objects o
LEFT JOIN records r ON o.id = r.object_id
GROUP BY o.id, o.name, o.label
ORDER BY record_count DESC;

-- Get recent records (last 7 days)
SELECT
    id,
    object_id,
    primary_value,
    created_at
FROM records
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

---

## relationships Examples

### Sample Data

```sql
INSERT INTO relationships (id, name, from_object_id, to_object_id, type, from_label, to_label, created_at, created_by)
VALUES
  (
    'rel_contact_companies',
    'contact_companies',
    'obj_contact',
    'obj_company',
    '1:N',  -- One contact can have many companies
    'Companies',  -- Label shown on Contact
    'Contact',    -- Label shown on Company
    '2026-01-15 14:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000'
  ),
  (
    'rel_company_contacts',
    'company_contacts',
    'obj_company',
    'obj_contact',
    'N:N',  -- Many-to-Many
    'Contacts',
    'Companies',
    '2026-01-15 14:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000'
  );
```

### Query Examples

```sql
-- Get all relationships for an object (bidirectional)
SELECT
    r.id,
    r.name,
    r.type,
    CASE
        WHEN r.from_object_id = 'obj_contact' THEN 'outgoing'
        ELSE 'incoming'
    END AS direction,
    r.from_label,
    r.to_label,
    fo.name AS from_object,
    to.name AS to_object
FROM relationships r
JOIN objects fo ON r.from_object_id = fo.id
JOIN objects to ON r.to_object_id = to.id
WHERE r.from_object_id = 'obj_contact'
   OR r.to_object_id = 'obj_contact';

-- Find 1:N relationships
SELECT
    r.id,
    r.name,
    fo.label AS from_object,
    to.label AS to_object,
    r.from_label,
    r.to_label
FROM relationships r
JOIN objects fo ON r.from_object_id = fo.id
JOIN objects to ON r.to_object_id = to.id
WHERE r.type = '1:N';

-- Find relationships between two specific objects
SELECT *
FROM relationships
WHERE (from_object_id = 'obj_contact' AND to_object_id = 'obj_company')
   OR (from_object_id = 'obj_company' AND to_object_id = 'obj_contact');
```

---

## relationship_records Examples

### Sample Data

```sql
INSERT INTO relationship_records (id, relationship_id, from_record_id, to_record_id, relationship_metadata, created_at, created_by)
VALUES
  (
    'rrec_john_acme',
    'rel_contact_companies',
    'rec_john_doe',    -- Contact
    'rec_acme_corp',   -- Company
    '{
      "role": "CEO",
      "since": "2020-01-01",
      "is_primary": true
    }',
    '2026-01-15 15:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000'
  ),
  (
    'rrec_jane_acme',
    'rel_contact_companies',
    'rec_jane_smith',  -- Contact
    'rec_acme_corp',   -- Company
    '{
      "role": "CTO",
      "since": "2021-06-15",
      "is_primary": false
    }',
    '2026-01-15 15:30:00+00',
    '550e8400-e29b-41d4-a716-446655440000'
  );
```

### Query Examples

```sql
-- Get all companies for a contact
SELECT
    rr.id AS link_id,
    rr.relationship_metadata->>'role' AS role,
    rr.relationship_metadata->>'since' AS since_date,
    r.id AS company_id,
    r.primary_value AS company_name,
    r.data
FROM relationship_records rr
JOIN records r ON rr.to_record_id = r.id
WHERE rr.relationship_id = 'rel_contact_companies'
  AND rr.from_record_id = 'rec_john_doe'
ORDER BY (rr.relationship_metadata->>'is_primary')::boolean DESC;

-- Get all contacts for a company (reverse lookup)
SELECT
    rr.id AS link_id,
    rr.relationship_metadata->>'role' AS role,
    r.id AS contact_id,
    r.primary_value AS contact_name,
    r.data->>'fld_email' AS email
FROM relationship_records rr
JOIN records r ON rr.from_record_id = r.id
WHERE rr.relationship_id = 'rel_contact_companies'
  AND rr.to_record_id = 'rec_acme_corp'
ORDER BY rr.created_at;

-- Find all relationships for a specific record (bidirectional)
SELECT
    rr.id,
    rel.name AS relationship_name,
    CASE
        WHEN rr.from_record_id = 'rec_john_doe' THEN 'outgoing'
        ELSE 'incoming'
    END AS direction,
    CASE
        WHEN rr.from_record_id = 'rec_john_doe' THEN r_to.primary_value
        ELSE r_from.primary_value
    END AS related_record_name,
    rr.relationship_metadata
FROM relationship_records rr
JOIN relationships rel ON rr.relationship_id = rel.id
LEFT JOIN records r_from ON rr.from_record_id = r_from.id
LEFT JOIN records r_to ON rr.to_record_id = r_to.id
WHERE rr.from_record_id = 'rec_john_doe'
   OR rr.to_record_id = 'rec_john_doe';

-- Count relationships per record
SELECT
    r.id,
    r.primary_value,
    COUNT(DISTINCT rr.id) AS total_relationships,
    COUNT(DISTINCT CASE WHEN rr.from_record_id = r.id THEN rr.id END) AS outgoing,
    COUNT(DISTINCT CASE WHEN rr.to_record_id = r.id THEN rr.id END) AS incoming
FROM records r
LEFT JOIN relationship_records rr
    ON r.id = rr.from_record_id OR r.id = rr.to_record_id
WHERE r.object_id = 'obj_contact'
GROUP BY r.id, r.primary_value
ORDER BY total_relationships DESC;
```

---

## applications Examples

### Sample Data

```sql
INSERT INTO applications (id, name, label, description, icon, config, published_at, created_at, updated_at, created_by)
VALUES
  (
    'app_crm',
    'CRM',
    'Customer Relationship Management',
    'Manage customers, contacts, and opportunities',
    '🤝',
    '{
      "objects": ["obj_contact", "obj_company", "obj_opportunity"],
      "theme": {
        "primaryColor": "#1E40AF",
        "logo": "/assets/crm-logo.png"
      },
      "navigation": [
        {"label": "Contacts", "object": "obj_contact"},
        {"label": "Companies", "object": "obj_company"}
      ]
    }',
    '2026-01-15 16:00:00+00',  -- Published
    '2026-01-15 10:00:00+00',
    '2026-01-15 16:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000'
  ),
  (
    'app_itsm',
    'ITSM',
    'IT Service Management',
    'Manage IT tickets and service requests',
    '🔧',
    '{
      "objects": ["obj_ticket", "obj_asset"],
      "theme": {
        "primaryColor": "#059669"
      }
    }',
    NULL,  -- Draft (not published)
    '2026-01-16 10:00:00+00',
    '2026-01-16 10:00:00+00',
    '550e8400-e29b-41d4-a716-446655440000'
  );
```

### Query Examples

```sql
-- Get all published applications
SELECT
    id,
    name,
    label,
    description,
    icon,
    published_at
FROM applications
WHERE published_at IS NOT NULL
ORDER BY published_at DESC;

-- Get draft applications
SELECT
    id,
    name,
    label,
    updated_at AS last_edited
FROM applications
WHERE published_at IS NULL
ORDER BY updated_at DESC;

-- Get application with objects
SELECT
    a.id,
    a.name,
    a.label,
    a.config->'objects' AS object_ids,
    json_agg(
        json_build_object(
            'id', o.id,
            'name', o.name,
            'label', o.label
        )
    ) AS objects
FROM applications a
CROSS JOIN LATERAL jsonb_array_elements_text(a.config->'objects') AS obj_id
LEFT JOIN objects o ON o.id = obj_id::text
WHERE a.id = 'app_crm'
GROUP BY a.id, a.name, a.label, a.config;

-- Publish application
UPDATE applications
SET
    published_at = NOW(),
    updated_at = NOW()
WHERE id = 'app_itsm';

-- Unpublish application (revert to draft)
UPDATE applications
SET
    published_at = NULL,
    updated_at = NOW()
WHERE id = 'app_crm';
```

---

## 🎯 COMPLEX QUERY EXAMPLES

### Example 1: Get Complete Object Schema

```sql
-- Get object with all its fields and configurations
SELECT
    o.id AS object_id,
    o.name AS object_name,
    o.label AS object_label,
    json_agg(
        json_build_object(
            'field_id', f.id,
            'field_name', f.name,
            'field_label', COALESCE(of.field_overrides->>'label', f.label),
            'field_type', f.type,
            'display_order', of.display_order,
            'is_required', of.is_required,
            'is_visible', of.is_visible,
            'config', f.config
        ) ORDER BY of.display_order
    ) AS fields
FROM objects o
LEFT JOIN object_fields of ON o.id = of.object_id
LEFT JOIN fields f ON of.field_id = f.id
WHERE o.id = 'obj_contact'
GROUP BY o.id, o.name, o.label;
```

### Example 2: Full Record with Related Records

```sql
-- Get contact with all companies and their details
SELECT
    r.id AS contact_id,
    r.primary_value AS contact_name,
    r.data AS contact_data,
    json_agg(
        json_build_object(
            'company_id', company.id,
            'company_name', company.primary_value,
            'company_data', company.data,
            'role', rr.relationship_metadata->>'role',
            'since', rr.relationship_metadata->>'since'
        )
    ) FILTER (WHERE company.id IS NOT NULL) AS companies
FROM records r
LEFT JOIN relationship_records rr
    ON r.id = rr.from_record_id
    AND rr.relationship_id = 'rel_contact_companies'
LEFT JOIN records company ON rr.to_record_id = company.id
WHERE r.id = 'rec_john_doe'
GROUP BY r.id, r.primary_value, r.data;
```

### Example 3: Application Dashboard Stats

```sql
-- Get statistics for an application
WITH app_objects AS (
    SELECT jsonb_array_elements_text(config->'objects') AS object_id
    FROM applications
    WHERE id = 'app_crm'
)
SELECT
    o.label AS object_label,
    COUNT(r.id) AS total_records,
    COUNT(r.id) FILTER (WHERE r.created_at > NOW() - INTERVAL '7 days') AS records_last_7_days,
    COUNT(r.id) FILTER (WHERE r.created_at > NOW() - INTERVAL '30 days') AS records_last_30_days
FROM app_objects ao
JOIN objects o ON ao.object_id = o.id
LEFT JOIN records r ON o.id = r.object_id
GROUP BY o.id, o.label
ORDER BY total_records DESC;
```

---

**Last Updated:** 2026-01-18
**Database:** PostgreSQL 16 (Supabase Local)
**Status:** ✅ Production Ready
