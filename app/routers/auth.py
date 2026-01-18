"""Authentication endpoints - Register, Login, Get User"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas import TokenResponse, UserRegister, UserResponse
from app.services import auth_service
from app.utils.rate_limit import limiter

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("5/minute")  # Max 5 registrations per minute per IP
async def register_user(
    request: Request,
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

    Stores user in PostgreSQL database with bcrypt-hashed password.
    """
    user = await auth_service.register_user(db, user_in)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")  # Max 10 login attempts per minute per IP
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Login user and return JWT token.

    Form data:
    - username: User email
    - password: User password

    Returns JWT token with 1-hour expiration.
    Verifies user credentials against PostgreSQL database.
    """
    # Authenticate user (verifies email, password, and active status)
    user = await auth_service.authenticate_user(db, form_data.username, form_data.password)

    # Create JWT token
    token_data = auth_service.create_token_for_user(user)

    return TokenResponse(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        expires_in=token_data["expires_in"],
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current authenticated user.

    Requires "Authorization: Bearer <token>" header.
    Fetches user data from PostgreSQL database.
    """
    user = await auth_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.post("/logout", status_code=204)
async def logout_user(
    request: Request,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user by blacklisting their current JWT token.

    Requires "Authorization: Bearer <token>" header.
    The token will be added to the blacklist and cannot be used again.
    """
    # Extract token from Authorization header
    from fastapi.security import HTTPBearer
    security = HTTPBearer()
    credentials = await security(request)
    token = credentials.credentials

    # Blacklist the token
    await auth_service.blacklist_token(db, token, user_id)

    return None  # 204 No Content
