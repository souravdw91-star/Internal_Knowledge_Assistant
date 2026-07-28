"""
=========================================================
Main FastAPI Application
=========================================================
"""

from fastapi import FastAPI

from backend.routes import router

app = FastAPI(
    title="Internal Knowledge Assistant",
    version="1.0.0"
)

# Register all API endpoints
app.include_router(router)


@app.get("/")
def home():
    """
    Health Check API
    """

    return {
        "status": "running",
        "application": "Internal Knowledge Assistant"
    }