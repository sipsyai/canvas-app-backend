# GET /api/records

## Genel Bakış
Bir object'e ait tüm record'ları listeler. Pagination desteği vardır.

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/records`
- **Authentication:** JWT Token gerekli
- **Response Status:** 200 OK

## Request Format

### Query Parameters
| Parametre | Tip | Zorunlu | Default | Açıklama |
|-----------|-----|---------|---------|----------|
| object_id | string | Evet | - | Object ID |
| page | integer | Hayır | 1 | Sayfa numarası (1-indexed) |
| page_size | integer | Hayır | 50 | Sayfa başına record sayısı (max: 100) |

### Örnek Requestler
```bash
# İlk 50 record
GET /api/records?object_id=obj_contact

# Sayfa 2, 25 record
GET /api/records?object_id=obj_contact&page=2&page_size=25

# Sayfa 3, 100 record (max)
GET /api/records?object_id=obj_contact&page=3&page_size=100
```

## Response Format

### Success Response (200 OK)
```json
{
  "total": 150,
  "page": 1,
  "page_size": 50,
  "records": [
    {
      "id": "rec_a1b2c3d4",
      "object_id": "obj_contact",
      "data": {
        "fld_name": "Ali Yılmaz",
        "fld_email": "ali@example.com"
      },
      "primary_value": "Ali Yılmaz",
      "created_by": "550e8400-e29b-41d4-a716-446655440000",
      "updated_by": "550e8400-e29b-41d4-a716-446655440000",
      "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-01-18T10:00:00Z",
      "updated_at": "2026-01-18T10:00:00Z"
    }
  ]
}
```

### Response Schema (RecordListResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| total | integer | Toplam record sayısı |
| page | integer | Mevcut sayfa |
| page_size | integer | Sayfa başına record |
| records | array | Record listesi (Array of RecordResponse) |

## Kod Akışı

**Router:** `app/routers/records.py`
```python
@router.get("/", response_model=RecordListResponse)
async def list_records(
    object_id: str = Query(..., description="Object ID to filter records"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * page_size
    records, total = await record_service.get_records_by_object(
        db, object_id, skip=skip, limit=page_size
    )
    return RecordListResponse(
        total=total, page=page, page_size=page_size, records=records
    )
```

**Service:**
```python
async def get_records_by_object(
    self, db: AsyncSession, object_id: str, skip: int = 0, limit: int = 100
) -> tuple[list[Record], int]:
    # Total count
    count_result = await db.execute(
        select(func.count()).select_from(Record).where(Record.object_id == object_id)
    )
    total = count_result.scalar_one()

    # Records
    result = await db.execute(
        select(Record)
        .where(Record.object_id == object_id)
        .offset(skip)
        .limit(limit)
        .order_by(Record.created_at.desc())
    )
    records = list(result.scalars().all())
    return records, total
```

**SQL:**
```sql
-- Total count
SELECT COUNT(*) FROM records WHERE object_id = 'obj_contact';

-- Records
SELECT * FROM records
WHERE object_id = 'obj_contact'
ORDER BY created_at DESC
OFFSET 0 LIMIT 50;
```

## Kullanım Örnekleri

### cURL
```bash
curl -X GET "http://localhost:8000/api/records?object_id=obj_contact&page=1&page_size=50" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Python (httpx)
```python
response = httpx.get(
    "http://localhost:8000/api/records",
    params={"object_id": "obj_contact", "page": 1, "page_size": 50},
    headers={"Authorization": f"Bearer {token}"}
)

data = response.json()
print(f"Total: {data['total']}, Page: {data['page']}/{data['total']//data['page_size']+1}")
for record in data['records']:
    print(f"- {record['primary_value']}")
```

## Pagination Örneği
```python
# Tüm record'ları al (pagination ile)
all_records = []
page = 1
page_size = 100

while True:
    response = httpx.get(
        "http://localhost:8000/api/records",
        params={"object_id": "obj_contact", "page": page, "page_size": page_size},
        headers={"Authorization": f"Bearer {token}"}
    )
    data = response.json()
    all_records.extend(data['records'])
    
    if len(data['records']) < page_size:
        break  # Son sayfa
    page += 1

print(f"Total records fetched: {len(all_records)}")
```

## İlgili Endpoint'ler
- [POST /api/records](01-create-record.md)
- [GET /api/records/search](06-search-records.md)
