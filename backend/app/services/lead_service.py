from fastapi import HTTPException, status
from fastapi import BackgroundTasks
import uuid
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
        from app.models.lead import LeadStatus

        success = await self.lead_repo.atomic_update_status(
            lead_id=lead_id,
            old_status=LeadStatus.NEW,
            new_status=LeadStatus.IN_PROGRESS,
            processed_by=f"@{tg_username}"
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
    
    async def get_all_leads(self) -> list[Lead]:
        return await self.lead_repo.get_all_descending()

    async def update_lead_status(self, lead_id: int, new_status: str, admin_username: str, user_id: uuid.UUID) -> Lead:
        from app.models.lead import LeadStatus

        lead = await self.lead_repo.get_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        old_status = lead.status
        lead.status = new_status
        
        if new_status == LeadStatus.IN_PROGRESS:
            lead.processed_by = admin_username
        elif new_status == LeadStatus.NEW:
            lead.processed_by = None

        await self.lead_repo.session.commit()
        await self.lead_repo.session.refresh(lead)

        await self.audit_repo.log_action(
            action=f"CHANGE_STATUS_FROM_{old_status}_TO_{new_status}",
            entity_type="lead",
            entity_id=lead_id,
            user_id=user_id
        )
        return lead

    async def delete_lead(self, lead_id: int, user_id: uuid.UUID):
        lead = await self.lead_repo.get_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        await self.lead_repo.delete(lead)

        await self.audit_repo.log_action(
            action="DELETE_LEAD",
            entity_type="lead",
            entity_id=lead_id,
            user_id=user_id
        )