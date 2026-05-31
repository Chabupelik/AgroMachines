from typing import Optional
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
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
    
    async def atomic_update_status(self, lead_id: int, old_status: LeadStatus, new_status: LeadStatus) -> bool:

        query = (
            update(self.model)
            .where(self.model.id == lead_id, self.model.status == old_status)
            .values(status=new_status, updated_at=datetime.now(timezone.utc))
        )
        result = await self.session.execute(query)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def get_all_descending(self) -> list[Lead]:
        query = select(self.model).order_by(self.model.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()