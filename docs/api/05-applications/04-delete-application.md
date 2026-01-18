# DELETE /api/applications/{app_id}

## Genel Bakış
Uygulamayı siler.

## Endpoint Bilgileri
- **Method:** DELETE
- **Path:** `/api/applications/{app_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 204 No Content

## Kullanım
```bash
curl -X DELETE http://localhost:8000/api/applications/app_crm \
  -H "Authorization: Bearer TOKEN"
```
