"""Object Model - Object Definitions (Contact, Company, etc.)"""
from datetime import UTC, datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship as db_relationship
from app.database import Base


class Object(Base):
    """
    Object definitions (similar to Salesforce sObjects).

    Examples:
    - Contact (custom)
    - Company (custom)
    - Opportunity (custom)
    - User (system)
    """
    __tablename__ = "objects"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Object Definition
    name = Column(String, nullable=False)
    label = Column(String, nullable=False)
    plural_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)  # Emoji or icon class

    # System/Custom Distinction
    is_custom = Column(Boolean, nullable=False, default=True)
    is_global = Column(Boolean, nullable=False, default=False)

    # Views configuration (TableView, FormView, Kanban, Calendar)
    views = Column(
        JSONB,
        nullable=False,
        server_default='{"forms": [], "tables": [], "kanbans": [], "calendars": []}'
    )

    # Permissions configuration (CRUD roles)
    permissions = Column(
        JSONB,
        nullable=False,
        server_default='{"create": ["all"], "read": ["all"], "update": ["all"], "delete": ["all"]}'
    )

    # Metadata
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    object_fields = db_relationship("ObjectField", back_populates="object", cascade="all, delete-orphan")
    records = db_relationship("Record", back_populates="object", cascade="all, delete-orphan")
    relationships_from = db_relationship(
        "Relationship",
        foreign_keys="Relationship.from_object_id",
        back_populates="from_object",
        cascade="all, delete-orphan"
    )
    relationships_to = db_relationship(
        "Relationship",
        foreign_keys="Relationship.to_object_id",
        back_populates="to_object",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Object(id={self.id}, name={self.name}, label={self.label})>"
