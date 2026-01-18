"""Object API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas import ObjectCreate, ObjectUpdate, ObjectResponse
from app.services import object_service

router = APIRouter()

@router.post("/", response_model=ObjectResponse, status_code=201)
async def create_object(
    object_in: ObjectCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create new object (Contact, Company, etc.).

    Example request:
    ```json
    {
        "name": "contact",
        "label": "Contact",
        "plural_label": "Contacts",
        "description": "Customer contacts",
        "icon": "👤"
    }
    ```
    """
    obj = await object_service.create_object(db, object_in, user_id)
    return obj

@router.get("/", response_model=list[ObjectResponse])
async def list_objects(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get all user's objects"""
    objects = await object_service.get_user_objects(db, user_id)
    return objects

@router.get("/{object_id}", response_model=ObjectResponse)
async def get_object(
    object_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get single object by ID"""
    obj = await object_service.get_by_id(db, object_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj

@router.patch("/{object_id}", response_model=ObjectResponse)
async def update_object(
    object_id: str,
    object_in: ObjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update existing object"""
    obj = await object_service.update_object(db, object_id, object_in)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj

@router.delete("/{object_id}", status_code=204)
async def delete_object(
    object_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete object (CASCADE: deletes fields, records)"""
    deleted = await object_service.delete(db, object_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Object not found")
    return None
