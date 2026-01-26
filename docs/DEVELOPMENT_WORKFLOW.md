# Development Workflow

## Adding a New Endpoint

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

## Database Migration

```bash
# 1. Make model changes in app/models/
# 2. Generate migration
alembic revision --autogenerate -m "Add category to fields"
# 3. Review migration file
# 4. Apply
alembic upgrade head
```

## Common Pitfalls

### Pitfall 1: Forgetting venv

```bash
# WRONG - Will fail or use wrong Python
pip install -r requirements.txt

# CORRECT
source venv/bin/activate
pip install -r requirements.txt
```

### Pitfall 2: bcrypt version incompatibility

```txt
# WRONG - bcrypt 5.x breaks passlib
passlib[bcrypt]==1.7.4
# Will auto-install bcrypt 5.x -> ERROR!

# CORRECT
passlib[bcrypt]==1.7.4
bcrypt==4.1.3  # MUST pin to 4.x
```

**Error:** `AttributeError: module 'bcrypt' has no attribute '__about__'`
**Fix:** `pip install bcrypt==4.1.3`

### Pitfall 3: SQLAlchemy relationship import conflict

```python
# WRONG
from sqlalchemy.orm import relationship

class Relationship(Base):  # Name conflict!
    from_object = relationship("Object", ...)  # TypeError!

# CORRECT
from sqlalchemy.orm import relationship as db_relationship

class Relationship(Base):
    from_object = db_relationship("Object", ...)
```

### Pitfall 4: datetime.utcnow() (deprecated)

```python
# WRONG
from datetime import datetime
created_at = datetime.utcnow()  # No timezone!

# CORRECT
from datetime import UTC, datetime
created_at = datetime.now(UTC)
```

**Ruff error:** `DTZ003`

### Pitfall 5: Mutable defaults

```python
# WRONG
class RecordCreate(BaseModel):
    data: dict = {}  # Shared across instances!

# CORRECT
class RecordCreate(BaseModel):
    data: dict = Field(default_factory=dict)
```

### Pitfall 6: Missing await

```python
# WRONG
result = db.execute(select(Field))  # Missing await!

# CORRECT
result = await db.execute(select(Field))
```

### Pitfall 7: Reserved keywords

```python
# WRONG
class MyModel(Base):
    metadata = Column(JSONB)  # Reserved in SQLAlchemy!

# CORRECT
class MyModel(Base):
    model_metadata = Column(JSONB)
```

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
