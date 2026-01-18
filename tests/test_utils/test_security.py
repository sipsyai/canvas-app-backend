"""Unit tests for security utilities"""
import pytest
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

def test_password_hashing():
    """Test password hashing and verification"""
    password = "MySecurePassword123"
    hashed = hash_password(password)

    # Hash should not equal plain password
    assert hashed != password

    # Verify should return True for correct password
    assert verify_password(password, hashed) is True

    # Verify should return False for wrong password
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_creation():
    """Test JWT token creation and decoding"""
    payload = {"sub": "user_123", "email": "test@example.com"}
    token = create_access_token(payload)

    # Token should be a string
    assert isinstance(token, str)
    assert len(token) > 0

    # Decode token
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user_123"
    assert decoded["email"] == "test@example.com"

def test_jwt_invalid_token():
    """Test JWT decoding with invalid token"""
    decoded = decode_access_token("invalid_token")
    assert decoded is None
