"""Unit tests for Record Service (JSONB handling)"""
import pytest
from app.services import record_service, object_service
from app.schemas import RecordCreate, ObjectCreate, RecordUpdate

@pytest.mark.asyncio
async def test_create_record_with_jsonb_data(db_session, test_user_id):
    """Test creating record with JSONB data"""
    # First create object
    object_in = ObjectCreate(
        name="contact",
        label="Contact",
        plural_label="Contacts",
    )
    obj = await object_service.create_object(db_session, object_in, user_id=test_user_id)

    # Create record
    record_in = RecordCreate(
        object_id=obj.id,
        data={
            "fld_name": "Ali Yılmaz",
            "fld_email": "ali@example.com",
            "fld_phone": "+90 555 1234567"
        }
    )
    record = await record_service.create_record(db_session, record_in, user_id=test_user_id)

    assert record.id.startswith("rec_")
    assert record.object_id == obj.id
    assert record.data["fld_name"] == "Ali Yılmaz"
    assert record.primary_value == "Ali Yılmaz"  # First text field

@pytest.mark.asyncio
async def test_update_record_merges_data(db_session, test_user_id):
    """Test that record update merges JSONB data, doesn't replace"""
    # Create object
    object_in = ObjectCreate(name="contact", label="Contact", plural_label="Contacts")
    obj = await object_service.create_object(db_session, object_in, user_id=test_user_id)

    # Create record
    record_in = RecordCreate(
        object_id=obj.id,
        data={
            "fld_name": "Ali Yılmaz",
            "fld_email": "ali@example.com"
        }
    )
    record = await record_service.create_record(db_session, record_in, user_id=test_user_id)

    # Update only email
    update_in = RecordUpdate(data={"fld_email": "newemail@example.com"})
    updated = await record_service.update_record(db_session, record.id, update_in, user_id=test_user_id)

    # Should merge, not replace
    assert updated.data["fld_name"] == "Ali Yılmaz"  # Still exists!
    assert updated.data["fld_email"] == "newemail@example.com"  # Updated
