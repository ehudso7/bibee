"""Voice persona endpoints."""
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.voice_persona import VoicePersonaCreate, VoicePersonaResponse
from app.services.voice_persona import VoicePersonaService
from app.utils.storage import save_upload

router = APIRouter()


@router.post("", response_model=VoicePersonaResponse)
async def create_voice_persona(
    data: VoicePersonaCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = VoicePersonaService(db)
    return await service.create(user.id, data)


@router.get("", response_model=List[VoicePersonaResponse])
async def list_voice_personas(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = VoicePersonaService(db)
    return await service.list_by_user(user.id)


@router.get("/{persona_id}", response_model=VoicePersonaResponse)
async def get_voice_persona(
    persona_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = VoicePersonaService(db)
    return await service.get_by_id(persona_id, user.id)


@router.post("/{persona_id}/samples")
async def upload_sample(
    persona_id: UUID,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = VoicePersonaService(db)
    path = await save_upload(file, f"samples/{user.id}/{persona_id}")
    await service.add_sample(persona_id, user.id, path)
    return {"message": "Sample uploaded", "path": path}


@router.delete("/{persona_id}")
async def delete_voice_persona(
    persona_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = VoicePersonaService(db)
    await service.delete(persona_id, user.id)
    return {"message": "Deleted"}
