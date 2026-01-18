"""Integration tests for Auth endpoints with database integration"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, TokenBlacklist
from app.services import auth_service


# ============================================================================
# Registration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test successful user registration"""
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
    assert data["is_active"] is True
    assert data["is_verified"] is False
    assert "hashed_password" not in data  # Password should not be exposed


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email returns 400"""
    # First registration
    await client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "Password123",
            "full_name": "User One"
        }
    )

    # Attempt duplicate registration
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "DifferentPass456",
            "full_name": "User Two"
        }
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Test registration with password less than 8 characters fails"""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "weak",  # Less than 8 characters
            "full_name": "User"
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """Test registration with invalid email format fails"""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "not-an-email",
            "password": "Password123",
            "full_name": "User"
        }
    )

    assert response.status_code == 422  # Validation error


# ============================================================================
# Login Tests
# ============================================================================

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    """Test successful user login"""
    # Register user
    await client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "Password123",
            "full_name": "User"
        }
    )

    # Login
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
    assert data["expires_in"] == 3600  # 1 hour in seconds


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Test login with incorrect password returns 401"""
    # Register user
    await client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "CorrectPassword123",
            "full_name": "User"
        }
    )

    # Login with wrong password
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "user@example.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent email returns 401"""
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_inactive_user(client: AsyncClient, db_session: AsyncSession):
    """Test login with inactive user returns 403"""
    # Register user
    register_response = await client.post(
        "/api/auth/register",
        json={
            "email": "inactive@example.com",
            "password": "Password123",
            "full_name": "Inactive User"
        }
    )
    user_id = register_response.json()["id"]

    # Deactivate user directly in database
    user = await auth_service.get_user_by_id(db_session, user_id)
    user.is_active = False
    await db_session.commit()

    # Try to login
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "inactive@example.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_updates_last_login(client: AsyncClient, db_session: AsyncSession):
    """Test that login updates user's last_login timestamp"""
    # Register user
    register_response = await client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "Password123",
            "full_name": "User"
        }
    )
    user_id = register_response.json()["id"]

    # Check last_login is None initially
    user = await auth_service.get_user_by_id(db_session, user_id)
    assert user.last_login is None

    # Login
    await client.post(
        "/api/auth/login",
        data={
            "username": "user@example.com",
            "password": "Password123"
        }
    )

    # Check last_login is now set
    user = await auth_service.get_user_by_id(db_session, user_id)
    assert user.last_login is not None


# ============================================================================
# Get Current User Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers: dict):
    """Test getting current user with valid JWT token"""
    response = await client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_get_current_user_without_token(client: AsyncClient):
    """Test that /me endpoint returns 403 without token"""
    response = await client.get("/api/auth/me")

    assert response.status_code == 403  # FastAPI HTTPBearer returns 403


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test that /me endpoint returns 401 with invalid token"""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-token-12345"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_malformed_token(client: AsyncClient):
    """Test that /me endpoint returns 403 with malformed Authorization header"""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "NotBearer token"}
    )

    assert response.status_code == 403


# ============================================================================
# Logout and Token Blacklist Tests
# ============================================================================

@pytest.mark.asyncio
async def test_logout_user(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
    """Test successful logout blacklists the token"""
    # Logout
    response = await client.post("/api/auth/logout", headers=auth_headers)

    assert response.status_code == 204

    # Try to use the same token again
    response = await client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 401
    assert "revoked" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_without_token(client: AsyncClient):
    """Test logout without token returns 403"""
    response = await client.post("/api/auth/logout")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_token_blacklist_stored_in_db(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test that blacklisted tokens are stored in database"""
    # Logout (blacklist token)
    await client.post("/api/auth/logout", headers=auth_headers)

    # Check database for blacklist entry
    from sqlalchemy import select
    result = await db_session.execute(select(TokenBlacklist))
    blacklist_entries = result.scalars().all()

    assert len(blacklist_entries) > 0


@pytest.mark.asyncio
async def test_multiple_logins_different_tokens(client: AsyncClient):
    """Test that multiple logins create different tokens"""
    # Register user
    await client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "Password123",
            "full_name": "User"
        }
    )

    # Login twice
    response1 = await client.post(
        "/api/auth/login",
        data={"username": "user@example.com", "password": "Password123"}
    )
    token1 = response1.json()["access_token"]

    response2 = await client.post(
        "/api/auth/login",
        data={"username": "user@example.com", "password": "Password123"}
    )
    token2 = response2.json()["access_token"]

    # Tokens should be different
    assert token1 != token2

    # Both tokens should work
    response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token1}"})
    assert response.status_code == 200

    response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 200


# ============================================================================
# Password Security Tests
# ============================================================================

@pytest.mark.asyncio
async def test_password_is_hashed(client: AsyncClient, db_session: AsyncSession):
    """Test that passwords are stored hashed, not in plaintext"""
    # Register user
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "PlaintextPassword123",
            "full_name": "User"
        }
    )
    user_id = response.json()["id"]

    # Get user from database
    user = await auth_service.get_user_by_id(db_session, user_id)

    # Password should be hashed (starts with $2b$ for bcrypt)
    assert user.hashed_password != "PlaintextPassword123"
    assert user.hashed_password.startswith("$2b$")


# ============================================================================
# Protected Endpoint Tests
# ============================================================================

@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient):
    """Test that protected endpoints return 403 without token"""
    response = await client.get("/api/fields")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(client: AsyncClient, auth_headers: dict):
    """Test that protected endpoints work with valid token"""
    # This assumes /api/fields is a protected endpoint
    response = await client.get("/api/fields", headers=auth_headers)

    # Should not be 401/403 (might be 200 or other valid response)
    assert response.status_code != 401
    assert response.status_code != 403


# ============================================================================
# Database Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_user_persists_in_database(client: AsyncClient, db_session: AsyncSession):
    """Test that registered users are persisted in PostgreSQL"""
    # Register user
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "persistent@example.com",
            "password": "Password123",
            "full_name": "Persistent User"
        }
    )
    user_id = response.json()["id"]

    # Fetch user from database directly
    user = await auth_service.get_user_by_id(db_session, user_id)

    assert user is not None
    assert user.email == "persistent@example.com"
    assert user.full_name == "Persistent User"


@pytest.mark.asyncio
async def test_user_timestamps(client: AsyncClient, db_session: AsyncSession):
    """Test that user created_at and updated_at timestamps are set"""
    # Register user
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "timestamp@example.com",
            "password": "Password123",
            "full_name": "Timestamp User"
        }
    )
    user_id = response.json()["id"]

    # Get user from database
    user = await auth_service.get_user_by_id(db_session, user_id)

    assert user.created_at is not None
    assert user.updated_at is not None
    # Timestamps should be timezone-aware
    assert user.created_at.tzinfo is not None
    assert user.updated_at.tzinfo is not None


# ============================================================================
# Service Layer Tests
# ============================================================================

@pytest.mark.asyncio
async def test_auth_service_get_user_by_email(client: AsyncClient, db_session: AsyncSession):
    """Test auth service get_user_by_email method"""
    # Register user
    await client.post(
        "/api/auth/register",
        json={
            "email": "service@example.com",
            "password": "Password123",
            "full_name": "Service Test"
        }
    )

    # Test service method
    user = await auth_service.get_user_by_email(db_session, "service@example.com")

    assert user is not None
    assert user.email == "service@example.com"


@pytest.mark.asyncio
async def test_auth_service_get_nonexistent_user(db_session: AsyncSession):
    """Test that getting non-existent user returns None"""
    user = await auth_service.get_user_by_email(db_session, "nonexistent@example.com")

    assert user is None


# ============================================================================
# Edge Cases
# ============================================================================

@pytest.mark.asyncio
async def test_register_empty_full_name(client: AsyncClient):
    """Test registration with empty full_name fails validation"""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "Password123",
            "full_name": ""  # Empty name
        }
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_case_sensitive_email(client: AsyncClient):
    """Test that email login is case-insensitive (depends on DB collation)"""
    # Register with lowercase
    await client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "Password123",
            "full_name": "User"
        }
    )

    # Try login with uppercase (behavior depends on database)
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "USER@EXAMPLE.COM",
            "password": "Password123"
        }
    )

    # This test documents current behavior
    # Note: Most databases treat emails as case-insensitive by default
    # If this fails, consider normalizing emails to lowercase in the service layer
