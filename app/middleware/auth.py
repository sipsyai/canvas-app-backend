"""Authentication middleware - JWT verification"""
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.utils.security import decode_access_token


# HTTP Bearer scheme (extracts token from "Authorization: Bearer <token>" header)
# auto_error=False prevents automatic 403, we handle 401 manually
security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> uuid.UUID:
    """
    Extract and validate JWT token, return user ID as UUID.
    Also checks if token is blacklisted.

    Usage in routers:
        @router.get("/protected")
        async def protected_route(user_id: uuid.UUID = Depends(get_current_user_id)):
            ...

    Raises:
        HTTPException 401 if token is invalid/expired/blacklisted
    """
    # Check if credentials were provided
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str: str = payload.get("sub")
    jti: str = payload.get("jti")

    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Check if token is blacklisted (only if jti exists)
    if jti:
        from app.services import auth_service
        is_blacklisted = await auth_service.is_token_blacklisted(db, jti)
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Convert string to UUID
    try:
        return uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
        )


async def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> uuid.UUID | None:
    """
    Optional authentication - returns user_id if token provided, None otherwise.

    Useful for public endpoints that behave differently for authenticated users.
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        return None

    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None

    # Convert string to UUID
    try:
        return uuid.UUID(user_id_str)
    except ValueError:
        return None
