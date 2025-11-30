"""Audio processing endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.project import ProjectService

router = APIRouter()


@router.post("/{project_id}/process-stems")
async def process_stems(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    project = await service.get_by_id(project_id, user.id)
    # In production, this would trigger a Celery task
    return {"message": "Stem separation started", "project_id": str(project_id)}


@router.post("/{project_id}/generate-vocals")
async def generate_vocals(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    project = await service.get_by_id(project_id, user.id)
    return {"message": "Vocal generation started", "project_id": str(project_id)}


@router.post("/{project_id}/mix")
async def mix_project(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    project = await service.get_by_id(project_id, user.id)
    return {"message": "Mixing started", "project_id": str(project_id)}
