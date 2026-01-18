# relationships Table

## Genel Bakış

**Amaç:** Object'ler arası ilişki tanımları (1:N, N:N)

**Tip:** Metadata Table
**ID Format:** rel_xxxxxxxx (8 hex chars)
**Relationship Types:** 1:N (One-to-Many), N:N (Many-to-Many)
**Example:** Contact → Company (1:N)

---

## Tablo Özellikleri

| Özellik | Değer |
|---------|-------|
| **Primary Key** | id (VARCHAR) |
| **Foreign Keys** | from_object_id → objects.id (CASCADE)<br>to_object_id → objects.id (CASCADE) |
| **Referenced By** | relationship_records (CASCADE) |
| **Cascade Deletes** | YES (when object deleted) |
| **Indexes** | 2 indexes (id) |
| **Row Estimate** | Hundreds |

---

## Kolonlar

### id (varchar) - Primary Key
- **Tip:** VARCHAR
- **Nullable:** NO
- **Format:** rel_ + 8 hex chars
- **Örnek:** rel_a1b2c3d4

### name (varchar)
- **Tip:** VARCHAR
- **Nullable:** NO
- **Açıklama:** Relationship name (identifier)
- **Örnek:** contact_companies, company_contacts

### from_object_id (varchar) - Foreign Key
- **Tip:** VARCHAR
- **Nullable:** NO
- **References:** objects.id (CASCADE)
- **Açıklama:** Source object
- **Örnek:** obj_contact

### to_object_id (varchar) - Foreign Key
- **Tip:** VARCHAR
- **Nullable:** NO
- **References:** objects.id (CASCADE)
- **Açıklama:** Target object
- **Örnek:** obj_company

### type (varchar)
- **Tip:** VARCHAR
- **Nullable:** NO
- **Allowed Values:** 1:N, N:N
- **Açıklama:** Relationship type
- **Examples:**
  - 1:N: One Contact → Many Companies
  - N:N: Many Companies ↔ Many Contacts

### from_label (text)
- **Tip:** TEXT
- **Nullable:** YES
- **Açıklama:** Label shown on source object
- **Örnek:** "Companies" (shown on Contact)

### to_label (text)
- **Tip:** TEXT
- **Nullable:** YES
- **Açıklama:** Label shown on target object
- **Örnek:** "Contact" (shown on Company)

### created_at (timestamptz)
- **Tip:** TIMESTAMP WITH TIME ZONE
- **Nullable:** NO
- **Default:** NOW()

### created_by (uuid)
- **Tip:** UUID
- **Nullable:** YES
- **References:** users.id (not enforced)

---

## Relationship Types

### 1:N (One-to-Many)

**Example:** Contact → Companies
- One Contact can have many Companies
- Company belongs to one Contact

```
Contact (1) ──► (N) Companies
```

**Use Cases:**
- Account → Contacts
- Company → Opportunities
- Ticket → Comments

### N:N (Many-to-Many)

**Example:** Projects ↔ Users
- One Project can have many Users
- One User can be in many Projects

```
Projects (N) ◄──► (N) Users
```

**Use Cases:**
- Products ↔ Categories
- Students ↔ Courses
- Tags ↔ Articles

---

## Best Practices

### Naming Convention

✅ GOOD:
- from: contact, to: company → "contact_companies"
- from: company, to: contact → "company_contacts"

❌ BAD:
- "rel_1", "relationship_1" (not descriptive)

### Bidirectional Relationships

For N:N, create TWO relationships for clarity:
```
rel_project_users: Project → User (N:N)
rel_user_projects: User → Project (N:N)
```

---

**Last Updated:** 2026-01-18
**Status:** ✅ Production Ready
