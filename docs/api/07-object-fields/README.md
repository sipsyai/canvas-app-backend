# Object-Field API Endpoints

Object-Field API, field'ları object'lere bağlar ve görüntüleme ayarlarını yönetir.

## Endpoints

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| POST | `/api/object-fields` | Field'ı object'e ekle | ✅ JWT |
| GET | `/api/object-fields?object_id=...` | Object field'larını listele | ✅ JWT |
| GET | `/api/object-fields/{object_field_id}` | Tek object-field getir | ✅ JWT |
| PATCH | `/api/object-fields/{object_field_id}` | Object-field güncelle | ✅ JWT |
| DELETE | `/api/object-fields/{object_field_id}` | Field'ı object'ten kaldır | ✅ JWT |

## Örnek Object-Field
```json
{
  "id": "ofd_a1b2c3d4",
  "object_id": "obj_contact",
  "field_id": "fld_email",
  "display_order": 0,
  "is_required": true,
  "is_visible": true,
  "is_readonly": false,
  "field_overrides": {}
}
```
