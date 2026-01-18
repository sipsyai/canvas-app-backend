# POST /api/auth/logout

## Genel Bakış
Kullanıcının JWT token'ını revoke eder (logout işlemi). Token blacklist'e eklenir ve bir daha kullanılamaz.

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/auth/logout`
- **Authentication:** JWT Bearer Token (Zorunlu)
- **Response Status:** 204 No Content

## Request Format

### Headers
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Request Body
Yok.

## Response Format

### Success Response (204 No Content)
Boş response (body yok).

### Error Responses

#### 403 Forbidden - Missing Token
```json
{
  "detail": "Not authenticated"
}
```

#### 401 Unauthorized - Invalid Token
```json
{
  "detail": "Invalid or expired token"
}
```

## Kod Akışı

### 1. Router Layer
**Dosya:** `app/routers/auth.py`

```python
@router.post("/logout", status_code=204)
async def logout_user(
    request: Request,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Extract token from Authorization header
    from fastapi.security import HTTPBearer
    security = HTTPBearer()
    credentials = await security(request)
    token = credentials.credentials

    # Blacklist the token
    await auth_service.blacklist_token(db, token, user_id)

    return None  # 204 No Content
```

### 2. Service Layer
**Dosya:** `app/services/auth_service.py`

```python
async def blacklist_token(
    self,
    db: AsyncSession,
    token: str,
    user_id: uuid.UUID,
) -> None:
    """Blacklist a token (logout)"""
    # Decode token to get JTI and expiration
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    jti = payload.get("jti")
    exp = payload.get("exp")

    # Convert exp timestamp to datetime
    expires_at = datetime.fromtimestamp(exp, tz=UTC)

    # Add to blacklist
    blacklist_entry = TokenBlacklist(
        jti=jti,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(blacklist_entry)
    await db.commit()
```

### 3. Token Blacklist Check
**Dosya:** `app/middleware/auth.py`

Her protected endpoint çağrısında token blacklist'te kontrol edilir:

```python
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> uuid.UUID:
    # ... token decode ...

    jti: str = payload.get("jti")

    # Check if token is blacklisted
    if jti:
        from app.services import auth_service
        is_blacklisted = await auth_service.is_token_blacklisted(db, jti)
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

    return user_id
```

## Database İşlemleri

### TokenBlacklist Table
```sql
CREATE TABLE token_blacklist (
  jti VARCHAR PRIMARY KEY,            -- JWT ID (unique token identifier)
  user_id UUID NOT NULL,              -- User who owned this token
  expires_at TIMESTAMPTZ NOT NULL,    -- Token expiration time
  blacklisted_at TIMESTAMPTZ NOT NULL -- When token was blacklisted
);

CREATE INDEX ix_token_blacklist_jti ON token_blacklist(jti);
CREATE INDEX ix_token_blacklist_user_id ON token_blacklist(user_id);
CREATE INDEX ix_token_blacklist_expires_at ON token_blacklist(expires_at);
```

### Model
```python
class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    jti = Column(String, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    blacklisted_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
```

## JWT Token ID (JTI)

### Token Structure with JTI
Login sırasında oluşturulan JWT token'da unique `jti` (JWT ID) bulunur:

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "jti": "7c9e6679-7425-40de-944b-e07fc1f90ae7",  // Unique token ID
  "exp": 1737218400
}
```

JTI kullanımı:
- Her token için unique ID
- Logout sırasında bu ID blacklist'e eklenir
- Token expire olana kadar blacklist'te kalır
- Expire olduktan sonra silinebilir (cleanup job)

## Kullanım Örnekleri

### cURL
```bash
# 1. Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=Password123" \
  | jq -r '.access_token')

# 2. Use token (works)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 3. Logout
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"

# 4. Try to use same token again (fails)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
# Returns: {"detail": "Token has been revoked"}
```

### Python (httpx)
```python
import httpx

# Login
login_response = httpx.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "user@example.com", "password": "Password123"}
)
token = login_response.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
user_response = httpx.get("http://localhost:8000/api/auth/me", headers=headers)
print(user_response.json())  # Works

# Logout
logout_response = httpx.post("http://localhost:8000/api/auth/logout", headers=headers)
print(logout_response.status_code)  # 204

# Try to use token again
try:
    httpx.get("http://localhost:8000/api/auth/me", headers=headers)
except httpx.HTTPStatusError as e:
    print(e.response.json())  # {"detail": "Token has been revoked"}
```

### JavaScript (fetch)
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    username: 'user@example.com',
    password: 'Password123'
  })
});

const { access_token } = await loginResponse.json();

// Use token
const headers = { 'Authorization': `Bearer ${access_token}` };
const userResponse = await fetch('http://localhost:8000/api/auth/me', { headers });
console.log(await userResponse.json());  // Works

// Logout
const logoutResponse = await fetch('http://localhost:8000/api/auth/logout', {
  method: 'POST',
  headers
});
console.log(logoutResponse.status);  // 204

// Clear token from storage
localStorage.removeItem('access_token');

// Try to use token again (will fail)
const failedResponse = await fetch('http://localhost:8000/api/auth/me', { headers });
console.log(await failedResponse.json());  // {"detail": "Token has been revoked"}
```

## Frontend Integration

### React Example
```typescript
import { useState } from 'react';

export function useAuth() {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('access_token')
  );

  const logout = async () => {
    if (!token) return;

    try {
      // Call logout endpoint
      await fetch('http://localhost:8000/api/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always remove token from storage
      localStorage.removeItem('access_token');
      setToken(null);
    }
  };

  return { logout };
}
```

## Güvenlik Notları

1. **Token Revocation:**
   - Logout sonrası token kullanılamaz
   - Blacklist database'de persist edilir
   - Expired token'lar cleanup job ile silinebilir

2. **Multiple Devices:**
   - Her device için farklı token (farklı JTI)
   - Logout sadece current token'ı revoke eder
   - Tüm device'lardan çıkış için: user'ın tüm token'larını blacklist'e ekle

3. **Token Cleanup:**
   - Expired token'lar blacklist'ten silinebilir
   - Cron job ile günlük cleanup önerilir
   - WHERE expires_at < NOW()

4. **Performance:**
   - Blacklist check her protected endpoint'te yapılır
   - Database query overhead'i minimal (indexed jti)
   - Redis cache ile optimize edilebilir

## Token Cleanup Script

### SQL
```sql
-- Delete expired tokens from blacklist
DELETE FROM token_blacklist
WHERE expires_at < NOW();
```

### Python (Alembic migration or cron job)
```python
from datetime import UTC, datetime
from sqlalchemy import delete
from app.models import TokenBlacklist

async def cleanup_expired_tokens(db: AsyncSession):
    """Remove expired tokens from blacklist"""
    stmt = delete(TokenBlacklist).where(
        TokenBlacklist.expires_at < datetime.now(UTC)
    )
    await db.execute(stmt)
    await db.commit()
```

## Test Senaryoları

### Başarılı Logout
```bash
# Request
POST /api/auth/logout
Authorization: Bearer eyJhbGci...

# Expected Response: 204 No Content
(empty body)
```

### Logout Without Token
```bash
# Request
POST /api/auth/logout

# Expected Response: 403 Forbidden
{
  "detail": "Not authenticated"
}
```

### Use Revoked Token
```bash
# Request (after logout)
GET /api/auth/me
Authorization: Bearer eyJhbGci... (blacklisted)

# Expected Response: 401 Unauthorized
{
  "detail": "Token has been revoked"
}
```

## İlgili Endpoint'ler

- [POST /api/auth/login](02-login.md) - Kullanıcı girişi (token alımı)
- [GET /api/auth/me](03-get-current-user.md) - Mevcut kullanıcı bilgilerini getir
- [POST /api/auth/register](01-register.md) - Kullanıcı kaydı

## Best Practices

1. **Always Clear Token:**
   - Logout endpoint çağrılsa da çağrılmasa da token'ı localStorage'dan sil
   - Network error durumunda bile token silinmeli

2. **Logout All Devices:**
   - User'ın tüm token'larını blacklist'e ekle
   - user_id ile query: SELECT jti FROM active_sessions WHERE user_id = ?

3. **Session Timeout:**
   - Frontend'de token expiration'ı track et
   - Expire olmadan önce refresh veya re-login iste

4. **Graceful Degradation:**
   - Logout endpoint fail olsa bile token'ı sil
   - User experience öncelikli

## Değişiklik Geçmişi

- **v2.0.0** (2026-01-18): Token revocation (logout) implemented
  - ✅ Token blacklist database table
  - ✅ JTI (JWT ID) in token payload
  - ✅ Blacklist check in middleware
  - ✅ Logout endpoint
  - ✅ Comprehensive tests
