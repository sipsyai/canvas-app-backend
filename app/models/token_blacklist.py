"""Token Blacklist Model - Store revoked JWT tokens"""
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base


class TokenBlacklist(Base):
    """
    Token blacklist for logout functionality.

    Stores JWT IDs (jti) of revoked tokens until they expire.
    """
    __tablename__ = "token_blacklist"

    # Primary Key (JWT ID)
    jti = Column(String, primary_key=True, index=True)

    # User who owned this token
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Token expiration time (auto-cleanup after this)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # When token was blacklisted
    blacklisted_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"<TokenBlacklist(jti={self.jti}, user_id={self.user_id})>"

    def to_dict(self) -> dict:
        """Convert to dictionary (useful for debugging)"""
        return {
            "jti": self.jti,
            "user_id": str(self.user_id),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "blacklisted_at": self.blacklisted_at.isoformat() if self.blacklisted_at else None,
        }
