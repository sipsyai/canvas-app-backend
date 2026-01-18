"""Integration tests for Auth endpoints"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration"""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "full_name": "New User"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    """Test user login"""
    # First register
    await client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "Password123",
            "full_name": "User"
        }
    )

    # Then login
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "user@example.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers: dict):
    """Test getting current user with JWT token"""
    response = await client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient):
    """Test that protected endpoints return 401 without token"""
    response = await client.get("/api/fields")

    assert response.status_code == 403  # FastAPI HTTPBearer returns 403
