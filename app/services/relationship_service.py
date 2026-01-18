"""Relationship Service - Relationship CRUD operations"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Relationship
from app.schemas import RelationshipCreate, RelationshipUpdate
from app.services.base import BaseService


class RelationshipService(BaseService[Relationship]):
    """Service for Relationship operations"""

    def __init__(self):
        super().__init__(Relationship)

    async def create_relationship(
        self,
        db: AsyncSession,
        relationship_in: RelationshipCreate,
        user_id: uuid.UUID,
    ) -> Relationship:
        """Create new relationship with validation"""
        # TODO: Validate from_object_id and to_object_id exist

        relationship_data = relationship_in.model_dump()
        relationship_data["id"] = f"rel_{uuid.uuid4().hex[:8]}"
        relationship_data["created_by"] = user_id
        return await self.create(db, relationship_data)

    async def get_relationships_for_object(
        self,
        db: AsyncSession,
        object_id: str,
    ) -> list[Relationship]:
        """Get all relationships where object is source or target"""
        result = await db.execute(
            select(Relationship).where(
                (Relationship.from_object_id == object_id) |
                (Relationship.to_object_id == object_id)
            )
        )
        return list(result.scalars().all())

    async def update_relationship(
        self,
        db: AsyncSession,
        relationship_id: str,
        relationship_in: RelationshipUpdate,
    ) -> Relationship | None:
        """Update existing relationship"""
        update_data = relationship_in.model_dump(exclude_unset=True)
        return await self.update(db, relationship_id, update_data)

# Singleton instance
relationship_service = RelationshipService()
