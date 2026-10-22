from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.db.database import DbSession
from app.db.redis import RedisClient
from app.models.user import RoleEnum, User
from app.repositories.user_repo import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


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
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        jti: str | None = payload.get("jti")
        token_iat: int | None = payload.get("iat")

        if user_id is None or token_type != "access":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    if jti and await redis.exists(f"token_blacklist:{jti}"):
        raise credentials_exception

    revoked_ts = await redis.get(f"user_revoked:{user_id}")
    if revoked_ts is not None and (token_iat is None or token_iat < int(revoked_ts)):
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_audit_viewer(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role not in [RoleEnum.SUPERADMIN, RoleEnum.ADMIN]:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для просмотра аудит-лога"
        )
    return current_user


async def rate_limiter(
    request: Request,
    redis: RedisClient,
) -> None:
    ip = request.client.host
    path = request.url.path
    key = f"rate_limit:{ip}:{path}"

    current_requests = await redis.incr(key)

    if current_requests == 1:
        await redis.expire(key, 60)

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
require_editor = RoleChecker([RoleEnum.SUPERADMIN, RoleEnum.ADMIN, RoleEnum.EDITOR])
require_manager = RoleChecker([RoleEnum.SUPERADMIN, RoleEnum.ADMIN, RoleEnum.MANAGER])
