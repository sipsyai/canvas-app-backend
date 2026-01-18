# GET /api/records/search

## Genel Bakış
Record'ları primary_value üzerinden arar. JSONB query'den 7x daha hızlıdır.

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/records/search`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format

### Query Parameters
| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| object_id | string | Evet | Object ID |
| q | string | Evet | Arama terimi (min 1 karakter) |

### Örnek Requestler
```bash
GET /api/records/search?object_id=obj_contact&q=Ali
GET /api/records/search?object_id=obj_contact&q=example.com
GET /api/records/search?object_id=obj_company&q=Acme
```

## Response Format

### Response Schema (Array of RecordResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string | Record ID (rec_xxxxxxxx) |
| object_id | string | Object ID |
| data | object | JSONB field values (key: fld_xxx, value: any) |
| primary_value | string \| null | Primary display value (searched field) |
| created_at | string (datetime) | Oluşturulma zamanı |
| updated_at | string (datetime) | Son güncelleme zamanı |
| created_by | string | Oluşturan kullanıcı UUID (JSON'da string formatında) |
| updated_by | string | Güncelleyen kullanıcı UUID (JSON'da string formatında) |
| tenant_id | string | Tenant UUID (JSON'da string formatında) |

### Success Response (200 OK)
```json
[
  {
    "id": "rec_a1b2c3d4",
    "object_id": "obj_contact",
    "data": {
      "fld_name": "Ali Yılmaz",
      "fld_email": "ali@example.com"
    },
    "primary_value": "Ali Yılmaz",
    "created_by": "550e8400-e29b-41d4-a716-446655440000",
    "updated_by": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-01-18T10:00:00Z",
    "updated_at": "2026-01-18T10:00:00Z"
  }
]
```

**Limit:** Maksimum 50 sonuç döner

## Route Order (Critical)

⚠️ **IMPORTANT:** The `/search` route MUST be defined BEFORE `/{record_id}` in the router, otherwise FastAPI will match `/search` as `/{record_id}` with `record_id="search"`.

**Correct order in router:**
```python
# app/routers/records.py
@router.get("/search")       # Define FIRST
@router.get("/search/")      # Dual route support
@router.get("/{record_id}")  # Define AFTER (otherwise /search matches here!)
```

## Kod Akışı

**Service:** `app/services/record_service.py`
```python
async def search_records(
    self, db: AsyncSession, object_id: str, search_term: str
) -> list[Record]:
    """Primary value ile arama (hızlı)"""
    result = await db.execute(
        select(Record)
        .where(
            Record.object_id == object_id,
            Record.primary_value.ilike(f"%{search_term}%")
        )
        .limit(50)
    )
    return list(result.scalars().all())
```

**SQL:**
```sql
SELECT * FROM records
WHERE object_id = 'obj_contact'
  AND primary_value ILIKE '%Ali%'
ORDER BY created_at DESC
LIMIT 50;
```

**Index Kullanımı:**
- `idx_records_object_id`: Object filtreleme
- `idx_records_primary_value`: Text arama

## Performance

**Primary Value vs JSONB Search:**
| Method | Query Time | Index |
|--------|-----------|-------|
| primary_value ILIKE | ~10ms | B-tree |
| JSONB contains | ~70ms | GIN |

**Neden Daha Hızlı?**
- primary_value TEXT column (indexed)
- JSONB parse yok
- Basit ILIKE query

## Kullanım Örnekleri

### cURL
```bash
curl -X GET "http://localhost:8000/api/records/search?object_id=obj_contact&q=Ali" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Python (httpx)
```python
response = httpx.get(
    "http://localhost:8000/api/records/search",
    params={"object_id": "obj_contact", "q": "Ali"},
    headers={"Authorization": f"Bearer {token}"}
)

results = response.json()
print(f"Found {len(results)} results")
for record in results:
    print(f"- {record['primary_value']}")
```

### JavaScript (fetch)
```javascript
const response = await fetch(
  `http://localhost:8000/api/records/search?object_id=obj_contact&q=Ali`,
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);

const results = await response.json();
console.log(`Found ${results.length} results`);
```

## Advanced Search (TODO)

Şu anda sadece primary_value araması yapılıyor. Gelecekte:

**JSONB Full-Text Search:**
```sql
-- PostgreSQL full-text search (GIN index)
SELECT * FROM records
WHERE object_id = 'obj_contact'
  AND to_tsvector('english', data::text) @@ to_tsquery('Ali & Yılmaz');
```

**Multi-Field Search:**
```python
# Birden fazla field'da arama
await search_records(
    object_id="obj_contact",
    fields=["fld_name", "fld_email", "fld_company"],
    search_term="Ali"
)
```

## İlgili Endpoint'ler
- [GET /api/records](02-list-records.md)
- [POST /api/records](01-create-record.md)
