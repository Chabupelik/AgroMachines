from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.db.database import get_db
from app.repositories.audit_repo import AuditRepository
from app.services.audit_service import AuditService
from app.schemas.audit import AuditLogResponse
from app.schemas.common import PaginatedResponse
from app.api.dependencies import require_superadmin, require_audit_viewer
from app.models.user import User

router = APIRouter()

def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    return AuditService(AuditRepository(db))

@router.get(
    "/", 
    response_model=PaginatedResponse[AuditLogResponse], 
    summary="Получить журнал аудита действий (Доступно только Суперадмину)"
)
async def get_audit_logs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: Optional[UUID] = Query(None, description="Фильтр по конкретному администратору"),
    action: Optional[str] = Query(None, description="Фильтр по типу действия (например CREATE_LEAD)"),
    entity_type: Optional[str] = Query(None, description="Фильтр по типу измененного объекта (например lead)"),
    audit_service: AuditService = Depends(get_audit_service),
):
    logs, total = await audit_service.get_logs(limit, offset, user_id, action, entity_type)
    return PaginatedResponse(total=total, limit=limit, offset=offset, data=logs)