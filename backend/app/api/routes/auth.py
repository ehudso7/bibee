"""Authentication endpoints."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.db import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth import AuthService
from app.extensions import limiter

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.register(data)


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.login(data.email, data.password)


@router.post("/logout")
async def logout():
    """Logout endpoint for token invalidation.

    Note: JWT tokens are stateless, so server-side invalidation requires
    a token blacklist (not implemented). The client should clear the token
    from storage. This endpoint acknowledges the logout request.
    """
    return {"message": "Successfully logged out"}
