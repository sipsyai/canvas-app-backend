# GET /api/objects/{object_id}

## Genel Bakış
Belirtilen ID'ye sahip object'ın detaylarını getirir.

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/objects/{object_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format
### Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| object_id | string | Object ID (örn: obj_contact) |

## Response Format
```json
{
  "id": "obj_contact",
  "name": "contact",
  "label": "Contact",
  "plural_name": "Contacts",
  "description": "Customer contacts",
  "icon": "👤",
  "is_custom": true,
  "is_global": false,
  "views": {},
  "permissions": {},
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T10:00:00Z"
}
```

### Error Responses
**404 Not Found:**
```json
{
  "detail": "Object not found"
}
```

## Kullanım Örnekleri
```bash
curl -X GET http://localhost:8000/api/objects/obj_contact \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## İlgili Endpoint'ler
- [PATCH /api/objects/{object_id}](04-update-object.md)
- [DELETE /api/objects/{object_id}](05-delete-object.md)
