"""
=========================================================
File: utils.py
Project: Internal Knowledge Assistant

Description
-----------
Common utility functions used throughout the application.

Responsibilities
----------------
- Logger configuration
- Session ID generation
- File validation
- Directory management
- JSON helpers
- Response formatter
- Error formatter
- SHA256 hashing (cache keys)
- URL validation

Author: Sourav
=========================================================
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from pathlib import Path
from urllib.parse import urlparse

from backend.config import LOG_LEVEL


# ==========================================================
# Logger Configuration
# ==========================================================

LOGGER = logging.getLogger("InternalKnowledgeAssistant")

if not LOGGER.handlers:

    LOGGER.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s | %(filename)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    LOGGER.addHandler(console_handler)


# ==========================================================
# Session Utilities
# ==========================================================

def generate_session_id() -> str:
    """
    Generates a unique UUID for each user session.

    Returns
    -------
    str
        UUID string
    """
    return str(uuid.uuid4())


# ==========================================================
# Hash Utilities
# ==========================================================

def generate_hash(text: str) -> str:
    """
    Generates SHA256 hash.

    Useful for:
        - Redis cache key
        - Duplicate document detection

    Parameters
    ----------
    text : str

    Returns
    -------
    str
    """
    return hashlib.sha256(text.encode()).hexdigest()


# ==========================================================
# File Utilities
# ==========================================================

ALLOWED_EXTENSIONS = {
    ".pdf"
}


def allowed_file(filename: str) -> bool:
    """
    Check if uploaded file is supported.

    Parameters
    ----------
    filename : str

    Returns
    -------
    bool
    """

    extension = Path(filename).suffix.lower()

    return extension in ALLOWED_EXTENSIONS


def ensure_directory(path: str | Path):
    """
    Creates directory if it does not exist.

    Parameters
    ----------
    path : str | Path
    """

    Path(path).mkdir(
        parents=True,
        exist_ok=True
    )


# ==========================================================
# URL Utilities
# ==========================================================

def is_valid_url(url: str) -> bool:
    """
    Validates URL.

    Parameters
    ----------
    url : str

    Returns
    -------
    bool
    """

    try:

        parsed = urlparse(url)

        return all(
            [
                parsed.scheme,
                parsed.netloc
            ]
        )

    except Exception:

        return False


# ==========================================================
# JSON Utilities
# ==========================================================

def save_json(filepath: str | Path, data: dict):
    """
    Saves dictionary into JSON file.

    Parameters
    ----------
    filepath : str | Path

    data : dict
    """

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_json(filepath: str | Path) -> dict:
    """
    Reads JSON file.

    Parameters
    ----------
    filepath : str | Path

    Returns
    -------
    dict
    """

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==========================================================
# Response Formatter
# ==========================================================

def success_response(
    answer: str,
    sources: list | None = None
) -> dict:
    """
    Standard API success response.

    Parameters
    ----------
    answer : str

    sources : list

    Returns
    -------
    dict
    """

    return {

        "success": True,

        "answer": answer,

        "sources": sources or []

    }


def error_response(
    message: str
) -> dict:
    """
    Standard API error response.

    Parameters
    ----------
    message : str

    Returns
    -------
    dict
    """

    return {

        "success": False,

        "message": message

    }


# ==========================================================
# File Size Utility
# ==========================================================

def file_size_mb(path: str | Path) -> float:
    """
    Returns file size in MB.

    Parameters
    ----------
    path : str | Path

    Returns
    -------
    float
    """

    size = os.path.getsize(path)

    return round(size / (1024 * 1024), 2)


# ==========================================================
# Pretty Printer
# ==========================================================

def print_banner():
    """
    Prints startup banner.
    """

    banner = """

=========================================================
        Internal Knowledge Assistant
---------------------------------------------------------
 LangChain
 Gemini
 FastAPI
 FAISS
 Redis
 LangSmith
=========================================================

"""

    LOGGER.info(banner)


# ==========================================================
# Exception Logger
# ==========================================================

def log_exception(exception: Exception):
    """
    Logs exceptions in a standardized format.

    Parameters
    ----------
    exception : Exception
    """

    LOGGER.exception(str(exception))