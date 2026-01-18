# GET /api/objects

## Genel Bakış
Kullanıcının oluşturduğu tüm object'leri listeler.

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/objects`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format
Query parametresi yok. Kullanıcının tüm object'leri döner.

## Response Format
```json
[
  {
    "id": "obj_contact",
    "name": "contact",
    "label": "Contact",
    "plural_name": "Contacts",
    "description": "Customer contacts",
    "icon": "👤",
    "is_custom": true,
    "is_global": false,
    "views": {},
    "permissions": {},
    "created_by": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-01-18T10:00:00Z",
    "updated_at": "2026-01-18T10:00:00Z"
  }
]
```

## Kod Akışı
**Service:** `app/services/object_service.py`
```python
async def get_user_objects(self, db: AsyncSession, user_id: uuid.UUID) -> list[Object]:
    result = await db.execute(
        select(Object).where(Object.created_by == user_id)
    )
    return list(result.scalars().all())
```

**SQL:**
```sql
SELECT * FROM objects WHERE created_by = '550e8400-e29b-41d4-a716-446655440000';
```

## Kullanım Örnekleri
```bash
curl -X GET http://localhost:8000/api/objects \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## İlgili Endpoint'ler
- [POST /api/objects](01-create-object.md)
- [GET /api/objects/{object_id}](03-get-object.md)
