"""Field API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas import FieldCreate, FieldUpdate, FieldResponse
from app.services import field_service

router = APIRouter()

@router.post("/", response_model=FieldResponse, status_code=201)
async def create_field(
    field_in: FieldCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create new field (custom field only).

    Example request:
    ```json
    {
        "name": "email",
        "label": "Email Address",
        "type": "email",
        "description": "Contact email",
        "config": {
            "validation": {"required": true, "regex": ".*@.*"}
        }
    }
    ```
    """
    field = await field_service.create_field(db, field_in, user_id)
    return field

@router.get("/", response_model=list[FieldResponse])
async def list_fields(
    category: str | None = Query(None, description="Filter by category"),
    is_system: bool | None = Query(None, description="Filter system fields"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get all fields (global + user's custom fields) with optional filters.

    Returns both system fields (Created By, Owner, etc.) and user's custom fields.

    Query Parameters:
    - category: Filter by field category (e.g., "Contact Info", "Business", "System")
    - is_system: Filter system fields (true = only system fields, false = only non-system)
    """
    fields = await field_service.get_fields(db, user_id, category, is_system)
    return fields

@router.get("/{field_id}", response_model=FieldResponse)
async def get_field(
    field_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get single field by ID"""
    field = await field_service.get_by_id(db, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field

@router.patch("/{field_id}", response_model=FieldResponse)
async def update_field(
    field_id: str,
    field_in: FieldUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update existing field (custom fields only)"""
    field = await field_service.update_field(db, field_id, field_in)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field

@router.delete("/{field_id}", status_code=204)
async def delete_field(
    field_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete field (custom fields only)"""
    deleted = await field_service.delete(db, field_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Field not found")
    return None
