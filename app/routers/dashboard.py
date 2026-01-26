"""Dashboard API Endpoints"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.services import (
    application_service,
    field_service,
    object_service,
    record_service,
)


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response"""
    total_records: int
    active_objects: int
    fields_count: int
    applications_count: int


router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
@router.get("/stats/", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get dashboard statistics for the current user.

    Returns counts for:
    - total_records: Total records across all objects
    - active_objects: Number of objects the user has
    - fields_count: Number of fields (global + user's own)
    - applications_count: Number of applications
    """
    # Get counts in parallel would be more efficient, but for simplicity:
    total_records = await record_service.count_all(db)
    active_objects = len(await object_service.get_user_objects(db, user_id))
    fields = await field_service.get_fields(db, user_id)
    fields_count = len(fields)
    applications = await application_service.get_user_applications(db, user_id)
    applications_count = len(applications)

    return DashboardStatsResponse(
        total_records=total_records,
        active_objects=active_objects,
        fields_count=fields_count,
        applications_count=applications_count,
    )
