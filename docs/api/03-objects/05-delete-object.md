# DELETE /api/objects/{object_id}

## Genel Bakış
Object'ı siler. CASCADE ile bağlı tüm object_fields ve records da silinir. **DİKKAT:** Bu işlem geri alınamaz!

## Endpoint Bilgileri
- **Method:** DELETE
- **Path:** `/api/objects/{object_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 204 No Content

## Request Format
### Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| object_id | string | Object ID |

## Response Format
**204 No Content** - Response body yok

### Error Responses
**404 Not Found:**
```json
{
  "detail": "Object not found"
}
```

## CASCADE Davranışı
Object silindiğinde şunlar da silinir:
1. **object_fields:** Object'e bağlı tüm field bağlantıları
2. **records:** Object'in tüm record'ları (JSONB data dahil)
3. **relationship_records:** İlişkili record bağlantıları

**SQL:**
```sql
DELETE FROM objects WHERE id = 'obj_contact';
-- CASCADE ile otomatik silinir:
-- - object_fields (field_id = 'obj_contact')
-- - records (object_id = 'obj_contact')
```

## Kullanım Örnekleri
```bash
curl -X DELETE http://localhost:8000/api/objects/obj_contact \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Python (httpx)
```python
response = httpx.delete(
    f"http://localhost:8000/api/objects/{object_id}",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 204:
    print("Object deleted successfully")
```

## Güvenlik Uyarıları
1. **Frontend'de confirmation gösterin!**
2. Silinen data geri alınamaz
3. Tüm record'lar ve ilişkiler kaybolur
4. Soft delete alternatifi düşünülebilir (is_deleted flag)

## İlgili Endpoint'ler
- [GET /api/objects](02-list-objects.md)
- [POST /api/objects](01-create-object.md)
