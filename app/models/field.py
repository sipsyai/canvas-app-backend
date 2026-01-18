"""Field Model - Master Field Library"""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship as db_relationship
from app.database import Base


class Field(Base):
    """
    Master field library containing both system (global) and custom fields.

    Examples:
    - System fields: created_by, created_at, owner
    - Custom fields: email, phone, company_name
    """
    __tablename__ = "fields"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Field Definition
    name = Column(String, nullable=False, unique=True)
    label = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'text', 'number', 'email', 'date', 'select', etc.
    description = Column(Text, nullable=True)

    # Configuration (validation, options, default_value, etc.)
    config = Column(JSONB, nullable=False, server_default='{}')

    # System/Custom Distinction
    is_global = Column(Boolean, nullable=False, default=False)  # System fields
    is_custom = Column(Boolean, nullable=False, default=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)  # User ID (no FK constraint for flexibility)

    # Relationships
    object_fields = db_relationship("ObjectField", back_populates="field", cascade="all, delete")

    def __repr__(self) -> str:
        return f"<Field(id={self.id}, name={self.name}, type={self.type})>"

    def to_dict(self) -> dict:
        """Convert to dictionary (useful for debugging)"""
        return {
            "id": self.id,
            "name": self.name,
            "label": self.label,
            "type": self.type,
            "config": self.config,
            "is_global": self.is_global,
            "is_custom": self.is_custom,
        }
