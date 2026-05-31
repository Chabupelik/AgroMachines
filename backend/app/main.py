import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine
from app.db.redis import redis_client
from app.api.v1.leads import router as leads_router

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
        await redis_client.aclose()
        print("💤 [SHUTDOWN] Database and Redis connections closed cleanly.")
    except Exception as e:
        print(f"❌ [SHUTDOWN] Error during connection teardown: {e}", file=sys.stderr)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-ready API for Agricultural Machinery Platform",
    version=settings.VERSION,
    openapi_url="/openapi.json" if settings.SHOW_DOCS else None,
    docs_url="/docs" if settings.SHOW_DOCS else None,
    redoc_url=None,
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://agromachines.chabupelik.su",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],     
    allow_headers=["*"],     
)

app.include_router(leads_router, prefix="/api/v1/leads", tags=["Leads"])

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": f"{settings.PROJECT_NAME} is running smoothly"
    }