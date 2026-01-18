"""Field Service - Field CRUD operations"""
import uuid

from sqlalchemy import select
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
