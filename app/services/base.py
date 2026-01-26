"""Base Service Class - Reusable CRUD operations"""
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseService(Generic[ModelType]):
    """Base service with common CRUD operations"""

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: str) -> ModelType | None:
        """Get single record by ID"""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Get all records with pagination"""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: dict) -> ModelType:
        """Create new record"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        id: str,
        obj_in: dict,
    ) -> ModelType | None:
        """Update existing record"""
        db_obj = await self.get_by_id(db, id)
        if not db_obj:
            return None

        for field, value in obj_in.items():
            if value is not None:  # Only update non-None values
                setattr(db_obj, field, value)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: str) -> bool:
        """Delete record by ID"""
        db_obj = await self.get_by_id(db, id)
        if not db_obj:
            return False

        await db.delete(db_obj)
        await db.commit()
        return True

    async def count_all(self, db: AsyncSession) -> int:
        """Count all records in the table"""
        result = await db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
