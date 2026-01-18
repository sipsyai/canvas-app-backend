# GET /api/auth/me

## Genel Bakış
JWT token ile authenticate edilmiş kullanıcının bilgilerini döner.

## Endpoint Bilgileri
- **Method:** GET
- **Path:** `/api/auth/me`
- **Authentication:** JWT Bearer Token (Zorunlu)
- **Response Status:** 200 OK

## Request Format

### Headers
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**NOT:** `Bearer` prefix zorunludur (OAuth2 standardı).

### Query Parameters
Yok.

### Request Body
Yok.

## Response Format

### Success Response (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Ali Yılmaz"
}
```

### Response Schema (UserResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | string (UUID) | Kullanıcı ID'si |
| email | string | Kullanıcı email adresi |
| full_name | string | Kullanıcı tam adı |

### Error Responses

#### 401 Unauthorized - Missing Token
```json
{
  "detail": "Not authenticated"
}
```

#### 401 Unauthorized - Invalid Token
```json
{
  "detail": "Could not validate credentials"
}
```

#### 401 Unauthorized - Expired Token
```json
{
  "detail": "Token has expired"
}
```

#### 404 Not Found - User Not Found
```json
{
  "detail": "User not found"
}
```

## Kod Akışı

### 1. Router Layer
**Dosya:** `app/routers/auth.py`

```python
@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
```

**Görevleri:**
- `get_current_user_id` dependency ile JWT'den user ID'yi extract eder
- Database session'ı alır
- User bilgilerini response olarak döner

### 2. Authentication Middleware
**Dosya:** `app/middleware/auth.py`

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> uuid.UUID:
    """
    Extract and validate user ID from JWT token.

    Raises HTTPException if token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        return uuid.UUID(user_id)

    except JWTError:
        raise credentials_exception
```

**Adımlar:**

1. **Token Extraction:**
   - `Authorization: Bearer <token>` header'ından token alınır
   - OAuth2PasswordBearer dependency kullanılır
   - Header yoksa 401 Unauthorized döner

2. **Token Decode:**
   - JWT token decode edilir (signature verify edilir)
   - SECRET_KEY ile imza doğrulanır
   - Algorithm: HS256

3. **Payload Validation:**
   - `sub` claim'den user ID alınır
   - Expiration time (`exp`) otomatik kontrol edilir
   - Süresi dolmuşsa jwt.ExpiredSignatureError fırlatır

4. **User ID Extraction:**
   - User ID UUID formatına çevrilir
   - Router function'a return edilir

### 3. Business Logic Layer
**Dosya:** `app/routers/auth.py`

```python
# Find user by ID (mock - replace with database query)
user = next(
    (u for u in MOCK_USERS.values() if u["id"] == str(user_id)),
    None,
)

if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )

return UserResponse(
    id=user["id"],
    email=user["email"],
    full_name=user["full_name"],
)
```

**NOT:** Şu anda MOCK_USERS kullanılıyor. Production'da PostgreSQL'den query edilecek:

```python
from app.models import User
from sqlalchemy import select

# Get user from database
result = await db.execute(
    select(User).where(User.id == user_id)
)
user = result.scalar_one_or_none()

if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )

return user
```

## JWT Token Validation Flow

```
1. Client Request
   ↓
   Authorization: Bearer eyJhbGci...

2. OAuth2PasswordBearer
   ↓
   Extract token from header

3. jwt.decode()
   ↓
   Verify signature with SECRET_KEY
   Check expiration time (exp claim)

4. Extract user_id (sub claim)
   ↓
   Convert to UUID

5. Database Query
   ↓
   Find user by ID

6. Return UserResponse
```

## Security Layer

### Token Validation
**Dosya:** `app/utils/security.py` & `app/middleware/auth.py`

**Security Checks:**

1. **Signature Verification:**
```python
payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
```
- Token'ın SECRET_KEY ile imzalandığı doğrulanır
- Signature yanlışsa jwt.InvalidSignatureError

2. **Expiration Check:**
```python
# Otomatik kontrol (jwt.decode içinde)
if current_time > payload["exp"]:
    raise jwt.ExpiredSignatureError
```
- Token'ın süresi dolmuşsa hata fırlatır

3. **Algorithm Validation:**
```python
algorithms=[JWT_ALGORITHM]  # Only HS256 allowed
```
- Sadece HS256 algoritmasına izin verilir
- Algorithm confusion attack'a karşı

## Kullanım Örnekleri

### cURL
```bash
# 1. Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ali@example.com&password=SecurePass123" \
  | jq -r '.access_token')

# 2. Get current user
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Python (httpx)
```python
import httpx

# 1. Login
login_response = httpx.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "ali@example.com", "password": "SecurePass123"}
)
access_token = login_response.json()["access_token"]

# 2. Get current user
user_response = httpx.get(
    "http://localhost:8000/api/auth/me",
    headers={"Authorization": f"Bearer {access_token}"}
)

if user_response.status_code == 200:
    user = user_response.json()
    print(f"Logged in as: {user['full_name']} ({user['email']})")
else:
    print(f"Error: {user_response.json()['detail']}")
```

### JavaScript (fetch)
```javascript
// 1. Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    username: 'ali@example.com',
    password: 'SecurePass123'
  })
});

const { access_token } = await loginResponse.json();

// 2. Get current user
const userResponse = await fetch('http://localhost:8000/api/auth/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

if (userResponse.ok) {
  const user = await userResponse.json();
  console.log(`Logged in as: ${user.full_name} (${user.email})`);
} else {
  const error = await userResponse.json();
  console.error('Error:', error.detail);
}
```

### Axios (with interceptor)
```javascript
import axios from 'axios';

// Setup axios with default authorization header
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Intercept requests to add token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login
const loginResponse = await api.post('/auth/login',
  new URLSearchParams({
    username: 'ali@example.com',
    password: 'SecurePass123'
  }),
  { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
);

localStorage.setItem('access_token', loginResponse.data.access_token);

// Get current user (token automatically added)
const userResponse = await api.get('/auth/me');
console.log('Current user:', userResponse.data);
```

## Güvenlik Notları

1. **Token Storage:**
   - Frontend'de localStorage veya sessionStorage'da saklanır
   - XSS risk: Token çalınabilir → Content Security Policy kullanılmalı
   - HTTPS zorunlu (token encrypted channel'dan gider)

2. **Token Expiration:**
   - 1 saatlik geçerlilik
   - Süresi dolmuş token kullanılamaz
   - Client refresh gerektirir (yeniden login veya refresh token)

3. **WWW-Authenticate Header:**
   - 401 response'larda `WWW-Authenticate: Bearer` header döner
   - OAuth2 standardı gereği

4. **User ID in JWT:**
   - Token'da user ID (`sub` claim) saklanır
   - Email de saklanır (opsiyonel, bilgi amaçlı)
   - Şifre asla saklanmaz

## Test Senaryoları

### Başarılı Request
```bash
# Request
GET /api/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Expected Response: 200 OK
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "full_name": "Test User"
}
```

### Missing Token
```bash
# Request (Authorization header yok)
GET /api/auth/me

# Expected Response: 401 Unauthorized
{
  "detail": "Not authenticated"
}
```

### Invalid Token
```bash
# Request
GET /api/auth/me
Authorization: Bearer invalid.token.here

# Expected Response: 401 Unauthorized
{
  "detail": "Could not validate credentials"
}
```

### Expired Token
```bash
# Request (1 saatten eski token)
GET /api/auth/me
Authorization: Bearer eyJhbGci... (expired)

# Expected Response: 401 Unauthorized
{
  "detail": "Token has expired"
}
```

### Wrong Prefix
```bash
# Request (Bearer prefix eksik)
GET /api/auth/me
Authorization: eyJhbGci...

# Expected Response: 401 Unauthorized
{
  "detail": "Not authenticated"
}
```

## Frontend Integration

### React Hook Example
```typescript
import { useState, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  full_name: string;
}

export function useCurrentUser() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('access_token');

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/api/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setUser(data);
        } else {
          // Token invalid or expired
          localStorage.removeItem('access_token');
          setError('Session expired');
        }
      } catch (err) {
        setError('Network error');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  return { user, loading, error };
}
```

## İlgili Endpoint'ler

- [POST /api/auth/login](02-login.md) - Kullanıcı girişi (token alımı)
- [POST /api/auth/register](01-register.md) - Kullanıcı kaydı

## Protected Endpoints Pattern

Bu endpoint, diğer protected endpoint'ler için şablon oluşturur:

```python
from app.middleware.auth import get_current_user_id

@router.post("/protected-endpoint")
async def protected_function(
    user_id: uuid.UUID = Depends(get_current_user_id),  # JWT required
    db: AsyncSession = Depends(get_db),
):
    # user_id authenticated user'ın ID'si
    # Business logic here
    pass
```

**Örnekler:**
- `/api/fields` - Field CRUD (JWT required)
- `/api/objects` - Object CRUD (JWT required)
- `/api/records` - Record CRUD (JWT required)

## Değişiklik Geçmişi

- **v1.0.0** (2026-01-18): Initial implementation with JWT authentication
- **TODO:** PostgreSQL user query integration
- **TODO:** User profile update endpoint
