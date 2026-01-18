# users Table

## Genel Bakış

**Amaç:** Kullanıcı kimlik doğrulama ve profil yönetimi

**Tip:** Core System Table
**ID Format:** UUID
**Created:** System initialization
**Migration:** Alembic

---

## Tablo Özellikleri

| Özellik | Değer |
|---------|-------|
| **Primary Key** | id (UUID) |
| **Unique Constraints** | email |
| **Foreign Keys** | Yok (root table) |
| **Referenced By** | fields, objects, records, relationships, applications |
| **Cascade Deletes** | Yok (FK constraints not enforced) |
| **Indexes** | 3 index (id, email unique) |
| **Row Estimate** | Variable (user count) |

---

## Kolonlar

### id (uuid) - Primary Key
- **Tip:** UUID
- **Nullable:** NO
- **Default:** Auto-generated
- **Açıklama:** Kullanıcı benzersiz kimliği
- **Örnek:** `550e8400-e29b-41d4-a716-446655440000`

### email (varchar) - Unique
- **Tip:** VARCHAR
- **Nullable:** NO
- **Default:** -
- **Unique:** YES
- **Açıklama:** Kullanıcı email adresi (login username)
- **Örnek:** `john.doe@example.com`

### hashed_password (varchar)
- **Tip:** VARCHAR
- **Nullable:** NO
- **Default:** -
- **Açıklama:** Bcrypt ile hashlenen şifre
- **Algoritma:** bcrypt (cost factor: 12)
- **Örnek:** `$2b$12$KIXxLhGvBZLXN5Zg2hVQYO...`

### full_name (varchar)
- **Tip:** VARCHAR
- **Nullable:** NO
- **Default:** -
- **Açıklama:** Kullanıcının tam adı
- **Örnek:** `John Doe`

### is_active (boolean)
- **Tip:** BOOLEAN
- **Nullable:** NO
- **Default:** true
- **Açıklama:** Hesap aktif mi?
- **Kullanım:** Hesap ban/suspend için

### is_verified (boolean)
- **Tip:** BOOLEAN
- **Nullable:** NO
- **Default:** false
- **Açıklama:** Email doğrulandı mı?
- **Kullanım:** Email verification workflow

### created_at (timestamptz)
- **Tip:** TIMESTAMP WITH TIME ZONE
- **Nullable:** NO
- **Default:** NOW()
- **Açıklama:** Hesap oluşturulma zamanı
- **Örnek:** `2026-01-15 10:00:00+00`

### updated_at (timestamptz)
- **Tip:** TIMESTAMP WITH TIME ZONE
- **Nullable:** NO
- **Default:** NOW()
- **Açıklama:** Son güncelleme zamanı
- **Not:** Manually updated

### last_login (timestamptz)
- **Tip:** TIMESTAMP WITH TIME ZONE
- **Nullable:** YES
- **Default:** NULL
- **Açıklama:** Son giriş zamanı
- **Kullanım:** Activity tracking, security monitoring

---

## İlişkiler

### Referenced By (Soft References - Not Enforced)

Bu tablonun `id` kolonu, diğer tablolarda `created_by` alanında referans edilir:

1. **fields.created_by** → users.id
2. **objects.created_by** → users.id
3. **records.created_by** → users.id
4. **records.updated_by** → users.id
5. **relationships.created_by** → users.id
6. **relationship_records.created_by** → users.id
7. **applications.created_by** → users.id

**Not:** Bu ilişkiler veritabanı seviyesinde enforce edilmez, uygulama seviyesinde yönetilir.

---

## Index'ler

### 1. users_pkey (UNIQUE)
```sql
CREATE UNIQUE INDEX users_pkey ON users USING btree (id);
```
**Amaç:** Primary key constraint
**Kullanım:** Hızlı id lookup
**Performans:** O(log n)

### 2. ix_users_email (UNIQUE)
```sql
CREATE UNIQUE INDEX ix_users_email ON users USING btree (email);
```
**Amaç:** Email uniqueness + login lookup
**Kullanım:** Login query (WHERE email = ?)
**Performans:** O(log n)

### 3. ix_users_id
```sql
CREATE INDEX ix_users_id ON users USING btree (id);
```
**Amaç:** Additional id index (SQLAlchemy)
**Kullanım:** Foreign key lookups

---

## Güvenlik

### Password Hashing

**Algoritma:** bcrypt
**Cost Factor:** 12 (default)
**Library:** passlib[bcrypt]

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash("user_password")  # $2b$12$...

# Verify password
is_valid = pwd_context.verify("user_password", hashed)  # True/False
```

**Neden bcrypt?**
- Adaptive hashing (cost factor increase as CPU power grows)
- Salt otomatik olarak hash'e dahil
- Rainbow table attack'lere karşı dayanıklı

### JWT Token Claims

**JWT Payload:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // users.id
  "email": "john.doe@example.com",
  "jti": "unique-token-id",
  "exp": 1737800000  // Expiration timestamp
}
```

**Token Lifetime:** 1 hour (3600 seconds)
**Refresh Strategy:** Re-login after expiration

---

## Örnek Kullanımlar

### Kullanıcı Kaydı (Register)

```python
from app.models.user import User
from app.utils.security import hash_password

new_user = User(
    email="newuser@example.com",
    hashed_password=hash_password("SecurePass123"),
    full_name="New User",
    is_active=True,
    is_verified=False,  # Email verification pending
    created_at=datetime.now(UTC),
    updated_at=datetime.now(UTC)
)

db.add(new_user)
await db.commit()
```

### Kullanıcı Girişi (Login)

```python
from app.utils.security import verify_password, create_access_token

# 1. Find user by email
user = await db.execute(
    select(User).where(User.email == "user@example.com")
)
user = user.scalar_one_or_none()

# 2. Verify password
if not user or not verify_password("password", user.hashed_password):
    raise HTTPException(status_code=401, detail="Invalid credentials")

# 3. Check if active
if not user.is_active:
    raise HTTPException(status_code=403, detail="Account inactive")

# 4. Update last_login
user.last_login = datetime.now(UTC)
await db.commit()

# 5. Generate JWT token
token = create_access_token({"sub": str(user.id), "email": user.email})
return {"access_token": token, "token_type": "bearer"}
```

### Email Verification

```python
# Mark email as verified
user.is_verified = True
user.updated_at = datetime.now(UTC)
await db.commit()
```

### Account Deactivation

```python
# Soft delete (deactivate)
user.is_active = False
user.updated_at = datetime.now(UTC)
await db.commit()

# Hard delete (not recommended - breaks created_by references)
# await db.delete(user)
# await db.commit()
```

---

## Örnek Sorgular

### 1. Aktif Kullanıcı Sayısı

```sql
SELECT
  COUNT(*) FILTER (WHERE is_active = true AND is_verified = true) AS active_users,
  COUNT(*) FILTER (WHERE is_active = true AND is_verified = false) AS pending_verification,
  COUNT(*) FILTER (WHERE is_active = false) AS inactive_users
FROM users;
```

### 2. Son 30 Günde Giriş Yapmayanlar

```sql
SELECT
  id,
  email,
  full_name,
  last_login
FROM users
WHERE last_login < NOW() - INTERVAL '30 days'
   OR last_login IS NULL
ORDER BY last_login NULLS LAST;
```

### 3. En Aktif Kullanıcılar (Content Creators)

```sql
SELECT
  u.id,
  u.email,
  u.full_name,
  COUNT(DISTINCT f.id) AS fields_created,
  COUNT(DISTINCT o.id) AS objects_created,
  COUNT(DISTINCT r.id) AS records_created
FROM users u
LEFT JOIN fields f ON u.id = f.created_by
LEFT JOIN objects o ON u.id = o.created_by
LEFT JOIN records r ON u.id = r.created_by
GROUP BY u.id, u.email, u.full_name
ORDER BY (COUNT(DISTINCT f.id) + COUNT(DISTINCT o.id) + COUNT(DISTINCT r.id)) DESC
LIMIT 10;
```

### 4. Email Domain Analizi

```sql
SELECT
  SUBSTRING(email FROM '@(.*)$') AS email_domain,
  COUNT(*) AS user_count
FROM users
WHERE is_active = true
GROUP BY email_domain
ORDER BY user_count DESC;
```

---

## Best Practices

### 1. Password Requirements

**Minimum Requirements:**
- ✅ En az 8 karakter
- ✅ En az 1 büyük harf
- ✅ En az 1 küçük harf
- ✅ En az 1 rakam

```python
# Pydantic validation
from pydantic import field_validator

class UserCreate(BaseModel):
    password: str = Field(..., min_length=8)

    @field_validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
```

### 2. Email Normalization

```python
# Always lowercase and strip whitespace
email = email.lower().strip()
```

### 3. Created/Updated Timestamp Management

```python
# On create
new_user.created_at = datetime.now(UTC)
new_user.updated_at = datetime.now(UTC)

# On update
user.updated_at = datetime.now(UTC)  # Manually set
```

### 4. Soft Delete vs Hard Delete

**Soft Delete (Recommended):**
```python
user.is_active = False
```

**Hard Delete (NOT recommended):**
- Breaks created_by references
- Loses audit trail
- Cannot recover user data

---

## Migration History

**Created:** Initial migration
**File:** `alembic/versions/001_initial.py`

**Changes:**
- 2026-01-15: Initial user table creation
- 2026-01-16: Added is_verified field
- 2026-01-17: Added last_login field

---

## İlgili Dosyalar

- **Model:** `app/models/user.py`
- **Schema:** `app/schemas/user.py`
- **Router:** `app/routers/auth.py`
- **Service:** `app/services/user_service.py`
- **Middleware:** `app/middleware/auth.py`
- **Utils:** `app/utils/security.py`

---

**Last Updated:** 2026-01-18
**Status:** ✅ Production Ready
