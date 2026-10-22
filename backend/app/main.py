import logging
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.leads import router as leads_router
from app.api.v1.machines import router as machines_router
from app.api.v1.telegram import router as telegram_router
from app.core.config import settings
from app.db.database import DbSession, engine
from app.db.redis import RedisClient, get_raw_redis_client
from app.schemas.common import ResponseError, ResponseOK

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("agroprom_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        await get_raw_redis_client().ping()
        logger.info("?? Database and Redis connections established successfully.")
    except Exception as e:
        logger.error(f"? Connection check failed: {e}")
        sys.exit(1)

    yield

    try:
        await engine.dispose()
        await get_raw_redis_client().aclose()
        logger.info("?? Database and Redis connections closed cleanly.")
    except Exception as e:
        logger.error(f"? Error during connection teardown: {e}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-ready API for Agricultural Machinery Platform",
    version=settings.VERSION,
    openapi_url="/openapi.json" if settings.SHOW_DOCS else None,
    docs_url="/docs" if settings.SHOW_DOCS else None,
    redoc_url="/redoc" if settings.SHOW_DOCS else None,
    lifespan=lifespan,
)

origins = ["https://agromachines.chabupelik.su"]

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
    logger.info(
        f'?? {request.client.host} - "{request.method} {request.url.path}" '
        f"{response.status_code} ({process_time_ms:.2f}ms)"
    )
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseError(message=exc.detail).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        f"[{' -> '.join(str(x) for x in e['loc'])}]: {e['msg']}" for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseError(
            message="Ошибка валидации входных данных", details=errors
        ).model_dump(),
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    errors = [
        f"[{' -> '.join(str(x) for x in e['loc'])}]: {e['msg']}" for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseError(
            message="Ошибка валидации входных данных", details=errors
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"?? {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Внутренняя ошибка сервера. Пожалуйста, попробуйте позже.",
        },
    )


@app.get(
    "/health",
    response_model=ResponseOK[dict],
    summary="Проверка доступности (Liveness)",
)
async def health_check():
    return ResponseOK(data={"message": "API is alive"})


@app.get(
    "/ready",
    response_model=ResponseOK[dict],
    summary="Проверка готовности к работе (Readiness)",
)
async def ready_check(
    db: DbSession,
    redis: RedisClient,
):
    try:
        await db.execute(text("SELECT 1"))
        await redis.ping()
        return ResponseOK(data={"postgres": "connected", "redis": "connected"})
    except Exception as e:
        logger.error(f"? [READY CHECK FAILED]: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "message": "Системы не готовы к работе: БД или Redis недоступны",
            },
        )


app.include_router(leads_router, prefix="/api/v1/leads", tags=["Leads"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(machines_router, prefix="/api/v1/machines", tags=["Machines"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["Audit Logs"])
app.include_router(
    telegram_router, prefix="/api/v1/telegram", tags=["Telegram Webhook"]
)

# Serve static frontend SPA if dist exists
frontend_dist = Path("/code/frontend/dist")
if not frontend_dist.is_dir():
    frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if frontend_dist.is_dir():
    assets_dir = frontend_dist / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith(
            ("api/", "health", "ready", "docs", "redoc", "openapi.json")
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Not Found"
            )
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        index_file = frontend_dist / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frontend build index.html not found",
        )
