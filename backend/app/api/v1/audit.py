from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import require_audit_viewer
from app.db.database import DbSession
from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.schemas.audit import AuditLogResponse
from app.schemas.common import PaginatedResponse
from app.services.audit_service import AuditService

router = APIRouter()


def get_audit_service(db: DbSession) -> AuditService:
    return AuditService(AuditRepository(db))


@router.get(
    "/",
    response_model=PaginatedResponse[AuditLogResponse],
    summary="Журнал аудит-действий (только суперадмин)",
)
async def get_audit_logs(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    user_id: Annotated[
        UUID | None, Query(description="Фильтр по ID пользователя")
    ] = None,
    action: Annotated[
        str | None, Query(description="Фильтр по типу действия (например CREATE_LEAD)")
    ] = None,
    entity_type: Annotated[
        str | None, Query(description="Фильтр по типу объекта (например lead)")
    ] = None,
    audit_service: Annotated[AuditService, Depends(get_audit_service)] = None,
    _: Annotated[User, Depends(require_audit_viewer)] = None,
):
    logs, total = await audit_service.get_logs(
        limit, offset, user_id, action, entity_type
    )
    return PaginatedResponse(total=total, limit=limit, offset=offset, data=logs)
