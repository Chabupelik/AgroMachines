from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import verify_telegram_secret
from app.db.database import DbSession
from app.db.redis import RedisClient
from app.repositories.audit_repo import AuditRepository
from app.repositories.lead_repo import LeadRepository
from app.services.lead_service import LeadService

router = APIRouter()


def get_lead_service(
    db: DbSession,
    redis: RedisClient,
) -> LeadService:
    return LeadService(
        lead_repo=LeadRepository(db),
        audit_repo=AuditRepository(db),
        redis=redis,
    )


LeadSrv = Annotated[LeadService, Depends(get_lead_service)]


@router.post("/webhook", dependencies=[Depends(verify_telegram_secret)])
async def telegram_webhook(
    update: dict,
    lead_srv: LeadSrv,
):
    await lead_srv.handle_telegram_update(update)
    return {"ok": True}
