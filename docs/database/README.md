# 🗄️ Database Documentation

Canvas App Backend veritabanı dokümantasyonu.

**Database:** PostgreSQL 16 (Supabase Local)
**ORM:** SQLAlchemy 2.0 (Async)
**Migrations:** Alembic

---

## 📚 Dokümantasyon Yapısı

```
docs/database/
├── README.md                    # Bu dosya (giriş noktası)
├── DATABASE_SCHEMA.md           # Tüm tabloların şema özeti
├── DATABASE_ER_DIAGRAM.md       # Entity Relationship diyagramları
├── TABLE_EXAMPLES.md            # Her tablo için örnek veriler
└── tables/                      # Her tablo için detaylı dokümantasyon
    ├── README.md                # Tablo listesi ve genel bakış
    ├── 01-users/
    │   └── README.md            # users tablosu detayları
    ├── 02-token-blacklist/
    │   └── README.md
    ├── 03-fields/
    │   └── README.md
    ├── 04-objects/
    │   └── README.md
    ├── 05-object-fields/
    │   └── README.md
    ├── 06-records/
    │   └── README.md            # JSONB hybrid model
    ├── 07-relationships/
    │   └── README.md
    ├── 08-relationship-records/
    │   └── README.md
    ├── 09-applications/
    │   └── README.md
    └── 10-alembic-version/
        └── README.md
```

---

## 🚀 Hızlı Başlangıç

### Yeni Gelenlere

1. **Genel Bakış**: [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
   - Tüm tabloların listesi
   - Kolon detayları
   - Index'ler
   - CASCADE davranışları

2. **İlişkiler**: [DATABASE_ER_DIAGRAM.md](DATABASE_ER_DIAGRAM.md)
   - ER diyagramları
   - Tablo ilişkileri
   - Foreign key constraints
   - Data flow patterns

3. **Örnekler**: [TABLE_EXAMPLES.md](TABLE_EXAMPLES.md)
   - Örnek veriler
   - Örnek sorgular
   - Best practices

### Detaylı İnceleme

Her tablo için detaylı dokümantasyon:
- [tables/README.md](tables/README.md) - Tüm tablolar listesi
- [tables/01-users/](tables/01-users/) - Kullanıcı tablosu
- [tables/06-records/](tables/06-records/) - Records tablosu (JSONB)

---

## 🎯 Ana Konseptler

### 1. JSONB Hybrid Model

**Problem:** Flexible schema + Type safety nasıl sağlanır?

**Çözüm:** Hybrid Model
- **Metadata:** Normalized (objects, fields, object_fields)
- **Data:** JSONB (records.data)
- **Search:** Denormalized (records.primary_value)

**Performans:**
- 7x daha hızlı (EAV pattern'e göre)
- Index'lenebilir search
- Type safety + Flexibility

📖 Detay: [tables/06-records/README.md](tables/06-records/README.md)

---

### 2. Object-Centric Architecture

**Objects** = Entity definitions (Contact, Company, Opportunity)
**Fields** = Attribute definitions (Name, Email, Phone)
**object_fields** = Object kullanır fields (N:N mapping)
**records** = Actual data (JSONB storage)

```
Object: "Contact"
├── Field: "Name" (display_order: 0, required: true)
├── Field: "Email" (display_order: 1, required: true)
└── Field: "Phone" (display_order: 2, required: false)

Record: rec_john_doe
└── data: {
      "fld_name": "John Doe",
      "fld_email": "john@example.com",
      "fld_phone": "+1 555 1234"
    }
```

📖 Detay: [DATABASE_SCHEMA.md#table-overview](DATABASE_SCHEMA.md#-table-overview)

---

### 3. Relationships (1:N, N:N)

**relationships** = Relationship definitions (Contact → Company)
**relationship_records** = Actual record links (John Doe → Acme Corp)

```
Relationship: "contact_companies" (1:N)
├── from_object: obj_contact
├── to_object: obj_company
├── type: "1:N"
└── labels: "Companies" / "Contact"

Relationship Record:
├── from_record: rec_john_doe (Contact)
├── to_record: rec_acme_corp (Company)
└── metadata: {"role": "CEO", "since": "2020-01-01"}
```

📖 Detay: [DATABASE_ER_DIAGRAM.md#relationship-cardinality](DATABASE_ER_DIAGRAM.md#-relationship-cardinality)

---

### 4. Multi-Tenancy

**Strategy:** Row-level tenant isolation
**Column:** records.tenant_id (VARCHAR)
**Enforcement:** Application-level (middleware)

```python
# Always filter by tenant_id
async def get_records(tenant_id: str):
    return await db.execute(
        select(Record).where(
            Record.object_id == object_id,
            Record.tenant_id == tenant_id  # Critical!
        )
    )
```

📖 Detay: [tables/06-records/README.md#multi-tenancy](tables/06-records/README.md#multi-tenancy)

---

## 📊 Tablo Kategorileri

### Core System Tables
- **users**: Kimlik doğrulama ve profiller
- **token_blacklist**: JWT token revocation
- **alembic_version**: Migration tracking

### Metadata Tables (Schema Definition)
- **fields**: Field definitions (text, number, email, etc.)
- **objects**: Object definitions (Contact, Company, etc.)
- **relationships**: Relationship definitions (1:N, N:N)

### Mapping Tables (N:N Relationships)
- **object_fields**: Object ↔ Field mapping
- **relationship_records**: Record ↔ Record links

### Data Tables (Actual Data)
- **records**: JSONB storage for flexible data

### Application Tables
- **applications**: Application configurations (CRM, ITSM, etc.)

📖 Detay: [tables/README.md#-tablo-tipleri](tables/README.md#-tablo-tipleri)

---

## 🔗 Tablo İlişkileri (CASCADE)

### Critical CASCADE Rules

1. **Delete Object → Deletes:**
   - All object_fields for that object (CASCADE)
   - All records for that object (CASCADE)
   - All relationships involving that object (CASCADE)
   - All relationship_records (via cascade chain)

2. **Delete Field → BLOCKED if:**
   - Field attached to any object (RESTRICT)
   - Must detach from all objects first

3. **Delete Record → Deletes:**
   - All relationship_records involving that record (CASCADE)

4. **Delete Relationship → Deletes:**
   - All relationship_records using that relationship (CASCADE)

📖 Detay: [DATABASE_ER_DIAGRAM.md#-cascade-delete-chains](DATABASE_ER_DIAGRAM.md#-cascade-delete-chains)

---

## 🎯 Sık Kullanılan Sorgular

### 1. Get Object Schema (with Fields)

```sql
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
-- 7x faster than JSONB search
SELECT * FROM records
WHERE object_id = 'obj_contact'
  AND primary_value ILIKE '%john%'
LIMIT 50;
```

### 3. Get Related Records

```sql
-- Get all companies for a contact
SELECT r.*
FROM relationship_records rr
JOIN records r ON rr.to_record_id = r.id
WHERE rr.relationship_id = 'rel_contact_companies'
  AND rr.from_record_id = 'rec_john_doe';
```

📖 Daha fazla: [TABLE_EXAMPLES.md#-complex-query-examples](TABLE_EXAMPLES.md#-complex-query-examples)

---

## 📈 Performans Rehberi

### Index Stratejisi

**Critical Indexes:**
1. `ix_records_object_id` - Filter by object type
2. `ix_records_primary_value` - Text search (7x faster)
3. `ix_records_created_at` - Time-based sorting
4. `ix_relationship_records_from_record_id` - Forward lookup
5. `ix_relationship_records_to_record_id` - Reverse lookup

### Best Practices

1. ✅ **Always filter by object_id first**
   ```sql
   WHERE object_id = 'obj_contact'  -- Uses index
   ```

2. ✅ **Use primary_value for text search**
   ```sql
   WHERE primary_value ILIKE '%search%'  -- 10ms
   ```

3. ❌ **Avoid JSONB queries if possible**
   ```sql
   WHERE data->>'fld_name' ILIKE '%search%'  -- 70ms
   ```

4. ✅ **Add GIN index for frequent JSONB paths**
   ```sql
   CREATE INDEX idx_email ON records USING GIN ((data->'fld_email'));
   ```

📖 Detay: [DATABASE_SCHEMA.md#-performance-indexes](DATABASE_SCHEMA.md#-performance-indexes)

---

## 🔐 Güvenlik

### 1. Password Storage
- **Algorithm:** bcrypt
- **Cost Factor:** 12
- **Library:** passlib[bcrypt]
- **Never:** Store plain text passwords

### 2. JWT Tokens
- **Lifetime:** 1 hour (3600 seconds)
- **Claims:** user_id, email, jti (token ID)
- **Revocation:** token_blacklist table
- **Cleanup:** Delete expired tokens daily

### 3. Multi-Tenancy
- **Strategy:** Row-level isolation via tenant_id
- **Enforcement:** Application middleware
- **Security:** Cannot be spoofed (from JWT)

### 4. SQL Injection Prevention
- **ORM:** SQLAlchemy parameterized queries
- **Validation:** Pydantic schema validation
- **Never:** String concatenation for SQL

📖 Detay: [DATABASE_SCHEMA.md#-security-considerations](DATABASE_SCHEMA.md#-security-considerations)

---

## 🛠️ Migration Yönetimi

### Alembic Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Current version
alembic current
```

### Migration Best Practices

1. ✅ **Always review auto-generated migrations**
2. ✅ **Test migrations on development first**
3. ✅ **Backup database before production migrations**
4. ✅ **Use descriptive migration messages**
5. ❌ **Never edit applied migrations**

**Migration Files:** `/alembic/versions/`

---

## 📊 Database Statistics

### Table Size Estimates

| Table | Expected Rows | Size Estimate |
|-------|--------------|---------------|
| users | Hundreds | Small (< 1 MB) |
| fields | Hundreds | Small (< 1 MB) |
| objects | Hundreds | Small (< 1 MB) |
| object_fields | Thousands | Small (< 10 MB) |
| **records** | **Millions** | **Large (GBs)** |
| relationships | Hundreds | Small (< 1 MB) |
| relationship_records | Millions | Medium (100s of MBs) |
| applications | Tens | Tiny (< 1 MB) |

**High-Volume Tables:**
- records (main data storage)
- relationship_records (relationship links)

**Partitioning Recommended:**
- records (by object_id or tenant_id)
- relationship_records (by relationship_id)

---

## 🧪 Testing Database

### Test Database Setup

```bash
# Create test database
createdb canvas_test

# Run migrations
DATABASE_URL=postgresql://localhost/canvas_test alembic upgrade head

# Run tests
pytest tests/
```

### Fixture Pattern

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def db_session():
    async with async_session() as session:
        yield session
        await session.rollback()  # Rollback after test
```

---

## 📚 İlgili Dokümantasyon

### Database
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Complete schema overview
- [DATABASE_ER_DIAGRAM.md](DATABASE_ER_DIAGRAM.md) - Relationship diagrams
- [TABLE_EXAMPLES.md](TABLE_EXAMPLES.md) - Sample data and queries
- [tables/](tables/) - Per-table documentation

### API
- [../api/](../api/) - API endpoint documentation
- [../BACKEND_ARCHITECTURE_ANALYSIS.md](../BACKEND_ARCHITECTURE_ANALYSIS.md) - Architecture decisions
- [../BACKEND_PROJECT_SPECIFICATION.md](../BACKEND_PROJECT_SPECIFICATION.md) - Project specification

### Code
- `/app/models/` - SQLAlchemy models
- `/app/schemas/` - Pydantic schemas
- `/alembic/versions/` - Migration files

---

## 🎓 Learning Path

### Beginner
1. Start: [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
2. Understand: [DATABASE_ER_DIAGRAM.md](DATABASE_ER_DIAGRAM.md)
3. Practice: [TABLE_EXAMPLES.md](TABLE_EXAMPLES.md)

### Intermediate
1. Deep Dive: [tables/06-records/README.md](tables/06-records/README.md) (JSONB)
2. Relationships: [tables/07-relationships/README.md](tables/07-relationships/README.md)
3. Performance: [DATABASE_SCHEMA.md#performance-indexes](DATABASE_SCHEMA.md#-performance-indexes)

### Advanced
1. Optimization: Partitioning strategies
2. Scaling: Read replicas, connection pooling
3. Multi-Tenancy: Schema separation vs row-level isolation

---

## ❓ FAQ

### Q: JSONB vs Normalized?
**A:** We use hybrid model - metadata normalized, data in JSONB. Best of both worlds.

### Q: Why not use Supabase Auth?
**A:** Custom JWT for full control, easier testing, no external dependencies.

### Q: How to handle schema changes?
**A:** Alembic migrations - all schema changes versioned and trackable.

### Q: Multi-tenancy strategy?
**A:** Row-level via tenant_id (current). Schema separation possible for future scaling.

### Q: JSONB performance?
**A:** Use primary_value for search (7x faster). Add GIN indexes for frequent JSONB paths.

---

**Last Updated:** 2026-01-18
**Database Version:** Check `alembic_version` table
**Status:** ✅ Production Ready
**Contributors:** Backend Team
