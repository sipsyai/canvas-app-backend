"""Application Service - Application CRUD operations"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Application
from app.schemas import ApplicationCreate, ApplicationUpdate
from app.services.base import BaseService


class ApplicationService(BaseService[Application]):
    """Service for Application operations"""

    def __init__(self):
        super().__init__(Application)

    async def create_application(
        self,
        db: AsyncSession,
        app_in: ApplicationCreate,
        user_id: uuid.UUID,
    ) -> Application:
        """Create new application"""
        app_data = app_in.model_dump()
        app_data["id"] = f"app_{uuid.uuid4().hex[:8]}"
        app_data["created_by"] = user_id
        return await self.create(db, app_data)

    async def publish_application(
        self,
        db: AsyncSession,
        app_id: str,
    ) -> Application | None:
        """Publish application (set published_at)"""
        app = await self.get_by_id(db, app_id)
        if not app:
            return None

        app.published_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(app)
        return app

    async def update_application(
        self,
        db: AsyncSession,
        app_id: str,
        app_in: ApplicationUpdate,
    ) -> Application | None:
        """Update existing application"""
        update_data = app_in.model_dump(exclude_unset=True)
        return await self.update(db, app_id, update_data)

    async def get_user_applications(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> list[Application]:
        """Get all applications created by a user"""
        result = await db.execute(
            select(Application).where(Application.created_by == user_id)
        )
        return list(result.scalars().all())

# Singleton instance
application_service = ApplicationService()
