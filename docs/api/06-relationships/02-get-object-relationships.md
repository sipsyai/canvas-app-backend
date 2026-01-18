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

### Response Schema (Array of RelationshipResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string | Relationship ID (rel_xxxxxxxx) |
| name | string | Relationship name |
| from_object_id | string | Source object ID |
| to_object_id | string | Target object ID |
| type | string | "1:N" (One-to-Many) or "N:N" (Many-to-Many) |
| from_label | string \| null | Label shown on source object |
| to_label | string \| null | Label shown on target object |
| created_at | string (datetime) | Oluşturulma zamanı |
| created_by | string | Oluşturan kullanıcı UUID (JSON'da string formatında) |

### Success Response (200 OK)
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
    "created_at": "2026-01-18T10:00:00Z",
    "created_by": "550e8400-e29b-41d4-a716-446655440000"
  }
]
```

**Empty Response (No relationships found):**
```json
[]
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
