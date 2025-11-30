"""User service."""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def update_usage(self, user_id: UUID, seconds: int):
        user = await self.get_by_id(user_id)
        if user:
            user.usage_seconds += seconds
            await self.db.commit()
