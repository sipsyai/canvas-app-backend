# POST /api/applications

## Genel Bakış
Yeni uygulama oluşturur (CRM, ITSM vb.).

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/applications`
- **Authentication:** JWT Token gerekli
- **Response Status:** 201 Created

## Request Format

### Request Schema (ApplicationCreate)
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| name | string | Evet | Application name (1-255 chars) |
| label | string | Hayır | Display label |
| description | string | Hayır | Application description |
| icon | string | Hayır | Icon (emoji or class name) |
| config | object | Hayır | Application configuration (default: {}) |

### Request Body Example
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

### Response Schema (ApplicationResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string | Application ID (app_xxxxxxxx) |
| name | string | Application name |
| label | string \| null | Application label (display name) |
| description | string \| null | Application description |
| icon | string \| null | Icon (emoji or class name) |
| config | object | Application configuration (JSONB) |
| created_at | string (datetime) | Oluşturulma zamanı |
| updated_at | string (datetime) | Son güncelleme zamanı |
| created_by | string | Oluşturan kullanıcı UUID (JSON'da string formatında) |
| published_at | string (datetime) \| null | Yayınlanma zamanı (null = draft) |

### Success Response (201 Created)
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
