"""RelationshipRecord Model - N:N Junction Table"""
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship as db_relationship
from app.database import Base


class RelationshipRecord(Base):
    """
    Junction table for N:N relationships.

    Example:
    - Contact "Ali Yılmaz" is related to Opportunity "BigDeal 2024"
    - Metadata: {"role": "Decision Maker", "influence": "High"}
    """
    __tablename__ = "relationship_records"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Foreign Keys
    relationship_id = Column(String, ForeignKey("relationships.id", ondelete="CASCADE"), nullable=False, index=True)
    from_record_id = Column(String, ForeignKey("records.id", ondelete="CASCADE"), nullable=False, index=True)
    to_record_id = Column(String, ForeignKey("records.id", ondelete="CASCADE"), nullable=False, index=True)

    # Optional Metadata (e.g., role, start_date, etc.)
    relationship_metadata = Column(JSONB, nullable=False, server_default='{}')

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    relationship = db_relationship("Relationship", back_populates="relationship_records")
    from_record = db_relationship("Record", foreign_keys=[from_record_id], back_populates="relationship_records_from")
    to_record = db_relationship("Record", foreign_keys=[to_record_id], back_populates="relationship_records_to")

    def __repr__(self) -> str:
        return f"<RelationshipRecord(from={self.from_record_id}, to={self.to_record_id})>"
