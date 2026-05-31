import uuid
from app.repositories.base import BaseRepository
from app.models.audit import AuditLog

class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, session):
        super().__init__(AuditLog, session)

    async def log_action(self, action: str, entity_type: str, entity_id: int, user_id: uuid.UUID = None) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id
        )
        return await self.add(log)