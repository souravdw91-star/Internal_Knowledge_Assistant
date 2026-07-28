"""
app.py

FastAPI entry point.
"""

from pathlib import Path
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import (
    APP_NAME,
    APP_VERSION,
    HOST,
    PORT,
    DEBUG,
    ALLOWED_ORIGINS,
)

from backend.routes import router
from backend.utils import LOGGER, print_banner
from backend.rag import rag_pipeline
from backend.cache import redis_cache
from backend.memory import redis_memory


# -------------------------------------------------------
# Paths
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


# -------------------------------------------------------
# FastAPI
# -------------------------------------------------------

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# -------------------------------------------------------
# Static Files
# -------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static",
)

# -------------------------------------------------------
# CORS
# -------------------------------------------------------

origins = (
    ["*"]
    if ALLOWED_ORIGINS == "*"
    else [o.strip() for o in ALLOWED_ORIGINS.split(",")]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# Startup
# -------------------------------------------------------

@app.on_event("startup")
async def startup():

    print_banner()

    LOGGER.info("Starting application...")

    try:

        if rag_pipeline.knowledge_base_exists():

            rag_pipeline.reload()

            LOGGER.info("Knowledge base loaded.")

        else:

            LOGGER.info("No FAISS index found.")

    except Exception as e:

        LOGGER.exception(e)

    if redis_cache.client:
        LOGGER.info("Redis cache ready.")
    else:
        LOGGER.warning("Redis cache unavailable.")

    if redis_memory.client:
        LOGGER.info("Redis memory ready.")
    else:
        LOGGER.warning("Redis memory unavailable.")

    LOGGER.info("Application started successfully.")


# -------------------------------------------------------
# Shutdown
# -------------------------------------------------------

@app.on_event("shutdown")
async def shutdown():

    LOGGER.info("Shutting down application...")

    try:
        if redis_cache.client:
            redis_cache.client.close()
    except Exception:
        pass

    try:
        if redis_memory.client:
            redis_memory.client.close()
    except Exception:
        pass

    LOGGER.info("Application stopped.")


# -------------------------------------------------------
# API Routes
# -------------------------------------------------------

app.include_router(router, prefix="/api")

# -------------------------------------------------------
# Frontend Routes
# -------------------------------------------------------

@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/style.css", include_in_schema=False)
async def style():
    return FileResponse(FRONTEND_DIR / "style.css")


@app.get("/script.js", include_in_schema=False)
async def script():
    return FileResponse(FRONTEND_DIR / "script.js")


# -------------------------------------------------------
# Health
# -------------------------------------------------------

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION,
        "knowledge_base": rag_pipeline.knowledge_base_exists(),
        "indexed_chunks": rag_pipeline.chunk_count(),
        "redis_cache": redis_cache.client is not None,
        "redis_memory": redis_memory.client is not None,
    }


# -------------------------------------------------------
# Run
# -------------------------------------------------------

if __name__ == "__main__":

    uvicorn.run(
        "backend.app:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
    )