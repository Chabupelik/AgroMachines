from fastapi import HTTPException, status
from datetime import timedelta
from app.core.config import settings
from app.core.security import verify_password, create_jwt_token
from app.repositories.user_repo import UserRepository
from app.models.user import User

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate_user(self, username: str, password: str) -> User:
        user = await self.user_repo.get_by_username(username)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
        
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
            
        return user

    def create_tokens(self, user_id: str, role: str):
        access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = create_jwt_token({"sub": str(user_id), "role": role, "type": "access"}, access_expires)
        refresh_token = create_jwt_token({"sub": str(user_id), "role": role, "type": "refresh"}, refresh_expires)

        return access_token, refresh_token