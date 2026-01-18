# relationship_records Table

## Genel Bakış

**Amaç:** Record'lar arası gerçek bağlantılar

**Tip:** Mapping/Data Table
**ID Format:** rrec_xxxxxxxx (8 hex chars)
**Pattern:** Record ↔ Record (via relationship definition)
**Example:** John Doe (Contact) → Acme Corp (Company)

---

## Tablo Özellikleri

| Özellik | Değer |
|---------|-------|
| **Primary Key** | id (VARCHAR) |
| **Foreign Keys** | relationship_id → relationships.id (CASCADE)<br>from_record_id → records.id (CASCADE)<br>to_record_id → records.id (CASCADE) |
| **Referenced By** | None (data table) |
| **Cascade Deletes** | YES (when relationship or record deleted) |
| **Indexes** | 5 indexes (critical for performance) |
| **Row Estimate:** | Millions (high volume) |

---

## Kolonlar

### id (varchar) - Primary Key
- **Format:** rrec_ + 8 hex chars
- **Örnek:** rrec_a1b2c3d4

### relationship_id (varchar) - Foreign Key
- **References:** relationships.id (CASCADE)
- **Açıklama:** Which relationship definition
- **Örnek:** rel_contact_companies

### from_record_id (varchar) - Foreign Key
- **References:** records.id (CASCADE)
- **Açıklama:** Source record
- **Örnek:** rec_john_doe (Contact)

### to_record_id (varchar) - Foreign Key
- **References:** records.id (CASCADE)
- **Açıklama:** Target record
- **Örnek:** rec_acme_corp (Company)

### relationship_metadata (jsonb)
- **Tip:** JSONB
- **Default:** {}
- **Açıklama:** Relationship-specific data
- **Example:**
```json
{
  "role": "CEO",
  "since": "2020-01-01",
  "is_primary": true,
  "notes": "Main contact"
}
```

### created_at (timestamptz)
- **Default:** NOW()

### created_by (uuid)
- **References:** users.id (not enforced)

---

## Index'ler (CRITICAL)

### 1. ix_relationship_records_relationship_id
**Purpose:** Filter by relationship
**Query:** WHERE relationship_id = ?

### 2. ix_relationship_records_from_record_id
**Purpose:** Forward lookup (get related records)
**Query:** WHERE from_record_id = ?
**Criticality:** ⚠️ CRITICAL

### 3. ix_relationship_records_to_record_id
**Purpose:** Reverse lookup (find who links to this record)
**Query:** WHERE to_record_id = ?
**Criticality:** ⚠️ CRITICAL

---

## Örnek Kullanımlar

### Link Records

```python
# Link Contact → Company
await relationship_record_service.create_relationship_record(
    db=db,
    relationship_record_in=RelationshipRecordCreate(
        relationship_id="rel_contact_companies",
        from_record_id="rec_john_doe",
        to_record_id="rec_acme_corp",
        relationship_metadata={
            "role": "CEO",
            "since": "2020-01-01"
        }
    ),
    user_id=user_id
)
```

### Query Related Records

```sql
-- Get all companies for a contact
SELECT r.*
FROM relationship_records rr
JOIN records r ON rr.to_record_id = r.id
WHERE rr.relationship_id = 'rel_contact_companies'
  AND rr.from_record_id = 'rec_john_doe';
```

### Bidirectional Query

```sql
-- Get all relationships for a record (both directions)
SELECT *
FROM relationship_records
WHERE from_record_id = 'rec_john_doe'
   OR to_record_id = 'rec_john_doe';
```

---

**Last Updated:** 2026-01-18
**Status:** ✅ Production Ready
**Performance:** Critical indexes for relationship queries
