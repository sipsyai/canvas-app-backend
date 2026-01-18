"""Record API Endpoints - Dynamic JSONB data"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas import RecordCreate, RecordUpdate, RecordResponse, RecordListResponse
from app.services import record_service

router = APIRouter()

# Support both /api/records and /api/records/ (with and without trailing slash)
@router.post("", response_model=RecordResponse, status_code=201)
@router.post("/", response_model=RecordResponse, status_code=201)
async def create_record(
    record_in: RecordCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create new record with JSONB data.

    Example request:
    ```json
    {
        "object_id": "obj_contact",
        "data": {
            "fld_name": "Ali Yılmaz",
            "fld_email": "ali@example.com",
            "fld_phone": "+90 555 1234567",
            "fld_company": "Acme Corp"
        }
    }
    ```

    Response includes auto-generated primary_value (first text field).
    """
    record = await record_service.create_record(db, record_in, user_id)
    return record

@router.get("", response_model=RecordListResponse)
@router.get("/", response_model=RecordListResponse)
async def list_records(
    object_id: str = Query(..., description="Object ID to filter records"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Records per page"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all records for an object with pagination.

    Example: GET /api/records?object_id=obj_contact&page=1&page_size=50
    """
    skip = (page - 1) * page_size
    records, total = await record_service.get_records_by_object(
        db, object_id, skip=skip, limit=page_size
    )
    return RecordListResponse(
        total=total,
        page=page,
        page_size=page_size,
        records=records,
    )

# IMPORTANT: Define /search BEFORE /{record_id} to avoid route conflict
@router.get("/search", response_model=list[RecordResponse])
@router.get("/search/", response_model=list[RecordResponse])
async def search_records(
    object_id: str = Query(..., description="Object ID"),
    q: str = Query(..., min_length=1, description="Search term"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search records by primary_value (fast text search).

    Example: GET /api/records/search?object_id=obj_contact&q=Ali
    """
    records = await record_service.search_records(db, object_id, q)
    return records

@router.get("/{record_id}", response_model=RecordResponse)
async def get_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get single record by ID"""
    record = await record_service.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.patch("/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: str,
    record_in: RecordUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Update record's JSONB data (MERGE, not replace).

    Example request:
    ```json
    {
        "data": {
            "fld_email": "newemail@example.com"
        }
    }
    ```

    This will update only fld_email, keeping other fields unchanged.
    """
    record = await record_service.update_record(db, record_id, record_in, user_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.delete("/{record_id}", status_code=204)
async def delete_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete record"""
    deleted = await record_service.delete(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return None
