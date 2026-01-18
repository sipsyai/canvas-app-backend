# alembic_version Table

## Genel Bakış

**Amaç:** Database migration version tracking

**Tip:** System Table (Alembic)
**Primary Key:** version_num
**Row Count:** 1 (single row table)
**Managed By:** Alembic migration tool

---

## Tablo Özellikleri

| Özellik | Değer |
|---------|-------|
| **Primary Key** | version_num (VARCHAR 32) |
| **Foreign Keys** | None |
| **Referenced By** | None |
| **Cascade Deletes** | None |
| **Indexes** | 1 (primary key) |
| **Row Estimate** | 1 (always) |

---

## Kolonlar

### version_num (varchar) - Primary Key
- **Tip:** VARCHAR(32)
- **Nullable:** NO
- **Açıklama:** Current migration version
- **Örnek:** a1b2c3d4e5f6
- **Format:** Alembic revision hash

---

## Usage

### Check Current Version

```bash
# Via Alembic CLI
alembic current

# Via SQL
SELECT version_num FROM alembic_version;
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1
```

### Migration History

```bash
# View history
alembic history

# View current + history
alembic current --verbose
```

---

## Migration Files

**Location:** /alembic/versions/
**Format:** {revision}_{description}.py
**Example:** a1b2c3d4e5f6_initial_tables.py

---

**Last Updated:** 2026-01-18
**Status:** ✅ System Table (Do Not Modify Manually)
