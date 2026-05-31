import sys
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine, get_db
from app.db.redis import redis_client
from app.api.v1.leads import router as leads_router
from app.api.v1.auth import router as auth_router
from app.api.v1.machines import router as machines_router
from app.schemas.common import ResponseOK, ResponseError

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        await redis_client.ping()
        print("🚀 [STARTUP] Database and Redis connections established successfully.")
    except Exception as e:
        print(f"❌ [STARTUP] Connection check failed: {e}", file=sys.stderr)
        sys.exit(1)
        
    yield
    
    try:
        await engine.dispose()
        await redis_client.close()
        print("💤 [SHUTDOWN] Database and Redis connections closed cleanly.")
    except Exception as e:
        print(f"❌ [SHUTDOWN] Error during connection teardown: {e}", file=sys.stderr)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-ready API for Agricultural Machinery Platform",
    version=settings.VERSION,
    openapi_url="/openapi.json" if settings.SHOW_DOCS else None,
    docs_url="/docs" if settings.SHOW_DOCS else None,
    redoc_url="/redoc" if settings.SHOW_DOCS else None,
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://chabupelik.su",
    "https://watcher.chabupelik.su",   
    "https://predator.chabupelik.su",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],     
    allow_headers=["*"],     
)

@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time_ms = (time.time() - start_time) * 1000
    print(f"📡 [API LOG] {request.client.host} - \"{request.method} {request.url.path}\" {response.status_code} ({process_time_ms:.2f}ms)")
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_response = ResponseError(message=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(x) for x in error["loc"])
        errors.append(f"[{loc}]: {error['msg']}")
    
    error_response = ResponseError(
        message="Ошибка валидации входящих данных",
        details=errors
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"💥 [CRITICAL ERROR] {request.method} {request.url.path}: {exc}", file=sys.stderr)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "Внутренняя ошибка сервера. Пожалуйста, попробуйте позже."}
    )

@app.get("/health", response_model=ResponseOK[dict], summary="Проверка жизнеспособности процесса (Liveness)")
async def health_check():
    """Просто проверяет, что процесс FastAPI жив и отвечает на запросы"""
    return ResponseOK(data={"message": "API is alive"})


@app.get("/ready", response_model=ResponseOK[dict], summary="Проверка готовности баз данных к работе (Readiness)")
async def ready_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        await redis_client.ping()
        return ResponseOK(data={"postgres": "connected", "redis": "connected"})
    except Exception as e:
        print(f"❌ [READY CHECK FAILED]: {e}", file=sys.stderr)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "message": "Система не готова к работе: База данных или Redis недоступны"}
        )


app.include_router(leads_router, prefix="/api/v1/leads", tags=["Leads"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(machines_router, prefix="/api/v1/machines", tags=["Machines"])