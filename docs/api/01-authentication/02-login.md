# POST /api/auth/login

## Genel Bakış
Kullanıcı girişi yapar ve JWT access token döner. OAuth2 Password Flow kullanır.

## Endpoint Bilgileri
- **Method:** POST
- **Path:** `/api/auth/login`
- **Authentication:** Gerekli değil (Public endpoint)
- **Response Status:** 200 OK
- **Content-Type:** `application/x-www-form-urlencoded` (OAuth2 standardı)

## Request Format

### Form Data (application/x-www-form-urlencoded)
```
username=user@example.com&password=SecurePassword123
```

**NOT:** OAuth2 standardı gereği:
- Email alanı `username` olarak gönderilir
- Content-Type `application/x-www-form-urlencoded` olmalıdır
- JSON değil, form data formatı kullanılır

### Request Schema (OAuth2PasswordRequestForm)
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| username | string | Evet | Kullanıcı email adresi |
| password | string | Evet | Kullanıcı şifresi |
| scope | string | Hayır | OAuth2 scope (kullanılmıyor) |
| grant_type | string | Hayır | OAuth2 grant type (varsayılan: password) |

## Response Format

### Success Response (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Response Schema (TokenResponse)
| Alan | Tip | Açıklama |
|------|-----|----------|
| access_token | string | JWT access token |
| token_type | string | Token tipi (her zaman "bearer") |
| expires_in | integer | Token geçerlilik süresi (saniye) - 3600 = 1 saat |

### Error Responses

#### 401 Unauthorized - Invalid Credentials
```json
{
  "detail": "Incorrect email or password"
}
```

#### 422 Unprocessable Entity - Missing Fields
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "username"],
      "msg": "Field required"
    }
  ]
}
```

## Kod Akışı

### 1. Router Layer
**Dosya:** `app/routers/auth.py`

```python
@router.post("/login", response_model=TokenResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
```

**Görevleri:**
- OAuth2PasswordRequestForm dependency ile form data'yı parse eder
- Database session'ı dependency injection ile alır
- Business logic'i çalıştırır
- JWT token ile response döner

### 2. Business Logic Layer

**Adımlar:**

1. **Kullanıcı Bulma:**
```python
user = MOCK_USERS.get(form_data.username)
if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
    )
```
- Email (username) ile kullanıcı aranır
- Kullanıcı bulunamazsa 401 döner

2. **Şifre Doğrulama:**
```python
if not verify_password(form_data.password, user["hashed_password"]):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
    )
```
- Girilen şifre bcrypt ile doğrulanır
- Yanlış şifrede 401 döner
- Güvenlik: "user not found" ve "wrong password" aynı hata mesajı (timing attack'a karşı)

3. **JWT Token Oluşturma:**
```python
access_token = create_access_token(
    data={"sub": user["id"], "email": user["email"]},
    expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
)
```
- User ID ve email payload'a eklenir
- 1 saatlik expiration time set edilir
- Token imzalanır

### 3. Security Layer
**Dosya:** `app/utils/security.py`

#### Password Verification
```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash"""
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)
```

**Güvenlik Özellikleri:**
- Constant-time comparison (timing attack'a karşı)
- bcrypt.checkpw kullanır
- Salt otomatik hash'ten extract edilir

#### JWT Token Creation
```python
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt
```

**JWT Özellikleri:**
- Algorithm: HS256 (HMAC-SHA256)
- Secret Key: Environment variable'dan alınır
- Payload:
  - `sub`: User ID (subject)
  - `email`: User email
  - `exp`: Expiration time (Unix timestamp)
  - `iat`: Issued at time (otomatik eklenir)

**Örnek JWT Payload:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "exp": 1737218400,
  "iat": 1737214800
}
```

## JWT Token Yapısı

### Token Format
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJleHAiOjE3MzcyMTg0MDB9.signature
```

**3 Part Structure:**
1. **Header** (Algorithm + Type):
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

2. **Payload** (User data + expiration):
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "exp": 1737218400
}
```

3. **Signature:**
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

### Token Kullanımı
Token, sonraki isteklerde `Authorization` header'ında gönderilir:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Configuration

### Environment Variables
**Dosya:** `.env`
```bash
SECRET_KEY=your-secret-key-here  # Generate: openssl rand -hex 32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60  # 1 hour
```

**Config Dosyası:** `app/config.py`
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
```

## Kullanım Örnekleri

### cURL
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ali@example.com&password=SecurePass123"
```

### Python (httpx)
```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/auth/login",
    data={
        "username": "ali@example.com",
        "password": "SecurePass123"
    }
)

if response.status_code == 200:
    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"Token: {access_token}")
    print(f"Expires in: {token_data['expires_in']} seconds")
else:
    print(f"Login failed: {response.json()['detail']}")
```

### JavaScript (fetch)
```javascript
const formData = new URLSearchParams();
formData.append('username', 'ali@example.com');
formData.append('password', 'SecurePass123');

const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: formData
});

if (response.ok) {
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  console.log('Login successful');
} else {
  const error = await response.json();
  console.error('Login failed:', error.detail);
}
```

### Token ile Protected Endpoint Çağrısı
```bash
# 1. Login (token al)
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ali@example.com&password=SecurePass123" \
  | jq -r '.access_token')

# 2. Protected endpoint çağır
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## Güvenlik Notları

1. **Password Security:**
   - Şifreler bcrypt ile hash'lenir
   - Constant-time comparison (timing attack prevention)
   - Aynı error message (user enumeration attack prevention)

2. **JWT Security:**
   - HS256 algorithm (symmetric key)
   - SECRET_KEY güvenli saklanmalı (environment variable)
   - Token'da sensitive data saklanmamalı (email OK, password NO)
   - 1 saatlik expiration (compromise risk reduction)

3. **HTTPS:**
   - Production'da HTTPS zorunlu
   - Token ve şifre encrypted channel'dan gider

4. **Rate Limiting:**
   - TODO: Brute force attack prevention için rate limiting eklenecek
   - Örn: 5 failed login attempt → 15 dakika ban

5. **Token Revocation:**
   - TODO: Logout sonrası token blacklist'e eklenecek
   - Redis ile revoked tokens cache'lenebilir

## Test Senaryoları

### Başarılı Login
```bash
# Request
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=test@example.com&password=Password123

# Expected Response: 200 OK
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Invalid Email
```bash
# Request
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=nonexistent@example.com&password=Password123

# Expected Response: 401 Unauthorized
{
  "detail": "Incorrect email or password"
}
```

### Wrong Password
```bash
# Request
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=test@example.com&password=WrongPassword

# Expected Response: 401 Unauthorized
{
  "detail": "Incorrect email or password"
}
```

### Missing Fields
```bash
# Request
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=test@example.com

# Expected Response: 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "password"],
      "msg": "Field required"
    }
  ]
}
```

## Token Decode Örneği

### Python
```python
import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Decode (verify signature)
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    print(f"User ID: {payload['sub']}")
    print(f"Email: {payload['email']}")
    print(f"Expires at: {payload['exp']}")
except jwt.ExpiredSignatureError:
    print("Token expired")
except jwt.InvalidTokenError:
    print("Invalid token")
```

### Online Decoder
[jwt.io](https://jwt.io/) - Token'ı decode edebilirsiniz (signature verify etmez)

## İlgili Endpoint'ler

- [POST /api/auth/register](01-register.md) - Kullanıcı kaydı
- [GET /api/auth/me](03-get-current-user.md) - Mevcut kullanıcı bilgilerini getir (JWT required)

## Best Practices

1. **Token Storage (Frontend):**
   - ✅ localStorage veya sessionStorage
   - ❌ Cookie (CSRF risk, bu projede kullanılmıyor)
   - ✅ Memory (XSS safe ama reload'da kaybolur)

2. **Token Refresh:**
   - TODO: Refresh token mechanism eklenebilir
   - Long-lived refresh token + short-lived access token

3. **Error Handling:**
   - Generic error messages (security)
   - Detailed logging (debugging, backend-only)

## Değişiklik Geçmişi

- **v1.0.0** (2026-01-18): Initial JWT implementation with HS256
- **TODO:** Refresh token mechanism
- **TODO:** Token blacklist (logout)
- **TODO:** Rate limiting
