# DELETE /api/records/{record_id}

## Genel Bakış
Record'ı siler. İlişkili relationship_record bağlantıları da CASCADE ile silinir.

## Endpoint Bilgileri
- **Method:** DELETE
- **Path:** `/api/records/{record_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 204 No Content

## Request Format
### Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| record_id | string | Record ID |

## Response Format
**204 No Content** - Response body yok

### Error Responses
**404 Not Found:**
```json
{
  "detail": "Record not found"
}
```

## CASCADE Davranışı
Record silindiğinde şunlar da silinir:
1. **relationship_records:** Bu record'un ilişki bağlantıları
   ```sql
   DELETE FROM relationship_records
   WHERE from_record_id = 'rec_a1b2c3d4' OR to_record_id = 'rec_a1b2c3d4';
   ```

## Kullanım Örnekleri
```bash
curl -X DELETE http://localhost:8000/api/records/rec_a1b2c3d4 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Python (httpx)
```python
response = httpx.delete(
    f"http://localhost:8000/api/records/{record_id}",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 204:
    print("Record deleted successfully")
```

## Güvenlik Notları
1. Frontend'de confirmation gösterin
2. Silinen JSONB data geri alınamaz
3. İlişkili record bağlantıları kaybolur

## İlgili Endpoint'ler
- [GET /api/records](02-list-records.md)
- [POST /api/records](01-create-record.md)
