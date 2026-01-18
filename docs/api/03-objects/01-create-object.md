# POST /api/objects

## Genel Bakış
Yeni bir object (veri tablosu) oluşturur. Object'ler Contact, Company, Opportunity gibi veri tiplerini temsil eder.

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/objects`
- **Authentication:** JWT Token gerekli
- **Response Status:** 201 Created

## Request Format

### Request Body (JSON)
```json
{
  "name": "contact",
  "label": "Contact",
  "plural_name": "Contacts",
  "description": "Customer contacts",
  "icon": "👤",
  "views": {
    "forms": [],
    "tables": [],
    "kanbans": [],
    "calendars": []
  },
  "permissions": {
    "create": ["all"],
    "read": ["all"],
    "update": ["all"],
    "delete": ["all"]
  }
}
```

### Request Schema (ObjectCreate)
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| name | string | Evet | Object adı (snake_case, 1-255 karakter) |
| label | string | Evet | Görünen ad (1-255 karakter) |
| plural_name | string | Evet | Çoğul isim (1-255 karakter) |
| description | string | Hayır | Object açıklaması |
| icon | string | Hayır | Icon (emoji veya class) |
| views | object | Hayır | View konfigürasyonları (default: boş) |
| permissions | object | Hayır | CRUD izinleri (default: all) |

## Response Format

### Response Schema (ObjectResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string | Otomatik oluşturulan object ID (obj_xxxxxxxx) |
| name | string | Object adı |
| label | string | Görünen ad |
| plural_name | string | Çoğul isim |
| description | string \| null | Object açıklaması |
| icon | string \| null | Icon (emoji veya class) |
| is_custom | boolean | Custom object mi? |
| is_global | boolean | Global object mi? |
| views | object | View konfigürasyonları |
| permissions | object | CRUD izinleri |
| created_by | string | Oluşturan kullanıcı UUID (JSON'da string formatında) |
| created_at | string (datetime) | Oluşturulma zamanı |
| updated_at | string (datetime) | Son güncelleme zamanı |

### Success Response (201 Created)
```json
{
  "id": "obj_a1b2c3d4",
  "name": "contact",
  "label": "Contact",
  "plural_name": "Contacts",
  "description": "Customer contacts",
  "icon": "👤",
  "is_custom": true,
  "is_global": false,
  "views": {
    "forms": [],
    "tables": [],
    "kanbans": [],
    "calendars": []
  },
  "permissions": {
    "create": ["all"],
    "read": ["all"],
    "update": ["all"],
    "delete": ["all"]
  },
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T10:00:00Z"
}
```

## Kod Akışı

### Router → Service → Database
**Router:** `app/routers/objects.py`
```python
@router.post("/", response_model=ObjectResponse, status_code=201)
async def create_object(
    object_in: ObjectCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    obj = await object_service.create_object(db, object_in, user_id)
    return obj
```

**Service:** `app/services/object_service.py`
```python
async def create_object(
    self, db: AsyncSession, object_in: ObjectCreate, user_id: uuid.UUID
) -> Object:
    object_data = object_in.model_dump()
    object_data["id"] = f"obj_{uuid.uuid4().hex[:8]}"
    object_data["created_by"] = user_id
    object_data["is_custom"] = True
    object_data["is_global"] = False
    return await self.create(db, object_data)
```

**SQL:**
```sql
INSERT INTO objects (id, name, label, plural_name, description, icon, 
                     is_custom, is_global, views, permissions, created_by)
VALUES ('obj_a1b2c3d4', 'contact', 'Contact', 'Contacts', 
        'Customer contacts', '👤', true, false, 
        '{}'::jsonb, '{"create":["all"],...}'::jsonb, 
        '550e8400-e29b-41d4-a716-446655440000')
RETURNING *;
```

## Kullanım Örnekleri

### cURL
```bash
curl -X POST http://localhost:8000/api/objects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "contact",
    "label": "Contact",
    "plural_name": "Contacts",
    "description": "Customer contacts",
    "icon": "👤"
  }'
```

### Python (httpx)
```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/objects",
    json={
        "name": "contact",
        "label": "Contact",
        "plural_name": "Contacts",
        "description": "Customer contacts",
        "icon": "👤"
    },
    headers={"Authorization": f"Bearer {token}"}
)
```

## İlgili Endpoint'ler
- [GET /api/objects](02-list-objects.md)
- [POST /api/object-fields](../07-object-fields/01-create-object-field.md) - Field'ları object'e ekle
