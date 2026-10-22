from datetime import timedelta
from uuid import UUID

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import create_jwt_token, hash_password, verify_password
from app.models.user import RoleEnum, User
from app.repositories.user_repo import UserRepository
from app.schemas.auth.requests import UserCreateRequest, UserUpdateRequest


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate_user(self, username: str, password: str) -> User:
        user = await self.user_repo.get_by_username(username)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
            )

        return user

    def create_tokens(self, user_id: str, role: str):
        access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = create_jwt_token(
            {"sub": str(user_id), "role": role, "type": "access"}, access_expires
        )
        refresh_token = create_jwt_token(
            {"sub": str(user_id), "role": role, "type": "refresh"}, refresh_expires
        )

        return access_token, refresh_token

    async def create_user(self, schema: UserCreateRequest) -> User:
        if schema.role == RoleEnum.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Назначение роли суперадминистратора через интерфейс запрещено.",
            )

        existing_user = await self.user_repo.get_by_username(schema.username)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Пользователь с таким именем уже существует"
            )

        tg_username = (
            schema.telegram_username.strip() if schema.telegram_username else None
        )
        if not tg_username:
            tg_username = None

        new_user = User(
            username=schema.username,
            password_hash=hash_password(schema.password),
            role=schema.role,
            telegram_username=tg_username,
        )
        user = await self.user_repo.add(new_user)
        await self.user_repo.session.commit()
        return user

    async def update_user(
        self, user_id: UUID, schema: UserUpdateRequest, current_user_id: UUID
    ) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if user.role == RoleEnum.SUPERADMIN and user.id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете редактировать профиль другого суперадминистратора.",
            )

        if schema.role is not None and schema.role == RoleEnum.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Назначение роли суперадминистратора через интерфейс запрещено.",
            )

        if (
            user.id == current_user_id
            and schema.role is not None
            and schema.role != RoleEnum.SUPERADMIN
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы не можете забрать роль суперадминистратора у самого себя.",
            )

        if schema.is_active is not None:
            user.is_active = schema.is_active
        if schema.role is not None:
            user.role = schema.role

        if schema.telegram_username is not None:
            tg_username = schema.telegram_username.strip()
            user.telegram_username = tg_username if tg_username else None

        if (
            hasattr(schema, "password")
            and schema.password is not None
            and schema.password.strip()
        ):
            user.password_hash = hash_password(schema.password)

        await self.user_repo.session.commit()
        await self.user_repo.session.refresh(user)
        return user

    async def delete_user(self, user_id: UUID, current_admin_id: UUID):
        if user_id == current_admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы не можете удалить свою собственную учетную запись суперадминистратора",
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if user.role == RoleEnum.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете удалить другого суперадминистратора.",
            )

        await self.user_repo.delete(user)
        await self.user_repo.session.commit()

    async def get_all_users(self) -> list[User]:
        return await self.user_repo.get_all_users()
