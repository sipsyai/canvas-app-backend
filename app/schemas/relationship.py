"""Relationship Schemas"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class RelationshipBase(BaseModel):
    """Base schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Relationship name")
    from_object_id: str = Field(..., description="Source object ID")
    to_object_id: str = Field(..., description="Target object ID")
    type: str = Field(..., pattern="^(1:N|N:N|lookup)$", description="Relationship type: 1:N, N:N, or lookup")
    from_label: str | None = Field(None, description="Label shown on 'from' object")
    to_label: str | None = Field(None, description="Label shown on 'to' object")


class RelationshipCreate(RelationshipBase):
    """Schema for creating a new relationship"""


class RelationshipUpdate(BaseModel):
    """Schema for updating a relationship (all fields optional)"""
    name: str | None = Field(None, min_length=1, max_length=255)
    from_label: str | None = None
    to_label: str | None = None


class RelationshipResponse(RelationshipBase):
    """Schema for relationship response"""
    id: str
    created_at: datetime
    created_by: uuid.UUID | None = None

    model_config = {"from_attributes": True}
