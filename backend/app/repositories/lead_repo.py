from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead, LeadStatus
from app.repositories.base import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, session: AsyncSession):
        super().__init__(Lead, session)

    async def get_active_by_phone(self, phone: str) -> Lead | None:
        query = select(self.model).where(
            self.model.client_phone == phone,
            self.model.status.in_([LeadStatus.NEW, LeadStatus.IN_PROGRESS]),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def atomic_update_status(
        self,
        lead_id: int,
        old_status: LeadStatus,
        new_status: LeadStatus,
        processed_by: str | None = None,
    ) -> bool:
        query = (
            update(self.model)
            .where(self.model.id == lead_id, self.model.status == old_status)
            .values(
                status=new_status,
                processed_by=processed_by,
                updated_at=datetime.now(UTC),
            )
        )
        result = await self.session.execute(query)
        return result.rowcount > 0

    async def get_all_descending(self, limit: int = 10, offset: int = 0) -> list[Lead]:
        query = (
            select(self.model)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
