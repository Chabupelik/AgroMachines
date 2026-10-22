import logging
import uuid

import redis.asyncio as aioredis
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select

from app.models.lead import Lead, LeadStatus
from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.lead_repo import LeadRepository
from app.schemas.lead.requests import LeadCreateRequest
from app.workers.telegram_tasks import task_notify_new_lead

logger = logging.getLogger(__name__)


class LeadService:
    def __init__(
        self,
        lead_repo: LeadRepository,
        audit_repo: AuditRepository,
        redis: aioredis.Redis | None = None,
    ) -> None:
        self.lead_repo = lead_repo
        self.audit_repo = audit_repo
        self.redis = redis

    async def create_lead(
        self, schema: LeadCreateRequest, bg_tasks: BackgroundTasks
    ) -> Lead:
        existing_active_lead = await self.lead_repo.get_active_by_phone(
            schema.client_phone
        )
        if existing_active_lead:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Заявка с этим телефоном уже активна или в обработке. Ожидайте звонка.",
            )

        new_lead = Lead(
            client_name=schema.client_name, client_phone=schema.client_phone
        )
        saved_lead = await self.lead_repo.add(new_lead)

        await self.audit_repo.log_action(
            action="CREATE_LEAD",
            entity_type="lead",
            entity_id=saved_lead.id,
            user_id=None,
        )

        await self.lead_repo.session.commit()

        bg_tasks.add_task(
            task_notify_new_lead,
            lead_id=saved_lead.id,
            name=saved_lead.client_name,
            phone=saved_lead.client_phone,
        )

        return saved_lead

    async def take_lead_from_tg(
        self,
        lead_id: int,
        tg_username: str,
    ) -> str:
        if not tg_username:
            return "TG_NOT_LINKED"

        lock_key = f"lock:lead:take:{lead_id}"

        if not self.redis:
            raise RuntimeError("Redis is required for LeadService")
        acquired = await self.redis.set(lock_key, "locked", ex=10, nx=True)

        if not acquired:
            return "ALREADY_TAKEN"

        try:
            stmt = select(User).where(User.telegram_username == tg_username)
            res = await self.lead_repo.session.execute(stmt)
            user = res.scalar_one_or_none()

            if not user:
                return "TG_NOT_LINKED"

            success = await self.lead_repo.atomic_update_status(
                lead_id=lead_id,
                old_status=LeadStatus.NEW,
                new_status=LeadStatus.IN_PROGRESS,
                processed_by=user.username,
            )

            if success:
                await self.audit_repo.log_action(
                    action=f"TAKE_LEAD_BY_TG_@{tg_username}",
                    entity_type="lead",
                    entity_id=lead_id,
                    user_id=user.id,
                )
                await self.lead_repo.session.commit()
                return "SUCCESS"

            lead = await self.lead_repo.get_by_id(lead_id)
            if not lead:
                return "NOT_FOUND"

            return "ALREADY_TAKEN"

        finally:
            if self.redis:
                await self.redis.delete(lock_key)

    async def get_all_leads(self, limit: int, offset: int):
        leads = await self.lead_repo.get_all_descending(limit, offset)
        total = await self.lead_repo.count()
        return leads, total

    async def update_lead_status(
        self,
        lead_id: int,
        new_status: str,
        admin_username: str,
        user_id: uuid.UUID,
    ) -> Lead:
        lead = await self.lead_repo.get_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        old_status = lead.status

        if new_status == LeadStatus.IN_PROGRESS and old_status != LeadStatus.NEW:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Заявка уже обрабатывается другим менеджером.",
            )

        if new_status == LeadStatus.DONE and old_status != LeadStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Заявку нельзя закрыть, так как она не находится в работе.",
            )

        lead.status = new_status

        if new_status == LeadStatus.IN_PROGRESS:
            lead.processed_by = admin_username
        elif new_status == LeadStatus.NEW:
            lead.processed_by = None

        await self.audit_repo.log_action(
            action=f"CHANGE_STATUS_FROM_{old_status}_TO_{new_status}",
            entity_type="lead",
            entity_id=lead_id,
            user_id=user_id,
        )

        await self.lead_repo.session.commit()
        await self.lead_repo.session.refresh(lead)

        if lead.tg_message_id:
            from app.integrations.telegram.client import edit_telegram_message
            from app.integrations.telegram.formatters import escape_markdown_v2

            safe_name = escape_markdown_v2(lead.client_name)
            safe_phone = escape_markdown_v2(lead.client_phone)
            safe_username = escape_markdown_v2(admin_username)

            new_text = ""
            if new_status == LeadStatus.IN_PROGRESS:
                new_text = (
                    f"?? *Заявка взята в работу\\!*\n\n"
                    f"?? *Имя:* {safe_name}\n"
                    f"?? *Телефон:* `{safe_phone}`\n\n"
                    f"?? *Заявка взята в работу через сайт менеджером @{safe_username}*"
                )
            elif new_status == LeadStatus.DONE:
                new_text = (
                    f"? *Заявка закрыта\\!*\n\n"
                    f"?? *Имя:* {safe_name}\n"
                    f"?? *Телефон:* `{safe_phone}`\n\n"
                    f"?? _Обработка успешно завершена менеджером @{safe_username}_"
                )

            if new_text:
                try:
                    await edit_telegram_message(
                        message_id=lead.tg_message_id, text=new_text, reply_markup=None
                    )
                except Exception as e:
                    logger.warning(
                        "Не удалось обновить статус заявки %s в Telegram: %s",
                        lead.id,
                        e,
                    )

        return lead

    async def delete_lead(self, lead_id: int, user_id: uuid.UUID) -> None:
        lead = await self.lead_repo.get_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        await self.lead_repo.delete(lead)

        await self.audit_repo.log_action(
            action="DELETE_LEAD",
            entity_type="lead",
            entity_id=lead_id,
            user_id=user_id,
        )
        await self.lead_repo.session.commit()
