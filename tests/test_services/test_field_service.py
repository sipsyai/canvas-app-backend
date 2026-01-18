"""Unit tests for Field Service"""
import pytest
from app.services import field_service
from app.schemas import FieldCreate

@pytest.mark.asyncio
async def test_create_field(db_session, test_user_id):
    """Test field creation"""
    field_in = FieldCreate(
        name="email",
        label="Email Address",
        type="email",
        description="Contact email",
        config={"validation": {"required": True}}
    )

    field = await field_service.create_field(db_session, field_in, user_id=test_user_id)

    assert field.id.startswith("fld_")
    assert field.name == "email"
    assert field.type == "email"
    assert field.created_by == test_user_id

@pytest.mark.asyncio
async def test_get_user_fields(db_session, test_user_id):
    """Test retrieving user's custom fields"""
    # Create two fields
    field1_in = FieldCreate(name="email", label="Email", type="email")
    field2_in = FieldCreate(name="phone", label="Phone", type="phone")

    await field_service.create_field(db_session, field1_in, user_id=test_user_id)
    await field_service.create_field(db_session, field2_in, user_id=test_user_id)

    # Retrieve fields
    fields = await field_service.get_user_fields(db_session, user_id=test_user_id)

    assert len(fields) == 2
    assert fields[0].name in ["email", "phone"]
