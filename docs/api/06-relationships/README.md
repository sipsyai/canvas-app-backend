# Relationship API Endpoints

Relationship API, object'ler arası ilişkileri tanımlar (Contact → Opportunities).

## Endpoints

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| POST | `/api/relationships` | İlişki tanımla | ✅ JWT |
| GET | `/api/relationships/objects/{object_id}` | Object ilişkilerini getir | ✅ JWT |
| DELETE | `/api/relationships/{relationship_id}` | İlişki tanımını sil | ✅ JWT |

## Relationship Tipleri
- **1:N** - One-to-Many (Contact → Opportunities)
- **N:N** - Many-to-Many (Products ↔ Orders)

## Örnek Relationship
```json
{
  "id": "rel_a1b2c3d4",
  "name": "contact_opportunities",
  "from_object_id": "obj_contact",
  "to_object_id": "obj_opportunity",
  "type": "1:N",
  "from_label": "Opportunities",
  "to_label": "Contact"
}
```
