# Testing Rules

globs: tests/**/*.py

## Pytest Async Pattern

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def db_session():
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def authenticated_user(db_session):
    # Create test user
    user = await user_service.create_user(db_session, ...)
    return user
```

## Test Structure

```python
# tests/test_fields.py
import pytest
from app.services import field_service
from app.schemas.field import FieldCreate

async def test_create_field(db_session, user_id):
    field = await field_service.create_field(
        db_session,
        FieldCreate(name="email", label="Email", type="email"),
        user_id
    )
    assert field.name == "email"
    assert field.created_by == user_id

async def test_create_field_invalid_type(db_session, user_id):
    with pytest.raises(ValueError):
        await field_service.create_field(...)
```

## Commands

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific file
pytest tests/test_fields.py -v

# Specific test
pytest tests/test_fields.py::test_create_field -v
```
