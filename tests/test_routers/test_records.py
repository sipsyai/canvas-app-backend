"""Integration tests for Record endpoints (JSONB)"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_get_record(client: AsyncClient, auth_headers: dict):
    """Test creating record with JSONB data and retrieving it"""
    # Create object first
    obj_response = await client.post(
        "/api/objects",
        headers=auth_headers,
        json={
            "name": "contact",
            "label": "Contact",
            "plural_label": "Contacts"
        }
    )
    object_id = obj_response.json()["id"]

    # Create record
    record_response = await client.post(
        "/api/records",
        headers=auth_headers,
        json={
            "object_id": object_id,
            "data": {
                "fld_name": "Ali Yılmaz",
                "fld_email": "ali@example.com"
            }
        }
    )

    assert record_response.status_code == 201
    record_data = record_response.json()
    assert record_data["data"]["fld_name"] == "Ali Yılmaz"
    assert record_data["primary_value"] == "Ali Yılmaz"

    # Get record
    record_id = record_data["id"]
    get_response = await client.get(f"/api/records/{record_id}", headers=auth_headers)

    assert get_response.status_code == 200
    assert get_response.json()["id"] == record_id

@pytest.mark.asyncio
async def test_list_records_with_pagination(client: AsyncClient, auth_headers: dict):
    """Test listing records with pagination"""
    # Create object
    obj_response = await client.post(
        "/api/objects",
        headers=auth_headers,
        json={"name": "contact", "label": "Contact", "plural_label": "Contacts"}
    )
    object_id = obj_response.json()["id"]

    # Create 5 records
    for i in range(5):
        await client.post(
            "/api/records",
            headers=auth_headers,
            json={
                "object_id": object_id,
                "data": {"fld_name": f"User {i}"}
            }
        )

    # List with pagination
    response = await client.get(
        f"/api/records?object_id={object_id}&page=1&page_size=3",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 3
    assert len(data["records"]) == 3
