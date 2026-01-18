"""Record Model - Dynamic Data Storage (JSONB Hybrid Pattern)"""
from datetime import datetime
from typing import Any
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship as db_relationship
from app.database import Base


class Record(Base):
    """
    Universal data storage using JSONB Hybrid Model.

    Example data:
    {
        "id": "rec_001",
        "object_id": "obj_contact",
        "data": {
            "fld_name": "Ali Yılmaz",
            "fld_email": "ali@example.com",
            "fld_phone": "+90 555 1234567"
        },
        "primary_value": "Ali Yılmaz"
    }
    """
    __tablename__ = "records"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Foreign Key
    object_id = Column(String, ForeignKey("objects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Dynamic Data (JSONB)
    data = Column(JSONB, nullable=False, server_default='{}')

    # Denormalized Primary Value (for performance - list views, search)
    primary_value = Column(Text, nullable=True, index=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Multi-tenancy (redundant check)
    tenant_id = Column(String, nullable=True)

    # Relationships
    object = db_relationship("Object", back_populates="records")
    relationship_records_from = db_relationship(
        "RelationshipRecord",
        foreign_keys="RelationshipRecord.from_record_id",
        back_populates="from_record",
        cascade="all, delete-orphan"
    )
    relationship_records_to = db_relationship(
        "RelationshipRecord",
        foreign_keys="RelationshipRecord.to_record_id",
        back_populates="to_record",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Record(id={self.id}, object_id={self.object_id}, primary_value={self.primary_value})>"

    def get_field_value(self, field_id: str) -> Any:
        """Get specific field value from JSONB data"""
        return self.data.get(field_id)

    def set_field_value(self, field_id: str, value: Any) -> None:
        """Set specific field value in JSONB data"""
        if self.data is None:
            self.data = {}
        self.data[field_id] = value
