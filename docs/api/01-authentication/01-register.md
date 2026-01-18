# POST /api/auth/register

## Genel Bakış
Yeni kullanıcı kaydı oluşturur. Email, şifre ve tam ad bilgileri ile kayıt gerçekleştirilir.

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/auth/register`
- **Authentication:** Gerekli değil (Public endpoint)
- **Response Status:** 201 Created
- **Rate Limit:** 5 requests/minute per IP

## Request Format

### Request Body (JSON)
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "full_name": "Ali Yılmaz"
}
```

### Request Schema (UserRegister)
| Alan | Tip | Zorunlu | Validasyon | Açıklama |
|------|-----|---------|------------|----------|
| email | string (EmailStr) | Evet | Email formatı | Kullanıcı email adresi |
| password | string | Evet | Min 8 karakter | Kullanıcı şifresi |
| full_name | string | Evet | Min 1 karakter | Kullanıcı tam adı |

## Response Format

### Success Response (201 Created)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Ali Yılmaz",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-01-18T17:30:00.000Z",
  "last_login": null
}
```

### Response Schema (UserResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string (UUID) | Kullanıcı ID'si |
| email | string | Kullanıcı email adresi |
| full_name | string | Kullanıcı tam adı |
| is_active | boolean | Kullanıcı aktif mi? |
| is_verified | boolean | Email doğrulandı mı? |
| created_at | string (ISO 8601) | Kayıt tarihi |
| last_login | string (ISO 8601) | Son giriş tarihi (null olabilir) |

### Error Responses

#### 400 Bad Request - Email Already Exists
```json
{
  "detail": "Email already registered"
}
```

#### 422 Unprocessable Entity - Validation Error
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "short",
      "ctx": {"min_length": 8}
    }
  ]
}
```

## Kod Akışı

### 1. Router Layer
**Dosya:** `app/routers/auth.py`

```python
@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("5/minute")  # Rate limiting
async def register_user(
    request: Request,
    user_in: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.register_user(db, user_in)
    return user
```

**Görevleri:**
- Request body'yi `UserRegister` Pydantic schema ile validate eder
- Rate limiting uygular (5 request/minute per IP)
- Database session'ı dependency injection ile alır
- Auth service'i çağırır
- Response'u `UserResponse` schema ile serialize eder

### 2. Validation Layer
**Dosya:** `app/schemas/auth.py`

```python
class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    full_name: str = Field(..., min_length=1, description="Full name")
```

**Görevleri:**
- Email formatını doğrular (EmailStr)
- Şifrenin minimum 8 karakter olduğunu kontrol eder
- Full name'in boş olmadığını kontrol eder

### 3. Service Layer (Business Logic)
**Dosya:** `app/services/auth_service.py`

**Adımlar:**

1. **Email Kontrolü (Database):**
```python
existing_user = await self.get_user_by_email(db, user_in.email)
if existing_user:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already registered",
    )
```
- PostgreSQL'den async query ile kullanıcı aranır
- Email unique constraint ile de korunur

2. **Password Hashing:**
```python
hashed_password = hash_password(user_in.password)
```
- Şifre bcrypt ile hash'lenir (app/utils/security.py)
- Salt otomatik eklenir
- bcrypt cost factor: 12 (varsayılan)

3. **User Creation (PostgreSQL):**
```python
user_data = {
    "id": uuid.uuid4(),
    "email": user_in.email,
    "full_name": user_in.full_name,
    "hashed_password": hashed_password,
    "is_active": True,
    "is_verified": False,
}

new_user = User(**user_data)
db.add(new_user)
await db.commit()
await db.refresh(new_user)
return new_user
```
- User kaydı PostgreSQL `users` tablosuna eklenir
- created_at ve updated_at otomatik set edilir (timezone-aware)
- Transaction commit ile persist edilir

### 4. Security Layer
**Dosya:** `app/utils/security.py`

```python
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')
```

**Güvenlik Özellikleri:**
- bcrypt algoritması (industry standard)
- Otomatik salt generation
- Cost factor: 12 (2^12 = 4096 iterations)
- bcrypt version: 4.1.3 (passlib uyumlu)

## Database İşlemleri

### Production Implementation (✅ Deployed)
**Tablo:** `users`
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  hashed_password VARCHAR NOT NULL,
  full_name VARCHAR NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  is_verified BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL,
  last_login TIMESTAMPTZ
);

CREATE UNIQUE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_id ON users(id);
```

**SQLAlchemy Model:**
```python
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    last_login = Column(DateTime(timezone=True), nullable=True)
```

**Service Layer Query:**
```python
from app.services import auth_service

# Kullanıcı kaydı
user = await auth_service.register_user(db, user_in)

# Email kontrolü (internal)
existing_user = await auth_service.get_user_by_email(db, email)
```

## Kullanım Örnekleri

### cURL
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ali@example.com",
    "password": "SecurePass123",
    "full_name": "Ali Yılmaz"
  }'
```

### Python (httpx)
```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/auth/register",
    json={
        "email": "ali@example.com",
        "password": "SecurePass123",
        "full_name": "Ali Yılmaz"
    }
)

if response.status_code == 201:
    user = response.json()
    print(f"User created: {user['id']}")
else:
    print(f"Error: {response.json()['detail']}")
```

### JavaScript (fetch)
```javascript
const response = await fetch('http://localhost:8000/api/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'ali@example.com',
    password: 'SecurePass123',
    full_name: 'Ali Yılmaz'
  })
});

if (response.ok) {
  const user = await response.json();
  console.log('User created:', user.id);
} else {
  const error = await response.json();
  console.error('Error:', error.detail);
}
```

## Güvenlik Notları

1. **Password Hashing:**
   - Şifreler plain text olarak asla saklanmaz
   - bcrypt ile hash'lenir (one-way function)
   - Salt otomatik eklenir (rainbow table attack'a karşı)

2. **Email Validation:**
   - Pydantic EmailStr validator kullanılır
   - RFC 5322 email formatı kontrolü

3. **Rate Limiting (✅ Implemented):**
   - SlowAPI kullanılarak implement edildi
   - 5 request/minute per IP
   - Brute-force registration attack'a karşı koruma

4. **HTTPS:**
   - Production'da HTTPS zorunlu olacak
   - Şifreler encrypted channel üzerinden iletilecek

5. **Password Requirements:**
   - Minimum 8 karakter
   - TODO: Komplekslik gereksinimleri eklenebilir (büyük harf, rakam, özel karakter)

## Test Senaryoları

### Başarılı Kayıt
```bash
# Request
POST /api/auth/register
{
  "email": "test@example.com",
  "password": "Password123",
  "full_name": "Test User"
}

# Expected Response: 201 Created
{
  "id": "...",
  "email": "test@example.com",
  "full_name": "Test User"
}
```

### Duplicate Email
```bash
# Request (email zaten kayıtlı)
POST /api/auth/register
{
  "email": "existing@example.com",
  "password": "Password123",
  "full_name": "Test User"
}

# Expected Response: 400 Bad Request
{
  "detail": "Email already registered"
}
```

### Invalid Email Format
```bash
# Request
POST /api/auth/register
{
  "email": "invalid-email",
  "password": "Password123",
  "full_name": "Test User"
}

# Expected Response: 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address"
    }
  ]
}
```

### Short Password
```bash
# Request
POST /api/auth/register
{
  "email": "test@example.com",
  "password": "short",
  "full_name": "Test User"
}

# Expected Response: 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters"
    }
  ]
}
```

## İlgili Endpoint'ler

- [POST /api/auth/login](02-login.md) - Kullanıcı girişi (JWT token alımı)
- [GET /api/auth/me](03-get-current-user.md) - Mevcut kullanıcı bilgilerini getir

## Değişiklik Geçmişi

- **v1.0.0** (2026-01-18): Initial mock implementation
- **v2.0.0** (2026-01-18): Production implementation
  - ✅ PostgreSQL `users` tablosu entegrasyonu
  - ✅ Service layer (auth_service.py)
  - ✅ Rate limiting (5/minute per IP)
  - ✅ User status fields (is_active, is_verified)
  - ✅ Timestamp tracking (created_at, updated_at, last_login)
  - ✅ Comprehensive test suite (35 tests)
