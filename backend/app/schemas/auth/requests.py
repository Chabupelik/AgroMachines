from pydantic import BaseModel
from typing import Optional
from app.models.user import RoleEnum
    
class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: RoleEnum
    telegram_username: Optional[str] = None
    
class UserUpdateRequest(BaseModel):
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None
    telegram_username: Optional[str] = None