from fastapi import APIRouter, Depends, Response, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.db.database import get_db
from app.core.config import settings
from app.schemas.auth.requests import LoginRequest
from app.schemas.auth.responses import TokenResponse
from app.repositories.user_repo import UserRepository
from app.services.auth_srv import AuthService

router = APIRouter()

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))

@router.post("/login", response_model=TokenResponse)
async def login(
    response: Response, 
    schema: LoginRequest, 
    auth_srv: AuthService = Depends(get_auth_service)
):
    user = await auth_srv.authenticate_user(schema.username, schema.password)
    
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

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="refresh_token", secure=True, httponly=True, samesite="strict")
    return {"status": "ok", "message": "Успешный выход"}