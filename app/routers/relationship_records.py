"""RelationshipRecord API Endpoints - Record linking"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas import RelationshipRecordCreate, RelationshipRecordResponse
from app.services import relationship_record_service

router = APIRouter()

# Support both /api/relationship-records and /api/relationship-records/ (with and without trailing slash)
@router.post("", response_model=RelationshipRecordResponse, status_code=201)
@router.post("/", response_model=RelationshipRecordResponse, status_code=201)
async def create_relationship_record(
    link_in: RelationshipRecordCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Link two records via relationship.

    Example: Link Contact to Opportunity
    ```json
    {
        "relationship_id": "rel_contact_opportunity",
        "from_record_id": "rec_ali",
        "to_record_id": "rec_bigdeal",
        "metadata": {"role": "Decision Maker"}
    }
    ```
    """
    link = await relationship_record_service.create_link(db, link_in, user_id)
    return link

@router.get("/records/{record_id}/related", response_model=list[RelationshipRecordResponse])
@router.get("/records/{record_id}/related/", response_model=list[RelationshipRecordResponse])
async def get_related_records(
    record_id: str,
    relationship_id: str = Query(..., description="Relationship ID"),
    db: AsyncSession = Depends(get_db),
):
    """Get all records related to a specific record via relationship"""
    links = await relationship_record_service.get_related_records(
        db, record_id, relationship_id
    )
    return links

@router.delete("/{link_id}", status_code=204)
@router.delete("/{link_id}/", status_code=204)
async def delete_relationship_record(
    link_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete relationship between records"""
    deleted = await relationship_record_service.delete(db, link_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Link not found")
    return None
