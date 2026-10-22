from sqlalchemy import select

from app.models.machine import Machine
from app.repositories.base import BaseRepository


class MachineRepository(BaseRepository[Machine]):
    def __init__(self, session):
        super().__init__(Machine, session)

    async def get_all_descending(
        self, limit: int = 10, offset: int = 0
    ) -> list[Machine]:
        query = (
            select(self.model)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
