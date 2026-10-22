from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    user_id: UUID | None
    action: str
    entity_type: str
    entity_id: int
    timestamp: datetime
    username: str | None = None

    model_config = ConfigDict(from_attributes=True)
