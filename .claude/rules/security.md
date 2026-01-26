# Security Rules

globs: app/middleware/**/*.py, app/utils/security.py, app/routers/auth.py

## JWT Authentication

**Files:**
- `app/utils/security.py` - hash_password(), create_access_token()
- `app/middleware/auth.py` - get_current_user_id()
- `app/routers/auth.py` - /register, /login, /me

## CRITICAL Dependencies

```txt
passlib[bcrypt]==1.7.4
bcrypt==4.1.3  # MUST pin to 4.x (not 5.x)
python-jose[cryptography]==3.3.0
```

**Error if bcrypt 5.x:** `AttributeError: module 'bcrypt' has no attribute '__about__'`

## Protected Endpoint Pattern

```python
from app.middleware.auth import get_current_user_id

@router.post("/", response_model=FieldResponse, status_code=201)
async def create_field(
    field_in: FieldCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),  # JWT required
):
    return await field_service.create_field(db, field_in, user_id)
```

## Security Checklist

- All endpoints require JWT (except /api/health, /api/auth/*)
- JWT tokens expire after 1 hour
- Passwords hashed with bcrypt (min 8 chars)
- SECRET_KEY generated with `openssl rand -hex 32`
- CORS origins whitelisted
- .env in .gitignore
