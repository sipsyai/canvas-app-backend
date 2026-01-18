"""Application Model - Application Containers (CRM, ITSM, etc.)"""
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Application(Base):
    """
    Application containers grouping multiple objects.

    Examples:
    - CRM (Contact, Company, Opportunity, Task)
    - ITSM (Ticket, Change Request, Configuration Item)
    """
    __tablename__ = "applications"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Application Definition
    name = Column(String, nullable=False)
    label = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)

    # Application Configuration (navigation, layout, permissions)
    config = Column(JSONB, nullable=False, server_default='{}')

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    created_by = Column(UUID(as_uuid=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, name={self.name})>"

    @property
    def is_published(self) -> bool:
        """Check if application is published"""
        return self.published_at is not None
