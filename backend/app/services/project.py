"""Project service."""
import os
import shutil
import logging
from uuid import UUID
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.config import settings

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, data: ProjectCreate) -> Project:
        project = Project(
            user_id=user_id,
            name=data.name,
            description=data.description,
            voice_persona_id=data.voice_persona_id,
            vocal_mode=data.vocal_mode,
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_by_id(self, project_id: UUID, user_id: UUID) -> Project:
        result = await self.db.execute(
            select(Project).where(Project.id == project_id, Project.user_id == user_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    async def list_by_user(
        self, user_id: UUID, page: int = 1, page_size: int = 20
    ) -> Tuple[List[Project], int]:
        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(Project).where(Project.user_id == user_id)
        )
        total = count_result.scalar() or 0

        # Get paginated results
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(Project.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def update(self, project_id: UUID, user_id: UUID, data: ProjectUpdate) -> Project:
        project = await self.get_by_id(project_id, user_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_status(self, project_id: UUID, status: ProjectStatus, **kwargs):
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if project:
            project.status = status
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            await self.db.commit()

    def _is_safe_path(self, path: str) -> bool:
        """Check if path is within the allowed storage directory."""
        if not path:
            return False
        try:
            real_path = os.path.realpath(path)
            storage_path = os.path.realpath(settings.storage_path)
            return real_path.startswith(storage_path + os.sep)
        except (ValueError, OSError):
            return False

    async def delete(self, project_id: UUID, user_id: UUID):
        project = await self.get_by_id(project_id, user_id)

        # Clean up associated files with path traversal protection
        file_paths = [
            project.original_path,
            project.stems_path,
            project.vocals_path,
            project.output_path,
        ]
        for path in file_paths:
            if path and self._is_safe_path(path):
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
                except OSError as e:
                    logger.warning(f"Failed to delete file: {e}")

        await self.db.delete(project)
        await self.db.commit()
