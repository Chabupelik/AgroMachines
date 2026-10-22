from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.db.database import DbSession
from app.db.redis import RedisClient
from app.models.user import RoleEnum, User
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service(db: DbSession, redis: RedisClient) -> AuthService:
    return AuthService(UserRepository(db), redis=redis)


AuthSrv = Annotated[AuthService, Depends(get_auth_service)]


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
    auth_service: AuthSrv,
) -> User:
    return await auth_service.get_user_from_token(token)


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
