"""ObjectField Schemas"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ObjectFieldBase(BaseModel):
    """Base schema with common fields"""
    object_id: str = Field(..., description="Object ID")
    field_id: str = Field(..., description="Field ID")
    display_order: int = Field(default=0, ge=0, description="Display order (0-based)")
    is_required: bool = Field(default=False, description="Is field required?")
    is_visible: bool = Field(default=True, description="Is field visible?")
    is_readonly: bool = Field(default=False, description="Is field read-only?")
    field_overrides: dict = Field(default_factory=dict, description="Field-specific config overrides")


class ObjectFieldCreate(ObjectFieldBase):
    """Schema for adding a field to an object"""


class ObjectFieldUpdate(BaseModel):
    """Schema for updating object-field mapping (all fields optional)"""
    display_order: int | None = Field(None, ge=0)
    is_required: bool | None = None
    is_visible: bool | None = None
    is_readonly: bool | None = None
    field_overrides: dict | None = None


class ObjectFieldResponse(ObjectFieldBase):
    """Schema for object-field response"""
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}
