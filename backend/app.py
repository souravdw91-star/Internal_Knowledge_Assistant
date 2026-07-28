"""
app.py

FastAPI entry point.
"""

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import (
    APP_NAME,
    APP_VERSION,
    HOST,
    PORT,
    DEBUG,
    ALLOWED_ORIGINS,
)

from backend.routes import router
from backend.utils import print_banner, LOGGER
from backend.rag import rag_pipeline
from backend.cache import redis_cache
from backend.memory import redis_memory


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


# -------------------------------------------------------
# CORS
# -------------------------------------------------------

origins = (
    ["*"]
    if ALLOWED_ORIGINS == "*"
    else [origin.strip() for origin in ALLOWED_ORIGINS.split(",")]
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
# Routers
# -------------------------------------------------------

app.include_router(router)


# -------------------------------------------------------
# Root
# -------------------------------------------------------

@app.get("/")
async def home():

    return {

        "application": APP_NAME,

        "version": APP_VERSION,

        "status": "Running",

        "docs": "/docs",

        "redoc": "/redoc",

    }


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