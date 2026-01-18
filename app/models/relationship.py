"""Relationship Model - Relationship Definitions"""
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship as db_relationship
from app.database import Base


class Relationship(Base):
    """
    Defines relationships between objects.

    Examples:
    - Contact → Opportunities (1:N)
    - Contact ↔ Companies (N:N)
    - Opportunity → Contact (N:1)
    """
    __tablename__ = "relationships"

    # Primary Key
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # From/To Objects
    from_object_id = Column(String, ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    to_object_id = Column(String, ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)

    # Relationship Type
    type = Column(String, nullable=False)  # '1:N' or 'N:N'

    # Display Labels
    from_label = Column(Text, nullable=True)  # e.g., "Opportunities" on Contact page
    to_label = Column(Text, nullable=True)    # e.g., "Contact" on Opportunity page

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    from_object = db_relationship("Object", foreign_keys=[from_object_id], back_populates="relationships_from")
    to_object = db_relationship("Object", foreign_keys=[to_object_id], back_populates="relationships_to")
    relationship_records = db_relationship("RelationshipRecord", back_populates="relationship", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Relationship(id={self.id}, from={self.from_object_id}, to={self.to_object_id}, type={self.type})>"
