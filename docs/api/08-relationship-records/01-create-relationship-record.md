# POST /api/relationship-records

## Genel Bakış
İki record'ı tanımlı bir relationship üzerinden bağlar.

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/relationship-records`
- **Authentication:** JWT Token gerekli
- **Response Status:** 201 Created

## Request Format
```json
{
  "relationship_id": "rel_contact_opportunity",
  "from_record_id": "rec_ali",
  "to_record_id": "rec_bigdeal",
  "relationship_metadata": {
    "role": "Decision Maker",
    "influence_level": "High"
  }
}
```

### Request Schema
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| relationship_id | string | Evet | Relationship ID |
| from_record_id | string | Evet | Kaynak record ID |
| to_record_id | string | Evet | Hedef record ID |
| relationship_metadata | object | Hayır | İlişki metadata (role, notes vb.) |

## Response Format

### Response Schema (RelationshipRecordResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string | Link ID (lnk_xxxxxxxx) |
| relationship_id | string | Relationship ID (rel_xxxxxxxx) |
| from_record_id | string | Source record ID (rec_xxxxxxxx) |
| to_record_id | string | Target record ID (rec_xxxxxxxx) |
| relationship_metadata | object | İlişkiye özel metadata (role, notes vb.) |
| created_at | string (datetime) | Oluşturulma zamanı |
| created_by | string | Oluşturan kullanıcı UUID |

### Success Response (201 Created)
```json
{
  "id": "lnk_a1b2c3d4",
  "relationship_id": "rel_contact_opportunity",
  "from_record_id": "rec_ali",
  "to_record_id": "rec_bigdeal",
  "relationship_metadata": {
    "role": "Decision Maker",
    "influence_level": "High"
  },
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
    "loc": ["body", "relationship_id"],
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
**Service:** `app/services/relationship_record_service.py`
```python
async def create_link(
    self, db: AsyncSession, link_in: RelationshipRecordCreate, user_id: uuid.UUID
) -> RelationshipRecord:
    link_data = link_in.model_dump()
    link_data["id"] = f"lnk_{uuid.uuid4().hex[:8]}"
    link_data["created_by"] = user_id
    return await self.create(db, link_data)
```

**SQL:**
```sql
INSERT INTO relationship_records (id, relationship_id, from_record_id, to_record_id, relationship_metadata, created_by)
VALUES (
  'lnk_a1b2c3d4',
  'rel_contact_opportunity',
  'rec_ali',
  'rec_bigdeal',
  '{"role": "Decision Maker"}'::jsonb,
  '550e8400-e29b-41d4-a716-446655440000'
)
RETURNING *;
```

## Kullanım
```bash
curl -X POST http://localhost:8000/api/relationship-records \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "relationship_id": "rel_contact_opportunity",
    "from_record_id": "rec_ali",
    "to_record_id": "rec_bigdeal",
    "relationship_metadata": {"role": "Decision Maker"}
  }'
```

### Python
```python
response = httpx.post(
    "http://localhost:8000/api/relationship-records",
    json={
        "relationship_id": "rel_contact_opportunity",
        "from_record_id": "rec_ali",
        "to_record_id": "rec_bigdeal",
        "relationship_metadata": {"role": "Decision Maker"}
    },
    headers={"Authorization": f"Bearer {token}"}
)
```

## İlgili Endpoint'ler
- [POST /api/relationships](../06-relationships/01-create-relationship.md) - İlişki tanımla
- [GET /api/relationship-records/records/{record_id}/related](02-get-related-records.md) - İlişkili record'ları getir
