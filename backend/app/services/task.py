"""Task service."""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.task import Task, TaskStatus, TaskType


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, task_type: TaskType, project_id: UUID = None, voice_persona_id: UUID = None) -> Task:
        task = Task(task_type=task_type, project_id=project_id, voice_persona_id=voice_persona_id)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update_status(self, task_id: UUID, status: TaskStatus, progress: int = None, error: str = None):
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if task:
            task.status = status
            if progress is not None:
                task.progress = progress
            if error:
                task.error_message = error
            await self.db.commit()

    async def get_by_project(self, project_id: UUID) -> list[Task]:
        result = await self.db.execute(select(Task).where(Task.project_id == project_id))
        return list(result.scalars().all())
