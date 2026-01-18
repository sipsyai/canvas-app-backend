# GET /api/object-fields/{object_field_id}

## Genel Bakış
Tek object-field bağlantısını getirir.

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/object-fields/{object_field_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Kullanım
```bash
curl http://localhost:8000/api/object-fields/ofd_a1b2c3d4 \
  -H "Authorization: Bearer TOKEN"
```

### Error Response
**404 Not Found:**
```json
{
  "detail": "ObjectField not found"
}
```
