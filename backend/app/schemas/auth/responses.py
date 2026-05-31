from pydantic import BaseModel
from app.models.user import RoleEnum

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum