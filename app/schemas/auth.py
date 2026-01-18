"""Auth Schemas - User registration, login, and responses"""
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    full_name: str = Field(..., min_length=1, description="Full name")


class UserLogin(BaseModel):
    """Schema for user login (not used with OAuth2PasswordRequestForm, but kept for docs)"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """Schema for user response (public profile)"""
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds (1 hour)


class TokenBlacklist(BaseModel):
    """Schema for blacklisted tokens"""
    jti: str = Field(..., description="JWT ID (unique token identifier)")
    user_id: uuid.UUID = Field(..., description="User ID")
    expires_at: datetime = Field(..., description="Token expiration time")
    blacklisted_at: datetime = Field(..., description="When token was blacklisted")
