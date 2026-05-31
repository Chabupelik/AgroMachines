from fastapi import HTTPException, status
from app.repositories.lead_repo import LeadRepository
from app.repositories.audit_repo import AuditRepository
from app.models.lead import Lead
from app.schemas.lead.requests import LeadCreateRequest

class LeadService:
    def __init__(self, lead_repo: LeadRepository, audit_repo: AuditRepository):
        self.lead_repo = lead_repo
        self.audit_repo = audit_repo

    async def create_lead(self, schema: LeadCreateRequest) -> Lead:
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

        return saved_lead