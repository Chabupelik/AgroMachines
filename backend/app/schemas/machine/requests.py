from pydantic import BaseModel, Field
from typing import Optional

class MachineBase(BaseModel):
    title: str = Field(..., max_length=255, description="Название техники")
    description: str | None = Field(None, description="Описание техники")
    specifications: dict = Field(default_factory=dict, description="Характеристики техники в формате JSON")
    price: float | None = Field(None, ge=0, description="Цена техники")
    is_available: bool = True

class MachineCreateRequest(MachineBase):
    pass

class MachineUpdateRequest(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    specifications: dict | None = None
    price: float | None = Field(None, ge=0)
    is_available: bool = True
    existing_image_urls: Optional[list[str]] = None