from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import create_jwt_token, hash_password, verify_password
from app.models.user import RoleEnum, User
from app.repositories.user_repo import UserRepository
from app.schemas.auth.requests import UserCreateRequest, UserUpdateRequest


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        redis: aioredis.Redis | None = None,
    ):
        self.user_repo = user_repo
        self.redis = redis

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

    def create_tokens(self, user_id: str | UUID, role: str) -> tuple[str, str]:
        access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = create_jwt_token(
            {"sub": str(user_id), "role": role, "type": "access", "jti": str(uuid4())},
            access_expires,
        )
        refresh_token = create_jwt_token(
            {"sub": str(user_id), "role": role, "type": "refresh", "jti": str(uuid4())},
            refresh_expires,
        )

        return access_token, refresh_token

    async def login(self, username: str, password: str) -> tuple[str, str, RoleEnum]:
        user = await self.authenticate_user(username, password)
        role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
        access_token, refresh_token = self.create_tokens(user.id, role_str)
        return access_token, refresh_token, user.role

    async def is_token_blacklisted(self, jti: str | None) -> bool:
        if not self.redis or not jti:
            return False
        return bool(await self.redis.exists(f"token_blacklist:{jti}"))

    async def blacklist_token(self, token_str: str | None) -> None:
        if not self.redis or not token_str:
            return
        try:
            payload = jwt.decode(
                token_str,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False},
            )
            jti = payload.get("jti")
            exp = payload.get("exp")
            if not jti or not exp:
                return

            now_ts = int(datetime.now(UTC).timestamp())
            ttl = int(exp) - now_ts
            if ttl > 0:
                await self.redis.setex(f"token_blacklist:{jti}", ttl, "revoked")
        except JWTError:
            pass

    async def revoke_user_tokens(self, user_id: UUID | str) -> None:
        if not self.redis:
            return
        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        now_ts = int(datetime.now(UTC).timestamp())
        await self.redis.setex(f"user_revoked:{user_id}", ttl, str(now_ts))

    async def is_user_token_revoked(
        self, user_id: UUID | str, token_iat: int | None
    ) -> bool:
        if not self.redis:
            return False
        revoked_ts = await self.redis.get(f"user_revoked:{user_id}")
        if revoked_ts is None:
            return False
        if token_iat is None:
            return True
        return token_iat < int(revoked_ts)

    async def logout(
        self, refresh_token: str | None = None, access_token: str | None = None
    ) -> None:
        if refresh_token:
            await self.blacklist_token(refresh_token)
        if access_token:
            await self.blacklist_token(access_token)
        elif refresh_token:
            try:
                payload = jwt.decode(
                    refresh_token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                    options={"verify_exp": False},
                )
                user_id = payload.get("sub")
                if user_id:
                    await self.revoke_user_tokens(user_id)
            except JWTError:
                pass

    async def refresh_tokens(
        self, refresh_token: str | None
    ) -> tuple[str, str, RoleEnum]:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Нет refresh-токена",
            )

        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh-токен недействителен или истёк",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный тип токена",
            )

        jti = payload.get("jti")
        if jti and await self.is_token_blacklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен отозван",
            )

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Некорректный идентификатор пользователя в токенe",
            )

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Некорректный формат идентификатора пользователя",
            )

        token_iat = payload.get("iat")
        if await self.is_user_token_revoked(user_id, token_iat):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Сессия пользователя была отозвана",
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден или неактивен",
            )

        await self.blacklist_token(refresh_token)

        role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
        new_access, new_refresh = self.create_tokens(user.id, role_str)
        return new_access, new_refresh, user.role

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

        is_security_change = (
            (schema.is_active is False)
            or (schema.role is not None and schema.role != user.role)
            or (
                hasattr(schema, "password")
                and schema.password is not None
                and schema.password.strip()
            )
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

        if is_security_change:
            await self.revoke_user_tokens(user.id)

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
        await self.revoke_user_tokens(user_id)

    async def get_all_users(self) -> list[User]:
        return await self.user_repo.get_all_users()
