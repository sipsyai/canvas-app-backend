# Record API Endpoints

Record API, object içindeki veri kayıtlarını (records) yönetir. Her record bir JSONB data field'ında dinamik field değerlerini saklar.

## Record Nedir?

Record, bir object'in veri satırıdır. Örneğin:
- Contact object'i → Her kişi bir record
- Company object'i → Her şirket bir record
- Opportunity object'i → Her fırsat bir record

## JSONB Hybrid Model

Records tablosu **normalized metadata + JSONB data** hibrit modelini kullanır:

```sql
CREATE TABLE records (
  id VARCHAR PRIMARY KEY,           -- rec_a1b2c3d4
  object_id VARCHAR NOT NULL,       -- obj_contact
  data JSONB NOT NULL,              -- {"fld_name": "Ali", "fld_email": "ali@example.com"}
  primary_value TEXT,               -- "Ali" (denormalized, hızlı arama için)
  created_by UUID,
  updated_by UUID,
  tenant_id VARCHAR,                -- Multi-tenancy
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);
```

## Endpoints

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| POST | `/api/records` | Yeni record oluştur | ✅ JWT |
| GET | `/api/records?object_id=...` | Record'ları listele (pagination) | ✅ JWT |
| GET | `/api/records/{record_id}` | Tek record getir | ✅ JWT |
| PATCH | `/api/records/{record_id}` | Record güncelle (MERGE) | ✅ JWT |
| DELETE | `/api/records/{record_id}` | Record sil | ✅ JWT |
| GET | `/api/records/search?object_id=...&q=...` | Record ara | ✅ JWT |

## Örnek Record Yapısı

```json
{
  "id": "rec_a1b2c3d4",
  "object_id": "obj_contact",
  "data": {
    "fld_name": "Ali Yılmaz",
    "fld_email": "ali@example.com",
    "fld_phone": "+90 555 1234567",
    "fld_company": "Acme Corp",
    "fld_created_at": "2026-01-18T10:00:00Z"
  },
  "primary_value": "Ali Yılmaz",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "updated_by": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T10:00:00Z"
}
```

## JSONB Data Format

**Field Key Format:** `fld_<field_id>`

```json
{
  "fld_a1b2c3d4": "Ali Yılmaz",        // Text field
  "fld_b2c3d4e5": "ali@example.com",   // Email field
  "fld_c3d4e5f6": 1500.50,             // Number/Currency field
  "fld_d4e5f6g7": true,                // Checkbox field
  "fld_e5f6g7h8": "2026-01-18",        // Date field
  "fld_f6g7h8i9": ["option1", "option2"] // Multiselect field
}
```

## Primary Value

`primary_value` ilk text-like field'ın değerini saklar:
- List view'lerde gösterilir
- Arama için kullanılır (JSONB query'den 7x daha hızlı)
- Otomatik oluşturulur (create/update sırasında)

## Detaylı Dokümantasyon

- [POST /api/records - Record Oluştur](01-create-record.md)
- [GET /api/records - Record Listele](02-list-records.md)
- [GET /api/records/{record_id} - Record Getir](03-get-record.md)
- [PATCH /api/records/{record_id} - Record Güncelle](04-update-record.md)
- [DELETE /api/records/{record_id} - Record Sil](05-delete-record.md)
- [GET /api/records/search - Record Ara](06-search-records.md)

## Code Flow

```
Request
  ↓
Router (app/routers/records.py)
  ↓
JWT Authentication
  ↓
Service Layer (record_service.py)
  ├── Primary value extraction
  ├── JSONB merge (update)
  └── Database operations
  ↓
PostgreSQL JSONB Storage
```

## Performance

**GIN Index ile hızlı JSONB sorgular:**
```sql
CREATE INDEX idx_records_data_gin ON records USING GIN(data);
CREATE INDEX idx_records_primary_value ON records(primary_value);
```

**Query Performance:**
- Primary value search: ~10ms (indexed)
- JSONB contains query: ~20-30ms (GIN indexed)
- JSONB nested query: ~50-100ms

## İlgili Endpoint'ler

- [Object API](../03-objects/README.md) - Record'ların ait olduğu object'ler
- [Field API](../02-fields/README.md) - Record data'sındaki field tanımları
- [Relationship-Record API](../08-relationship-records/README.md) - Record'lar arası ilişkiler
