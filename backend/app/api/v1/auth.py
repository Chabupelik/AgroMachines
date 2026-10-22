from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.api.dependencies import rate_limiter, require_superadmin
from app.core.config import settings
from app.db.database import DbSession
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth.requests import UserCreateRequest, UserUpdateRequest
from app.schemas.auth.responses import TokenResponse, UserResponse
from app.schemas.common import ResponseOK
from app.services.auth_service import AuthService

router = APIRouter()


def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(UserRepository(db))


@router.post(
    "/login", response_model=TokenResponse, dependencies=[Depends(rate_limiter)]
)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_srv: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_srv.authenticate_user(form_data.username, form_data.password)
    access_token, refresh_token = auth_srv.create_tokens(user.id, user.role)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token, role=user.role)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    auth_srv: Annotated[AuthService, Depends(get_auth_service)],
):
    """Rolling Refresh: проверяет refresh-токен и выдаёт новый."""
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Нет refresh-токена")

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Неверный тип токена")

        new_access, new_refresh = auth_srv.create_tokens(
            payload["sub"], payload["role"]
        )

        response.set_cookie(
            key="refresh_token",
            value=new_refresh,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
        return TokenResponse(access_token=new_access, role=payload["role"])

    except JWTError:
        raise HTTPException(
            status_code=401, detail="Refresh-токен недействителен или истёк"
        )


@router.post(
    "/users",
    response_model=ResponseOK[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя (только суперадмин)",
)
async def create_user(
    schema: UserCreateRequest,
    auth_srv: Annotated[AuthService, Depends(get_auth_service)],
    current_admin: Annotated[User, Depends(require_superadmin)],
):
    new_user = await auth_srv.create_user(schema)
    return {"data": new_user}


@router.put(
    "/users/{user_id}",
    response_model=ResponseOK[UserResponse],
    summary="Изменить роль/данные пользователя (только суперадмин)",
)
async def update_user(
    user_id: UUID,
    schema: UserUpdateRequest,
    auth_srv: Annotated[AuthService, Depends(get_auth_service)],
    current_admin: Annotated[User, Depends(require_superadmin)],
):
    updated_user = await auth_srv.update_user(user_id, schema, current_admin.id)
    return {"data": updated_user}


@router.get(
    "/users",
    response_model=ResponseOK[list[UserResponse]],
    summary="Список пользователей (только суперадмин)",
)
async def get_users(
    auth_srv: Annotated[AuthService, Depends(get_auth_service)],
    current_admin: Annotated[User, Depends(require_superadmin)],
):
    all_users = await auth_srv.get_all_users()
    return {"data": all_users}


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя из системы (только суперадмин)",
)
async def delete_user(
    user_id: UUID,
    auth_srv: Annotated[AuthService, Depends(get_auth_service)],
    current_admin: Annotated[User, Depends(require_superadmin)],
):
    await auth_srv.delete_user(user_id, current_admin.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="refresh_token", secure=True, httponly=True, samesite="strict"
    )
    return {"status": "ok", "message": "Успешный выход"}
