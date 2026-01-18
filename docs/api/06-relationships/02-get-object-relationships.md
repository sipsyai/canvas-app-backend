# GET /api/relationships/objects/{object_id}

## Genel Bakış
Bir object'in tüm ilişkilerini getirir (kaynak veya hedef olarak).

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/relationships/objects/{object_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format
### Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| object_id | string | Object ID |

## Response Format
```json
[
  {
    "id": "rel_contact_opportunities",
    "name": "contact_opportunities",
    "from_object_id": "obj_contact",
    "to_object_id": "obj_opportunity",
    "type": "1:N",
    "from_label": "Opportunities",
    "to_label": "Contact",
    "created_at": "2026-01-18T10:00:00Z"
  }
]
```

## Kod Akışı
**Service:**
```python
async def get_relationships_for_object(
    self, db: AsyncSession, object_id: str
) -> list[Relationship]:
    result = await db.execute(
        select(Relationship).where(
            (Relationship.from_object_id == object_id) |
            (Relationship.to_object_id == object_id)
        )
    )
    return list(result.scalars().all())
```

## Kullanım
```bash
curl http://localhost:8000/api/relationships/objects/obj_contact \
  -H "Authorization: Bearer TOKEN"
```
