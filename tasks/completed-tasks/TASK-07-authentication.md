# TASK-07: JWT Authentication

**Phase:** 7/8
**Tahmini Süre:** 1 saat
**Bağımlılık:** Phase 6 (API Routers) ✅
**Durum:** ⏳ Bekliyor

---

## 🎯 Görev Açıklaması

**Supabase Auth entegrasyonu** veya **JWT-based authentication** ekle:
- User registration/login endpoints
- JWT token generation/validation
- Protected routes (authentication required)
- Get current user dependency
- Password hashing (bcrypt)

**ÖNEMLE:** Supabase kullanıyorsan, Supabase Auth'u entegre et. Local development için JWT implementasyonu yap.

---

## 📋 Ön Gereksinimler

- [x] Phase 6 tamamlandı (API routers mevcut)
- [x] python-jose, passlib, bcrypt kurulu
- [x] Supabase credentials (opsiyonel)

---

## 📁 Oluşturulacak Dosyalar

```
app/
├── middleware/
│   ├── __init__.py
│   └── auth.py           # JWT verification middleware
├── routers/
│   └── auth.py           # /api/auth endpoints (NEW)
└── utils/
    ├── __init__.py
    └── security.py       # Password hashing, JWT utils
```

---

## 🔧 Implementation

### app/utils/security.py
```python
"""Security utilities - Password hashing, JWT tokens"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Payload to encode (e.g., {"sub": user_id, "email": "user@example.com"})
        expires_delta: Token expiration time (default: 1 hour)

    Returns:
        JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify JWT token.

    Returns:
        Payload dict if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

---

### app/middleware/auth.py
```python
"""Authentication middleware - JWT verification"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.utils.security import decode_access_token

# HTTP Bearer scheme (extracts token from "Authorization: Bearer <token>" header)
security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Extract and validate JWT token, return user ID.

    Usage in routers:
        @router.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user_id)):
            ...

    Raises:
        HTTPException 401 if token is invalid/expired
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return user_id

async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    """
    Optional authentication - returns user_id if token provided, None otherwise.

    Useful for public endpoints that behave differently for authenticated users.
    """
    if credentials is None:
        return None

    return await get_current_user_id(credentials)
```

---

### app/routers/auth.py (NEW)
```python
"""Authentication endpoints - Register, Login, Get User"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()

# Schemas
class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    full_name: str = Field(..., min_length=1, description="Full name")

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds

# Mock user storage (REPLACE with real database in production!)
# For MVP, use in-memory dict. For production, use auth.users table.
MOCK_USERS = {}

@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(
    user_in: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register new user.

    Example request:
    ```json
    {
        "email": "user@example.com",
        "password": "SecurePassword123",
        "full_name": "Ali Yılmaz"
    }
    ```

    TODO: Store user in auth.users table (Supabase or local PostgreSQL)
    """
    # Check if user already exists
    if user_in.email in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = hash_password(user_in.password)

    # Create user (mock - replace with database)
    user_id = f"user_{len(MOCK_USERS) + 1}"
    MOCK_USERS[user_in.email] = {
        "id": user_id,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "hashed_password": hashed_password,
    }

    return UserResponse(
        id=user_id,
        email=user_in.email,
        full_name=user_in.full_name,
    )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Login user and return JWT token.

    Form data:
    - username: User email
    - password: User password

    Returns JWT token with 1-hour expiration.
    """
    # Get user (mock - replace with database query)
    user = MOCK_USERS.get(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verify password
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create JWT token
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(access_token=access_token)

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current authenticated user.

    Requires "Authorization: Bearer <token>" header.
    """
    # Find user by ID (mock - replace with database query)
    user = next(
        (u for u in MOCK_USERS.values() if u["id"] == user_id),
        None
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

---

### Update app/main.py (Include auth router)
```python
"""Canvas App Backend - Main Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import (
    auth,  # NEW!
    fields,
    objects,
    object_fields,
    records,
    relationships,
    relationship_records,
    applications,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="REST API for Object-Centric No-Code Platform",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])  # NEW!
app.include_router(fields.router, prefix="/api/fields", tags=["Fields"])
app.include_router(objects.router, prefix="/api/objects", tags=["Objects"])
app.include_router(object_fields.router, prefix="/api/object-fields", tags=["Object Fields"])
app.include_router(records.router, prefix="/api/records", tags=["Records"])
app.include_router(relationships.router, prefix="/api/relationships", tags=["Relationships"])
app.include_router(relationship_records.router, prefix="/api/relationship-records", tags=["Relationship Records"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])

# ... (rest of the file)
```

---

### Update app/routers/*.py (Replace mock auth)

**Before (all routers):**
```python
def get_current_user_id() -> str:
    return "user_123"  # Mock
```

**After (all routers):**
```python
from app.middleware.auth import get_current_user_id
# Remove mock function, use real dependency
```

---

## ✅ Başarı Kriterleri

Tamamlandığında şunlar olmalı:

- [ ] `app/utils/security.py` oluşturulmuş (password hashing, JWT utils)
- [ ] `app/middleware/auth.py` oluşturulmuş (JWT verification)
- [ ] `app/routers/auth.py` oluşturulmuş (/register, /login, /me)
- [ ] Tüm router'larda mock auth kaldırılmış, real auth kullanılıyor
- [ ] Password hashing çalışıyor (bcrypt)
- [ ] JWT token generation/verification çalışıyor

**Test:**
```bash
# 1. Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "full_name": "Test User"
  }'

# Expected: 201 Created with user response

# 2. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPassword123"

# Expected: JWT token {"access_token": "eyJ...", "token_type": "bearer"}

# 3. Get current user (with token)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJ..."

# Expected: User info

# 4. Protected endpoint (create field)
curl -X POST http://localhost:8000/api/fields \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "email",
    "label": "Email",
    "type": "email"
  }'

# Expected: 201 Created (if token valid), 401 Unauthorized (if no token)
```

---

## 🐛 Troubleshooting

**Problem: "Invalid token" error even with correct token**
- **Çözüm**: SECRET_KEY doğru olduğundan emin ol (.env dosyasında)

**Problem: Password verification always fails**
- **Çözüm**: Bcrypt cost factor çok yüksek olabilir. `pwd_context` ayarlarını kontrol et.

**Problem: CORS error when calling from frontend**
- **Çözüm**: `settings.CORS_ORIGINS` frontend URL'ini içerdiğinden emin ol

---

## 🔒 Production Checklist

**⚠️ Mock user storage'ı production'da KULLANMA!**

Replace with:
1. **Supabase Auth** (önerilen):
   ```python
   from supabase import create_client
   supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
   user = supabase.auth.sign_up(email, password)
   ```

2. **auth.users table** (local PostgreSQL):
   ```sql
   CREATE TABLE auth.users (
       id TEXT PRIMARY KEY,
       email TEXT UNIQUE NOT NULL,
       full_name TEXT,
       hashed_password TEXT NOT NULL,
       created_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```

---

## 📚 İlgili Dökümanlar

- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- Supabase Auth: https://supabase.com/docs/guides/auth

---

**Sonraki Task:** `TASK-08-testing.md` (Unit tests, integration tests)
