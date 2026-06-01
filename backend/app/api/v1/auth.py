from fastapi import APIRouter, Depends, Response, Request, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from uuid import UUID

from app.db.database import get_db
from app.core.config import settings
from app.schemas.common import ResponseOK
from app.schemas.auth.requests import UserCreateRequest, UserUpdateRequest
from app.schemas.auth.responses import TokenResponse, UserResponse
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService
from app.api.dependencies import rate_limiter, require_superadmin
from app.models.user import User

router = APIRouter()

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limiter)])
async def login(
    response: Response, 
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_srv: AuthService = Depends(get_auth_service)
):
    user = await auth_srv.authenticate_user(form_data.username, form_data.password)
    access_token, refresh_token = auth_srv.create_tokens(user.id, user.role)
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,          
        samesite="strict",    
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return TokenResponse(access_token=access_token, role=user.role)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, response: Response, auth_srv: AuthService = Depends(get_auth_service)):
    """Метод Rolling Refresh: проверяет старую куку и выдает новые токены"""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Токен обновления отсутствует")

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Неверный тип токена")
        
        new_access, new_refresh = auth_srv.create_tokens(payload["sub"], payload["role"])
        
        response.set_cookie(
            key="refresh_token", value=new_refresh, httponly=True, secure=True,
            samesite="strict", max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        return TokenResponse(access_token=new_access, role=payload["role"])
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Токен недействителен или истек")
    

@router.post(
    "/users", 
    response_model=ResponseOK[UserResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Создать нового пользователя (Доступно только Суперадмину)"
)
async def create_user(
    schema: UserCreateRequest,
    auth_srv: AuthService = Depends(get_auth_service),
    current_admin: User = Depends(require_superadmin)
):
    new_user = await auth_srv.create_user(schema)
    return {"data": new_user}

@router.put(
    "/users/{user_id}", 
    response_model=ResponseOK[UserResponse],
    summary="Обновить роль или статус пользователя (Доступно только Суперадмину)"
)
async def update_user(
    user_id: UUID,
    schema: UserUpdateRequest,
    auth_srv: AuthService = Depends(get_auth_service),
    current_admin: User = Depends(require_superadmin)
):
    updated_user = await auth_srv.update_user(user_id, schema)
    return {"data": updated_user}

@router.get(
    "/users", 
    response_model=ResponseOK[list[UserResponse]], 
    summary="Получить список всех пользователей (Доступно только Суперадмину)"
)
async def get_users(
    auth_srv: AuthService = Depends(get_auth_service),
    current_admin: User = Depends(require_superadmin)
):
    all_users = await auth_srv.get_all_users()
    return {"data": all_users}

@router.delete(
    "/users/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя из системы (Доступно только Суперадмину)"
)
async def delete_user(
    user_id: UUID,
    auth_srv: AuthService = Depends(get_auth_service),
    current_admin: User = Depends(require_superadmin)
):
    await auth_srv.delete_user(user_id, current_admin.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="refresh_token", secure=True, httponly=True, samesite="strict")
    return {"status": "ok", "message": "Успешный выход"}