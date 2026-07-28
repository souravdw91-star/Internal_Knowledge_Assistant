from fastapi import FastAPI
from backend.routes import router

app = FastAPI(
    title="Internal Knowledge Assistant",
    version="1.0.0"
)

# Register all API routes
app.include_router(router)

@app.get("/")
def home():
    return {
        "status": "running",
        "message": "Internal Knowledge Assistant API"
    }