"""ObjectField Service - ObjectField CRUD operations"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ObjectField
from app.schemas import ObjectFieldCreate, ObjectFieldUpdate
from app.services.base import BaseService


class ObjectFieldService(BaseService[ObjectField]):
    """Service for ObjectField operations"""

    def __init__(self):
        super().__init__(ObjectField)

    async def create_object_field(
        self,
        db: AsyncSession,
        object_field_in: ObjectFieldCreate,
        user_id: uuid.UUID,
    ) -> ObjectField:
        """Create new object field with auto-generated ID"""
        object_field_data = object_field_in.model_dump()
        object_field_data["id"] = f"ofd_{uuid.uuid4().hex[:8]}"
        object_field_data["created_by"] = user_id
        return await self.create(db, object_field_data)

    async def get_fields_for_object(
        self,
        db: AsyncSession,
        object_id: str,
    ) -> list[ObjectField]:
        """Get all fields for a specific object"""
        result = await db.execute(
            select(ObjectField)
            .where(ObjectField.object_id == object_id)
            .order_by(ObjectField.display_order)
        )
        return list(result.scalars().all())

    async def update_object_field(
        self,
        db: AsyncSession,
        object_field_id: str,
        object_field_in: ObjectFieldUpdate,
    ) -> ObjectField | None:
        """Update existing object field"""
        update_data = object_field_in.model_dump(exclude_unset=True)
        return await self.update(db, object_field_id, update_data)

# Singleton instance
object_field_service = ObjectFieldService()
