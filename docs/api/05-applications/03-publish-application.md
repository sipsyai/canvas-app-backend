# POST /api/applications/{app_id}/publish

## Genel Bakış
Uygulamayı yayınlar (published_at timestamp atar).

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/applications/{app_id}/publish`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| app_id | string | Application ID (app_xxxxxxxx) |

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
| published_at | string (datetime) \| null | Yayınlanma zamanı (NOW() when published) |

### Success Response (200 OK)
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
