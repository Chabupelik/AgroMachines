from fastapi import HTTPException, status
from fastapi import BackgroundTasks
from app.workers.telegram_tasks import task_notify_new_lead
from app.repositories.lead_repo import LeadRepository
from app.repositories.audit_repo import AuditRepository
from app.models.lead import Lead, LeadStatus
from app.schemas.lead.requests import LeadCreateRequest

class LeadService:
    def __init__(self, lead_repo: LeadRepository, audit_repo: AuditRepository):
        self.lead_repo = lead_repo
        self.audit_repo = audit_repo

    async def create_lead(self, schema: LeadCreateRequest, bg_tasks: BackgroundTasks) -> Lead:
        existing_active_lead = await self.lead_repo.get_active_by_phone(schema.client_phone)
        if existing_active_lead:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="У вас уже есть активная заявка в обработке. Мы свяжемся с вами в ближайшее время."
            )

        new_lead = Lead(
            client_name=schema.client_name,
            client_phone=schema.client_phone
        )
        saved_lead = await self.lead_repo.add(new_lead)

        await self.audit_repo.log_action(
            action="CREATE_LEAD",
            entity_type="lead",
            entity_id=saved_lead.id,
            user_id=None 
        )

        bg_tasks.add_task(
            task_notify_new_lead,
            lead_id=saved_lead.id,
            name=saved_lead.client_name,
            phone=saved_lead.client_phone
        )

        return saved_lead
    async def take_lead_from_tg(self, lead_id: int, tg_username: str) -> str:

        success = await self.lead_repo.atomic_update_status(
            lead_id=lead_id,
            old_status=LeadStatus.NEW,
            new_status=LeadStatus.IN_PROGRESS
        )
        
        if success:
            await self.audit_repo.log_action(
                action=f"TAKE_LEAD_BY_TG_@{tg_username}",
                entity_type="lead",
                entity_id=lead_id,
                user_id=None
            )
            return "SUCCESS"
            
        lead = await self.lead_repo.get_by_id(lead_id)
        if not lead:
            return "NOT_FOUND"
            
        return "ALREADY_TAKEN"