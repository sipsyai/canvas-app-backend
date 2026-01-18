"""Relationship API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas import RelationshipCreate, RelationshipUpdate, RelationshipResponse
from app.services import relationship_service

router = APIRouter()

@router.post("/", response_model=RelationshipResponse, status_code=201)
async def create_relationship(
    relationship_in: RelationshipCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create relationship between objects.

    Example: Contact → Opportunities (1:N)
    ```json
    {
        "name": "contact_opportunities",
        "from_object_id": "obj_contact",
        "to_object_id": "obj_opportunity",
        "type": "1:N",
        "from_label": "Opportunities",
        "to_label": "Contact"
    }
    ```
    """
    rel = await relationship_service.create_relationship(db, relationship_in, user_id)
    return rel

@router.get("/objects/{object_id}", response_model=list[RelationshipResponse])
async def get_object_relationships(
    object_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all relationships for an object"""
    relationships = await relationship_service.get_relationships_for_object(db, object_id)
    return relationships

@router.delete("/{relationship_id}", status_code=204)
async def delete_relationship(
    relationship_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete relationship definition"""
    deleted = await relationship_service.delete(db, relationship_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return None
