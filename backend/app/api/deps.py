"""API dependencies."""
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.db import get_db
from app.models.user import User
from app.services.auth import AuthService
from app.utils.token_blacklist import is_token_blacklisted, get_user_token_invalidation_time

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from the JWT token.

    Validates:
    - Token signature and expiry
    - Token type is "access"
    - Token is not blacklisted
    - Token was issued after any user-level invalidation
    - User exists in database
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        token_type = payload.get("type")
        jti = payload.get("jti")
        iat = payload.get("iat")

        if not user_id or token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token")

        # Check if this specific token is blacklisted
        if jti and await is_token_blacklisted(jti):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        # Check if all user tokens were invalidated (e.g., password change)
        # Normalize iat to int for consistent comparison with Redis timestamp
        if iat:
            iat_timestamp = int(iat) if isinstance(iat, (int, float)) else 0
            invalidation_time = await get_user_token_invalidation_time(user_id)
            if invalidation_time and iat_timestamp < invalidation_time:
        if iat:
            invalidation_time = await get_user_token_invalidation_time(user_id)
            if invalidation_time and iat < invalidation_time:
                raise HTTPException(status_code=401, detail="Token has been invalidated")

        auth_service = AuthService(db)
        return await auth_service.get_user_by_id(UUID(user_id))

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired") from None
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token") from None
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token") from None


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Get the current user if authenticated, or None if not.

    Useful for endpoints that have different behavior for authenticated vs anonymous users.
    """
    if credentials is None:
        return None

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        token_type = payload.get("type")
        jti = payload.get("jti")
        iat = payload.get("iat")

        if not user_id or token_type != "access":
            return None

        if jti and await is_token_blacklisted(jti):
            return None

        # Normalize iat to int for consistent comparison with Redis timestamp
        if iat:
            iat_timestamp = int(iat) if isinstance(iat, (int, float)) else 0
            invalidation_time = await get_user_token_invalidation_time(user_id)
            if invalidation_time and iat_timestamp < invalidation_time:
        if iat:
            invalidation_time = await get_user_token_invalidation_time(user_id)
            if invalidation_time and iat < invalidation_time:
                return None

        auth_service = AuthService(db)
        return await auth_service.get_user_by_id(UUID(user_id))

    except (jwt.PyJWTError, ValueError):
        return None
