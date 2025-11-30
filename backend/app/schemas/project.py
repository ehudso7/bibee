"""Project schemas."""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.project import ProjectStatus, VocalMode


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    voice_persona_id: Optional[UUID] = None
    vocal_mode: VocalMode = VocalMode.REPLACE


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    voice_persona_id: Optional[UUID] = None
    vocal_mode: Optional[VocalMode] = None
    mix_settings: Optional[Dict[str, Any]] = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: ProjectStatus
    vocal_mode: VocalMode
    duration_seconds: Optional[float]
    mix_settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
