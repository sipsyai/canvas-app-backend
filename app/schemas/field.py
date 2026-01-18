"""Field Schemas"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FieldBase(BaseModel):
    """Base schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Unique field name (snake_case)")
    label: str = Field(..., min_length=1, max_length=255, description="Display label")
    type: str = Field(..., description="Field type: text, number, email, date, select, etc.")
    description: str | None = Field(None, description="Field description")
    config: dict = Field(default_factory=dict, description="Field configuration (validation, options, etc.)")
    category: str | None = Field(None, description="Field category (Contact Info, Business, System, etc.)")


class FieldCreate(FieldBase):
    """Schema for creating a new field"""
    is_custom: bool = Field(default=True, description="Custom field (vs system field)")


class FieldUpdate(BaseModel):
    """Schema for updating a field (all fields optional)"""
    name: str | None = Field(None, min_length=1, max_length=255)
    label: str | None = Field(None, min_length=1, max_length=255)
    type: str | None = None
    description: str | None = None
    config: dict | None = None
    category: str | None = None


class FieldResponse(FieldBase):
    """Schema for field response"""
    id: str
    is_global: bool
    is_system_field: bool
    is_custom: bool
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None = None

    model_config = {"from_attributes": True}  # Pydantic 2.x (was orm_mode in v1)
