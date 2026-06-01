from typing import Optional
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(self.model).where(self.model.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_users(self) -> list[User]:
        query = select(self.model).order_by(self.model.username)
        result = await self.session.execute(query)
        return result.scalars().all()