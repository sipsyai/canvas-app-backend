"""Application Schemas"""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ApplicationBase(BaseModel):
    """Base schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Application name")
    label: str | None = Field(None, description="Application label")
    description: str | None = Field(None, description="Application description")
    icon: str | None = Field(None, description="Icon (emoji or class)")
    config: dict[str, Any] = Field(default_factory=dict, description="Application configuration")


class ApplicationCreate(ApplicationBase):
    """Schema for creating a new application"""


class ApplicationUpdate(BaseModel):
    """Schema for updating an application (all fields optional)"""
    name: str | None = Field(None, min_length=1, max_length=255)
    label: str | None = None
    description: str | None = None
    icon: str | None = None
    config: dict[str, Any] | None = None


class ApplicationResponse(ApplicationBase):
    """Schema for application response"""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None = None
    published_at: datetime | None = None

    model_config = {"from_attributes": True}

    @property
    def is_published(self) -> bool:
        """Check if application is published"""
        return self.published_at is not None
