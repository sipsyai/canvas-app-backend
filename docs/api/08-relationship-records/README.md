# Relationship-Record API Endpoints

Relationship-Record API, record'lar arası bağlantıları yönetir (junction table).

## Endpoints

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| POST | `/api/relationship-records` | Record'ları bağla | ✅ JWT |
| GET | `/api/relationship-records/records/{record_id}/related?relationship_id=...` | İlişkili record'ları getir | ✅ JWT |
| DELETE | `/api/relationship-records/{link_id}` | Bağlantıyı kaldır | ✅ JWT |

## Örnek Relationship-Record
```json
{
  "id": "lnk_a1b2c3d4",
  "relationship_id": "rel_contact_opportunity",
  "from_record_id": "rec_ali",
  "to_record_id": "rec_bigdeal",
  "relationship_metadata": {
    "role": "Decision Maker",
    "influence_level": "High"
  },
  "created_at": "2026-01-18T10:00:00Z"
}
```

## Kullanım Senaryosu
1. Contact → Opportunities ilişkisini tanımla (Relationship API)
2. Ali contact'ını BigDeal opportunity'sine bağla (Relationship-Record API)
3. Ali'ye bağlı tüm opportunity'leri getir (GET related records)
