from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException

from app.core.config import settings
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


@router.post("/webhook")
async def telegram_webhook(
    update: dict,
    lead_srv: LeadSrv,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
):
    if x_telegram_bot_api_secret_token != settings.TG_WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Fake Telegram request")

    await lead_srv.handle_telegram_update(update)
    return {"ok": True}
