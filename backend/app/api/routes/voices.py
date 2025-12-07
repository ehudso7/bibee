"""Voice persona endpoints."""
import math
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.voice_persona import VoicePersonaCreate, VoicePersonaResponse, VoicePersonaListResponse
from app.services.voice_persona import VoicePersonaService
from app.utils.storage import save_upload, validate_audio_file

router = APIRouter()


@router.post("", response_model=VoicePersonaResponse)
async def create_voice_persona(
    data: VoicePersonaCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new voice persona."""
    service = VoicePersonaService(db)
    return await service.create(user.id, data)


@router.get("", response_model=VoicePersonaListResponse)
async def list_voice_personas(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all voice personas for the current user with pagination."""
    service = VoicePersonaService(db)
    personas, total = await service.list_by_user(user.id, page, page_size)
    pages = math.ceil(total / page_size) if total > 0 else 0
    return VoicePersonaListResponse(
        items=personas,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{persona_id}", response_model=VoicePersonaResponse)
async def get_voice_persona(
    persona_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific voice persona by ID."""
    service = VoicePersonaService(db)
    return await service.get_by_id(persona_id, user.id)


@router.post("/{persona_id}/samples")
async def upload_sample(
    persona_id: UUID,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a voice sample for a persona."""
    # Validate audio file
    validate_audio_file(file)

    service = VoicePersonaService(db)
    # Verify user owns this persona before saving file
    await service.get_by_id(persona_id, user.id)

    path = await save_upload(file, f"samples/{user.id}/{persona_id}")
    await service.add_sample(persona_id, user.id, path)
    return {"message": "Sample uploaded successfully", "path": path}


@router.delete("/{persona_id}")
async def delete_voice_persona(
    persona_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a voice persona."""
    service = VoicePersonaService(db)
    await service.delete(persona_id, user.id)
    return {"message": "Voice persona deleted successfully"}
