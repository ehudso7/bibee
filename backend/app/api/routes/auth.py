"""Authentication endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.register(data)


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
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
