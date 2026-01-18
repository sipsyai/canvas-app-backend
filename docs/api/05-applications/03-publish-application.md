# POST /api/applications/{app_id}/publish

## Genel Bakış
Uygulamayı yayınlar (published_at timestamp atar).

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/applications/{app_id}/publish`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Response Format
```json
{
  "id": "app_crm",
  "name": "CRM",
  "published_at": "2026-01-18T12:00:00Z"
}
```

## Kullanım
```bash
curl -X POST http://localhost:8000/api/applications/app_crm/publish \
  -H "Authorization: Bearer TOKEN"
```
