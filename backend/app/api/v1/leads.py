from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Request,
    Response,
    status,
)

from app.api.dependencies import (
    get_client_ip,
    rate_limiter,
    require_manager,
    require_superadmin,
)
from app.db.database import DbSession
from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.lead_repo import LeadRepository
from app.schemas.common import PaginatedResponse, ResponseError, ResponseOK
from app.schemas.lead.requests import LeadCreateRequest
from app.schemas.lead.responses import LeadResponse
from app.services.lead_service import LeadService

router = APIRouter()


def get_lead_service(db: DbSession) -> LeadService:
    return LeadService(LeadRepository(db), AuditRepository(db))


LeadSrv = Annotated[LeadService, Depends(get_lead_service)]
CurrentManager = Annotated[User, Depends(require_manager)]
CurrentSuperAdmin = Annotated[User, Depends(require_superadmin)]


@router.post(
    "/",
    response_model=ResponseOK[LeadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Создать заявку — публичный эндпоинт",
    responses={
        400: {"model": ResponseError, "description": "Ошибка верификации"},
        409: {"model": ResponseError, "description": "Дубликат активной заявки"},
        429: {
            "model": ResponseError,
            "description": "Превышен лимит запросов (Rate Limit)",
        },
    },
    dependencies=[Depends(rate_limiter)],
)
async def create_lead(
    request: Request,
    schema: LeadCreateRequest,
    background_tasks: BackgroundTasks,
    lead_service: LeadSrv,
):
    client_ip = get_client_ip(request)
    lead = await lead_service.create_lead(schema, background_tasks, client_ip=client_ip)
    return {"data": lead}


@router.get(
    "/",
    response_model=PaginatedResponse[LeadResponse],
    summary="Список заявок (только менеджер/админ)",
)
async def get_leads(
    lead_service: LeadSrv,
    current_user: CurrentManager,
    limit: int = 10,
    offset: int = 0,
):
    leads, total = await lead_service.get_all_leads(limit, offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, data=leads)


@router.put(
    "/{lead_id}",
    response_model=ResponseOK[LeadResponse],
    summary="Изменить статус заявки (только менеджер/админ)",
)
async def update_lead_status(
    lead_id: int,
    new_status: str,
    background_tasks: BackgroundTasks,
    lead_service: LeadSrv,
    current_user: CurrentManager,
):
    lead = await lead_service.update_lead_status(
        lead_id,
        new_status,
        current_user.username,
        current_user.id,
        background_tasks,
    )
    return ResponseOK(data=lead)


@router.delete(
    "/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить заявку (только суперадмин)",
)
async def delete_lead(
    lead_id: int,
    lead_service: LeadSrv,
    current_user: CurrentSuperAdmin,
):
    await lead_service.delete_lead(lead_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
