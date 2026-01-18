"""Object Service - Object CRUD operations"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Object
from app.schemas import ObjectCreate, ObjectUpdate
from app.services.base import BaseService


class ObjectService(BaseService[Object]):
    """Service for Object operations"""

    def __init__(self):
        super().__init__(Object)

    async def create_object(
        self,
        db: AsyncSession,
        object_in: ObjectCreate,
        user_id: uuid.UUID,
    ) -> Object:
        """Create new object with auto-generated ID"""
        object_data = object_in.model_dump()
        object_data["id"] = f"obj_{uuid.uuid4().hex[:8]}"
        object_data["created_by"] = user_id
        object_data["is_custom"] = True
        object_data["is_global"] = False
        return await self.create(db, object_data)

    async def get_user_objects(self, db: AsyncSession, user_id: uuid.UUID) -> list[Object]:
        """Get user's custom objects"""
        result = await db.execute(
            select(Object).where(Object.created_by == user_id)
        )
        return list(result.scalars().all())

    async def update_object(
        self,
        db: AsyncSession,
        object_id: str,
        object_in: ObjectUpdate,
    ) -> Object | None:
        """Update existing object"""
        update_data = object_in.model_dump(exclude_unset=True)
        return await self.update(db, object_id, update_data)

# Singleton instance
object_service = ObjectService()
