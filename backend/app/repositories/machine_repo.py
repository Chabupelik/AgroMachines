from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.machine import Machine

class MachineRepository(BaseRepository[Machine]):
    def __init__(self, session):
        super().__init__(Machine, session)

    async def get_all_descending(self) -> list[Machine]:
        query = select(self.model).order_by(self.model.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()