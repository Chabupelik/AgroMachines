from fastapi import APIRouter, Depends, status
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.repositories.lead_repo import LeadRepository
from app.repositories.audit_repo import AuditRepository
from app.services.lead_service import LeadService
from app.schemas.lead.requests import LeadCreateRequest
from app.schemas.lead.responses import LeadResponse

router = APIRouter()

def get_lead_service(db: AsyncSession = Depends(get_db)) -> LeadService:
    lead_repo = LeadRepository(db)
    audit_repo = AuditRepository(db)
    return LeadService(lead_repo, audit_repo)

@router.post(
    "/",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую заявку на обратный звонок"
)
async def create_lead(
    schema: LeadCreateRequest,
    background_tasks: BackgroundTasks,
    lead_service: LeadService = Depends(get_lead_service)
):
    return await lead_service.create_lead(schema, background_tasks)