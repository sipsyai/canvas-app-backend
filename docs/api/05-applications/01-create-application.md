# POST /api/applications

## Genel Bakış
Yeni uygulama oluşturur (CRM, ITSM vb.).

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/applications`
- **Authentication:** JWT Token gerekli
- **Response Status:** 201 Created

## Request Format
```json
{
  "name": "CRM",
  "label": "Customer Relationship Management",
  "description": "Manage customers",
  "icon": "🤝",
  "config": {
    "objects": ["obj_contact", "obj_company"]
  }
}
```

## Response Format
```json
{
  "id": "app_a1b2c3d4",
  "name": "CRM",
  "label": "Customer Relationship Management",
  "description": "Manage customers",
  "icon": "🤝",
  "config": {"objects": ["obj_contact", "obj_company"]},
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "published_at": null,
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T10:00:00Z"
}
```

## Kullanım
```bash
curl -X POST http://localhost:8000/api/applications \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name": "CRM", "label": "CRM App"}'
```
