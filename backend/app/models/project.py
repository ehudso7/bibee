"""Project model."""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db import Base


class ProjectStatus(str, enum.Enum):
    CREATED = "created"
    UPLOADING = "uploading"
    PROCESSING_STEMS = "processing_stems"
    STEMS_READY = "stems_ready"
    GENERATING_VOCALS = "generating_vocals"
    VOCALS_READY = "vocals_ready"
    MIXING = "mixing"
    COMPLETED = "completed"
    FAILED = "failed"


class VocalMode(str, enum.Enum):
    REMOVE = "remove"
    REPLACE = "replace"
    BLEND = "blend"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    voice_persona_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("voice_personas.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.CREATED)
    vocal_mode: Mapped[VocalMode] = mapped_column(Enum(VocalMode), default=VocalMode.REPLACE)
    original_path: Mapped[str] = mapped_column(String(500), nullable=True)
    stems_path: Mapped[str] = mapped_column(String(500), nullable=True)
    vocals_path: Mapped[str] = mapped_column(String(500), nullable=True)
    output_path: Mapped[str] = mapped_column(String(500), nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    mix_settings: Mapped[dict] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="projects")
    voice_persona = relationship("VoicePersona")
