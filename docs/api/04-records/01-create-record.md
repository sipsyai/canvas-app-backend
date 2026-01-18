# POST /api/records

## Genel Bakış
Yeni record oluşturur. JSONB data field'ında dinamik field değerlerini saklar. Primary value otomatik oluşturulur.

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/records`
- **Authentication:** JWT Token gerekli
- **Response Status:** 201 Created

## Request Format

### Request Body (JSON)
```json
{
  "object_id": "obj_contact",
  "data": {
    "fld_name": "Ali Yılmaz",
    "fld_email": "ali@example.com",
    "fld_phone": "+90 555 1234567",
    "fld_company": "Acme Corp"
  }
}
```

### Request Schema (RecordCreate)
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| object_id | string | Evet | Object ID (örn: obj_contact) |
| data | object | Evet | Field değerleri (key: fld_xxx, value: any) |

## Response Format

### Response Schema (RecordResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string | Record ID (rec_xxxxxxxx) |
| object_id | string | Object ID |
| data | object | JSONB field values (key: fld_xxx, value: any) |
| primary_value | string \| null | Primary display value (first text field, max 255 chars) |
| created_at | string (datetime) | Oluşturulma zamanı |
| updated_at | string (datetime) | Son güncelleme zamanı |
| created_by | string | Oluşturan kullanıcı UUID (JSON'da string formatında) |
| updated_by | string | Güncelleyen kullanıcı UUID (JSON'da string formatında) |
| tenant_id | string | Tenant UUID (JSON'da string formatında) |

### Success Response (201 Created)
```json
{
  "id": "rec_a1b2c3d4",
  "object_id": "obj_contact",
  "data": {
    "fld_name": "Ali Yılmaz",
    "fld_email": "ali@example.com",
    "fld_phone": "+90 555 1234567",
    "fld_company": "Acme Corp"
  },
  "primary_value": "Ali Yılmaz",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "updated_by": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T10:00:00Z"
}
```

## Kod Akışı

**Service:** `app/services/record_service.py`
```python
async def create_record(
    self, db: AsyncSession, record_in: RecordCreate, user_id: uuid.UUID
) -> Record:
    # Primary value'yu çıkar (ilk text field)
    primary_value = self._extract_primary_value(record_in.data)
    
    record_data = {
        "id": f"rec_{uuid.uuid4().hex[:8]}",
        "object_id": record_in.object_id,
        "data": record_in.data,
        "primary_value": primary_value,
        "created_by": user_id,
        "updated_by": user_id,
        "tenant_id": str(user_id),
    }
    return await self.create(db, record_data)
```

**Primary Value Extraction:**
```python
def _extract_primary_value(self, data: dict[str, Any]) -> str | None:
    """İlk text-like field'ın değerini al"""
    for key, value in data.items():
        if isinstance(value, str) and value.strip():
            return value[:255]  # Max 255 karakter
    return None
```

**SQL:**
```sql
INSERT INTO records (id, object_id, data, primary_value, created_by, updated_by, tenant_id)
VALUES (
  'rec_a1b2c3d4',
  'obj_contact',
  '{"fld_name": "Ali Yılmaz", ...}'::jsonb,
  'Ali Yılmaz',
  '550e8400-e29b-41d4-a716-446655440000',
  '550e8400-e29b-41d4-a716-446655440000',
  '550e8400-e29b-41d4-a716-446655440000'
)
RETURNING *;
```

## Kullanım Örnekleri

### cURL
```bash
curl -X POST http://localhost:8000/api/records \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "object_id": "obj_contact",
    "data": {
      "fld_name": "Ali Yılmaz",
      "fld_email": "ali@example.com"
    }
  }'
```

### Python (httpx)
```python
response = httpx.post(
    "http://localhost:8000/api/records",
    json={
        "object_id": "obj_contact",
        "data": {
            "fld_name": "Ali Yılmaz",
            "fld_email": "ali@example.com",
            "fld_phone": "+90 555 1234567"
        }
    },
    headers={"Authorization": f"Bearer {token}"}
)
```

## Field Key Format
Data object'indeki key'ler `fld_<field_id>` formatında olmalıdır:
```json
{
  "fld_a1b2c3d4": "Ali Yılmaz",      // ✅ Doğru
  "name": "Ali Yılmaz"               // ❌ Yanlış
}
```

## İlgili Endpoint'ler
- [GET /api/records](02-list-records.md)
- [PATCH /api/records/{record_id}](04-update-record.md)
