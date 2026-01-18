"""Field Service - Field CRUD operations"""
import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Field
from app.schemas import FieldCreate, FieldUpdate
from app.services.base import BaseService


class FieldService(BaseService[Field]):
    """Service for Field operations"""

    def __init__(self):
        super().__init__(Field)

    async def create_field(
        self,
        db: AsyncSession,
        field_in: FieldCreate,
        user_id: uuid.UUID,
    ) -> Field:
        """Create new field with auto-generated ID"""
        field_data = field_in.model_dump()
        field_data["id"] = f"fld_{uuid.uuid4().hex[:8]}"
        field_data["created_by"] = user_id
        return await self.create(db, field_data)

    async def get_fields(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        category: str | None = None,
        is_system: bool | None = None,
    ) -> list[Field]:
        """Get fields (global + user's own), optionally filter by category and system"""
        query = select(Field).where(
            or_(
                Field.is_global == True,
                Field.created_by == user_id
            )
        )

        # Filter by category if provided
        if category:
            query = query.where(Field.category == category)

        # Filter by system fields if provided
        if is_system is not None:
            query = query.where(Field.is_system_field == is_system)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_global_fields(self, db: AsyncSession) -> list[Field]:
        """Get all global (system) fields"""
        result = await db.execute(
            select(Field).where(Field.is_global is True)
        )
        return list(result.scalars().all())

    async def get_user_fields(self, db: AsyncSession, user_id: uuid.UUID) -> list[Field]:
        """Get user's custom fields"""
        # Query for fields created by this user
        result = await db.execute(
            select(Field).where(
                Field.created_by == user_id,
                Field.is_custom == True
            )
        )
        return list(result.scalars().all())

    async def update_field(
        self,
        db: AsyncSession,
        field_id: str,
        field_in: FieldUpdate,
    ) -> Field | None:
        """Update existing field"""
        update_data = field_in.model_dump(exclude_unset=True)
        return await self.update(db, field_id, update_data)

# Singleton instance
field_service = FieldService()
