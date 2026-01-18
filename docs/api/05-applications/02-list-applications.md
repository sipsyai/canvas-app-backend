# GET /api/applications

## Genel Bakış
Tüm uygulamaları listeler.

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/applications`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format
Query parametreleri: skip, limit (pagination)

## Response Format
```json
[
  {
    "id": "app_crm",
    "name": "CRM",
    "label": "CRM",
    "published_at": "2026-01-18T12:00:00Z"
  }
]
```

## Kullanım
```bash
curl http://localhost:8000/api/applications \
  -H "Authorization: Bearer TOKEN"
```
