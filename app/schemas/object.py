"""Object Schemas"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ObjectBase(BaseModel):
    """Base schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Object name (snake_case)")
    label: str = Field(..., min_length=1, max_length=255, description="Display label")
    plural_label: str = Field(..., min_length=1, max_length=255, description="Plural label")
    description: str | None = Field(None, description="Object description")
    icon: str | None = Field(None, description="Icon (emoji or class)")


class ObjectCreate(ObjectBase):
    """Schema for creating a new object"""


class ObjectUpdate(BaseModel):
    """Schema for updating an object (all fields optional)"""
    name: str | None = Field(None, min_length=1, max_length=255)
    label: str | None = Field(None, min_length=1, max_length=255)
    plural_label: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    icon: str | None = None


class ObjectResponse(ObjectBase):
    """Schema for object response"""
    id: str
    is_custom: bool
    is_global: bool
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None = None

    model_config = {"from_attributes": True}
