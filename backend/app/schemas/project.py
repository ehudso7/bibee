"""Project schemas."""
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, List, Generic, TypeVar
from app.models.project import ProjectStatus, VocalMode

T = TypeVar("T")


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    voice_persona_id: Optional[UUID] = None
    vocal_mode: VocalMode = VocalMode.REPLACE

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Project name cannot be empty")
        return v


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    voice_persona_id: Optional[UUID] = None
    vocal_mode: Optional[VocalMode] = None
    mix_settings: Optional[Dict[str, Any]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Project name cannot be empty")
        return v


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


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


class ProjectListResponse(PaginatedResponse[ProjectResponse]):
    """Paginated project list response."""

    pass
