# 🚀 Authentication Quick Start Guide

## Files Added

```
app/
├── middleware/
│   ├── __init__.py          # Updated: exports auth functions
│   └── auth.py              # NEW: JWT verification middleware
├── routers/
│   └── auth.py              # NEW: /api/auth endpoints
└── utils/
    └── security.py          # NEW: Password & JWT utilities
```

## Quick Test (5 minutes)

### 1. Start the Server
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456",
    "full_name": "Test User"
  }'
```

**Expected Response:**
```json
{
  "id": "user_1",
  "email": "test@example.com",
  "full_name": "Test User"
}
```

### 3. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test123456"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Save the token!** You'll need it for protected endpoints.

### 4. Test Protected Endpoint
```bash
# Replace YOUR_TOKEN_HERE with the actual token from step 3
curl -X POST http://localhost:8000/api/fields \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "email",
    "label": "Email Address",
    "type": "email"
  }'
```

**Expected Response:** 201 Created with field data

**Without token:**
```bash
curl -X POST http://localhost:8000/api/fields \
  -H "Content-Type: application/json" \
  -d '{"name": "email", "label": "Email", "type": "email"}'
```

**Expected Response:** 401 Unauthorized

## API Documentation

Visit: http://localhost:8000/docs

Interactive API docs with built-in authentication testing!

## Common Issues

### 1. "Module not found" errors
```bash
source venv/bin/activate  # Always activate venv first!
pip install -r requirements.txt
```

### 2. "Invalid token" errors
- Check token expiration (1 hour)
- Ensure token is in format: `Bearer <token>`
- Verify SECRET_KEY in .env matches

### 3. bcrypt warnings
Safe to ignore the warning:
```
(trapped) error reading bcrypt version
```
This is a passlib internal check - functionality is not affected.

## Integration Example

### Python/JavaScript Frontend

```javascript
// 1. Register
const registerResponse = await fetch('http://localhost:8000/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'Password123',
    full_name: 'John Doe'
  })
});

// 2. Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=user@example.com&password=Password123'
});

const { access_token } = await loginResponse.json();

// 3. Use token for protected requests
const fieldsResponse = await fetch('http://localhost:8000/api/fields', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

## Next Steps

1. ✅ Test all endpoints with authentication
2. 🔄 Replace MOCK_USERS with database (production)
3. 🔒 Add refresh tokens (optional)
4. 📧 Add email verification (optional)
5. 🔐 Integrate Supabase Auth (optional)

## Need Help?

- Check `/docs` endpoint for interactive API documentation
- Read `tasks/TASK-07-COMPLETED.md` for detailed implementation notes
- Review `CLAUDE.md` for project guidelines
