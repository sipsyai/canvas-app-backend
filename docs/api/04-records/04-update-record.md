# PATCH /api/records/{record_id}

## Genel Bakış
Record'ı günceller. **JSONB data MERGE edilir** (replace edilmez). Sadece gönderilen field'lar değişir.

## Endpoint Bilgileri
- **Method:** PATCH
- **Path:** `/api/records/{record_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format

### Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| record_id | string | Record ID |

### Request Body
```json
{
  "data": {
    "fld_email": "newemail@example.com",
    "fld_phone": "+90 555 9876543"
  }
}
```

**DİKKAT:** Sadece gönderilen field'lar güncellenir, diğerleri korunur!

## Response Format

### Response Schema (RecordResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string | Record ID (rec_xxxxxxxx) |
| object_id | string | Object ID |
| data | object | JSONB field values (MERGED with update data) |
| primary_value | string \| null | Primary display value (auto-updated if first field changes) |
| created_at | string (datetime) | Oluşturulma zamanı (değişmez) |
| updated_at | string (datetime) | Son güncelleme zamanı (otomatik güncellenir) |
| created_by | string | Oluşturan kullanıcı UUID (JSON'da string formatında) |
| updated_by | string | Güncelleyen kullanıcı UUID (JSON'da string formatında) |
| tenant_id | string | Tenant UUID (JSON'da string formatında) |

### Success Response (200 OK)
```json
{
  "id": "rec_a1b2c3d4",
  "object_id": "obj_contact",
  "data": {
    "fld_name": "Ali Yılmaz",              // Değişmedi (gönderilmedi)
    "fld_email": "newemail@example.com",   // Güncellendi
    "fld_phone": "+90 555 9876543",        // Güncellendi
    "fld_company": "Acme Corp"             // Değişmedi (gönderilmedi)
  },
  "primary_value": "Ali Yılmaz",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "updated_by": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T11:30:00Z"
}
```

## JSONB Merge Davranışı

**Service:** `app/services/record_service.py`
```python
async def update_record(
    self, db: AsyncSession, record_id: str, record_in: RecordUpdate, user_id: uuid.UUID
) -> Record | None:
    record = await self.get_by_id(db, record_id)
    if not record:
        return None

    # MERGE data (don't replace!)
    if record_in.data:
        record.data = {**record.data, **record_in.data}

    # Update primary_value
    record.primary_value = self._extract_primary_value(record.data)
    record.updated_by = user_id

    await db.commit()
    await db.refresh(record)
    return record
```

**Python Merge:**
```python
# Mevcut data
current_data = {
    "fld_name": "Ali Yılmaz",
    "fld_email": "old@example.com",
    "fld_company": "Acme Corp"
}

# Güncelleme data
update_data = {
    "fld_email": "new@example.com",
    "fld_phone": "+90 555 1234567"
}

# Merge sonucu
merged_data = {**current_data, **update_data}
# Sonuç:
# {
#   "fld_name": "Ali Yılmaz",       // Korundu
#   "fld_email": "new@example.com", // Güncellendi
#   "fld_company": "Acme Corp",     // Korundu
#   "fld_phone": "+90 555 1234567"  // Eklendi
# }
```

## Kullanım Örnekleri

### cURL
```bash
curl -X PATCH http://localhost:8000/api/records/rec_a1b2c3d4 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "data": {
      "fld_email": "newemail@example.com"
    }
  }'
```

### Python (httpx)
```python
response = httpx.patch(
    f"http://localhost:8000/api/records/{record_id}",
    json={
        "data": {
            "fld_email": "newemail@example.com",
            "fld_phone": "+90 555 9876543"
        }
    },
    headers={"Authorization": f"Bearer {token}"}
)
```

## Field Silme

Bir field'ı silmek için `null` gönderin:
```json
{
  "data": {
    "fld_phone": null
  }
}
```

**Sonuç:**
```json
{
  "data": {
    "fld_name": "Ali Yılmaz",
    "fld_email": "ali@example.com",
    "fld_phone": null           // Null olarak ayarlandı
  }
}
```

**Tamamen kaldırmak için PostgreSQL JSONB operatörü gerekir** (şu anda desteklenmiyor).

## İlgili Endpoint'ler
- [GET /api/records/{record_id}](03-get-record.md)
- [DELETE /api/records/{record_id}](05-delete-record.md)
