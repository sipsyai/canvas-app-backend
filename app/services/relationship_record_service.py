"""RelationshipRecord Service - Junction table CRUD"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RelationshipRecord
from app.schemas import RelationshipRecordCreate
from app.services.base import BaseService


class RelationshipRecordService(BaseService[RelationshipRecord]):
    """Service for RelationshipRecord operations"""

    def __init__(self):
        super().__init__(RelationshipRecord)

    async def create_link(
        self,
        db: AsyncSession,
        link_in: RelationshipRecordCreate,
        user_id: uuid.UUID,
    ) -> RelationshipRecord:
        """Create relationship between two records"""
        link_data = link_in.model_dump()
        link_data["id"] = f"lnk_{uuid.uuid4().hex[:8]}"
        link_data["created_by"] = user_id
        return await self.create(db, link_data)

    async def get_related_records(
        self,
        db: AsyncSession,
        record_id: str,
        relationship_id: str,
    ) -> list[RelationshipRecord]:
        """Get all related records via a specific relationship"""
        result = await db.execute(
            select(RelationshipRecord).where(
                RelationshipRecord.relationship_id == relationship_id,
                (
                    (RelationshipRecord.from_record_id == record_id) |
                    (RelationshipRecord.to_record_id == record_id)
                )
            )
        )
        return list(result.scalars().all())

# Singleton instance
relationship_record_service = RelationshipRecordService()
