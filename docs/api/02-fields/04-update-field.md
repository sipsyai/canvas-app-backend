# PATCH /api/fields/{field_id}

## Genel Bakış
Mevcut bir field'ı günceller. Sadece gönderilen field'lar güncellenir (partial update). Sistem field'ları güncellenemez.

## Endpoint Bilgileri
- **Method:** PATCH
- **Path:** `/api/fields/{field_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format

### Path Parameters
| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| field_id | string | Evet | Field ID (örn: fld_a1b2c3d4) |

### Request Body (JSON) - Tüm field'lar opsiyonel
```json
{
  "label": "Email Address (Updated)",
  "description": "Updated description",
  "config": {
    "validation": {
      "required": false,
      "regex": "^[^@]+@[^@]+\\.[^@]+$"
    },
    "placeholder": "new@example.com"
  }
}
```

### Request Schema (FieldUpdate)
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| name | string | Hayır | Field adı (1-255 karakter) |
| label | string | Hayır | Görünen ad (1-255 karakter) |
| type | string | Hayır | Field tipi |
| description | string | Hayır | Field açıklaması |
| config | object | Hayır | Field konfigürasyonu |
| category | string | Hayır | Kategori |

**NOT:** Tüm field'lar opsiyoneldir. Sadece değiştirmek istediğiniz field'ları gönderin.

## Response Format

### Success Response (200 OK)
```json
{
  "id": "fld_a1b2c3d4",
  "name": "email",
  "label": "Email Address (Updated)",
  "type": "email",
  "description": "Updated description",
  "category": "Contact Info",
  "is_global": false,
  "is_system_field": false,
  "is_custom": true,
  "config": {
    "validation": {
      "required": false,
      "regex": "^[^@]+@[^@]+\\.[^@]+$"
    },
    "placeholder": "new@example.com"
  },
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T11:30:00Z"
}
```

### Error Responses

#### 404 Not Found - Field Bulunamadı
```json
{
  "detail": "Field not found"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

## Kod Akışı

### 1. Router Layer
**Dosya:** `app/routers/fields.py`

```python
@router.patch("/{field_id}", response_model=FieldResponse)
async def update_field(
    field_id: str,
    field_in: FieldUpdate,
    db: AsyncSession = Depends(get_db),
):
    field = await field_service.update_field(db, field_id, field_in)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field
```

### 2. Service Layer
**Dosya:** `app/services/field_service.py`

```python
async def update_field(
    self,
    db: AsyncSession,
    field_id: str,
    field_in: FieldUpdate,
) -> Field | None:
    update_data = field_in.model_dump(exclude_unset=True)
    return await self.update(db, field_id, update_data)
```

**Önemli:** `exclude_unset=True` sayesinde sadece gönderilen field'lar güncellenir.

### 3. Database Layer
```python
# BaseService.update()
async def update(self, db: AsyncSession, id: str, data: dict) -> ModelType | None:
    obj = await self.get_by_id(db, id)
    if not obj:
        return None

    for key, value in data.items():
        setattr(obj, key, value)

    await db.commit()
    await db.refresh(obj)
    return obj
```

### 4. SQL Query
```sql
-- 1. Field'ı bul
SELECT * FROM fields WHERE id = 'fld_a1b2c3d4';

-- 2. Güncelle
UPDATE fields
SET
  label = 'Email Address (Updated)',
  description = 'Updated description',
  config = '{"validation": {...}}'::jsonb,
  updated_at = NOW()
WHERE id = 'fld_a1b2c3d4'
RETURNING *;
```

## Kullanım Örnekleri

### cURL
```bash
# Sadece label güncelle
curl -X PATCH http://localhost:8000/api/fields/fld_a1b2c3d4 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "label": "Email Address (Updated)"
  }'

# Birden fazla field güncelle
curl -X PATCH http://localhost:8000/api/fields/fld_a1b2c3d4 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "label": "Email Address (Updated)",
    "description": "Updated description",
    "config": {
      "validation": {
        "required": false
      }
    }
  }'
```

### Python (httpx)
```python
import httpx

token = "YOUR_JWT_TOKEN"
field_id = "fld_a1b2c3d4"

response = httpx.patch(
    f"http://localhost:8000/api/fields/{field_id}",
    json={
        "label": "Email Address (Updated)",
        "description": "Updated description"
    },
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 200:
    field = response.json()
    print(f"Field updated: {field['label']}")
elif response.status_code == 404:
    print("Field not found")
```

### JavaScript (fetch)
```javascript
const token = "YOUR_JWT_TOKEN";
const fieldId = "fld_a1b2c3d4";

const response = await fetch(`http://localhost:8000/api/fields/${fieldId}`, {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    label: 'Email Address (Updated)',
    description: 'Updated description'
  })
});

if (response.ok) {
  const field = await response.json();
  console.log('Field updated:', field.label);
}
```

## Partial Update Örnekleri

### Sadece Label Güncelle
```json
{
  "label": "New Label"
}
```
→ Sadece `label` ve `updated_at` değişir, diğer field'lar aynı kalır.

### Sadece Config Güncelle
```json
{
  "config": {
    "validation": {
      "required": false
    }
  }
}
```
→ **DİKKAT:** Config tamamen değiştirilir (merge edilmez), diğer field'lar aynı kalır.

### Config Merge İçin
```python
# Frontend'de mevcut config'i al, merge et, gönder
current_field = await get_field(field_id)
merged_config = {**current_field["config"], **new_config}

await update_field(field_id, {"config": merged_config})
```

## Güvenlik Notları

1. **Field Ownership:**
   - Şu anda ownership kontrolü yok
   - TODO: Sadece field sahibi güncelleyebilmeli

2. **System Field Protection:**
   - TODO: is_system_field=true olan field'lar güncellenemez olmalı

## İlgili Endpoint'ler

- [POST /api/fields](01-create-field.md) - Yeni field oluştur
- [GET /api/fields](02-list-fields.md) - Tüm field'ları listele
- [GET /api/fields/{field_id}](03-get-field.md) - Tek field getir
- [DELETE /api/fields/{field_id}](05-delete-field.md) - Field sil
