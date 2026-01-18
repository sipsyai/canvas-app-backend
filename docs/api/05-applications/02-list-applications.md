# GET /api/applications

## Genel Bakış
Tüm uygulamaları listeler.

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/applications`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format

### Query Parameters
| Parametre | Tip | Zorunlu | Varsayılan | Açıklama |
|-----------|-----|---------|------------|----------|
| skip | integer | Hayır | 0 | Number of records to skip (pagination) |
| limit | integer | Hayır | 100 | Max records to return |

### Örnek Requestler
```bash
GET /api/applications
GET /api/applications?skip=0&limit=10
GET /api/applications?skip=10&limit=10
```

## Response Format

### Response Schema (Array of ApplicationResponse)
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

### Success Response (200 OK)
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
