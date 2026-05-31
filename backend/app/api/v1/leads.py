from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.repositories.lead_repo import LeadRepository
from app.services.lead_service import LeadService
from app.schemas.lead.requests import LeadCreateRequest
from app.schemas.lead.responses import LeadResponse

router = APIRouter()

def get_lead_service(db: AsyncSession = Depends(get_db)) -> LeadService:
    lead_repo = LeadRepository(db)
    return LeadService(lead_repo)

@router.post(
    "/",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую заявку на обратный звонок"
)
async def create_lead(
    schema: LeadCreateRequest,
    lead_service: LeadService = Depends(get_lead_service)
):
    return await lead_service.create_lead(schema)