from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.user import RoleEnum


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum


class UserResponse(BaseModel):
    id: UUID
    username: str
    role: RoleEnum
    is_active: bool
    telegram_username: str | None = None

    model_config = ConfigDict(from_attributes=True)
