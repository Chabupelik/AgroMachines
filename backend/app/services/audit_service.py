import uuid

from app.repositories.audit_repo import AuditRepository


class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo

    async def log(
        self, action: str, entity_type: str, entity_id: int, user_id: uuid.UUID = None
    ):
        await self.audit_repo.log_action(action, entity_type, entity_id, user_id)

    async def get_logs(
        self,
        limit: int,
        offset: int,
        user_id: uuid.UUID | None = None,
        action: str | None = None,
        entity_type: str | None = None,
    ):
        logs_with_users = await self.audit_repo.get_filtered_logs(
            limit, offset, user_id, action, entity_type
        )
        total = await self.audit_repo.count_filtered_logs(user_id, action, entity_type)

        final_logs = []
        for log, username in logs_with_users:
            log.username = username
            final_logs.append(log)

        return final_logs, total
