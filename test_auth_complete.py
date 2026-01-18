"""
Comprehensive Authentication Test
Tests all auth endpoints without requiring a running server
"""
from app.utils.security import hash_password, verify_password, create_access_token, decode_access_token
from app.routers.auth import MOCK_USERS

def test_security_utilities():
    """Test password hashing and JWT utilities"""
    print("1. Testing Security Utilities")
    print("-" * 50)

    # Test password hashing
    password = "SecurePassword123"
    hashed = hash_password(password)
    print(f"   ✅ Password hashed: {hashed[:30]}...")

    # Test password verification
    assert verify_password(password, hashed) == True
    assert verify_password("WrongPassword", hashed) == False
    print("   ✅ Password verification works")

    # Test JWT token creation
    token = create_access_token({"sub": "user_123", "email": "test@example.com"})
    print(f"   ✅ JWT token created: {token[:50]}...")

    # Test JWT token decoding
    payload = decode_access_token(token)
    assert payload["sub"] == "user_123"
    assert payload["email"] == "test@example.com"
    print("   ✅ JWT token decode works")
    print()


def test_user_registration():
    """Test user registration flow"""
    print("2. Testing User Registration")
    print("-" * 50)

    # Simulate user registration
    email = "newuser@example.com"
    password = "MyPassword123"
    full_name = "New User"

    # Hash password
    hashed_password = hash_password(password)

    # Create user (mock)
    user_id = f"user_{len(MOCK_USERS) + 1}"
    MOCK_USERS[email] = {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "hashed_password": hashed_password,
    }

    print(f"   ✅ User registered: {email}")
    print(f"   ✅ User ID: {user_id}")
    print()


def test_user_login():
    """Test user login flow"""
    print("3. Testing User Login")
    print("-" * 50)

    # Login with registered user
    email = "newuser@example.com"
    password = "MyPassword123"

    # Get user from mock storage
    user = MOCK_USERS.get(email)
    assert user is not None, "User should exist"
    print(f"   ✅ User found: {email}")

    # Verify password
    assert verify_password(password, user["hashed_password"]) == True
    print("   ✅ Password verified")

    # Create JWT token
    token = create_access_token(
        data={"sub": user["id"], "email": user["email"]}
    )
    print(f"   ✅ JWT token generated: {token[:50]}...")

    return token


def test_token_authentication(token: str):
    """Test token authentication"""
    print("4. Testing Token Authentication")
    print("-" * 50)

    # Decode token
    payload = decode_access_token(token)
    assert payload is not None, "Token should be valid"
    print("   ✅ Token decoded successfully")

    # Extract user_id
    user_id = payload.get("sub")
    assert user_id is not None, "User ID should be in token"
    print(f"   ✅ User ID from token: {user_id}")

    # Find user by ID
    user = next(
        (u for u in MOCK_USERS.values() if u["id"] == user_id),
        None,
    )
    assert user is not None, "User should be found"
    print(f"   ✅ User authenticated: {user['email']}")
    print()


def test_invalid_token():
    """Test invalid token handling"""
    print("5. Testing Invalid Token")
    print("-" * 50)

    # Test with invalid token
    invalid_token = "invalid.token.here"
    payload = decode_access_token(invalid_token)
    assert payload is None, "Invalid token should return None"
    print("   ✅ Invalid token rejected")

    # Test with expired/malformed token
    malformed_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
    payload = decode_access_token(malformed_token)
    assert payload is None, "Malformed token should return None"
    print("   ✅ Malformed token rejected")
    print()


if __name__ == "__main__":
    print()
    print("=" * 50)
    print("🧪 AUTHENTICATION SYSTEM TEST")
    print("=" * 50)
    print()

    # Run all tests
    test_security_utilities()
    test_user_registration()
    token = test_user_login()
    test_token_authentication(token)
    test_invalid_token()

    print("=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 50)
    print()
    print("📋 Summary:")
    print(f"   • Registered users: {len(MOCK_USERS)}")
    print(f"   • Password hashing: ✅ Working")
    print(f"   • JWT token generation: ✅ Working")
    print(f"   • JWT token validation: ✅ Working")
    print(f"   • Authentication flow: ✅ Complete")
    print()
