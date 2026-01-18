"""Record Schemas"""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RecordBase(BaseModel):
    """Base schema with common fields"""
    object_id: str = Field(..., description="Object ID this record belongs to")
    data: dict[str, Any] = Field(..., description="Dynamic field data (JSONB)")


class RecordCreate(RecordBase):
    """Schema for creating a new record"""


class RecordUpdate(BaseModel):
    """Schema for updating a record (all fields optional)"""
    data: dict[str, Any] | None = Field(None, description="Updated field data")


class RecordResponse(RecordBase):
    """Schema for record response"""
    id: str
    primary_value: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None = None
    updated_by: uuid.UUID | None = None
    tenant_id: str | None = None

    model_config = {"from_attributes": True}


class RecordListResponse(BaseModel):
    """Schema for paginated record list"""
    total: int = Field(..., description="Total record count")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Records per page")
    records: list[RecordResponse] = Field(..., description="List of records")
