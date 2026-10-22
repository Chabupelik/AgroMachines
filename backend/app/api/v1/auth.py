from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

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


AuthSrv = Annotated[AuthService, Depends(get_auth_service)]
CurrentSuperAdmin = Annotated[User, Depends(require_superadmin)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


def delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        secure=True,
        httponly=True,
        samesite="strict",
    )


@router.post(
    "/login", response_model=TokenResponse, dependencies=[Depends(rate_limiter)]
)
async def login(
    response: Response,
    form_data: OAuth2Form,
    auth_srv: AuthSrv,
):
    access_token, refresh_token, role = await auth_srv.login(
        form_data.username, form_data.password
    )
    set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token, role=role)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    auth_srv: AuthSrv,
):
    token = request.cookies.get("refresh_token")
    access_token, new_refresh, role = await auth_srv.refresh_tokens(token)
    set_refresh_cookie(response, new_refresh)
    return TokenResponse(access_token=access_token, role=role)


@router.post(
    "/users",
    response_model=ResponseOK[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя (только суперадмин)",
)
async def create_user(
    schema: UserCreateRequest,
    auth_srv: AuthSrv,
    current_admin: CurrentSuperAdmin,
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
    auth_srv: AuthSrv,
    current_admin: CurrentSuperAdmin,
):
    updated_user = await auth_srv.update_user(user_id, schema, current_admin.id)
    return {"data": updated_user}


@router.get(
    "/users",
    response_model=ResponseOK[list[UserResponse]],
    summary="Список пользователей (только суперадмин)",
)
async def get_users(
    auth_srv: AuthSrv,
    current_admin: CurrentSuperAdmin,
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
    auth_srv: AuthSrv,
    current_admin: CurrentSuperAdmin,
):
    await auth_srv.delete_user(user_id, current_admin.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout")
async def logout(response: Response):
    delete_refresh_cookie(response)
    return {"status": "ok", "message": "Успешный выход"}
