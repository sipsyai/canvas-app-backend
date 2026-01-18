# DELETE /api/applications/{app_id}

## Genel Bakış
Uygulamayı siler.

## Endpoint Bilgileri
- **Method:** DELETE
- **Path:** `/api/applications/{app_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 204 No Content

## Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| app_id | string | Application ID (app_xxxxxxxx) |

## Response Format

### Success Response (204 No Content)
Response body: Empty

### Error Responses
**404 Not Found:**
```json
{
  "detail": "Application not found"
}
```

## Kullanım
```bash
curl -X DELETE http://localhost:8000/api/applications/app_crm \
  -H "Authorization: Bearer TOKEN"
```
