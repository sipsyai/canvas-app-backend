"""RelationshipRecord Schemas"""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RelationshipRecordBase(BaseModel):
    """Base schema with common fields"""
    relationship_id: str = Field(..., description="Relationship ID")
    from_record_id: str = Field(..., description="Source record ID")
    to_record_id: str = Field(..., description="Target record ID")
    relationship_metadata: dict[str, Any] = Field(default_factory=dict, description="Optional relationship metadata")


class RelationshipRecordCreate(RelationshipRecordBase):
    """Schema for creating a relationship between records"""


class RelationshipRecordUpdate(BaseModel):
    """Schema for updating relationship metadata"""
    relationship_metadata: dict[str, Any] | None = None


class RelationshipRecordResponse(RelationshipRecordBase):
    """Schema for relationship record response"""
    id: str
    created_at: datetime
    created_by: uuid.UUID | None = None

    model_config = {"from_attributes": True}
