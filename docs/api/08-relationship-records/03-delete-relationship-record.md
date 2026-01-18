# DELETE /api/relationship-records/{link_id}

## Genel Bakış
İki record arasındaki bağlantıyı kaldırır. Record'lar kendileri silinmez.

## Endpoint Bilgileri
- **Method:** DELETE
- **Path:** `/api/relationship-records/{link_id}`
- **Authentication:** JWT Token gerekli
- **Response Status:** 204 No Content

## Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| link_id | string | Link ID (lnk_xxxxxxxx) |

## Response Format

### Success Response (204 No Content)
Response body: Empty

### Error Responses

**404 Not Found:**
```json
{
  "detail": "Link not found"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

## NOT
Bu işlem sadece bağlantıyı siler:
- ✅ relationship_records tablosundan link silinir
- ❌ from_record ve to_record silinmez
- ❌ Relationship tanımı silinmez

## Kod Akışı
**SQL:**
```sql
DELETE FROM relationship_records WHERE id = 'lnk_a1b2c3d4';
```

## Kullanım

### cURL
```bash
curl -X DELETE http://localhost:8000/api/relationship-records/lnk_a1b2c3d4 \
  -H "Authorization: Bearer TOKEN"
```

### Python
```python
response = httpx.delete(
    f"http://localhost:8000/api/relationship-records/{link_id}",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 204:
    print("Link deleted successfully")
```

## Kullanım Senaryosu

**Ali'yi BigDeal opportunity'sinden kaldır:**
```python
# 1. Ali'nin BigDeal'e bağlantısını bul
related = get_related_records(
    record_id="rec_ali",
    relationship_id="rel_contact_opportunity"
)

# 2. BigDeal link'ini bul
bigdeal_link = next(
    link for link in related
    if link["to_record_id"] == "rec_bigdeal"
)

# 3. Link'i sil
delete_relationship_record(bigdeal_link["id"])
```

## İlgili Endpoint'ler
- [POST /api/relationship-records](01-create-relationship-record.md) - Record bağla
- [GET /api/relationship-records/records/{record_id}/related](02-get-related-records.md) - İlişkili record'ları getir
