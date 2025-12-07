"""Authentication endpoints."""
from datetime import timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from app.config import settings
from app.db import get_db
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, Token,
    RefreshTokenRequest, AccessTokenResponse, MessageResponse
)
from app.services.auth import AuthService
from app.extensions import limiter
from app.utils.security import create_access_token, decode_token, get_token_expiry_delta
from app.utils.token_blacklist import blacklist_token, blacklist_user_tokens

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    service = AuthService(db)
    return await service.register(data)


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return access and refresh tokens."""
    service = AuthService(db)
    return await service.login(data.email, data.password)


@router.post("/refresh", response_model=AccessTokenResponse)
@limiter.limit("30/minute")
async def refresh_token(
    request: Request,
    data: RefreshTokenRequest,
):
    """Exchange a refresh token for a new access token.

    The refresh token is not rotated - it remains valid until its expiry.
    Only the access token is refreshed.
    """
    try:
        payload = decode_token(data.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Create new access token
        new_access_token = create_access_token({"sub": user_id})

        return AccessTokenResponse(access_token=new_access_token)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired") from None
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from None


@router.post("/logout", response_model=MessageResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Logout and invalidate the current access token.

    The token is added to a blacklist until its natural expiry time.
    This prevents the token from being used even if it hasn't expired yet.
    """
    try:
        payload = decode_token(credentials.credentials)
        jti = payload.get("jti")
        token_type = payload.get("type", "access")

        if jti:
            # Blacklist the token until it would naturally expire
            expiry_delta = get_token_expiry_delta(token_type)
            await blacklist_token(jti, expiry_delta)

        return MessageResponse(message="Successfully logged out")

    except jwt.PyJWTError:
        # Even if token is invalid, acknowledge logout
        return MessageResponse(message="Successfully logged out")


@router.post("/revoke-all", response_model=MessageResponse)
async def revoke_all_tokens(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Revoke all tokens for the current user.

    This is useful after a password change or if the user suspects
    their account has been compromised. All existing tokens will
    become invalid immediately.
    """
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Also blacklist the current token
        jti = payload.get("jti")
        token_type = payload.get("type", "access")
        if jti:
            expiry_delta = get_token_expiry_delta(token_type)
            await blacklist_token(jti, expiry_delta)

        # Invalidate all user tokens
        await blacklist_user_tokens(user_id)

        return MessageResponse(message="All tokens have been revoked")

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token") from None
