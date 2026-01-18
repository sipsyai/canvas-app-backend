# DELETE /api/relationships/{relationship_id}

## Genel Bakış
İlişki tanımını siler. Bağlı relationship_records da silinir (CASCADE).

## Endpoint Bilgileri
- **Method:** DELETE
- **Path:** `/api/relationships/{relationship_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 204 No Content

## Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| relationship_id | string | Relationship ID (rel_xxxxxxxx) |

## Response Format

### Success Response (204 No Content)
Response body: Empty

### Error Responses
**404 Not Found:**
```json
{
  "detail": "Relationship not found"
}
```

## CASCADE Davranışı
Relationship silindiğinde:
- **relationship_records:** Bu ilişki üzerinden bağlı tüm record bağlantıları silinir

## Kullanım
```bash
curl -X DELETE http://localhost:8000/api/relationships/rel_a1b2c3d4 \
  -H "Authorization: Bearer TOKEN"
```

### Error Response
**404 Not Found:**
```json
{
  "detail": "Relationship not found"
}
```
