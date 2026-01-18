"""ObjectField Model - N:N Mapping between Objects and Fields"""
from datetime import UTC, datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship as db_relationship
from app.database import Base


class ObjectField(Base):
    """
    N:N mapping table connecting objects to fields.

    Example:
    - Contact object has Email field
    - Contact object has Phone field
    - Company object has Email field (reused!)
    """
    __tablename__ = "object_fields"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Foreign Keys
    object_id = Column(String, ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(String, ForeignKey("fields.id", ondelete="RESTRICT"), nullable=False)

    # Field Configuration
    display_order = Column(Integer, nullable=False, default=0)
    is_required = Column(Boolean, nullable=False, default=False)
    is_visible = Column(Boolean, nullable=False, default=True)
    is_readonly = Column(Boolean, nullable=False, default=False)

    # Field-specific overrides (override field.config for this object)
    field_overrides = Column(JSONB, nullable=False, server_default='{}')

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    # Relationships
    object = db_relationship("Object", back_populates="object_fields")
    field = db_relationship("Field", back_populates="object_fields")

    def __repr__(self) -> str:
        return f"<ObjectField(object_id={self.object_id}, field_id={self.field_id})>"
