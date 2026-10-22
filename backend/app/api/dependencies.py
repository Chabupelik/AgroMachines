import json
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError as JWTError

from app.core.config import settings
from app.db.database import DbSession
from app.db.redis import RedisClient
from app.models.user import RoleEnum, User
from app.repositories.user_repo import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_client_ip(request: Request) -> str:
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()

    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
    redis: RedisClient,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учётные данные (токен истёк или неверен)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_str: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        jti: str | None = payload.get("jti")
        token_iat: int | None = payload.get("iat")

        if not user_id_str or token_type != "access":
            raise credentials_exception

        user_id = UUID(user_id_str)

    except (JWTError, ValueError):
        raise credentials_exception

    async with redis.pipeline(transaction=True) as pipe:
        if jti:
            pipe.exists(f"token_blacklist:{jti}")
        pipe.get(f"user_revoked:{user_id}")
        pipe.get(f"user_cache:{user_id}")
        pipe_results = await pipe.execute()

    idx = 0
    if jti:
        if pipe_results[idx]:
            raise credentials_exception
        idx += 1

    revoked_ts = pipe_results[idx]
    idx += 1
    if revoked_ts is not None and (token_iat is None or token_iat < int(revoked_ts)):
        raise credentials_exception

    cached_user_json = pipe_results[idx]
    if cached_user_json:
        try:
            cached_data = json.loads(cached_user_json)
            user = User(
                id=UUID(cached_data["id"]),
                username=cached_data["username"],
                password_hash=cached_data["password_hash"],
                role=RoleEnum(cached_data["role"]),
                telegram_username=cached_data.get("telegram_username"),
                is_active=cached_data["is_active"],
            )
            if not user.is_active:
                raise credentials_exception
            return user
        except HTTPException:
            raise
        except Exception:
            pass

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if user is None or not user.is_active:
        raise credentials_exception

    user_data = {
        "id": str(user.id),
        "username": user.username,
        "password_hash": user.password_hash,
        "role": user.role.value,
        "telegram_username": user.telegram_username,
        "is_active": user.is_active,
    }
    await redis.setex(f"user_cache:{user.id}", 120, json.dumps(user_data))

    return user


async def rate_limiter(
    request: Request,
    redis: RedisClient,
) -> None:
    ip = get_client_ip(request)
    path = request.url.path
    key = f"rate_limit:{ip}:{path}"

    async with redis.pipeline(transaction=True) as pipe:
        pipe.incr(key)
        pipe.expire(key, 60, nx=True)
        res = await pipe.execute()

    current_requests = res[0]

    if current_requests > 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком много запросов. Подождите, попробуйте позже.",
        )


class RoleChecker:
    def __init__(self, allowed_roles: list[RoleEnum]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Доступ запрещён. Требуется одна из ролей: {[r.value for r in self.allowed_roles]}",
            )
        return user


require_superadmin = RoleChecker([RoleEnum.SUPERADMIN])
require_audit_viewer = RoleChecker([RoleEnum.SUPERADMIN, RoleEnum.ADMIN])
require_editor = RoleChecker([RoleEnum.SUPERADMIN, RoleEnum.ADMIN, RoleEnum.EDITOR])
require_manager = RoleChecker([RoleEnum.SUPERADMIN, RoleEnum.ADMIN, RoleEnum.MANAGER])


def verify_telegram_secret(
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
) -> None:
    if x_telegram_bot_api_secret_token != settings.TG_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Fake Telegram request",
        )
