# applications Table

## Genel Bakış

**Amaç:** Application configurations (CRM, ITSM, etc.)

**Tip:** System Table
**ID Format:** app_xxxxxxxx (8 hex chars)
**Examples:** CRM, ITSM, Project Management
**Draft/Published:** via published_at timestamp

---

## Tablo Özellikleri

| Özellik | Değer |
|---------|-------|
| **Primary Key** | id (VARCHAR) |
| **Foreign Keys** | None |
| **Referenced By** | None (standalone) |
| **Cascade Deletes** | None |
| **Indexes** | 2 indexes (id) |
| **Row Estimate** | Tens |

---

## Kolonlar

### id (varchar) - Primary Key
- **Format:** app_ + 8 hex chars
- **Örnek:** app_crm

### name (varchar)
- **Nullable:** NO
- **Örnek:** CRM, ITSM, Project Management

### label (varchar)
- **Nullable:** YES
- **Örnek:** Customer Relationship Management

### description (text)
- **Nullable:** YES
- **Örnek:** Manage customers, contacts, and opportunities

### icon (varchar)
- **Nullable:** YES
- **Örnek:** 🤝, 🔧, 📊

### config (jsonb)
- **Default:** {}
- **Açıklama:** Application configuration
- **Example:**
```json
{
  "objects": ["obj_contact", "obj_company"],
  "theme": {
    "primaryColor": "#1E40AF"
  },
  "navigation": [...]
}
```

### published_at (timestamptz)
- **Nullable:** YES
- **Default:** NULL
- **Açıklama:** Publication timestamp
- **NULL = Draft, Timestamp = Published**

### created_at (timestamptz)
- **Default:** NOW()

### updated_at (timestamptz)
- **Default:** NOW()

### created_by (uuid)
- **References:** users.id (not enforced)

---

## Draft/Published Pattern

### Draft
```python
{
    "published_at": None  # Not published
}
```

### Published
```python
{
    "published_at": "2026-01-18T10:00:00Z"  # Published
}
```

### Publish Application

```python
# Publish
app.published_at = datetime.now(UTC)
await db.commit()

# Unpublish (revert to draft)
app.published_at = None
await db.commit()
```

---

**Last Updated:** 2026-01-18
**Status:** ✅ Production Ready
