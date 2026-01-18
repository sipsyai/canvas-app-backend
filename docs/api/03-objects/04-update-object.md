# PATCH /api/objects/{object_id}

## Genel Bakış
Mevcut object'ı günceller. Partial update desteklenir (sadece gönderilen field'lar değişir).

## Endpoint Bilgileri
- **Method:** PATCH
- **Path:** `/api/objects/{object_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format
### Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| object_id | string | Object ID |

### Request Body (Tüm field'lar opsiyonel)
```json
{
  "label": "Contact (Updated)",
  "description": "Updated description",
  "icon": "📞"
}
```

## Response Format

### Response Schema (ObjectResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string | Object ID |
| name | string | Object adı |
| label | string | Görünen ad |
| plural_name | string | Çoğul isim |
| description | string \| null | Object açıklaması |
| icon | string \| null | Icon |
| is_custom | boolean | Custom object mi? |
| is_global | boolean | Global object mi? |
| views | object | View konfigürasyonları |
| permissions | object | CRUD izinleri |
| created_by | string | Oluşturan kullanıcı UUID (JSON'da string formatında) |
| created_at | string (datetime) | Oluşturulma zamanı |
| updated_at | string (datetime) | Son güncelleme zamanı |

### Success Response (200 OK)
```json
{
  "id": "obj_contact",
  "name": "contact",
  "label": "Contact (Updated)",
  "plural_name": "Contacts",
  "description": "Updated description",
  "icon": "📞",
  "is_custom": true,
  "is_global": false,
  "views": {},
  "permissions": {},
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T11:30:00Z"
}
```

### Error Responses
**404 Not Found:**
```json
{
  "detail": "Object not found"
}
```

## Kod Akışı
**Service:** `app/services/object_service.py`
```python
async def update_object(
    self, db: AsyncSession, object_id: str, object_in: ObjectUpdate
) -> Object | None:
    update_data = object_in.model_dump(exclude_unset=True)
    return await self.update(db, object_id, update_data)
```

## Kullanım Örnekleri
```bash
curl -X PATCH http://localhost:8000/api/objects/obj_contact \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"label": "Contact (Updated)"}'
```

## İlgili Endpoint'ler
- [GET /api/objects/{object_id}](03-get-object.md)
- [DELETE /api/objects/{object_id}](05-delete-object.md)
