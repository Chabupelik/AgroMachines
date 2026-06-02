from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MachineResponse(BaseModel):
    id: int
    title: str
    description: str | None
    specifications: dict
    price: float | None
    image_urls: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)