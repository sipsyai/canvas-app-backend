# Field API Endpoints

Field API, form alanlarını (fields) yönetmek için kullanılır. Her field bir veri tipini temsil eder (text, email, number, date, lookup vb.).

## Field Nedir?

Field, Canvas App'de dinamik veri alanlarıdır. İki tip field vardır:
1. **System Fields** (Global): Tüm object'lerde kullanılabilen sistem alanları (created_at, created_by, owner vb.)
2. **Custom Fields**: Kullanıcıların oluşturduğu özel alanlar

## Endpoints

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| POST | `/api/fields` | Yeni field oluştur | ✅ JWT |
| GET | `/api/fields` | Tüm field'ları listele | ✅ JWT |
| GET | `/api/fields/{field_id}` | Tek field getir | ✅ JWT |
| PATCH | `/api/fields/{field_id}` | Field güncelle | ✅ JWT |
| DELETE | `/api/fields/{field_id}` | Field sil | ✅ JWT |

## Field Tipleri

| Tip | Açıklama | Örnek |
|-----|----------|-------|
| text | Tek satır metin | "Ali Yılmaz" |
| textarea | Çok satır metin | "Uzun açıklama..." |
| email | Email adresi | "ali@example.com" |
| phone | Telefon numarası | "+90 555 1234567" |
| number | Sayı | 42 |
| currency | Para birimi | 1000.50 |
| date | Tarih | "2026-01-18" |
| datetime | Tarih + saat | "2026-01-18T10:30:00Z" |
| checkbox | Boolean | true/false |
| select | Dropdown seçim | "Option A" |
| multiselect | Çoklu seçim | ["Option A", "Option B"] |
| lookup | İlişkili kayıt referansı | "rec_abc123" |
| url | Web URL | "https://example.com" |

## Field Kategorileri

- **System**: Sistem alanları (created_at, owner vb.)
- **Contact Info**: İletişim bilgileri (email, phone vb.)
- **Business**: İş bilgileri (company, job title vb.)
- **Address**: Adres bilgileri
- **Custom**: Özel kategoriler

## Örnek Field Yapısı

```json
{
  "id": "fld_abc12345",
  "name": "email",
  "label": "Email Address",
  "type": "email",
  "description": "Contact email address",
  "category": "Contact Info",
  "is_global": false,
  "is_system_field": false,
  "is_custom": true,
  "config": {
    "validation": {
      "required": true,
      "regex": "^[^@]+@[^@]+\\.[^@]+$"
    },
    "placeholder": "user@example.com"
  },
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T10:00:00Z"
}
```

## Config Yapısı

Field config JSONB formatında esnektir ve field tipine göre değişir:

### Text/Email/Phone
```json
{
  "validation": {
    "required": true,
    "minLength": 3,
    "maxLength": 255,
    "regex": "pattern"
  },
  "placeholder": "Enter text..."
}
```

### Number/Currency
```json
{
  "validation": {
    "min": 0,
    "max": 1000,
    "precision": 2
  },
  "currency": "USD",
  "displayFormat": "$0,0.00"
}
```

### Select/Multiselect
```json
{
  "options": [
    {"value": "option1", "label": "Option 1", "color": "#FF0000"},
    {"value": "option2", "label": "Option 2", "color": "#00FF00"}
  ],
  "allowCustom": false
}
```

### Lookup
```json
{
  "lookupObject": "obj_contact",
  "displayField": "fld_name",
  "filterBy": {"fld_status": "active"}
}
```

## Detaylı Dokümantasyon

- [POST /api/fields - Field Oluştur](01-create-field.md)
- [GET /api/fields - Field Listele](02-list-fields.md)
- [GET /api/fields/{field_id} - Field Getir](03-get-field.md)
- [PATCH /api/fields/{field_id} - Field Güncelle](04-update-field.md)
- [DELETE /api/fields/{field_id} - Field Sil](05-delete-field.md)

## Code Flow

```
Request
  ↓
Router (app/routers/fields.py)
  ↓
Pydantic Validation (FieldCreate/FieldUpdate schema)
  ↓
JWT Authentication (get_current_user_id)
  ↓
Service Layer (field_service.py)
  ↓
SQLAlchemy ORM (Field model)
  ↓
PostgreSQL Database
```

## Database Tablo

**Tablo:** `public.fields`

```sql
CREATE TABLE fields (
  id VARCHAR PRIMARY KEY,                    -- fld_abc12345
  name VARCHAR(255) NOT NULL,                -- email
  label VARCHAR(255) NOT NULL,               -- Email Address
  type VARCHAR(50) NOT NULL,                 -- email
  description TEXT,
  category VARCHAR(100),                     -- Contact Info
  is_global BOOLEAN DEFAULT FALSE,           -- System field mi?
  is_system_field BOOLEAN DEFAULT FALSE,     -- created_at, owner gibi
  is_custom BOOLEAN DEFAULT TRUE,            -- Kullanıcı custom field'ı
  config JSONB DEFAULT '{}'::jsonb,          -- Esnekli ayarlar
  created_by UUID,                           -- Creator user ID
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fields_created_by ON fields(created_by);
CREATE INDEX idx_fields_is_global ON fields(is_global);
CREATE INDEX idx_fields_category ON fields(category);
CREATE INDEX idx_fields_type ON fields(type);
CREATE INDEX idx_fields_config_gin ON fields USING GIN(config);
```

## İlgili Endpoint'ler

- [Object-Field API](../07-object-fields/README.md) - Field'ları object'lere attach etme
- [Record API](../04-records/README.md) - Field value'larını kaydetme

## Best Practices

1. **Field Naming:**
   - Küçük harf + underscore (snake_case)
   - Descriptive: `email_address` > `ea`

2. **Config Schema:**
   - Validasyon kurallarını config'de sakla
   - Type-specific config kullan

3. **Global vs Custom:**
   - System fields `is_global=true` olmalı
   - User fields `is_custom=true` olmalı

4. **Deletion:**
   - Field'a bağlı object_field ve record data silinir (CASCADE)
   - Dikkatli kullan!
