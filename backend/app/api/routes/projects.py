"""Project endpoints."""
import asyncio
import math
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.project import ProjectStatus
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectListResponse
from app.services.project import ProjectService
from app.utils.storage import save_upload

router = APIRouter()


@router.post("", response_model=ProjectResponse)
async def create_project(
    data: ProjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.create(user.id, data)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    items, total = await service.list_by_user(user.id, page, page_size)
    pages = math.ceil(total / page_size) if total > 0 else 1
    return ProjectListResponse(
        items=items, total=total, page=page, page_size=page_size, pages=pages
    )


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
    await service.get_by_id(project_id, user.id)  # Verify access
    path = await save_upload(file, f"projects/{user.id}/{project_id}")
    # Lazy import to avoid loading heavy audio dependencies at startup
    from app.utils.audio import get_audio_duration
    # Run blocking audio duration calculation in thread pool
    duration = await asyncio.to_thread(get_audio_duration, path)
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
