# POST /api/fields

## Genel Bakış
Yeni bir custom field oluşturur. Field'lar veri alanlarını temsil eder (email, telefon, text vb.). Oluşturulan field daha sonra object'lere attach edilebilir.

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/fields`
- **Authentication:** JWT Token gerekli
- **Response Status:** 201 Created

## Request Format

### Request Body (JSON)
```json
{
  "name": "email",
  "label": "Email Address",
  "type": "email",
  "description": "Contact email address",
  "category": "Contact Info",
  "config": {
    "validation": {
      "required": true,
      "regex": "^[^@]+@[^@]+\\.[^@]+$"
    },
    "placeholder": "user@example.com"
  }
}
```

### Request Schema (FieldCreate)
| Alan | Tip | Zorunlu | Validasyon | Açıklama |
|------|-----|---------|------------|----------|
| name | string | Evet | 1-255 karakter | Field adı (snake_case) |
| label | string | Evet | 1-255 karakter | Görünen ad |
| type | string | Evet | - | Field tipi (text, email, number, date vb.) |
| description | string | Hayır | - | Field açıklaması |
| category | string | Hayır | - | Kategori (Contact Info, Business vb.) |
| config | object | Hayır | - | Field konfigürasyonu (validasyon, options vb.) |
| is_custom | boolean | Hayır | Default: true | Custom field mi? |

## Response Format

### Success Response (201 Created)
```json
{
  "id": "fld_a1b2c3d4",
  "name": "email",
  "label": "Email Address",
  "type": "email",
  "description": "Contact email address",
  "category": "Contact Info",
  "is_global": false,
  "is_system_field": false,
  "is_custom": true,
  "config": {
    "validation": {
      "required": true,
      "regex": "^[^@]+@[^@]+\\.[^@]+$"
    },
    "placeholder": "user@example.com"
  },
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T10:00:00Z"
}
```

### Response Schema (FieldResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string | Otomatik oluşturulan field ID (fld_xxxxxxxx) |
| name | string | Field adı |
| label | string | Görünen ad |
| type | string | Field tipi |
| description | string \| null | Field açıklaması |
| category | string \| null | Kategori |
| is_global | boolean | Global field mi? (tüm kullanıcılar için) |
| is_system_field | boolean | Sistem field'ı mı? (created_at, owner vb.) |
| is_custom | boolean | Custom field mi? |
| config | object | Field konfigürasyonu |
| created_by | string | Oluşturan kullanıcı UUID (JSON'da string formatında) |
| created_at | string (datetime) | Oluşturulma zamanı |
| updated_at | string (datetime) | Son güncelleme zamanı |

### Error Responses

#### 401 Unauthorized - JWT Token Eksik/Geçersiz
```json
{
  "detail": "Not authenticated"
}
```

#### 422 Unprocessable Entity - Validation Error
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

## Kod Akışı

### 1. Router Layer
**Dosya:** `app/routers/fields.py`

```python
@router.post("/", response_model=FieldResponse, status_code=201)
async def create_field(
    field_in: FieldCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    field = await field_service.create_field(db, field_in, user_id)
    return field
```

**Görevleri:**
- Request body'yi `FieldCreate` Pydantic schema ile validate eder
- JWT token'dan user_id'yi çıkarır (get_current_user_id middleware)
- Database session'ı dependency injection ile alır
- Service layer'ı çağırır
- Response'u `FieldResponse` schema ile serialize eder

### 2. Service Layer
**Dosya:** `app/services/field_service.py`

```python
async def create_field(
    self,
    db: AsyncSession,
    field_in: FieldCreate,
    user_id: uuid.UUID,
) -> Field:
    """Create new field with auto-generated ID"""
    field_data = field_in.model_dump()
    field_data["id"] = f"fld_{uuid.uuid4().hex[:8]}"
    field_data["created_by"] = user_id
    return await self.create(db, field_data)
```

**Adımlar:**
1. Pydantic model'i dict'e çevirir (`model_dump()`)
2. Otomatik ID oluşturur: `fld_` prefix + 8 karakter hex
3. `created_by` field'ına user_id'yi atar
4. BaseService'in `create()` methodunu çağırır

### 3. Database Layer
**Dosya:** `app/services/base.py` (BaseService.create)

```python
async def create(self, db: AsyncSession, data: dict) -> ModelType:
    """Create new record"""
    obj = self.model(**data)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj
```

**SQL Query (SQLAlchemy tarafından oluşturulur):**
```sql
INSERT INTO fields (
  id, name, label, type, description, category,
  is_global, is_system_field, is_custom, config,
  created_by, created_at, updated_at
) VALUES (
  'fld_a1b2c3d4', 'email', 'Email Address', 'email',
  'Contact email address', 'Contact Info',
  false, false, true, '{"validation": {...}}'::jsonb,
  '550e8400-e29b-41d4-a716-446655440000', NOW(), NOW()
)
RETURNING *;
```

## Kullanım Örnekleri

### cURL
```bash
curl -X POST http://localhost:8000/api/fields \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "email",
    "label": "Email Address",
    "type": "email",
    "description": "Contact email address",
    "category": "Contact Info",
    "config": {
      "validation": {
        "required": true,
        "regex": "^[^@]+@[^@]+\\.[^@]+$"
      },
      "placeholder": "user@example.com"
    }
  }'
```

### Python (httpx)
```python
import httpx

# Login ve token alma (önce)
token = "YOUR_JWT_TOKEN"

response = httpx.post(
    "http://localhost:8000/api/fields",
    json={
        "name": "email",
        "label": "Email Address",
        "type": "email",
        "description": "Contact email address",
        "category": "Contact Info",
        "config": {
            "validation": {
                "required": True,
                "regex": "^[^@]+@[^@]+\\.[^@]+$"
            },
            "placeholder": "user@example.com"
        }
    },
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 201:
    field = response.json()
    print(f"Field created: {field['id']}")
else:
    print(f"Error: {response.json()['detail']}")
```

### JavaScript (fetch)
```javascript
const token = "YOUR_JWT_TOKEN";

const response = await fetch('http://localhost:8000/api/fields', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    name: 'email',
    label: 'Email Address',
    type: 'email',
    description: 'Contact email address',
    category: 'Contact Info',
    config: {
      validation: {
        required: true,
        regex: '^[^@]+@[^@]+\\.[^@]+$'
      },
      placeholder: 'user@example.com'
    }
  })
});

if (response.ok) {
  const field = await response.json();
  console.log('Field created:', field.id);
} else {
  const error = await response.json();
  console.error('Error:', error.detail);
}
```

## Field Tipleri

| Tip | Açıklama | Config Örneği |
|-----|----------|---------------|
| text | Tek satır metin | `{"maxLength": 255}` |
| textarea | Çok satır metin | `{"rows": 5}` |
| email | Email adresi | `{"regex": "email pattern"}` |
| phone | Telefon numarası | `{"format": "+90 5XX XXX XXXX"}` |
| number | Sayı | `{"min": 0, "max": 1000}` |
| currency | Para | `{"currency": "USD", "precision": 2}` |
| date | Tarih | `{"format": "YYYY-MM-DD"}` |
| datetime | Tarih+saat | `{"timezone": "UTC"}` |
| checkbox | Boolean | `{"default": false}` |
| select | Dropdown | `{"options": [{"value": "a", "label": "A"}]}` |
| multiselect | Çoklu seçim | `{"options": [...], "max": 5}` |
| lookup | İlişkili kayıt | `{"lookupObject": "obj_contact"}` |
| url | Web URL | `{"openInNewTab": true}` |

## Güvenlik Notları

1. **JWT Authentication:**
   - Endpoint JWT token gerektirir
   - Token'ın geçerliliği her request'te kontrol edilir
   - User ID token'dan çıkarılır (created_by için)

2. **Input Validation:**
   - Pydantic schema ile otomatik validasyon
   - name ve label boş olamaz (min 1 karakter)
   - type field'ı zorunludur

3. **User Isolation:**
   - created_by otomatik atanır (JWT'den)
   - Kullanıcı başka birinin field'ını oluşturamaz

## İlgili Endpoint'ler

- [GET /api/fields](02-list-fields.md) - Tüm field'ları listele
- [GET /api/fields/{field_id}](03-get-field.md) - Tek field getir
- [PATCH /api/fields/{field_id}](04-update-field.md) - Field güncelle
- [DELETE /api/fields/{field_id}](05-delete-field.md) - Field sil
- [POST /api/object-fields](../07-object-fields/01-create-object-field.md) - Field'ı object'e attach et
