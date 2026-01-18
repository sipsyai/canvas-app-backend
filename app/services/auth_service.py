"""Auth Service - User authentication and authorization"""
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, TokenBlacklist
from app.schemas import UserRegister
from app.services.base import BaseService
from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


class AuthService(BaseService[User]):
    """Service for authentication operations"""

    def __init__(self):
        super().__init__(User)

    async def get_user_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> User | None:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def register_user(
        self,
        db: AsyncSession,
        user_in: UserRegister,
    ) -> User:
        """
        Register a new user.

        Args:
            db: Database session
            user_in: User registration data

        Returns:
            Created user

        Raises:
            HTTPException 400: If email already exists
        """
        # Check if user already exists
        existing_user = await self.get_user_by_email(db, user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Hash password
        hashed_password = hash_password(user_in.password)

        # Create user
        user_data = {
            "id": uuid.uuid4(),
            "email": user_in.email,
            "full_name": user_in.full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_verified": False,
        }

        new_user = User(**user_data)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> User:
        """
        Authenticate user with email and password.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            Authenticated user

        Raises:
            HTTPException 401: If credentials are invalid
        """
        user = await self.get_user_by_email(db, email)

        # Check if user exists
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # Update last login
        user.last_login = datetime.now(UTC)
        await db.commit()
        await db.refresh(user)

        return user

    def create_token_for_user(self, user: User) -> dict:
        """
        Create JWT access token for user.

        Args:
            user: User object

        Returns:
            Dictionary with access_token, token_type, expires_in, and jti
        """
        # Generate unique JTI (JWT ID) for token revocation
        jti = str(uuid.uuid4())

        # Create token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "jti": jti,
            },
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
            "jti": jti,  # Return jti for potential blacklist storage
        }

    async def is_token_blacklisted(self, db: AsyncSession, jti: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            db: Database session
            jti: JWT ID

        Returns:
            True if token is blacklisted, False otherwise
        """
        result = await db.execute(
            select(TokenBlacklist).where(TokenBlacklist.jti == jti)
        )
        return result.scalar_one_or_none() is not None

    async def blacklist_token(
        self,
        db: AsyncSession,
        token: str,
        user_id: uuid.UUID,
    ) -> None:
        """
        Blacklist a token (logout).

        Args:
            db: Database session
            token: JWT token string
            user_id: User ID

        Raises:
            HTTPException 401: If token is invalid
        """
        # Decode token to get JTI and expiration
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti or not exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # Convert exp timestamp to datetime
        expires_at = datetime.fromtimestamp(exp, tz=UTC)

        # Add to blacklist
        blacklist_entry = TokenBlacklist(
            jti=jti,
            user_id=user_id,
            expires_at=expires_at,
        )
        db.add(blacklist_entry)
        await db.commit()


# Singleton instance
auth_service = AuthService()
