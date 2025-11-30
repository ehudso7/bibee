"""API router configuration."""
from fastapi import APIRouter
from app.api.routes import auth, users, voices, projects, audio, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(voices.router, prefix="/voices", tags=["voices"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
