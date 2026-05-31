import uuid
from app.repositories.audit_repo import AuditRepository

class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo

    async def log(self, action: str, entity_type: str, entity_id: int, user_id: uuid.UUID = None):
        await self.audit_repo.log_action(action, entity_type, entity_id, user_id)