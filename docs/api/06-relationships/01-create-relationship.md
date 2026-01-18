# POST /api/relationships

## Genel Bakış
İki object arasında ilişki tanımlar.

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/relationships`
- **Authentication:** JWT Token gerekli
- **Response Status:** 201 Created

## Request Format
```json
{
  "name": "contact_opportunities",
  "from_object_id": "obj_contact",
  "to_object_id": "obj_opportunity",
  "type": "1:N",
  "from_label": "Opportunities",
  "to_label": "Contact"
}
```

### Request Schema
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| name | string | Evet | İlişki adı |
| from_object_id | string | Evet | Kaynak object |
| to_object_id | string | Evet | Hedef object |
| type | string | Evet | "1:N" veya "N:N" |
| from_label | string | Hayır | Kaynak taraftaki label |
| to_label | string | Hayır | Hedef taraftaki label |

## Response Format

### Response Schema (RelationshipResponse)
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

### Success Response (201 Created)
```json
{
  "id": "rel_a1b2c3d4",
  "name": "contact_opportunities",
  "from_object_id": "obj_contact",
  "to_object_id": "obj_opportunity",
  "type": "1:N",
  "from_label": "Opportunities",
  "to_label": "Contact",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z"
}
```

### Error Responses
**422 Unprocessable Entity (missing required field):**
```json
{
  "detail": [{
    "type": "missing",
    "loc": ["body", "name"],
    "msg": "Field required"
  }]
}
```

**422 Unprocessable Entity (invalid type):**
```json
{
  "detail": [{
    "type": "string_pattern_mismatch",
    "loc": ["body", "type"],
    "msg": "String should match pattern '^(1:N|N:N)$'"
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
**Service:** `app/services/relationship_service.py`
```python
async def create_relationship(
    self, db: AsyncSession, relationship_in: RelationshipCreate, user_id: uuid.UUID
) -> Relationship:
    relationship_data = relationship_in.model_dump()
    relationship_data["id"] = f"rel_{uuid.uuid4().hex[:8]}"
    relationship_data["created_by"] = user_id
    return await self.create(db, relationship_data)
```

## Kullanım
```bash
curl -X POST http://localhost:8000/api/relationships \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "name": "contact_opportunities",
    "from_object_id": "obj_contact",
    "to_object_id": "obj_opportunity",
    "type": "1:N"
  }'
```

## İlgili Endpoint'ler
- [POST /api/relationship-records](../08-relationship-records/01-create-relationship-record.md) - Record'ları bağla
