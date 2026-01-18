# GET /api/object-fields

## Genel Bakış
Bir object'e bağlı tüm field'ları listeler (display_order sırasına göre).

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/object-fields`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format
### Query Parameters
| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| object_id | string | Evet | Object ID |

## Response Format

### Response Schema (Array of ObjectFieldResponse)
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

### Success Response (200 OK)
```json
[
  {
    "id": "ofd_name",
    "object_id": "obj_contact",
    "field_id": "fld_name",
    "display_order": 0,
    "is_required": true,
    "is_visible": true,
    "is_readonly": false,
    "field_overrides": {},
    "created_at": "2026-01-18T10:00:00Z"
  },
  {
    "id": "ofd_email",
    "object_id": "obj_contact",
    "field_id": "fld_email",
    "display_order": 1,
    "is_required": true,
    "is_visible": true,
    "is_readonly": false,
    "field_overrides": {},
    "created_at": "2026-01-18T10:01:00Z"
  }
]
```

**Empty Response (No fields attached to object):**
```json
[]
```

## Kod Akışı
**Service:**
```python
async def get_fields_for_object(
    self, db: AsyncSession, object_id: str
) -> list[ObjectField]:
    result = await db.execute(
        select(ObjectField)
        .where(ObjectField.object_id == object_id)
        .order_by(ObjectField.display_order)
    )
    return list(result.scalars().all())
```

## Kullanım
```bash
curl "http://localhost:8000/api/object-fields?object_id=obj_contact" \
  -H "Authorization: Bearer TOKEN"
```
