from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db
from app.db.redis import redis_client
from app.repositories.user_repo import UserRepository
from app.models.user import User, RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные (токен истек или неверен)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if user is None or not user.is_active:
        raise credentials_exception
        
    return user

def require_audit_viewer(current_user: User = Depends(get_current_user)):
    if current_user.role not in [RoleEnum.SUPERADMIN, RoleEnum.ADMIN]:
        raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра журнала безопасности")
    return current_user

async def rate_limiter(request: Request):
    ip = request.client.host
    path = request.url.path
    key = f"rate_limit:{ip}:{path}"
    
    current_requests = await redis_client.get(key)
    
    if current_requests and int(current_requests) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком много запросов. Пожалуйста, попробуйте позже."
        )
        
    await redis_client.incr(key)
    
    if not current_requests:
        await redis_client.expire(key, 60)

class RoleChecker:
    def __init__(self, allowed_roles: list[RoleEnum]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Доступ запрещен. Необходима одна из ролей: {[r.value for r in self.allowed_roles]}"
            )
        return user

require_superadmin = RoleChecker([RoleEnum.SUPERADMIN])
require_editor = RoleChecker([RoleEnum.SUPERADMIN, RoleEnum.ADMIN, RoleEnum.EDITOR])
require_manager = RoleChecker([RoleEnum.SUPERADMIN, RoleEnum.ADMIN, RoleEnum.MANAGER])