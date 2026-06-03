# src/app/repositories/audit_repo.py

import uuid
from typing import Optional
from sqlalchemy import select, func
from app.repositories.base import BaseRepository
from app.models.audit import AuditLog
from app.models.user import User

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
    async def get_filtered_logs(
        self, 
        limit: int = 20, 
        offset: int = 0, 
        user_id: Optional[uuid.UUID] = None, 
        action: Optional[str] = None, 
        entity_type: Optional[str] = None
    ) -> list[tuple[AuditLog, Optional[str]]]: 
        
        query = (
            select(self.model, User.username)
            .outerjoin(User, self.model.user_id == User.id)
            .order_by(self.model.timestamp.desc())
        )

        if user_id:
            query = query.where(self.model.user_id == user_id)
        if action:
            query = query.where(self.model.action == action)
        if entity_type:
            query = query.where(self.model.entity_type == entity_type)

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.all() 

    async def count_filtered_logs(
        self, 
        user_id: Optional[uuid.UUID] = None, 
        action: Optional[str] = None, 
        entity_type: Optional[str] = None
    ) -> int:
        query = select(func.count()).select_from(self.model)

        if user_id:
            query = query.where(self.model.user_id == user_id)
        if action:
            query = query.where(self.model.action == action)
        if entity_type:
            query = query.where(self.model.entity_type == entity_type)

        result = await self.session.execute(query)
        return result.scalar_one()