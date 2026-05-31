from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.lead import Lead, LeadStatus

class LeadRepository(BaseRepository[Lead]):
    def __init__(self, session: AsyncSession):
        super().__init__(Lead, session)

    async def get_active_by_phone(self, phone: str) -> Optional[Lead]:
        query = select(self.model).where(
            self.model.client_phone == phone,
            self.model.status.in_([LeadStatus.NEW, LeadStatus.IN_PROGRESS])
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()