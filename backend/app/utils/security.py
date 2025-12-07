"""Security utilities."""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Create a JWT access token with JTI for blacklisting support."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "jti": str(uuid.uuid4()),  # Unique token ID for blacklisting
    })
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with JTI for blacklisting support."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
        "jti": str(uuid.uuid4()),  # Unique token ID for blacklisting
    })
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token.

    Args:
        token: The JWT token string

    Returns:
        The decoded token payload

    Raises:
        jwt.PyJWTError: If token is invalid or expired
    """
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )


def get_token_expiry_delta(token_type: str) -> timedelta:
    """Get the expiry duration for a token type.

    Args:
        token_type: Either "access" or "refresh"

    Returns:
        The timedelta for token expiry
    """
    if token_type == "refresh":
        return timedelta(days=settings.refresh_token_expire_days)
    return timedelta(minutes=settings.access_token_expire_minutes)
