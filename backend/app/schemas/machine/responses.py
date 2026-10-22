from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.machine.requests import SpecificationValue


class MachineResponse(BaseModel):
    id: int
    title: str
    description: str | None
    specifications: dict[str, SpecificationValue] = Field(default_factory=dict)
    price: float | None
    image_urls: list[str]
    created_at: datetime
    is_available: bool = True

    model_config = ConfigDict(from_attributes=True)
