# Application API Endpoints

Application API, no-code uygulamaları (CRM, ITSM vb.) yönetir.

## Endpoints

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| POST | `/api/applications` | Yeni uygulama oluştur | ✅ JWT |
| GET | `/api/applications` | Uygulamaları listele | ✅ JWT |
| POST | `/api/applications/{app_id}/publish` | Uygulamayı yayınla | ✅ JWT |
| DELETE | `/api/applications/{app_id}` | Uygulamayı sil | ✅ JWT |

## Örnek Application
```json
{
  "id": "app_crm",
  "name": "CRM",
  "label": "Customer Relationship Management",
  "description": "Manage customers and opportunities",
  "icon": "🤝",
  "config": {
    "objects": ["obj_contact", "obj_company", "obj_opportunity"],
    "navigation": [...]
  },
  "published_at": "2026-01-18T12:00:00Z",
  "created_at": "2026-01-18T10:00:00Z"
}
```
