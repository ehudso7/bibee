"""Task schemas."""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.task import TaskStatus, TaskType


class TaskResponse(BaseModel):
    id: UUID
    task_type: TaskType
    status: TaskStatus
    progress: int
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
