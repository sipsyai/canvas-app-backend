# GET /api/records/{record_id}

## Genel Bakış
Belirtilen ID'ye sahip record'ı getirir.

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/records/{record_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format
### Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| record_id | string | Record ID (örn: rec_a1b2c3d4) |

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

### Success Response (200 OK)
```json
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
```

### Error Responses
**404 Not Found:**
```json
{
  "detail": "Record not found"
}
```

## Kullanım Örnekleri
```bash
curl -X GET http://localhost:8000/api/records/rec_a1b2c3d4 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## İlgili Endpoint'ler
- [PATCH /api/records/{record_id}](04-update-record.md)
- [DELETE /api/records/{record_id}](05-delete-record.md)
