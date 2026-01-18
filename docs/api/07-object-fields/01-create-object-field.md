# POST /api/object-fields

## Genel Bakış
Field'ı object'e bağlar (attach eder).

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/object-fields`
- **Authentication:** JWT Token gerekli
- **Response Status:** 201 Created

## Request Format
```json
{
  "object_id": "obj_contact",
  "field_id": "fld_email",
  "display_order": 0,
  "is_required": true,
  "is_visible": true,
  "is_readonly": false
}
```

### Request Schema
| Alan | Tip | Zorunlu | Default | Açıklama |
|------|-----|---------|---------|----------|
| object_id | string | Evet | - | Object ID |
| field_id | string | Evet | - | Field ID |
| display_order | integer | Hayır | 0 | Görüntüleme sırası |
| is_required | boolean | Hayır | false | Zorunlu mu? |
| is_visible | boolean | Hayır | true | Görünür mü? |
| is_readonly | boolean | Hayır | false | Salt okunur mu? |
| field_overrides | object | Hayır | {} | Field-specific config |

## Response Format

### Response Schema (ObjectFieldResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string | Object-field ID (ofd_xxxxxxxx) |
| object_id | string | Object ID (obj_xxxxxxxx) |
| field_id | string | Field ID (fld_xxxxxxxx) |
| display_order | integer | Görüntüleme sırası (0+) |
| is_required | boolean | Zorunlu mu? |
| is_visible | boolean | Görünür mü? |
| is_readonly | boolean | Salt okunur mu? |
| field_overrides | object | Field-specific config overrides |
| created_at | string (datetime) | Oluşturulma zamanı |

### Success Response (201 Created)
```json
{
  "id": "ofd_a1b2c3d4",
  "object_id": "obj_contact",
  "field_id": "fld_email",
  "display_order": 0,
  "is_required": true,
  "is_visible": true,
  "is_readonly": false,
  "field_overrides": {},
  "created_at": "2026-01-18T10:00:00Z"
}
```

### Error Responses

**422 Unprocessable Entity (missing required field):**
```json
{
  "detail": [{
    "type": "missing",
    "loc": ["body", "object_id"],
    "msg": "Field required"
  }]
}
```

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

## Kod Akışı
**Service:** `app/services/object_field_service.py`
```python
async def create_object_field(
    self, db: AsyncSession, object_field_in: ObjectFieldCreate, user_id: uuid.UUID
) -> ObjectField:
    object_field_data = object_field_in.model_dump()
    object_field_data["id"] = f"ofd_{uuid.uuid4().hex[:8]}"
    # Note: ObjectField model doesn't have created_by column (it's a mapping table)
    return await self.create(db, object_field_data)
```

## Kullanım
```bash
curl -X POST http://localhost:8000/api/object-fields \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "object_id": "obj_contact",
    "field_id": "fld_email",
    "is_required": true
  }'
```
