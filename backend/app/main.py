import sys
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.db.database import engine
from app.db.redis import redis_client
from app.api.v1.leads import router as leads_router
from sqlalchemy import text

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
    "https://agromachines.chabupelik.su"

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
    """Мидлварь логирования: замеряет время обработки запроса и пишет красивый лог"""
    start_time = time.time()
    
    response: Response = await call_next(request)
    
    process_time_ms = (time.time() - start_time) * 1000
    
    print(f"📡 [API LOG] {request.client.host} - \"{request.method} {request.url.path}\" {response.status_code} ({process_time_ms:.2f}ms)")
    
    return response

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Перехватывает стандартные HTTPException и возвращает красивый JSON"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Перехватывает ошибки валидации Pydantic и делает из них читабельный список ошибок"""
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(x) for x in error["loc"])
        errors.append(f"[{loc}]: {error['msg']}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status": "error", "message": "; ".join(errors)}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"💥 [CRITICAL ERROR] {request.method} {request.url.path}: {exc}", file=sys.stderr)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "Внутренняя ошибка сервера. Пожалуйста, попробуйте позже."}
    )


app.include_router(leads_router, prefix="/api/v1/leads", tags=["Leads"])


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": f"{settings.PROJECT_NAME} is running smoothly"
    }