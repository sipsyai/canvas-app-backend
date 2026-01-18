# Object API Endpoints

Object API, veri tablolarını (objects) yönetmek için kullanılır. Her object bir veri tipini temsil eder (Contact, Company, Opportunity vb.).

## Object Nedir?

Object, Canvas App'de dinamik veri tablolarıdır. Her object:
- Field'ları barındırır (object_fields ile bağlantı)
- Record'ları saklar
- View konfigürasyonları tutar (form, table, kanban vb.)
- Permission ayarları içerir

## Endpoints

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| POST | `/api/objects` | Yeni object oluştur | ✅ JWT |
| GET | `/api/objects` | Kullanıcı object'lerini listele | ✅ JWT |
| GET | `/api/objects/{object_id}` | Tek object getir | ✅ JWT |
| PATCH | `/api/objects/{object_id}` | Object güncelle | ✅ JWT |
| DELETE | `/api/objects/{object_id}` | Object sil (CASCADE) | ✅ JWT |

## Örnek Object Yapısı

```json
{
  "id": "obj_contact",
  "name": "contact",
  "label": "Contact",
  "plural_name": "Contacts",
  "description": "Customer contacts",
  "icon": "👤",
  "is_custom": true,
  "is_global": false,
  "views": {
    "forms": [
      {"id": "form_default", "name": "Default", "fields": [...]}
    ],
    "tables": [
      {"id": "table_all", "name": "All Contacts", "columns": [...]}
    ],
    "kanbans": [],
    "calendars": []
  },
  "permissions": {
    "create": ["all"],
    "read": ["all"],
    "update": ["all"],
    "delete": ["all"]
  },
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T10:00:00Z"
}
```

## Detaylı Dokümantasyon

- [POST /api/objects - Object Oluştur](01-create-object.md)
- [GET /api/objects - Object Listele](02-list-objects.md)
- [GET /api/objects/{object_id} - Object Getir](03-get-object.md)
- [PATCH /api/objects/{object_id} - Object Güncelle](04-update-object.md)
- [DELETE /api/objects/{object_id} - Object Sil](05-delete-object.md)

## Database Tablo

**Tablo:** `public.objects`

```sql
CREATE TABLE objects (
  id VARCHAR PRIMARY KEY,                    -- obj_contact
  name VARCHAR(255) NOT NULL,                -- contact
  label VARCHAR(255) NOT NULL,               -- Contact
  plural_name VARCHAR(255) NOT NULL,         -- Contacts
  description TEXT,
  icon VARCHAR(50),                          -- 👤 (emoji)
  is_custom BOOLEAN DEFAULT TRUE,
  is_global BOOLEAN DEFAULT FALSE,
  views JSONB DEFAULT '{}'::jsonb,           -- View configurations
  permissions JSONB DEFAULT '{}'::jsonb,     -- CRUD permissions
  created_by UUID,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_objects_created_by ON objects(created_by);
CREATE INDEX idx_objects_name ON objects(name);
CREATE INDEX idx_objects_views_gin ON objects USING GIN(views);
CREATE INDEX idx_objects_permissions_gin ON objects USING GIN(permissions);
```

## İlgili Endpoint'ler

- [Field API](../02-fields/README.md) - Field'lar oluşturma
- [Object-Field API](../07-object-fields/README.md) - Field'ları object'e bağlama
- [Record API](../04-records/README.md) - Object record'ları

## Code Flow

```
Request
  ↓
Router (app/routers/objects.py)
  ↓
JWT Authentication (get_current_user_id)
  ↓
Service Layer (object_service.py)
  ↓
SQLAlchemy ORM (Object model)
  ↓
PostgreSQL Database
```
