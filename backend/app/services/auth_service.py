from fastapi import HTTPException, status
from datetime import timedelta
from uuid import UUID
from app.core.config import settings
from app.core.security import verify_password, create_jwt_token
from app.repositories.user_repo import UserRepository
from app.models.user import User
from app.schemas.auth.requests import UserCreateRequest, UserUpdateRequest
from app.core.security import hash_password

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
    
    async def create_user(self, schema: UserCreateRequest) -> User:
        existing_user = await self.user_repo.get_by_username(schema.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
        
        new_user = User(
            username=schema.username,
            password_hash=hash_password(schema.password),
            role=schema.role
        )
        return await self.user_repo.add(new_user)
    
    async def update_user(self, user_id: UUID, schema: UserUpdateRequest) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if schema.role is not None:
            user.role = schema.role
        if schema.is_active is not None:
            user.is_active = schema.is_active

        await self.user_repo.session.commit()
        await self.user_repo.session.refresh(user)
        return user

    async def delete_user(self, user_id: UUID, current_admin_id: UUID):
        if user_id == current_admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Вы не можете удалить свою собственную учетную запись суперадминистратора"
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        await self.user_repo.delete(user)
        
    async def get_all_users(self) -> list[User]:
        return await self.user_repo.get_all_users()