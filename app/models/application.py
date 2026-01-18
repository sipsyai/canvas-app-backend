"""Application Model - Application Containers (CRM, ITSM, etc.)"""
from datetime import datetime
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
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)

    # Application Configuration (navigation, layout, permissions)
    config = Column(JSONB, nullable=False, server_default='{}')

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    published_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, name={self.name})>"

    @property
    def is_published(self) -> bool:
        """Check if application is published"""
        return self.published_at is not None
