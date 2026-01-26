# API Design Rules

globs: app/routers/**/*.py

## Service Layer Pattern (CRITICAL)

ALL business logic in services, NOT routers:

```python
# routers/fields.py - Thin layer
@router.post("/", response_model=FieldResponse, status_code=201)
async def create_field(
    field_in: FieldCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return await field_service.create_field(db, field_in, user_id)

# services/field_service.py - Business logic
async def create_field(db: AsyncSession, field: FieldCreate, user_id: str) -> Field:
    new_field = Field(**field.model_dump(), created_by=user_id)
    db.add(new_field)
    await db.commit()
    return new_field
```

## Router Best Practices

```python
# Always specify response_model and status_code
@router.post("/", response_model=FieldResponse, status_code=201)
@router.get("/", response_model=list[FieldResponse])
@router.delete("/{field_id}", status_code=204)

# Use Query() for validation
@router.get("/")
async def list_records(
    object_id: str = Query(..., description="Object ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    ...
```

## Endpoint Order

1. Pydantic schema (`schemas/`)
2. Business logic in service (`services/`)
3. Router endpoint (`routers/`)
4. Write tests (`tests/`)
