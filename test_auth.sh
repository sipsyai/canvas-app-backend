#!/bin/bash

# Test script for authentication endpoints

BASE_URL="http://localhost:8000"

echo "🧪 Testing Authentication Endpoints"
echo "===================================="
echo ""

# 1. Test Register
echo "1. Testing /api/auth/register..."
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "full_name": "Test User"
  }')

echo "Response: ${REGISTER_RESPONSE}"
echo ""

# 2. Test Login
echo "2. Testing /api/auth/login..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPassword123")

echo "Response: ${LOGIN_RESPONSE}"
echo ""

# Extract token (basic parsing - works for simple cases)
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo "✅ Token received: ${TOKEN:0:50}..."
    echo ""

    # 3. Test /me endpoint
    echo "3. Testing /api/auth/me..."
    ME_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/auth/me" \
      -H "Authorization: Bearer ${TOKEN}")

    echo "Response: ${ME_RESPONSE}"
    echo ""

    # 4. Test protected endpoint (create field)
    echo "4. Testing protected endpoint /api/fields..."
    FIELD_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/fields" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "test_field",
        "label": "Test Field",
        "type": "text"
      }')

    echo "Response: ${FIELD_RESPONSE}"
    echo ""
else
    echo "❌ Failed to get token from login response"
fi

echo "===================================="
echo "✅ Authentication testing complete!"
