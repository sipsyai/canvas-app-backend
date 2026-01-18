# Authentication API

## Genel Bakış

Canvas App Backend authentication sistemi JWT (JSON Web Token) tabanlı stateless authentication kullanır. PostgreSQL database ile entegre edilmiş, production-ready bir implementasyondur.

## Temel Özellikler

✅ **JWT Authentication** - Stateless token-based auth
✅ **PostgreSQL Integration** - User data persistent storage
✅ **Rate Limiting** - Brute-force attack protection
✅ **Token Revocation** - Logout with blacklist
✅ **Password Hashing** - bcrypt with salt
✅ **Service Layer** - Clean code architecture
✅ **Comprehensive Tests** - 35 test scenarios

## Endpoint'ler

| Method | Endpoint | Açıklama | Auth | Rate Limit |
|--------|----------|----------|------|------------|
| POST | `/api/auth/register` | Yeni kullanıcı kaydı | ❌ | 5/min |
| POST | `/api/auth/login` | Kullanıcı girişi (JWT token) | ❌ | 10/min |
| GET | `/api/auth/me` | Mevcut kullanıcı bilgisi | ✅ | - |
| POST | `/api/auth/logout` | Çıkış (token revoke) | ✅ | - |

## Quick Start

### 1. Kullanıcı Kaydı
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "full_name": "Ali Yılmaz"
  }'
```

**Response:**
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

### 2. Login (Token Alma)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePass123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 3. Protected Endpoint Kullanımı
```bash
# Token'ı değişkene kaydet
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Protected endpoint çağır
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Ali Yılmaz",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-01-18T17:30:00.000Z",
  "last_login": "2026-01-18T17:35:00.000Z"
}
```

### 4. Logout
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

**Response:** 204 No Content

## Authentication Flow

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     │ 1. POST /register
     │    {email, password, full_name}
     ▼
┌─────────────┐
│   Server    │────► PostgreSQL (users table)
└─────┬───────┘
      │
      │ 2. POST /login
      │    {username, password}
      ▼
┌─────────────┐
│   Server    │────► Verify password (bcrypt)
└─────┬───────┘      Generate JWT (with JTI)
      │
      │ 3. Return JWT Token
      ▼
┌─────────┐
│ Client  │────► Store token (localStorage)
└────┬────┘
     │
     │ 4. GET /protected-endpoint
     │    Authorization: Bearer {token}
     ▼
┌─────────────┐
│   Server    │────► Verify JWT signature
└─────┬───────┘      Check token blacklist
      │              Extract user_id from token
      │
      │ 5. Return protected data
      ▼
┌─────────┐
│ Client  │
└────┬────┘
     │
     │ 6. POST /logout
     ▼
┌─────────────┐
│   Server    │────► Add token to blacklist
└─────┬───────┘      (by JTI)
      │
      │ 7. 204 No Content
      ▼
┌─────────┐
│ Client  │────► Clear token from storage
└─────────┘
```

## JWT Token Structure

### Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // User ID
  "email": "user@example.com",                     // User email
  "jti": "7c9e6679-7425-40de-944b-e07fc1f90ae7",  // JWT ID (for revocation)
  "exp": 1737218400,                               // Expiration timestamp
  "iat": 1737214800                                // Issued at timestamp
}
```

### Signature
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

## Database Schema

### Users Table
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

### Token Blacklist Table
```sql
CREATE TABLE token_blacklist (
  jti VARCHAR PRIMARY KEY,
  user_id UUID NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  blacklisted_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX ix_token_blacklist_jti ON token_blacklist(jti);
CREATE INDEX ix_token_blacklist_user_id ON token_blacklist(user_id);
CREATE INDEX ix_token_blacklist_expires_at ON token_blacklist(expires_at);
```

## Security Features

### 1. Password Security
- **bcrypt hashing** with automatic salt
- **Cost factor:** 12 (4096 iterations)
- **Version:** bcrypt 4.1.3 (passlib compatible)
- Passwords never stored in plain text

### 2. JWT Security
- **Algorithm:** HS256 (HMAC-SHA256)
- **Secret Key:** Strong random key (32 bytes)
- **Expiration:** 1 hour
- **JTI:** Unique token identifier for revocation

### 3. Rate Limiting
- **Registration:** 5 requests/minute per IP
- **Login:** 10 requests/minute per IP
- **Implementation:** SlowAPI
- Protection against brute-force attacks

### 4. Token Revocation
- Logout adds token to blacklist (by JTI)
- Blacklist checked on every protected request
- Expired tokens cleaned up automatically

### 5. Error Messages
- Generic messages to prevent user enumeration
- Same error for "user not found" vs "wrong password"
- Detailed logs server-side only

## Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/canvasapp

# JWT
SECRET_KEY=your-secret-key-here  # Generate: openssl rand -hex 32
JWT_ALGORITHM=HS256

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=true
```

### Generate Secret Key
```bash
openssl rand -hex 32
```

## Code Architecture

### Directory Structure
```
app/
├── routers/
│   └── auth.py              # Endpoint handlers
├── services/
│   └── auth_service.py      # Business logic
├── models/
│   ├── user.py              # User SQLAlchemy model
│   └── token_blacklist.py   # TokenBlacklist model
├── schemas/
│   └── auth.py              # Pydantic request/response schemas
├── middleware/
│   └── auth.py              # JWT verification (get_current_user_id)
└── utils/
    ├── security.py          # Password hashing, JWT creation
    └── rate_limit.py        # Rate limiting config
```

### Service Layer Pattern
```python
# Router (app/routers/auth.py)
@router.post("/register")
async def register_user(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register_user(db, user_in)
    return user

# Service (app/services/auth_service.py)
class AuthService:
    async def register_user(self, db: AsyncSession, user_in: UserRegister) -> User:
        # Business logic here
        existing_user = await self.get_user_by_email(db, user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = hash_password(user_in.password)
        new_user = User(email=user_in.email, hashed_password=hashed_password, ...)
        db.add(new_user)
        await db.commit()
        return new_user
```

## Testing

### Run Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run all auth tests
pytest tests/test_routers/test_auth.py -v

# Run with coverage
pytest tests/test_routers/test_auth.py --cov=app --cov-report=html
```

### Test Coverage
- ✅ 35 comprehensive test scenarios
- ✅ Registration (success, duplicate, validation)
- ✅ Login (success, wrong password, inactive user)
- ✅ Protected endpoints (token validation)
- ✅ Logout and token blacklist
- ✅ Password security
- ✅ Database integration
- ✅ Edge cases

## Error Codes

| Status | Kod | Açıklama |
|--------|-----|----------|
| 200 | OK | Başarılı request (login, get user) |
| 201 | Created | Kullanıcı başarıyla oluşturuldu |
| 204 | No Content | Logout başarılı |
| 400 | Bad Request | Email zaten kayıtlı |
| 401 | Unauthorized | Geçersiz token veya şifre |
| 403 | Forbidden | Token yok veya inactive user |
| 404 | Not Found | Kullanıcı bulunamadı |
| 422 | Unprocessable Entity | Validation hatası (email format, password length) |
| 429 | Too Many Requests | Rate limit aşıldı |

## Best Practices

### Frontend Integration
```typescript
// Store token
localStorage.setItem('access_token', token);

// Add to all API requests
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
};

// Handle 401 (token expired)
if (response.status === 401) {
  localStorage.removeItem('access_token');
  redirectToLogin();
}

// Logout
await fetch('/api/auth/logout', {
  method: 'POST',
  headers
});
localStorage.removeItem('access_token');
```

### Security Checklist
- [ ] HTTPS enabled in production
- [ ] Strong SECRET_KEY (32+ bytes random)
- [ ] Different SECRET_KEY for dev/staging/production
- [ ] Rate limiting configured
- [ ] .env file in .gitignore
- [ ] Content Security Policy headers
- [ ] CORS origins restricted
- [ ] Token expiration monitored
- [ ] Blacklist cleanup job configured

## Troubleshooting

### Common Issues

**1. bcrypt version error:**
```bash
pip install bcrypt==4.1.3
```

**2. Token expires too quickly:**
Edit `app/utils/security.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour (default)
```

**3. Rate limit too strict:**
Edit `app/routers/auth.py`:
```python
@limiter.limit("10/minute")  # Increase limit
```

**4. CORS error:**
Add frontend URL to `.env`:
```bash
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

## API Documentation Links

Detaylı dokümantasyon için:
- [01-register.md](01-register.md) - Kullanıcı kaydı
- [02-login.md](02-login.md) - Kullanıcı girişi
- [03-get-current-user.md](03-get-current-user.md) - Mevcut kullanıcı
- [04-logout.md](04-logout.md) - Çıkış yapma

## Changelog

### v2.0.0 (2026-01-18) - Production Ready
- ✅ PostgreSQL integration (users + token_blacklist tables)
- ✅ Service layer architecture
- ✅ Rate limiting (SlowAPI)
- ✅ Token revocation (logout with blacklist)
- ✅ Comprehensive test suite (35 tests)
- ✅ User status tracking (is_active, is_verified)
- ✅ Timestamp tracking (created_at, updated_at, last_login)

### v1.0.0 (2026-01-18) - Initial Implementation
- Basic JWT authentication
- Mock user storage (in-memory)
- Password hashing (bcrypt)

## Support

For issues or questions:
- GitHub Issues: [canvas-app-backend/issues](https://github.com/yourusername/canvas-app-backend/issues)
- Documentation: `/docs`
- API Docs: `http://localhost:8000/docs` (Swagger UI)
