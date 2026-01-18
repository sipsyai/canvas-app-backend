# GET /api/object-fields/{object_field_id}

## Genel Bakış
Tek object-field bağlantısını getirir.

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/object-fields/{object_field_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| object_field_id | string | Object-field ID (ofd_xxxxxxxx) |

## Response Format

### Response Schema (ObjectFieldResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string | Object-field ID (ofd_xxxxxxxx) |
| object_id | string | Object ID (obj_xxxxxxxx) |
| field_id | string | Field ID (fld_xxxxxxxx) |
| display_order | integer | Görüntüleme sırası (0+) |
| is_required | boolean | Zorunlu mu? |
| is_visible | boolean | Görünür mü? |
| is_readonly | boolean | Salt okunur mu? |
| field_overrides | object | Field-specific config overrides |
| created_at | string (datetime) | Oluşturulma zamanı |

### Success Response (200 OK)
```json
{
  "id": "ofd_a1b2c3d4",
  "object_id": "obj_contact",
  "field_id": "fld_email",
  "display_order": 0,
  "is_required": true,
  "is_visible": true,
  "is_readonly": false,
  "field_overrides": {},
  "created_at": "2026-01-18T10:00:00Z"
}
```

### Error Response
**404 Not Found:**
```json
{
  "detail": "ObjectField not found"
}
```

## Kullanım
```bash
curl http://localhost:8000/api/object-fields/ofd_a1b2c3d4 \
  -H "Authorization: Bearer TOKEN"
```
