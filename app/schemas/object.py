"""Object Schemas"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ObjectBase(BaseModel):
    """Base schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Object name (snake_case)")
    label: str = Field(..., min_length=1, max_length=255, description="Display label")
    plural_name: str = Field(..., min_length=1, max_length=255, description="Plural name")
    description: str | None = Field(None, description="Object description")
    icon: str | None = Field(None, description="Icon (emoji or class)")


class ObjectCreate(ObjectBase):
    """Schema for creating a new object"""
    views: dict = Field(
        default_factory=lambda: {
            "forms": [],
            "tables": [],
            "kanbans": [],
            "calendars": []
        },
        description="View configurations (TableView, FormView, Kanban, Calendar)"
    )
    permissions: dict = Field(
        default_factory=lambda: {
            "create": ["all"],
            "read": ["all"],
            "update": ["all"],
            "delete": ["all"]
        },
        description="CRUD permissions configuration"
    )


class ObjectUpdate(BaseModel):
    """Schema for updating an object (all fields optional)"""
    name: str | None = Field(None, min_length=1, max_length=255)
    label: str | None = Field(None, min_length=1, max_length=255)
    plural_name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    icon: str | None = None
    views: dict | None = Field(None, description="View configurations")
    permissions: dict | None = Field(None, description="CRUD permissions")


class ObjectResponse(ObjectBase):
    """Schema for object response"""
    id: str
    is_custom: bool
    is_global: bool
    views: dict
    permissions: dict
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None = None

    model_config = {"from_attributes": True}
