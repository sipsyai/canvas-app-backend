# GET /api/fields/{field_id}

## Genel Bakış
Belirtilen ID'ye sahip field'ın detaylarını getirir. Hem global field'lar hem de kullanıcının custom field'ları için çalışır.

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/fields/{field_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format

### Path Parameters
| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| field_id | string | Evet | Field ID (örn: fld_a1b2c3d4) |

### Örnek Request
```bash
GET /api/fields/fld_a1b2c3d4
```

## Response Format

### Success Response (200 OK)
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

### Error Responses

#### 404 Not Found - Field Bulunamadı
```json
{
  "detail": "Field not found"
}
```

#### 401 Unauthorized - JWT Token Eksik/Geçersiz
```json
{
  "detail": "Not authenticated"
}
```

## Kod Akışı

### 1. Router Layer
**Dosya:** `app/routers/fields.py`

```python
@router.get("/{field_id}", response_model=FieldResponse)
async def get_field(
    field_id: str,
    db: AsyncSession = Depends(get_db),
):
    field = await field_service.get_by_id(db, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field
```

### 2. Service Layer
**Dosya:** `app/services/base.py` (BaseService)

```python
async def get_by_id(self, db: AsyncSession, id: str) -> ModelType | None:
    result = await db.execute(
        select(self.model).where(self.model.id == id)
    )
    return result.scalar_one_or_none()
```

### 3. Database Query
```sql
SELECT * FROM fields WHERE id = 'fld_a1b2c3d4';
```

## Kullanım Örnekleri

### cURL
```bash
curl -X GET http://localhost:8000/api/fields/fld_a1b2c3d4 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Python (httpx)
```python
import httpx

token = "YOUR_JWT_TOKEN"
field_id = "fld_a1b2c3d4"

response = httpx.get(
    f"http://localhost:8000/api/fields/{field_id}",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 200:
    field = response.json()
    print(f"Field: {field['label']} ({field['type']})")
elif response.status_code == 404:
    print("Field not found")
```

### JavaScript (fetch)
```javascript
const token = "YOUR_JWT_TOKEN";
const fieldId = "fld_a1b2c3d4";

const response = await fetch(`http://localhost:8000/api/fields/${fieldId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

if (response.ok) {
  const field = await response.json();
  console.log(`Field: ${field.label} (${field.type})`);
} else if (response.status === 404) {
  console.error('Field not found');
}
```

## İlgili Endpoint'ler

- [POST /api/fields](01-create-field.md) - Yeni field oluştur
- [GET /api/fields](02-list-fields.md) - Tüm field'ları listele
- [PATCH /api/fields/{field_id}](04-update-field.md) - Field güncelle
- [DELETE /api/fields/{field_id}](05-delete-field.md) - Field sil
