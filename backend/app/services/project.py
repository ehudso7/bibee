"""Project service."""
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate


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

    async def list_by_user(self, user_id: UUID) -> List[Project]:
        result = await self.db.execute(
            select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

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

    async def delete(self, project_id: UUID, user_id: UUID):
        project = await self.get_by_id(project_id, user_id)
        await self.db.delete(project)
        await self.db.commit()
