from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.lead import LeadStatus


class LeadResponse(BaseModel):
    id: int
    client_name: str
    client_phone: str
    status: LeadStatus
    created_at: datetime
    tg_message_id: int | None
    processed_by: str | None

    model_config = ConfigDict(from_attributes=True)
