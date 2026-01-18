# TASK-08: Testing (Unit & Integration Tests)

**Phase:** 8/8 (Final)
**Tahmini Süre:** 1.5 saat
**Bağımlılık:** Phase 7 (Authentication) ✅
**Durum:** ⏳ Bekliyor

---

## 🎯 Görev Açıklaması

Backend için **comprehensive test suite** oluştur:
- Unit tests (services, utils)
- Integration tests (API endpoints)
- Database fixtures (test data)
- Test coverage reports
- CI/CD ready

**Framework:** pytest + pytest-asyncio

---

## 📋 Ön Gereksinimler

- [x] Phase 7 tamamlandı (tüm endpoints hazır)
- [x] pytest, pytest-asyncio, httpx kurulu
- [x] Test database configured

---

## 📁 Oluşturulacak Dosyalar

```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── test_utils/
│   ├── __init__.py
│   └── test_security.py  # Password hashing, JWT tests
├── test_services/
│   ├── __init__.py
│   ├── test_field_service.py
│   ├── test_object_service.py
│   └── test_record_service.py
└── test_routers/
    ├── __init__.py
    ├── test_auth.py      # Auth endpoints
    ├── test_fields.py    # Field endpoints
    ├── test_objects.py   # Object endpoints
    └── test_records.py   # Record endpoints (most important!)
```

---

## 🔧 Implementation

### tests/conftest.py (Shared Fixtures)
```python
"""Pytest configuration and shared fixtures"""
import asyncio
import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient
from app.main import app
from app.database import Base, get_db
from app.config import settings

# Test database URL (use separate database for tests!)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/canvas_app_dev", "/canvas_app_test")

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create clean database for each test.

    Creates all tables before test, drops them after test.
    """
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Provide session
    async with TestSessionLocal() as session:
        yield session

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP client for testing API endpoints.

    Overrides get_db dependency to use test database.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict:
    """
    Create test user and return auth headers.

    Usage:
        async def test_protected_endpoint(client, auth_headers):
            response = await client.get("/api/fields", headers=auth_headers)
    """
    # Register user
    register_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "full_name": "Test User"
    }
    await client.post("/api/auth/register", json=register_data)

    # Login
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123"
    }
    response = await client.post("/api/auth/login", data=login_data)
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
```

---

### tests/test_utils/test_security.py
```python
"""Unit tests for security utilities"""
import pytest
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

def test_password_hashing():
    """Test password hashing and verification"""
    password = "MySecurePassword123"
    hashed = hash_password(password)

    # Hash should not equal plain password
    assert hashed != password

    # Verify should return True for correct password
    assert verify_password(password, hashed) is True

    # Verify should return False for wrong password
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_creation():
    """Test JWT token creation and decoding"""
    payload = {"sub": "user_123", "email": "test@example.com"}
    token = create_access_token(payload)

    # Token should be a string
    assert isinstance(token, str)
    assert len(token) > 0

    # Decode token
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user_123"
    assert decoded["email"] == "test@example.com"

def test_jwt_invalid_token():
    """Test JWT decoding with invalid token"""
    decoded = decode_access_token("invalid_token")
    assert decoded is None
```

---

### tests/test_services/test_field_service.py
```python
"""Unit tests for Field Service"""
import pytest
from app.services import field_service
from app.schemas import FieldCreate

@pytest.mark.asyncio
async def test_create_field(db_session):
    """Test field creation"""
    field_in = FieldCreate(
        name="email",
        label="Email Address",
        type="email",
        description="Contact email",
        config={"validation": {"required": True}}
    )

    field = await field_service.create_field(db_session, field_in, user_id="user_123")

    assert field.id.startswith("fld_")
    assert field.name == "email"
    assert field.type == "email"
    assert field.created_by == "user_123"

@pytest.mark.asyncio
async def test_get_user_fields(db_session):
    """Test retrieving user's custom fields"""
    # Create two fields
    field1_in = FieldCreate(name="email", label="Email", type="email")
    field2_in = FieldCreate(name="phone", label="Phone", type="phone")

    await field_service.create_field(db_session, field1_in, user_id="user_123")
    await field_service.create_field(db_session, field2_in, user_id="user_123")

    # Retrieve fields
    fields = await field_service.get_user_fields(db_session, user_id="user_123")

    assert len(fields) == 2
    assert fields[0].name in ["email", "phone"]
```

---

### tests/test_services/test_record_service.py
```python
"""Unit tests for Record Service (JSONB handling)"""
import pytest
from app.services import record_service, object_service
from app.schemas import RecordCreate, ObjectCreate

@pytest.mark.asyncio
async def test_create_record_with_jsonb_data(db_session):
    """Test creating record with JSONB data"""
    # First create object
    object_in = ObjectCreate(
        name="contact",
        label="Contact",
        plural_label="Contacts",
    )
    obj = await object_service.create_object(db_session, object_in, user_id="user_123")

    # Create record
    record_in = RecordCreate(
        object_id=obj.id,
        data={
            "fld_name": "Ali Yılmaz",
            "fld_email": "ali@example.com",
            "fld_phone": "+90 555 1234567"
        }
    )
    record = await record_service.create_record(db_session, record_in, user_id="user_123")

    assert record.id.startswith("rec_")
    assert record.object_id == obj.id
    assert record.data["fld_name"] == "Ali Yılmaz"
    assert record.primary_value == "Ali Yılmaz"  # First text field

@pytest.mark.asyncio
async def test_update_record_merges_data(db_session):
    """Test that record update merges JSONB data, doesn't replace"""
    # Create object
    object_in = ObjectCreate(name="contact", label="Contact", plural_label="Contacts")
    obj = await object_service.create_object(db_session, object_in, user_id="user_123")

    # Create record
    record_in = RecordCreate(
        object_id=obj.id,
        data={
            "fld_name": "Ali Yılmaz",
            "fld_email": "ali@example.com"
        }
    )
    record = await record_service.create_record(db_session, record_in, user_id="user_123")

    # Update only email
    from app.schemas import RecordUpdate
    update_in = RecordUpdate(data={"fld_email": "newemail@example.com"})
    updated = await record_service.update_record(db_session, record.id, update_in, user_id="user_123")

    # Should merge, not replace
    assert updated.data["fld_name"] == "Ali Yılmaz"  # Still exists!
    assert updated.data["fld_email"] == "newemail@example.com"  # Updated
```

---

### tests/test_routers/test_auth.py
```python
"""Integration tests for Auth endpoints"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration"""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "full_name": "New User"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    """Test user login"""
    # First register
    await client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "Password123",
            "full_name": "User"
        }
    )

    # Then login
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "user@example.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers: dict):
    """Test getting current user with JWT token"""
    response = await client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient):
    """Test that protected endpoints return 401 without token"""
    response = await client.get("/api/fields")

    assert response.status_code == 403  # FastAPI HTTPBearer returns 403
```

---

### tests/test_routers/test_fields.py
```python
"""Integration tests for Field endpoints"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_field(client: AsyncClient, auth_headers: dict):
    """Test creating field via API"""
    response = await client.post(
        "/api/fields",
        headers=auth_headers,
        json={
            "name": "email",
            "label": "Email Address",
            "type": "email",
            "config": {"validation": {"required": True}}
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "email"
    assert data["type"] == "email"
    assert data["id"].startswith("fld_")

@pytest.mark.asyncio
async def test_list_fields(client: AsyncClient, auth_headers: dict):
    """Test listing fields"""
    # Create two fields
    await client.post("/api/fields", headers=auth_headers, json={"name": "email", "label": "Email", "type": "email"})
    await client.post("/api/fields", headers=auth_headers, json={"name": "phone", "label": "Phone", "type": "phone"})

    # List fields
    response = await client.get("/api/fields", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

@pytest.mark.asyncio
async def test_get_field_not_found(client: AsyncClient, auth_headers: dict):
    """Test getting non-existent field returns 404"""
    response = await client.get("/api/fields/fld_nonexistent", headers=auth_headers)

    assert response.status_code == 404
```

---

### tests/test_routers/test_records.py
```python
"""Integration tests for Record endpoints (JSONB)"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_get_record(client: AsyncClient, auth_headers: dict):
    """Test creating record with JSONB data and retrieving it"""
    # Create object first
    obj_response = await client.post(
        "/api/objects",
        headers=auth_headers,
        json={
            "name": "contact",
            "label": "Contact",
            "plural_label": "Contacts"
        }
    )
    object_id = obj_response.json()["id"]

    # Create record
    record_response = await client.post(
        "/api/records",
        headers=auth_headers,
        json={
            "object_id": object_id,
            "data": {
                "fld_name": "Ali Yılmaz",
                "fld_email": "ali@example.com"
            }
        }
    )

    assert record_response.status_code == 201
    record_data = record_response.json()
    assert record_data["data"]["fld_name"] == "Ali Yılmaz"
    assert record_data["primary_value"] == "Ali Yılmaz"

    # Get record
    record_id = record_data["id"]
    get_response = await client.get(f"/api/records/{record_id}", headers=auth_headers)

    assert get_response.status_code == 200
    assert get_response.json()["id"] == record_id

@pytest.mark.asyncio
async def test_list_records_with_pagination(client: AsyncClient, auth_headers: dict):
    """Test listing records with pagination"""
    # Create object
    obj_response = await client.post(
        "/api/objects",
        headers=auth_headers,
        json={"name": "contact", "label": "Contact", "plural_label": "Contacts"}
    )
    object_id = obj_response.json()["id"]

    # Create 5 records
    for i in range(5):
        await client.post(
            "/api/records",
            headers=auth_headers,
            json={
                "object_id": object_id,
                "data": {"fld_name": f"User {i}"}
            }
        )

    # List with pagination
    response = await client.get(
        f"/api/records?object_id={object_id}&page=1&page_size=3",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 3
    assert len(data["records"]) == 3
```

---

## 🚀 Running Tests

### Run all tests
```bash
# Activate venv
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_services/test_record_service.py

# Run specific test
pytest tests/test_routers/test_auth.py::test_register_user -v
```

### Expected output
```
========================= test session starts =========================
collected 15 items

tests/test_utils/test_security.py ....                         [ 26%]
tests/test_services/test_field_service.py ..                   [ 40%]
tests/test_services/test_record_service.py ..                  [ 53%]
tests/test_routers/test_auth.py ....                           [ 80%]
tests/test_routers/test_fields.py ...                          [ 93%]
tests/test_routers/test_records.py ..                          [100%]

========================== 15 passed in 3.42s =========================
```

---

## ✅ Başarı Kriterleri

Tamamlandığında şunlar olmalı:

- [ ] `tests/` klasöründe 10+ test dosyası
- [ ] `conftest.py` ile shared fixtures (db_session, client, auth_headers)
- [ ] Unit tests (services, utils) yazılmış
- [ ] Integration tests (routers/endpoints) yazılmış
- [ ] Test coverage > 80%
- [ ] Tüm testler başarılı (pytest geçiyor)
- [ ] CI/CD ready (pytest çalışıyor)

---

## 📊 Test Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open report
open htmlcov/index.html
```

**Target Coverage:**
- Overall: > 80%
- Services: > 90%
- Routers: > 85%
- Utils: > 95%

---

## 🐛 Troubleshooting

**Problem: "Event loop is closed" error**
- **Çözüm**: `conftest.py`'de `event_loop` fixture doğru tanımlandı mı kontrol et

**Problem: Tests fail with database errors**
- **Çözüm**: Test database'i elle oluştur:
  ```bash
  createdb canvas_app_test
  ```

**Problem: AsyncClient errors**
- **Çözüm**: httpx versiyonu 0.25+ olmalı

---

## 📚 İlgili Dökümanlar

- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- FastAPI Testing: https://fastapi.tiangolo.com/tutorial/testing/

---

**SON TASK! 🎉**

Backend MVP tamamlandı:
- ✅ Database migration
- ✅ ORM models
- ✅ Pydantic schemas
- ✅ Business services
- ✅ API routers
- ✅ JWT authentication
- ✅ Testing

**Next:** Deploy to production! 🚀
