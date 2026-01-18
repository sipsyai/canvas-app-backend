"""Authentication endpoints - Register, Login, Get User"""
import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()


# Schemas
class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    full_name: str = Field(..., min_length=1, description="Full name")


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds


# Mock user storage (REPLACE with real database in production!)
# For MVP, use in-memory dict. For production, use auth.users table.
MOCK_USERS: dict = {}


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(
    user_in: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register new user.

    Example request:
    ```json
    {
        "email": "user@example.com",
        "password": "SecurePassword123",
        "full_name": "Ali Yılmaz"
    }
    ```

    TODO: Store user in auth.users table (Supabase or local PostgreSQL)
    """
    # Check if user already exists
    if user_in.email in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = hash_password(user_in.password)

    # Create user (mock - replace with database)
    user_id = str(uuid.uuid4())
    MOCK_USERS[user_in.email] = {
        "id": user_id,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "hashed_password": hashed_password,
    }

    return UserResponse(
        id=user_id,
        email=user_in.email,
        full_name=user_in.full_name,
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Login user and return JWT token.

    Form data:
    - username: User email
    - password: User password

    Returns JWT token with 1-hour expiration.
    """
    # Get user (mock - replace with database query)
    user = MOCK_USERS.get(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verify password
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create JWT token
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current authenticated user.

    Requires "Authorization: Bearer <token>" header.
    """
    # Find user by ID (mock - replace with database query)
    user = next(
        (u for u in MOCK_USERS.values() if u["id"] == str(user_id)),
        None,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
    )
