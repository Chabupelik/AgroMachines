from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.lead import LeadStatus

class LeadResponse(BaseModel):
    id: int
    client_name: str
    client_phone: str
    status: LeadStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)