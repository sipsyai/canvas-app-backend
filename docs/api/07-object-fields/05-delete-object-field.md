# DELETE /api/object-fields/{object_field_id}

## Genel Bakış
Field'ı object'ten kaldırır (bağlantıyı siler). Field kendisi silinmez, sadece object-field bağlantısı silinir.

## Endpoint Bilgileri
- **Method:** DELETE
- **Path:** `/api/object-fields/{object_field_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 204 No Content

## NOT
Field silinmez, sadece object'ten kaldırılır. Field hala field'lar tablosunda kalır ve başka object'lerde kullanılabilir.

## Kullanım
```bash
curl -X DELETE http://localhost:8000/api/object-fields/ofd_a1b2c3d4 \
  -H "Authorization: Bearer TOKEN"
```

### Error Response
**404 Not Found:**
```json
{
  "detail": "ObjectField not found"
}
```
