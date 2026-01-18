# DELETE /api/fields/{field_id}

## Genel Bakış
Field'ı siler. Field'a bağlı tüm object_field bağlantıları ve record data'ları da CASCADE ile silinir. Sistem field'ları silinemez.

## Endpoint Bilgileri
- **Method:** DELETE
- **Path:** `/api/fields/{field_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 204 No Content

## Request Format

### Path Parameters
| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| field_id | string | Evet | Field ID (örn: fld_a1b2c3d4) |

### Örnek Request
```bash
DELETE /api/fields/fld_a1b2c3d4
```

## Response Format

### Success Response (204 No Content)
Response body yok. Başarılı silme işleminde sadece 204 status code döner.

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
@router.delete("/{field_id}", status_code=204)
async def delete_field(
    field_id: str,
    db: AsyncSession = Depends(get_db),
):
    deleted = await field_service.delete(db, field_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Field not found")
    return None
```

### 2. Service Layer
**Dosya:** `app/services/base.py` (BaseService)

```python
async def delete(self, db: AsyncSession, id: str) -> bool:
    obj = await self.get_by_id(db, id)
    if not obj:
        return False

    await db.delete(obj)
    await db.commit()
    return True
```

### 3. Database Query
```sql
-- 1. Field'ı bul
SELECT * FROM fields WHERE id = 'fld_a1b2c3d4';

-- 2. Field'ı sil (CASCADE ile bağlı kayıtlar da silinir)
DELETE FROM fields WHERE id = 'fld_a1b2c3d4';
```

## CASCADE Davranışı

Field silindiğinde **CASCADE** ile şunlar da silinir:

### 1. ObjectField Bağlantıları
```sql
-- object_fields tablosundaki bağlantılar silinir
DELETE FROM object_fields WHERE field_id = 'fld_a1b2c3d4';
```

### 2. Record JSONB Data
```sql
-- UYARI: Record data JSONB içinde, otomatik silinmez!
-- Manuel cleanup gerekebilir:
UPDATE records
SET data = data - 'fld_a1b2c3d4'
WHERE data ? 'fld_a1b2c3d4';
```

**NOT:** Şu anda record JSONB data'sı otomatik temizlenmiyor. Production'da background job ile cleanup yapılmalı.

## Kullanım Örnekleri

### cURL
```bash
curl -X DELETE http://localhost:8000/api/fields/fld_a1b2c3d4 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Python (httpx)
```python
import httpx

token = "YOUR_JWT_TOKEN"
field_id = "fld_a1b2c3d4"

response = httpx.delete(
    f"http://localhost:8000/api/fields/{field_id}",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 204:
    print("Field deleted successfully")
elif response.status_code == 404:
    print("Field not found")
```

### JavaScript (fetch)
```javascript
const token = "YOUR_JWT_TOKEN";
const fieldId = "fld_a1b2c3d4";

const response = await fetch(`http://localhost:8000/api/fields/${fieldId}`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

if (response.status === 204) {
  console.log('Field deleted successfully');
} else if (response.status === 404) {
  console.error('Field not found');
}
```

## Güvenlik Notları

1. **Ownership Kontrolü:**
   - TODO: Sadece field sahibi silebilmeli
   - Şu anda herhangi bir JWT'li kullanıcı silebilir

2. **System Field Protection:**
   - TODO: is_system_field=true olan field'lar silinemez olmalı
   - Sistem field'larını silmek uygulamayı bozabilir

3. **Confirmation:**
   - Frontend'de deletion confirmation gösterin
   - CASCADE davranışını kullanıcıya bildirin

## Best Practices

### 1. Silmeden Önce Kontrol
```python
# Field'ın kaç object'te kullanıldığını kontrol et
object_field_count = await db.execute(
    select(func.count()).select_from(ObjectField)
    .where(ObjectField.field_id == field_id)
)
count = object_field_count.scalar_one()

if count > 0:
    # Kullanıcıya uyarı göster
    print(f"Warning: Field is used in {count} objects")
```

### 2. Soft Delete Alternatifi
```python
# Hard delete yerine soft delete kullan
field.is_deleted = True
field.deleted_at = datetime.now(UTC)
await db.commit()
```

### 3. Record Data Cleanup
```python
# Background job ile record data temizliği
async def cleanup_deleted_field_data(field_id: str):
    await db.execute(
        update(Record)
        .values(data=func.jsonb_remove(Record.data, field_id))
        .where(Record.data.has_key(field_id))
    )
```

## Silme Etkisi

### Örnek Senaryo
Field: `fld_email` (Email Address)
- 3 object'te kullanılıyor (Contact, Company, Lead)
- 150 record'da data var

**Silme Sonrası:**
1. `object_fields` tablosundan 3 kayıt silinir
2. `fields` tablosundan 1 kayıt silinir
3. `records` tablosundaki JSONB data'da `fld_email` key'i kalır (manuel cleanup gerekir)

**Önerilen Cleanup:**
```sql
UPDATE records
SET data = data - 'fld_email'
WHERE data ? 'fld_email';
```

## İlgili Endpoint'ler

- [POST /api/fields](01-create-field.md) - Yeni field oluştur
- [GET /api/fields](02-list-fields.md) - Tüm field'ları listele
- [GET /api/fields/{field_id}](03-get-field.md) - Tek field getir
- [PATCH /api/fields/{field_id}](04-update-field.md) - Field güncelle
- [GET /api/object-fields?object_id=...](../07-object-fields/02-list-object-fields.md) - Field kullanımını kontrol et
