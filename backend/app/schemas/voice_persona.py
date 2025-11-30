"""Voice persona schemas."""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.models.voice_persona import PersonaStatus


class VoicePersonaCreate(BaseModel):
    name: str
    description: Optional[str] = None


class VoicePersonaResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: PersonaStatus
    sample_paths: List[str]
    created_at: datetime

    class Config:
        from_attributes = True
