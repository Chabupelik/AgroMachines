from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class AuditLogResponse(BaseModel):
    id: int
    user_id: UUID | None
    action: str
    entity_type: str
    entity_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)