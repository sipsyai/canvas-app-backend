# Code Style Rules

globs: app/**/*.py

## Async/Await (MANDATORY)

All I/O operations must be async:

```python
async def get_object(db: AsyncSession, id: str) -> Object:
    result = await db.execute(select(Object).where(Object.id == id))
    return result.scalar_one_or_none()
```

## Type Hints (MANDATORY)

Use modern Python 3.10+ syntax:

```python
# CORRECT
name: str | None = None
config: dict[str, Any] | None = None
data: dict[str, Any] = Field(default_factory=dict)

# WRONG - Old syntax
from typing import Optional, Dict
name: Optional[str] = None
```

## Pydantic v2 (MANDATORY)

```python
class FieldResponse(BaseModel):
    id: str
    name: str
    model_config = {"from_attributes": True}

# v2 methods
field.model_dump()       # NOT .dict()
Model.model_validate()   # NOT .from_orm()
```

## Common Pitfalls

| Pitfall | Wrong | Correct |
|---------|-------|---------|
| Missing await | `db.execute(...)` | `await db.execute(...)` |
| Mutable defaults | `data: dict = {}` | `data: dict = Field(default_factory=dict)` |
| datetime | `datetime.utcnow()` | `datetime.now(UTC)` |
