"""ObjectField API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas import ObjectFieldCreate, ObjectFieldUpdate, ObjectFieldResponse
from app.services import object_field_service

router = APIRouter()

@router.post("/", response_model=ObjectFieldResponse, status_code=201)
async def create_object_field(
    object_field_in: ObjectFieldCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create new object field (attach field to object).

    Example request:
    ```json
    {
        "object_id": "obj_contact",
        "field_id": "fld_email",
        "display_order": 0,
        "is_required": true,
        "is_visible": true
    }
    ```
    """
    object_field = await object_field_service.create_object_field(db, object_field_in, user_id)
    return object_field

@router.get("/", response_model=list[ObjectFieldResponse])
async def list_object_fields(
    object_id: str = Query(..., description="Object ID to filter fields"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all fields for an object.

    Example: GET /api/object-fields?object_id=obj_contact
    """
    object_fields = await object_field_service.get_fields_for_object(db, object_id)
    return object_fields

@router.get("/{object_field_id}", response_model=ObjectFieldResponse)
async def get_object_field(
    object_field_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get single object field by ID"""
    object_field = await object_field_service.get_by_id(db, object_field_id)
    if not object_field:
        raise HTTPException(status_code=404, detail="ObjectField not found")
    return object_field

@router.patch("/{object_field_id}", response_model=ObjectFieldResponse)
async def update_object_field(
    object_field_id: str,
    object_field_in: ObjectFieldUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update existing object field"""
    object_field = await object_field_service.update_object_field(db, object_field_id, object_field_in)
    if not object_field:
        raise HTTPException(status_code=404, detail="ObjectField not found")
    return object_field

@router.delete("/{object_field_id}", status_code=204)
async def delete_object_field(
    object_field_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete object field"""
    deleted = await object_field_service.delete(db, object_field_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="ObjectField not found")
    return None
