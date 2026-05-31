from fastapi import APIRouter, Depends, status, BackgroundTasks, Request, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.repositories.lead_repo import LeadRepository
from app.repositories.audit_repo import AuditRepository
from app.services.lead_service import LeadService
from app.schemas.lead.requests import LeadCreateRequest
from app.schemas.lead.responses import LeadResponse
from app.integrations.captcha.turnstile import verify_turnstile_token
from app.api.dependencies import rate_limiter, require_manager, require_superadmin
from app.models.user import User

router = APIRouter()

def get_lead_service(db: AsyncSession = Depends(get_db)) -> LeadService:
    return LeadService(LeadRepository(db), AuditRepository(db))

@router.post(
    "/",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую заявку на обратный звонок (Открыто для всех)",
    dependencies=[Depends(rate_limiter)] 
)
async def create_lead(
    request: Request,
    schema: LeadCreateRequest,
    background_tasks: BackgroundTasks,
    lead_service: LeadService = Depends(get_lead_service)
):
    is_human = await verify_turnstile_token(schema.captcha_token, request.client.host)
    if not is_human:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Проверка безопасности (капча) не пройдена. Пожалуйста, попробуйте еще раз."
        )

    return await lead_service.create_lead(schema, background_tasks)


@router.get(
    "/",
    response_model=list[LeadResponse],
    summary="Получить список всех заявок (Только Админ/Менеджер)"
)
async def get_leads(
    lead_service: LeadService = Depends(get_lead_service),
    current_user: User = Depends(require_manager)
):
    return await lead_service.get_all_leads()


@router.put(
    "/{lead_id}",
    response_model=LeadResponse,
    summary="Изменить статус заявки (Только Админ/Менеджер)"
)
async def update_lead_status(
    lead_id: int,
    new_status: str,
    lead_service: LeadService = Depends(get_lead_service),
    current_user: User = Depends(require_manager)
):
    return await lead_service.update_lead_status(lead_id, new_status, current_user.id)


@router.delete(
    "/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить заявку (Только Суперадмин)"
)
async def delete_lead(
    lead_id: int,
    lead_service: LeadService = Depends(get_lead_service),
    current_user: User = Depends(require_superadmin)
):
    await lead_service.delete_lead(lead_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)