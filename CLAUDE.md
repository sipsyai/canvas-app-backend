# CLAUDE.md - Canvas App Backend

FastAPI-based REST API for an object-centric no-code platform.

## Project Overview

**Tech Stack:**
- **Framework:** FastAPI 0.115+
- **Language:** Python 3.11+
- **Database:** PostgreSQL 16 (Supabase)
- **ORM:** SQLAlchemy 2.0 (async)
- **Auth:** Custom JWT + bcrypt
- **Testing:** pytest + pytest-asyncio
- **Linting:** ruff

## ⚠️ CRITICAL: Virtual Environment

**ALWAYS activate venv before running ANY command:**

```bash
# 1. Activate venv (REQUIRED)
source venv/bin/activate

# 2. Verify
which python  # Should show: venv/bin/python

# 3. Now you can run commands
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

**Why mandatory:**
- Prevents version conflicts
- `pip` might not exist without venv
- Project uses Python 3.11 with specific dependencies

## Core Architecture

### Read These Documents First

1. **BACKEND_ARCHITECTURE_ANALYSIS.md** - Architecture analysis and decisions
2. **DATABASE_VISUAL_SCHEMA.md** - Database schema
3. **BACKEND_PROJECT_SPECIFICATION.md** - API specification

### Technology Constraints (DO NOT CHANGE)

```yaml
Framework: FastAPI 0.115+    # NOT Flask/Django
Database: PostgreSQL 16      # NOT MySQL/MongoDB
ORM: SQLAlchemy 2.0+ async  # NOT sync
Auth: Custom JWT + bcrypt    # NOT Supabase Auth
Testing: pytest              # NOT unittest
```

### Database Pattern: JSONB Hybrid Model

**Pattern:** Normalized metadata + JSONB for dynamic data

```sql
-- ✅ CORRECT
CREATE TABLE records (
  id UUID PRIMARY KEY,
  object_id UUID REFERENCES objects(id),
  data JSONB NOT NULL,      -- Dynamic field values
  primary_value TEXT,        -- Denormalized
  created_at TIMESTAMPTZ
);
```

**Why JSONB over EAV:** 7x faster, 3x less storage, simpler code.

## Project Structure

```
app/
├── main.py              # FastAPI entry
├── config.py            # Settings (SECRET_KEY, JWT_ALGORITHM)
├── database.py          # SQLAlchemy async setup
├── models/              # ORM models (Field, Object, Record, etc.)
├── schemas/             # Pydantic schemas
├── routers/             # API endpoints
│   ├── auth.py          # /register, /login, /me
│   ├── fields.py        # Field CRUD
│   ├── objects.py       # Object CRUD
│   └── records.py       # Record CRUD
├── services/            # Business logic (CRITICAL - logic goes here)
├── middleware/
│   └── auth.py          # JWT verification (get_current_user_id)
└── utils/
    └── security.py      # Password hashing + JWT utils
```

## Code Style Standards

### 1. Async/Await (MANDATORY)

All I/O operations must be async:

```python
# ✅ CORRECT
async def get_object(db: AsyncSession, id: str) -> Object:
    result = await db.execute(select(Object).where(Object.id == id))
    return result.scalar_one_or_none()
```

### 2. Type Hints (MANDATORY)

Use modern Python 3.10+ syntax:

```python
# ✅ CORRECT - Modern syntax
from pydantic import BaseModel

class FieldUpdate(BaseModel):
    name: str | None = None
    config: dict[str, Any] | None = None
    data: dict[str, Any] = Field(default_factory=dict)

# ❌ WRONG - Old syntax
from typing import Optional, Dict
name: Optional[str] = None
config: Optional[Dict[str, Any]] = None
```

### 3. Pydantic v2 (MANDATORY)

```python
# ✅ CORRECT - Pydantic v2
class FieldResponse(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}

# Use v2 methods
field_dict = field.model_dump()
field_obj = FieldResponse.model_validate(orm_obj)

# ❌ WRONG - Pydantic v1 (deprecated)
class Config:
    orm_mode = True
field.dict()  # Deprecated!
```

**Key changes:**
- `orm_mode = True` → `model_config = {"from_attributes": True}`
- `.dict()` → `.model_dump()`
- `.from_orm()` → `.model_validate()`

### 4. Service Layer Pattern (CRITICAL)

ALL business logic in services, NOT routers:

```python
# ✅ CORRECT
# routers/fields.py
@router.post("/", response_model=FieldResponse, status_code=201)
async def create_field(
    field_in: FieldCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    field = await field_service.create_field(db, field_in, user_id)
    return field

# services/field_service.py
async def create_field(db: AsyncSession, field: FieldCreate, user_id: str) -> Field:
    # Business logic here
    new_field = Field(**field.model_dump(), created_by=user_id)
    db.add(new_field)
    await db.commit()
    return new_field
```

### 5. Router Best Practices

```python
# Always specify response_model and status_code
@router.post("/", response_model=FieldResponse, status_code=201)
@router.get("/", response_model=list[FieldResponse])
@router.delete("/{field_id}", status_code=204)  # Return None

# Use Query() for validation
from fastapi import Query

@router.get("/")
async def list_records(
    object_id: str = Query(..., description="Object ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    ...
```

### 6. SQLAlchemy Best Practices

```python
# ✅ Use alias to avoid conflicts
from sqlalchemy.orm import relationship as db_relationship

class Relationship(Base):
    from_object = db_relationship("Object", back_populates="relationships_from")

# ✅ String references prevent circular imports
class Object(Base):
    records = db_relationship("Record", back_populates="object")

# ✅ Always specify ondelete
object_id = Column(String, ForeignKey("objects.id", ondelete="CASCADE"))

# ✅ Use timezone-aware datetime
from datetime import UTC, datetime
created_at = datetime.now(UTC)  # NOT datetime.utcnow()
```

## Authentication (JWT)

**Implementation:** Custom JWT with bcrypt password hashing

**Files:**
- `app/utils/security.py` - hash_password(), create_access_token()
- `app/middleware/auth.py` - get_current_user_id()
- `app/routers/auth.py` - /register, /login, /me

**CRITICAL Dependencies:**
```txt
passlib[bcrypt]==1.7.4
bcrypt==4.1.3  # MUST pin to 4.x (not 5.x)
python-jose[cryptography]==3.3.0
```

**Protected Endpoint Pattern:**
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

**Testing Endpoints:**
```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123", "full_name": "Test"}'

# 2. Login (get token)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test123"

# 3. Use token
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Environment Variables

Required in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/canvasapp

# Security (JWT)
SECRET_KEY=your-secret-key-here  # Generate: openssl rand -hex 32
JWT_ALGORITHM=HS256

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=true
```

**SECRET_KEY Security:**
- Never commit to version control
- Generate: `openssl rand -hex 32`
- Use different keys for dev/staging/production

## Development Commands

```bash
# ALWAYS activate venv first!
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Tests
pytest
pytest --cov=app --cov-report=html

# Linting
ruff check .
ruff check . --fix
ruff format .

# Database migrations
alembic revision --autogenerate -m "Migration message"
alembic upgrade head
alembic downgrade -1
```

## Common Workflows

### Adding a New Endpoint

**Order:**
1. Pydantic schema (`schemas/`)
2. Business logic in service (`services/`)
3. Router endpoint (`routers/`)
4. Write tests (`tests/`)

**Example:**
```python
# 1. Schema (schemas/field.py)
class FieldCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str

# 2. Service (services/field_service.py)
async def create_field(db: AsyncSession, field: FieldCreate, user_id: str) -> Field:
    new_field = Field(**field.model_dump(), created_by=user_id)
    db.add(new_field)
    await db.commit()
    return new_field

# 3. Router (routers/fields.py)
@router.post("/", response_model=FieldResponse, status_code=201)
async def create_field(
    field_in: FieldCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return await field_service.create_field(db, field_in, user_id)
```

### Database Migration

```bash
# 1. Make model changes in app/models/
# 2. Generate migration
alembic revision --autogenerate -m "Add category to fields"
# 3. Review migration file
# 4. Apply
alembic upgrade head
```

## Common Pitfalls (CRITICAL)

### ❌ Pitfall 1: Forgetting venv

```bash
# ❌ WRONG - Will fail or use wrong Python
pip install -r requirements.txt

# ✅ CORRECT
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ Pitfall 2: bcrypt version incompatibility

```txt
# ❌ WRONG - bcrypt 5.x breaks passlib
passlib[bcrypt]==1.7.4
# Will auto-install bcrypt 5.x → ERROR!

# ✅ CORRECT
passlib[bcrypt]==1.7.4
bcrypt==4.1.3  # MUST pin to 4.x
```

**Error:** `AttributeError: module 'bcrypt' has no attribute '__about__'`

**Fix:** `pip install bcrypt==4.1.3`

### ❌ Pitfall 3: SQLAlchemy relationship import conflict

```python
# ❌ WRONG
from sqlalchemy.orm import relationship

class Relationship(Base):  # Name conflict!
    from_object = relationship("Object", ...)  # TypeError!

# ✅ CORRECT
from sqlalchemy.orm import relationship as db_relationship

class Relationship(Base):
    from_object = db_relationship("Object", ...)
```

### ❌ Pitfall 4: datetime.utcnow() (deprecated)

```python
# ❌ WRONG
from datetime import datetime
created_at = datetime.utcnow()  # No timezone!

# ✅ CORRECT
from datetime import UTC, datetime
created_at = datetime.now(UTC)
```

**Ruff error:** `DTZ003`

### ❌ Pitfall 5: Mutable defaults

```python
# ❌ WRONG
class RecordCreate(BaseModel):
    data: dict = {}  # Shared across instances!

# ✅ CORRECT
class RecordCreate(BaseModel):
    data: dict = Field(default_factory=dict)
```

### ❌ Pitfall 6: Missing await

```python
# ❌ WRONG
result = db.execute(select(Field))  # Missing await!

# ✅ CORRECT
result = await db.execute(select(Field))
```

### ❌ Pitfall 7: Reserved keywords

```python
# ❌ WRONG
class MyModel(Base):
    metadata = Column(JSONB)  # Reserved in SQLAlchemy!

# ✅ CORRECT
class MyModel(Base):
    model_metadata = Column(JSONB)
```

## Database Guidelines

### JSONB Queries

```python
# Query JSONB field
result = await db.execute(
    select(Record).where(Record.data["fld_email"].astext == "user@example.com")
)

# Use GIN index
result = await db.execute(
    select(Record).where(Record.data.contains({"fld_email": "user@example.com"}))
)
```

### GIN Indexes (MANDATORY)

```sql
-- In migration file
CREATE INDEX idx_records_data_gin ON records USING GIN(data);
CREATE INDEX idx_records_email ON records USING GIN((data->'fld_email'));
```

### Eager Loading (Prevent N+1)

```python
# ✅ CORRECT
from sqlalchemy.orm import selectinload

result = await db.execute(
    select(Object)
    .options(selectinload(Object.fields))
    .where(Object.id == object_id)
)
```

## Performance Guidelines

### Pagination

Always paginate large result sets:

```python
async def get_records(
    db: AsyncSession,
    object_id: str,
    page: int = 1,
    page_size: int = 50
) -> list[Record]:
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Record)
        .where(Record.object_id == object_id)
        .offset(offset)
        .limit(page_size)
    )
    return result.scalars().all()
```

## Security Checklist

- [ ] All endpoints require JWT (except /api/health, /api/auth/*)
- [ ] JWT tokens expire after 1 hour
- [ ] Passwords hashed with bcrypt (min 8 chars)
- [ ] SECRET_KEY is strong (`openssl rand -hex 32`)
- [ ] bcrypt pinned to 4.1.3
- [ ] All inputs validated via Pydantic
- [ ] CORS origins whitelisted
- [ ] .env in .gitignore
- [ ] SQL injection prevented (SQLAlchemy parameterized queries)

## Debugging

### Enable SQL Logging

```python
# app/database.py
engine = create_async_engine(DATABASE_URL, echo=True)
```

### Add Logging

```python
import logging
logger = logging.getLogger(__name__)

async def create_field(...):
    logger.info(f"Creating field: {field.name}")
```

## API Documentation

FastAPI auto-generates docs:
- Interactive: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Testing

```python
# tests/conftest.py
@pytest.fixture
async def db_session():
    async with async_session() as session:
        yield session
        await session.rollback()

# tests/test_fields.py
async def test_create_field(db_session, user_id):
    field = await field_service.create_field(
        db_session,
        FieldCreate(name="email", label="Email", type="email"),
        user_id
    )
    assert field.name == "email"
    assert field.created_by == user_id
```

## Summary

**Stack:** FastAPI + PostgreSQL + SQLAlchemy (async) + JWT Auth
**Pattern:** JSONB Hybrid Model (NOT EAV)
**Architecture:** Service Layer + Pydantic v2 + Type hints
**Critical:** venv, bcrypt==4.1.3, datetime.now(UTC)

**Questions?**
1. Check architecture docs first
2. Look for similar patterns in existing code
3. Follow FastAPI best practices
