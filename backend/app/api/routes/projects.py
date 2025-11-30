"""Project endpoints."""
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.project import ProjectStatus
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project import ProjectService
from app.utils.storage import save_upload
from app.utils.audio import get_audio_duration

router = APIRouter()


@router.post("", response_model=ProjectResponse)
async def create_project(
    data: ProjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.create(user.id, data)


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.list_by_user(user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.get_by_id(project_id, user.id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.update(project_id, user.id, data)


@router.post("/{project_id}/upload")
async def upload_audio(
    project_id: UUID,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    project = await service.get_by_id(project_id, user.id)
    path = await save_upload(file, f"projects/{user.id}/{project_id}")
    duration = get_audio_duration(path)
    await service.update_status(project_id, ProjectStatus.UPLOADING, original_path=path, duration_seconds=duration)
    return {"message": "Uploaded", "path": path, "duration": duration}


@router.delete("/{project_id}")
async def delete_project(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    await service.delete(project_id, user.id)
    return {"message": "Deleted"}
