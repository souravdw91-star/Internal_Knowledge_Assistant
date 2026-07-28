"""
=========================================================
File: config.py
Project: Internal Knowledge Assistant

Description:
------------
Centralized configuration file for the application.

This module:
- Loads environment variables
- Initializes Gemini configuration
- Initializes LangSmith configuration
- Stores Redis settings
- Stores FAISS settings
- Stores Upload settings
- Stores RAG settings

Author: Sourav
=========================================================
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# --------------------------------------------------------
# Load .env
# --------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


# ========================================================
# FastAPI Configuration
# ========================================================

APP_NAME = os.getenv("APP_NAME", "Internal Knowledge Assistant")

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

HOST = os.getenv("HOST", "127.0.0.1")

PORT = int(os.getenv("PORT", 8000))

DEBUG = os.getenv("DEBUG", "True").lower() == "true"


# ========================================================
# Gemini Configuration
# ========================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GEMINI_CHAT_MODEL = os.getenv(
    "GEMINI_CHAT_MODEL",
    "gemini-2.5-flash"
)

GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "models/text-embedding-004"
)


# ========================================================
# LangSmith
# ========================================================

LANGCHAIN_TRACING_V2 = os.getenv(
    "LANGCHAIN_TRACING_V2",
    "true"
)

LANGCHAIN_API_KEY = os.getenv(
    "LANGCHAIN_API_KEY"
)

LANGCHAIN_PROJECT = os.getenv(
    "LANGCHAIN_PROJECT",
    "Internal_Knowledge_Assistant"
)

LANGCHAIN_ENDPOINT = os.getenv(
    "LANGCHAIN_ENDPOINT",
    "https://api.smith.langchain.com"
)


# ========================================================
# Redis
# ========================================================

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

REDIS_DB = int(os.getenv("REDIS_DB", 0))

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")


# ========================================================
# FAISS
# ========================================================

FAISS_INDEX_PATH = BASE_DIR / os.getenv(
    "FAISS_INDEX_PATH",
    "faiss_index"
)


# ========================================================
# Upload Folder
# ========================================================

UPLOAD_FOLDER = BASE_DIR / os.getenv(
    "UPLOAD_FOLDER",
    "uploads"
)

UPLOAD_FOLDER.mkdir(exist_ok=True)

FAISS_INDEX_PATH.mkdir(exist_ok=True)


# ========================================================
# Text Splitter
# ========================================================

CHUNK_SIZE = int(
    os.getenv("CHUNK_SIZE", 1000)
)

CHUNK_OVERLAP = int(
    os.getenv("CHUNK_OVERLAP", 200)
)


# ========================================================
# Retriever
# ========================================================

TOP_K = int(
    os.getenv("TOP_K", 5)
)

SEARCH_TYPE = os.getenv(
    "SEARCH_TYPE",
    "similarity"
)

SEARCH_SCORE_THRESHOLD = float(
    os.getenv(
        "SEARCH_SCORE_THRESHOLD",
        0.70
    )
)


# ========================================================
# Cache
# ========================================================

CACHE_ENABLED = (
    os.getenv(
        "CACHE_ENABLED",
        "True"
    ).lower()
    == "true"
)

CACHE_TTL = int(
    os.getenv(
        "CACHE_TTL",
        3600
    )
)


# ========================================================
# Memory
# ========================================================

MEMORY_ENABLED = (
    os.getenv(
        "MEMORY_ENABLED",
        "True"
    ).lower()
    == "true"
)

MEMORY_WINDOW = int(
    os.getenv(
        "MEMORY_WINDOW",
        10
    )
)


# ========================================================
# Logging
# ========================================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
)


# ========================================================
# LLM Parameters
# ========================================================

TEMPERATURE = float(
    os.getenv(
        "TEMPERATURE",
        0.2
    )
)

TOP_P = float(
    os.getenv(
        "TOP_P",
        0.9
    )
)

MAX_OUTPUT_TOKENS = int(
    os.getenv(
        "MAX_OUTPUT_TOKENS",
        2048
    )
)


# ========================================================
# URL Loader
# ========================================================

USER_AGENT = os.getenv(
    "USER_AGENT",
    "InternalKnowledgeAssistant/1.0"
)


# ========================================================
# CORS
# ========================================================

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "*"
)


# ========================================================
# Session
# ========================================================

SESSION_TIMEOUT = int(
    os.getenv(
        "SESSION_TIMEOUT",
        1800
    )
)


# ========================================================
# Feature Flags
# ========================================================

ENABLE_SOURCE_CITATION = (
    os.getenv(
        "ENABLE_SOURCE_CITATION",
        "True"
    ).lower()
    == "true"
)

ENABLE_URL_UPLOAD = (
    os.getenv(
        "ENABLE_URL_UPLOAD",
        "True"
    ).lower()
    == "true"
)

ENABLE_PDF_UPLOAD = (
    os.getenv(
        "ENABLE_PDF_UPLOAD",
        "True"
    ).lower()
    == "true"
)

ENABLE_CHAT_HISTORY = (
    os.getenv(
        "ENABLE_CHAT_HISTORY",
        "True"
    ).lower()
    == "true"
)

ENABLE_REDIS_CACHE = (
    os.getenv(
        "ENABLE_REDIS_CACHE",
        "True"
    ).lower()
    == "true"
)

ENABLE_REDIS_MEMORY = (
    os.getenv(
        "ENABLE_REDIS_MEMORY",
        "True"
    ).lower()
    == "true"
)


# ========================================================
# Validation
# ========================================================

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY is missing. "
        "Please configure your .env file."
    )

if not LANGCHAIN_API_KEY:
    raise ValueError(
        "LANGCHAIN_API_KEY is missing. "
        "Please configure your .env file."
    )