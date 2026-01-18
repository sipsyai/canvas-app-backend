"""Integration tests for Field endpoints"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_field(client: AsyncClient, auth_headers: dict):
    """Test creating field via API"""
    response = await client.post(
        "/api/fields",
        headers=auth_headers,
        json={
            "name": "email",
            "label": "Email Address",
            "type": "email",
            "config": {"validation": {"required": True}}
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "email"
    assert data["type"] == "email"
    assert data["id"].startswith("fld_")

@pytest.mark.asyncio
async def test_list_fields(client: AsyncClient, auth_headers: dict):
    """Test listing fields"""
    # Create two fields
    await client.post("/api/fields", headers=auth_headers, json={"name": "email", "label": "Email", "type": "email"})
    await client.post("/api/fields", headers=auth_headers, json={"name": "phone", "label": "Phone", "type": "phone"})

    # List fields
    response = await client.get("/api/fields", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

@pytest.mark.asyncio
async def test_get_field_not_found(client: AsyncClient, auth_headers: dict):
    """Test getting non-existent field returns 404"""
    response = await client.get("/api/fields/fld_nonexistent", headers=auth_headers)

    assert response.status_code == 404
