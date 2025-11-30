"""Voice persona service."""
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.voice_persona import VoicePersona, PersonaStatus
from app.schemas.voice_persona import VoicePersonaCreate


class VoicePersonaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, data: VoicePersonaCreate) -> VoicePersona:
        persona = VoicePersona(user_id=user_id, name=data.name, description=data.description)
        self.db.add(persona)
        await self.db.commit()
        await self.db.refresh(persona)
        return persona

    async def get_by_id(self, persona_id: UUID, user_id: UUID) -> VoicePersona:
        result = await self.db.execute(
            select(VoicePersona).where(VoicePersona.id == persona_id, VoicePersona.user_id == user_id)
        )
        persona = result.scalar_one_or_none()
        if not persona:
            raise HTTPException(status_code=404, detail="Voice persona not found")
        return persona

    async def list_by_user(self, user_id: UUID) -> List[VoicePersona]:
        result = await self.db.execute(select(VoicePersona).where(VoicePersona.user_id == user_id))
        return list(result.scalars().all())

    async def add_sample(self, persona_id: UUID, user_id: UUID, sample_path: str):
        persona = await self.get_by_id(persona_id, user_id)
        persona.sample_paths = persona.sample_paths + [sample_path]
        await self.db.commit()

    async def update_status(self, persona_id: UUID, status: PersonaStatus, model_path: str = None):
        result = await self.db.execute(select(VoicePersona).where(VoicePersona.id == persona_id))
        persona = result.scalar_one_or_none()
        if persona:
            persona.status = status
            if model_path:
                persona.model_path = model_path
            await self.db.commit()

    async def delete(self, persona_id: UUID, user_id: UUID):
        persona = await self.get_by_id(persona_id, user_id)
        await self.db.delete(persona)
        await self.db.commit()
