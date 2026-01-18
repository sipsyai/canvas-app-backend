# GET /api/relationship-records/records/{record_id}/related

## Genel Bakış
Bir record'a belirli bir ilişki üzerinden bağlı tüm record'ları getirir.

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/relationship-records/records/{record_id}/related`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format

### Path Parameters
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| record_id | string | Record ID |

### Query Parameters
| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| relationship_id | string | Evet | Relationship ID |

### Örnek Request
```bash
GET /api/relationship-records/records/rec_ali/related?relationship_id=rel_contact_opportunity
```

## Response Format
```json
[
  {
    "id": "lnk_a1b2c3d4",
    "relationship_id": "rel_contact_opportunity",
    "from_record_id": "rec_ali",
    "to_record_id": "rec_bigdeal",
    "relationship_metadata": {
      "role": "Decision Maker"
    },
    "created_at": "2026-01-18T10:00:00Z"
  },
  {
    "id": "lnk_b2c3d4e5",
    "relationship_id": "rel_contact_opportunity",
    "from_record_id": "rec_ali",
    "to_record_id": "rec_mediumdeal",
    "relationship_metadata": {
      "role": "Influencer"
    },
    "created_at": "2026-01-18T11:00:00Z"
  }
]
```

## Kod Akışı
**Service:**
```python
async def get_related_records(
    self, db: AsyncSession, record_id: str, relationship_id: str
) -> list[RelationshipRecord]:
    result = await db.execute(
        select(RelationshipRecord).where(
            RelationshipRecord.relationship_id == relationship_id,
            (
                (RelationshipRecord.from_record_id == record_id) |
                (RelationshipRecord.to_record_id == record_id)
            )
        )
    )
    return list(result.scalars().all())
```

**SQL:**
```sql
SELECT * FROM relationship_records
WHERE relationship_id = 'rel_contact_opportunity'
  AND (from_record_id = 'rec_ali' OR to_record_id = 'rec_ali');
```

## Kullanım

### cURL
```bash
curl "http://localhost:8000/api/relationship-records/records/rec_ali/related?relationship_id=rel_contact_opportunity" \
  -H "Authorization: Bearer TOKEN"
```

### Python
```python
response = httpx.get(
    f"http://localhost:8000/api/relationship-records/records/rec_ali/related",
    params={"relationship_id": "rel_contact_opportunity"},
    headers={"Authorization": f"Bearer {token}"}
)

related = response.json()
print(f"Found {len(related)} related records")
```

## Kullanım Senaryosu

**Ali contact'ının tüm opportunity'lerini getir:**
```python
# 1. Contact-Opportunity ilişkisini bul
relationship_id = "rel_contact_opportunity"

# 2. Ali'ye bağlı opportunity'leri getir
related_links = get_related_records(
    record_id="rec_ali",
    relationship_id=relationship_id
)

# 3. Opportunity record'larını getir
for link in related_links:
    opportunity_id = link["to_record_id"]
    opportunity = get_record(opportunity_id)
    print(f"- {opportunity['data']['fld_name']}: {opportunity['data']['fld_amount']}")
```

## İlgili Endpoint'ler
- [POST /api/relationship-records](01-create-relationship-record.md) - Record bağla
- [DELETE /api/relationship-records/{link_id}](03-delete-relationship-record.md) - Bağlantıyı kaldır
