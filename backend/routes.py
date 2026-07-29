"""
routes.py

FastAPI API routes.
"""

from pathlib import Path

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
)

from pydantic import BaseModel

from backend.loader import DocumentLoader
from backend.rag import rag_pipeline
from backend.cache import redis_cache
from backend.memory import redis_memory
from backend.config import (
    UPLOAD_FOLDER,
    ENABLE_PDF_UPLOAD,
    ENABLE_URL_UPLOAD,
)

from backend.utils import (
    allowed_file,
    generate_session_id,
    LOGGER,
)

router = APIRouter(tags=["Internal Knowledge Assistant"])

loader = DocumentLoader()


# ==========================================================
# Request Models
# ==========================================================

class ChatRequest(BaseModel):

    question: str

    session_id: str | None = None


class URLRequest(BaseModel):

    url: str


# ==========================================================
# Upload PDF
# ==========================================================

@router.post("/upload/pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    if not ENABLE_PDF_UPLOAD:

        raise HTTPException(
            status_code=403,
            detail="PDF upload is disabled."
        )

    if not allowed_file(file.filename):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    try:

        upload_path = Path(UPLOAD_FOLDER)

        upload_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = upload_path / file.filename

        with open(destination, "wb") as f:

            f.write(await file.read())

        chunks = loader.load_pdf_chunks(
            str(destination)
        )

        rag_pipeline.index_documents(
            chunks
        )

        redis_cache.clear()

        return {

            "success": True,

            "message": "PDF uploaded successfully.",

            "filename": file.filename,

            "chunks": len(chunks),

            "indexed_chunks": rag_pipeline.chunk_count()

        }

    except Exception as e:

        LOGGER.exception(e)

        err_str = str(e).lower()
        if "authentication" in err_str or "unauthenticated" in err_str or "401" in err_str or "blocked" in err_str:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired Gemini API key. Please check your GOOGLE_API_KEY in the .env file."
            )
        if "429" in err_str or "quota" in err_str or "rate limit" in err_str:
            raise HTTPException(
                status_code=429,
                detail="Gemini API rate limit or quota exceeded. Please wait a moment before trying again."
            )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================================
# Upload Website
# ==========================================================

@router.post("/upload/url")
async def upload_url(
    request: URLRequest
):

    if not ENABLE_URL_UPLOAD:

        raise HTTPException(
            status_code=403,
            detail="URL upload is disabled."
        )

    try:

        chunks = loader.load_url_chunks(
            request.url
        )

        rag_pipeline.index_documents(
            chunks
        )

        redis_cache.clear()

        return {

            "success": True,

            "message": "Website indexed successfully.",

            "url": request.url,

            "chunks": len(chunks),

            "indexed_chunks": rag_pipeline.chunk_count()

        }

    except Exception as e:

        LOGGER.exception(e)

        err_str = str(e).lower()
        if "authentication" in err_str or "unauthenticated" in err_str or "401" in err_str or "blocked" in err_str:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired Gemini API key. Please check your GOOGLE_API_KEY in the .env file."
            )
        if "429" in err_str or "quota" in err_str or "rate limit" in err_str:
            raise HTTPException(
                status_code=429,
                detail="Gemini API rate limit or quota exceeded. Please wait a moment before trying again."
            )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================================
# Upload PDF + Ask Question
# ==========================================================

@router.post("/upload-and-chat")
async def upload_and_chat(
    file: UploadFile = File(...),
    question: str = Form(...),
    session_id: str | None = Form(None),
):

    if session_id is None:

        session_id = generate_session_id()

    if not allowed_file(file.filename):

        raise HTTPException(
            status_code=400,
            detail="Invalid file type."
        )

    try:

        upload_path = Path(UPLOAD_FOLDER)

        upload_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = upload_path / file.filename

        with open(destination, "wb") as f:

            f.write(await file.read())

        chunks = loader.load_pdf_chunks(
            str(destination)
        )

        rag_pipeline.index_documents(
            chunks
        )

        redis_cache.clear()

        response = rag_pipeline.chat(

            question=question,

            session_id=session_id,

            memory=redis_memory,

            cache=redis_cache,

        )

        return {

            "success": True,

            "session_id": session_id,

            "filename": file.filename,

            "indexed_chunks": rag_pipeline.chunk_count(),

            **response,

        }

    except Exception as e:

        LOGGER.exception(e)

        err_str = str(e).lower()
        if "authentication" in err_str or "unauthenticated" in err_str or "401" in err_str or "blocked" in err_str:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired Gemini API key. Please check your GOOGLE_API_KEY in the .env file."
            )
        if "429" in err_str or "quota" in err_str or "rate limit" in err_str:
            raise HTTPException(
                status_code=429,
                detail="Gemini API rate limit or quota exceeded. Please wait a moment before trying again."
            )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    # ==========================================================
# Chat
# ==========================================================

@router.post("/chat")
async def chat(request: ChatRequest):

    try:

        session_id = request.session_id or generate_session_id()

        response = rag_pipeline.chat(
            question=request.question,
            session_id=session_id,
            memory=redis_memory,
            cache=redis_cache,
        )

        return {
            "success": True,
            "session_id": session_id,
            **response,
        }

    except Exception as e:

        LOGGER.exception(e)

        err_str = str(e).lower()
        if "authentication" in err_str or "unauthenticated" in err_str or "401" in err_str or "blocked" in err_str:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired Gemini API key. Please check your GOOGLE_API_KEY in the .env file."
            )
        if "429" in err_str or "quota" in err_str or "rate limit" in err_str:
            raise HTTPException(
                status_code=429,
                detail="Gemini API rate limit or quota exceeded. Please wait a moment before trying again."
            )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# Chat History
# ==========================================================

@router.get("/history/{session_id}")
async def chat_history(session_id: str):

    try:

        history = redis_memory.get_history(session_id)

        return {
            "success": True,
            "session_id": session_id,
            "history": history,
            "messages": history,
            "count": len(history),
        }

    except Exception as e:

        LOGGER.exception(e)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# New Session
# ==========================================================

@router.get("/session/new")
async def new_session():

    return {
        "success": True,
        "session_id": generate_session_id(),
    }


# ==========================================================
# Health
# ==========================================================

@router.get("/health")
async def health():

    return {
        "success": True,
        "status": "healthy",
        "pipeline": rag_pipeline.health(),
        "cache": redis_cache.stats(),
        "memory": redis_memory.stats(),
    }


# ==========================================================
# Statistics
# ==========================================================

@router.get("/stats")
async def stats():

    return {
        "success": True,
        "rag": rag_pipeline.stats(),
        "cache": redis_cache.stats(),
        "memory": redis_memory.stats(),
    }


# ==========================================================
# Clear Cache
# ==========================================================

@router.delete("/cache")
async def clear_cache():

    try:

        redis_cache.clear()

        return {
            "success": True,
            "message": "Cache cleared.",
        }

    except Exception as e:

        LOGGER.exception(e)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# Clear Session Memory
# ==========================================================

@router.delete("/memory/{session_id}")
async def clear_memory(session_id: str):

    try:

        redis_memory.clear_session(session_id)

        return {
            "success": True,
            "session_id": session_id,
            "message": "Conversation memory cleared.",
        }

    except Exception as e:

        LOGGER.exception(e)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# Delete Knowledge Base
# ==========================================================

@router.delete("/knowledge-base")
async def delete_knowledge_base():

    try:

        rag_pipeline.clear_knowledge_base()

        redis_cache.clear()

        return {
            "success": True,
            "message": "Knowledge base deleted successfully.",
        }

    except Exception as e:

        LOGGER.exception(e)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# Reload Vector Store
# ==========================================================

@router.post("/reload")
async def reload_pipeline():

    try:

        rag_pipeline.reload()

        return {
            "success": True,
            "message": "Pipeline reloaded successfully.",
            "indexed_chunks": rag_pipeline.chunk_count(),
        }

    except Exception as e:

        LOGGER.exception(e)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# Clear Cache
# ==========================================================

@router.delete("/cache")
async def clear_cache():

    try:

        redis_cache.clear()

        return {
            "success": True,
            "message": "Cache cleared successfully.",
        }

    except Exception as e:

        LOGGER.exception(e)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# Ping
# ==========================================================

@router.get("/")
async def root():

    return {
        "application": "Internal Knowledge Assistant",
        "version": "1.0.0",
        "status": "Running",
    }