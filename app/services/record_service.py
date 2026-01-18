"""Record Service - Record CRUD with JSONB handling"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Record
from app.schemas import RecordCreate, RecordUpdate
from app.services.base import BaseService


class RecordService(BaseService[Record]):
    """Service for Record operations (JSONB hybrid model)"""

    def __init__(self):
        super().__init__(Record)

    async def create_record(
        self,
        db: AsyncSession,
        record_in: RecordCreate,
        user_id: uuid.UUID,
    ) -> Record:
        """
        Create new record with JSONB data.

        Example:
        record_in.data = {
            "fld_name": "John Doe",
            "fld_email": "john@example.com"
        }
        """
        # Generate primary_value from first text field
        primary_value = self._extract_primary_value(record_in.data)

        record_data = {
            "id": f"rec_{uuid.uuid4().hex[:8]}",
            "object_id": record_in.object_id,
            "data": record_in.data,
            "primary_value": primary_value,
            "created_by": user_id,
            "updated_by": user_id,
            "tenant_id": str(user_id),  # Multi-tenancy (String column)
        }
        return await self.create(db, record_data)

    async def get_records_by_object(
        self,
        db: AsyncSession,
        object_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Record], int]:
        """
        Get all records for an object with pagination.
        Returns: (records, total_count)
        """
        # Get total count
        count_result = await db.execute(
            select(func.count()).select_from(Record).where(Record.object_id == object_id)
        )
        total = count_result.scalar_one()

        # Get records
        result = await db.execute(
            select(Record)
            .where(Record.object_id == object_id)
            .offset(skip)
            .limit(limit)
            .order_by(Record.created_at.desc())
        )
        records = list(result.scalars().all())

        return records, total

    async def get_records(self, db: AsyncSession, object_id: str) -> list[Record]:
        """Alias for get_records_by_object (returns only records list)"""
        records, _ = await self.get_records_by_object(db, object_id)
        return records

    async def update_record(
        self,
        db: AsyncSession,
        record_id: str,
        record_in: RecordUpdate,
        user_id: uuid.UUID,
    ) -> Record | None:
        """
        Update record's JSONB data.

        IMPORTANT: Merges data, doesn't replace!
        """
        record = await self.get_by_id(db, record_id)
        if not record:
            return None

        # Merge data (don't replace!)
        if record_in.data:
            record.data = {**record.data, **record_in.data}

        # Update primary_value
        record.primary_value = self._extract_primary_value(record.data)
        record.updated_by = user_id

        await db.commit()
        await db.refresh(record)
        return record

    async def search_records(
        self,
        db: AsyncSession,
        object_id: str,
        search_term: str,
    ) -> list[Record]:
        """
        Search records using primary_value (faster than JSONB search).
        For advanced JSONB search, use PostgreSQL full-text search.
        """
        result = await db.execute(
            select(Record)
            .where(
                Record.object_id == object_id,
                Record.primary_value.ilike(f"%{search_term}%")
            )
            .limit(50)
        )
        return list(result.scalars().all())

    def _extract_primary_value(self, data: dict[str, Any]) -> str | None:
        """
        Extract primary value from JSONB data (first text-like field).
        Used for list views and search.
        """
        for _key, value in data.items():
            if isinstance(value, str) and value.strip():
                return value[:255]  # Max 255 chars
        return None

# Singleton instance
record_service = RecordService()
