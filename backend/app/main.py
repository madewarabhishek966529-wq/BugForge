import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.database.init_db import init_db
from backend.app.api.projects import router as projects_router
from backend.app.api.bugs import router as bugs_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bugforge.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"Error initializing DB: {e}")
    yield
    logger.info("BugForge API shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["health"])

def health_check():
    return {
        "status": "ok",
        "service": "BugForge API"
    }

app.include_router(projects_router, prefix=settings.API_V1_STR)
app.include_router(bugs_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
