"""Application API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.services import application_service

router = APIRouter()

# Support both /api/applications and /api/applications/ (with and without trailing slash)
@router.post("", response_model=ApplicationResponse, status_code=201)
@router.post("/", response_model=ApplicationResponse, status_code=201)
async def create_application(
    app_in: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create new application (CRM, ITSM, etc.).

    Example request:
    ```json
    {
        "name": "CRM",
        "description": "Customer Relationship Management",
        "icon": "🤝",
        "config": {
            "objects": ["obj_contact", "obj_company", "obj_opportunity"],
            "navigation": [...]
        }
    }
    ```
    """
    app = await application_service.create_application(db, app_in, user_id)
    return app

@router.get("", response_model=list[ApplicationResponse])
@router.get("/", response_model=list[ApplicationResponse])
async def list_applications(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all applications"""
    apps = await application_service.get_all(db, skip=skip, limit=limit)
    return apps


@router.get("/{app_id}", response_model=ApplicationResponse)
@router.get("/{app_id}/", response_model=ApplicationResponse)
async def get_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get single application by ID"""
    app = await application_service.get_by_id(db, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.post("/{app_id}/publish", response_model=ApplicationResponse)
@router.post("/{app_id}/publish/", response_model=ApplicationResponse)
async def publish_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Publish application (sets published_at timestamp)"""
    app = await application_service.publish_application(db, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.delete("/{app_id}", status_code=204)
@router.delete("/{app_id}/", status_code=204)
async def delete_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete application"""
    deleted = await application_service.delete(db, app_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
    return None
