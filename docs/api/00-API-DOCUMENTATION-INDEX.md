# Canvas App Backend - API Documentation Index

Tüm API endpoint'leri için kapsamlı dokümantasyon.

## Genel Bakış

Canvas App Backend, FastAPI ile geliştirilmiş bir REST API'dir. PostgreSQL JSONB hybrid model kullanarak esnek, no-code veri yönetimi sunar.

## Kimlik Doğrulama (Authentication)

Tüm endpoint'ler (public olanlar hariç) JWT token gerektirir.

**Public Endpoints:**
- POST /api/auth/register
- POST /api/auth/login

**Protected Endpoints:**
- Authorization header gerekli: `Authorization: Bearer YOUR_JWT_TOKEN`

## API Kategorileri

### 1. Authentication (3 endpoints)
Kullanıcı kaydı, giriş ve kimlik doğrulama.

📁 **Klasör:** `01-authentication/`

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| [/api/auth/register](01-authentication/01-register.md) | POST | Yeni kullanıcı kaydı |
| [/api/auth/login](01-authentication/02-login.md) | POST | Kullanıcı girişi (JWT token) |
| [/api/auth/me](01-authentication/03-get-current-user.md) | GET | Mevcut kullanıcı bilgileri |

### 2. Fields (5 endpoints)
Form alanları (email, text, number vb.) yönetimi.

📁 **Klasör:** `02-fields/`
📄 **README:** [Fields API Overview](02-fields/README.md)

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| [/api/fields](02-fields/01-create-field.md) | POST | Yeni field oluştur |
| [/api/fields](02-fields/02-list-fields.md) | GET | Field'ları listele (filtreleme) |
| [/api/fields/{field_id}](02-fields/03-get-field.md) | GET | Tek field getir |
| [/api/fields/{field_id}](02-fields/04-update-field.md) | PATCH | Field güncelle |
| [/api/fields/{field_id}](02-fields/05-delete-field.md) | DELETE | Field sil |

### 3. Objects (5 endpoints)
Veri tabloları (Contact, Company vb.) yönetimi.

📁 **Klasör:** `03-objects/`
📄 **README:** [Objects API Overview](03-objects/README.md)

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| [/api/objects](03-objects/01-create-object.md) | POST | Yeni object oluştur |
| [/api/objects](03-objects/02-list-objects.md) | GET | Object'leri listele |
| [/api/objects/{object_id}](03-objects/03-get-object.md) | GET | Tek object getir |
| [/api/objects/{object_id}](03-objects/04-update-object.md) | PATCH | Object güncelle |
| [/api/objects/{object_id}](03-objects/05-delete-object.md) | DELETE | Object sil (CASCADE) |

### 4. Records (6 endpoints)
JSONB ile dinamik veri kayıtları.

📁 **Klasör:** `04-records/`
📄 **README:** [Records API Overview](04-records/README.md)

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| [/api/records](04-records/01-create-record.md) | POST | Yeni record oluştur |
| [/api/records](04-records/02-list-records.md) | GET | Record'ları listele (pagination) |
| [/api/records/{record_id}](04-records/03-get-record.md) | GET | Tek record getir |
| [/api/records/{record_id}](04-records/04-update-record.md) | PATCH | Record güncelle (MERGE) |
| [/api/records/{record_id}](04-records/05-delete-record.md) | DELETE | Record sil |
| [/api/records/search](04-records/06-search-records.md) | GET | Record ara (primary_value) |

### 5. Applications (4 endpoints)
No-code uygulamalar (CRM, ITSM vb.) yönetimi.

📁 **Klasör:** `05-applications/`
📄 **README:** [Applications API Overview](05-applications/README.md)

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| [/api/applications](05-applications/01-create-application.md) | POST | Yeni uygulama oluştur |
| [/api/applications](05-applications/02-list-applications.md) | GET | Uygulamaları listele |
| [/api/applications/{app_id}/publish](05-applications/03-publish-application.md) | POST | Uygulamayı yayınla |
| [/api/applications/{app_id}](05-applications/04-delete-application.md) | DELETE | Uygulamayı sil |

### 6. Relationships (3 endpoints)
Object'ler arası ilişki tanımları (1:N, N:N).

📁 **Klasör:** `06-relationships/`
📄 **README:** [Relationships API Overview](06-relationships/README.md)

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| [/api/relationships](06-relationships/01-create-relationship.md) | POST | İlişki tanımla |
| [/api/relationships/objects/{object_id}](06-relationships/02-get-object-relationships.md) | GET | Object ilişkilerini getir |
| [/api/relationships/{relationship_id}](06-relationships/03-delete-relationship.md) | DELETE | İlişki tanımını sil |

### 7. Object-Fields (5 endpoints)
Field'ları object'lere bağlama (junction table).

📁 **Klasör:** `07-object-fields/`
📄 **README:** [Object-Fields API Overview](07-object-fields/README.md)

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| [/api/object-fields](07-object-fields/01-create-object-field.md) | POST | Field'ı object'e ekle |
| [/api/object-fields](07-object-fields/02-list-object-fields.md) | GET | Object field'larını listele |
| [/api/object-fields/{object_field_id}](07-object-fields/03-get-object-field.md) | GET | Tek object-field getir |
| [/api/object-fields/{object_field_id}](07-object-fields/04-update-object-field.md) | PATCH | Object-field güncelle |
| [/api/object-fields/{object_field_id}](07-object-fields/05-delete-object-field.md) | DELETE | Field'ı object'ten kaldır |

### 8. Relationship-Records (3 endpoints)
Record'lar arası bağlantılar (junction table).

📁 **Klasör:** `08-relationship-records/`
📄 **README:** [Relationship-Records API Overview](08-relationship-records/README.md)

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| [/api/relationship-records](08-relationship-records/01-create-relationship-record.md) | POST | Record'ları bağla |
| [/api/relationship-records/records/{record_id}/related](08-relationship-records/02-get-related-records.md) | GET | İlişkili record'ları getir |
| [/api/relationship-records/{link_id}](08-relationship-records/03-delete-relationship-record.md) | DELETE | Bağlantıyı kaldır |

## Endpoint Sayıları

| Kategori | Endpoint Sayısı | Toplam Dosya |
|----------|----------------|--------------|
| Authentication | 3 | 3 |
| Fields | 5 | 6 (README dahil) |
| Objects | 5 | 6 (README dahil) |
| Records | 6 | 7 (README dahil) |
| Applications | 4 | 5 (README dahil) |
| Relationships | 3 | 4 (README dahil) |
| Object-Fields | 5 | 6 (README dahil) |
| Relationship-Records | 3 | 4 (README dahil) |
| **TOPLAM** | **34 endpoints** | **41 dosya** |

## Hızlı Başlangıç

### 1. Kullanıcı Kaydı ve Giriş
```bash
# Kayıt ol
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Pass123", "full_name": "Ali"}'

# Giriş yap (JWT token al)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=Pass123"

# Response:
# {"access_token": "eyJ...", "token_type": "bearer"}
```

### 2. Field Oluştur
```bash
curl -X POST http://localhost:8000/api/fields \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "email",
    "label": "Email",
    "type": "email"
  }'
```

### 3. Object Oluştur
```bash
curl -X POST http://localhost:8000/api/objects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "contact",
    "label": "Contact",
    "plural_name": "Contacts"
  }'
```

### 4. Field'ı Object'e Ekle
```bash
curl -X POST http://localhost:8000/api/object-fields \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "object_id": "obj_contact",
    "field_id": "fld_email",
    "is_required": true
  }'
```

### 5. Record Oluştur
```bash
curl -X POST http://localhost:8000/api/records \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "object_id": "obj_contact",
    "data": {
      "fld_email": "ali@example.com"
    }
  }'
```

## Teknoloji Stack

- **Framework:** FastAPI 0.115+
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0+ (async)
- **Auth:** Custom JWT + bcrypt
- **Data Model:** JSONB Hybrid (normalized metadata + JSONB data)

## Mimari Özellikler

### JSONB Hybrid Model
```sql
-- Normalized metadata
id, object_id, primary_value, created_at, updated_by

-- Dynamic JSONB data
data = {"fld_email": "ali@example.com", "fld_phone": "+90 555..."}
```

**Avantajları:**
- 7x daha hızlı (EAV'ye göre)
- 3x daha az storage
- Esnek schema (no migrations for new fields)
- GIN index ile hızlı JSONB sorgular

### Service Layer Pattern
```
Request → Router → Service Layer → Database
```

**Tüm business logic service layer'da:**
- `app/services/field_service.py`
- `app/services/object_service.py`
- `app/services/record_service.py`
- vb.

### JWT Authentication
```python
# Protected endpoint pattern
@router.get("/")
async def list_fields(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),  # JWT gerekli
):
    ...
```

## Veri Akışı Örneği

### Contact CRM Oluşturma
```python
# 1. Field'ları oluştur
email_field = create_field(name="email", type="email")
phone_field = create_field(name="phone", type="phone")
company_field = create_field(name="company", type="text")

# 2. Contact object'i oluştur
contact_obj = create_object(name="contact", label="Contact", plural_name="Contacts")

# 3. Field'ları object'e ekle
add_field_to_object(contact_obj.id, email_field.id, display_order=0, is_required=True)
add_field_to_object(contact_obj.id, phone_field.id, display_order=1)
add_field_to_object(contact_obj.id, company_field.id, display_order=2)

# 4. Record'lar oluştur
ali = create_record(
    object_id=contact_obj.id,
    data={
        "fld_email": "ali@example.com",
        "fld_phone": "+90 555 1234567",
        "fld_company": "Acme Corp"
    }
)

# 5. Opportunity object'i oluştur
opportunity_obj = create_object(name="opportunity", label="Opportunity", plural_name="Opportunities")

# 6. Contact → Opportunity ilişkisi tanımla
relationship = create_relationship(
    from_object_id=contact_obj.id,
    to_object_id=opportunity_obj.id,
    type="1:N",
    from_label="Opportunities",
    to_label="Contact"
)

# 7. Record'ları bağla
link_records(
    relationship_id=relationship.id,
    from_record_id=ali.id,
    to_record_id=bigdeal_opportunity.id
)
```

## Error Handling

Tüm endpoint'ler standart HTTP status code'ları kullanır:

| Status | Açıklama |
|--------|----------|
| 200 | OK - Başarılı GET/PATCH |
| 201 | Created - Başarılı POST |
| 204 | No Content - Başarılı DELETE |
| 400 | Bad Request - İş mantığı hatası |
| 401 | Unauthorized - JWT token eksik/geçersiz |
| 404 | Not Found - Kayıt bulunamadı |
| 422 | Unprocessable Entity - Validation hatası |

### Error Response Format
```json
{
  "detail": "Error message here"
}
```

### Validation Error Format (422)
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

## Performance

### Indexed Columns
```sql
-- Fields
CREATE INDEX idx_fields_created_by ON fields(created_by);
CREATE INDEX idx_fields_category ON fields(category);

-- Records
CREATE INDEX idx_records_object_id ON records(object_id);
CREATE INDEX idx_records_primary_value ON records(primary_value);
CREATE INDEX idx_records_data_gin ON records USING GIN(data);

-- Object-Fields
CREATE INDEX idx_object_fields_object_id ON object_fields(object_id);
```

### Query Performance
| Query Type | Average Time | Index Used |
|------------|--------------|------------|
| List records | ~10-20ms | B-tree (object_id) |
| Search by primary_value | ~10ms | B-tree (primary_value) |
| JSONB contains query | ~20-30ms | GIN (data) |
| Nested JSONB query | ~50-100ms | GIN (data) |

## Güvenlik

### JWT Token
- **Algorithm:** HS256
- **Expiration:** 1 hour
- **Secret Key:** Environment variable (SECRET_KEY)

### Password Hashing
- **Algorithm:** bcrypt
- **Cost Factor:** 12 (2^12 iterations)
- **bcrypt Version:** 4.1.3 (passlib compatible)

### Input Validation
- Pydantic schema ile otomatik validation
- SQL injection prevention (SQLAlchemy parameterized queries)
- XSS prevention (JSON response, no HTML rendering)

## Gelişmiş Özellikler

### Pagination
```python
# Record listele (pagination)
GET /api/records?object_id=obj_contact&page=2&page_size=50
```

### Filtering
```python
# Field'ları kategori ile filtrele
GET /api/fields?category=Contact Info&is_system=false
```

### Search
```python
# Record ara (primary_value ile)
GET /api/records/search?object_id=obj_contact&q=Ali
```

### JSONB Merge (Update)
```python
# Mevcut data: {"fld_name": "Ali", "fld_email": "old@example.com"}
# Update data: {"fld_email": "new@example.com"}
# Sonuç: {"fld_name": "Ali", "fld_email": "new@example.com"}  # MERGE!
```

## İlgili Dokümantasyon

- [Backend Architecture Analysis](../../BACKEND_ARCHITECTURE_ANALYSIS.md)
- [Backend Project Specification](../../BACKEND_PROJECT_SPECIFICATION.md)
- [Database Visual Schema](../../DATABASE_VISUAL_SCHEMA.md)
- [CLAUDE.md](../../CLAUDE.md) - Development guidelines

## API Testing

### Interactive Docs
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### cURL Collection
Tüm endpoint'ler için cURL örnekleri her dokümantasyon dosyasında mevcuttur.

### Python Client Example
```python
import httpx

# Login
response = httpx.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "user@example.com", "password": "Pass123"}
)
token = response.json()["access_token"]

# Authenticated request
fields = httpx.get(
    "http://localhost:8000/api/fields",
    headers={"Authorization": f"Bearer {token}"}
).json()
```

## Değişiklik Geçmişi

- **v1.0.0** (2026-01-18): Initial API documentation
  - 34 endpoints documented
  - 7 API categories
  - Turkish language documentation
  - Code examples (cURL, Python, JavaScript)

## Katkıda Bulunma

Dokümantasyon güncellemeleri için:
1. İlgili endpoint dosyasını düzenleyin
2. Code example'ları test edin
3. README'leri güncelleyin
4. Pull request oluşturun

## Lisans

Canvas App Backend - Internal Documentation
