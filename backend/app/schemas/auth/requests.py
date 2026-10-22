from pydantic import BaseModel

from app.models.user import RoleEnum


class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: RoleEnum
    telegram_username: str | None = None


class UserUpdateRequest(BaseModel):
    role: RoleEnum | None = None
    is_active: bool | None = None
    telegram_username: str | None = None
    password: str | None = None
