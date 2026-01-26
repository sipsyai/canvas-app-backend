# Database Rules

globs: app/models/**/*.py, app/services/**/*.py

## SQLAlchemy Async (MANDATORY)

```python
# Alias to avoid conflicts
from sqlalchemy.orm import relationship as db_relationship

class Relationship(Base):
    from_object = db_relationship("Object", back_populates="relationships_from")

# String references prevent circular imports
class Object(Base):
    records = db_relationship("Record", back_populates="object")

# Always specify ondelete
object_id = Column(String, ForeignKey("objects.id", ondelete="CASCADE"))
```

## JSONB Pattern

```python
# Query JSONB field
result = await db.execute(
    select(Record).where(Record.data["fld_email"].astext == "user@example.com")
)

# GIN index query
result = await db.execute(
    select(Record).where(Record.data.contains({"fld_email": "user@example.com"}))
)
```

## GIN Indexes (MANDATORY)

```sql
CREATE INDEX idx_records_data_gin ON records USING GIN(data);
```

## Eager Loading (Prevent N+1)

```python
from sqlalchemy.orm import selectinload

result = await db.execute(
    select(Object)
    .options(selectinload(Object.fields))
    .where(Object.id == object_id)
)
```

## Pagination (MANDATORY)

```python
async def get_records(db: AsyncSession, object_id: str, page: int = 1, page_size: int = 50):
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Record).where(Record.object_id == object_id).offset(offset).limit(page_size)
    )
    return result.scalars().all()
```

## Reserved Keywords

Avoid: `metadata` (SQLAlchemy reserved) -> Use `model_metadata`
