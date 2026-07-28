"""
=========================================================
File: routes.py

Purpose
-------
Defines every API endpoint used by FastAPI.

Responsibilities
----------------
1. Upload PDF
2. Upload URL

Currently this file DOES NOT perform AI tasks.

It simply:
    Receives request
    Saves file
    Calls loader.py
    Returns result
=========================================================
"""

import os
import shutil

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException

from pydantic import BaseModel

from backend.loader import load_pdf
from backend.loader import load_url


router = APIRouter()

UPLOAD_FOLDER = "uploads"

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class URLRequest(BaseModel):
    """
    Request body for URL upload.
    """

    url: str


@router.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF.

    Steps
    -----
    1. Validate extension
    2. Save file
    3. Read using loader.py
    4. Return information
    """

    # Allow only PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Save uploaded file
    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Read PDF
    documents = load_pdf(file_path)

    return {
        "status": "success",
        "filename": file.filename,
        "pages": len(documents),
        "preview": documents[0].page_content[:300]
        if documents else ""
    }


@router.post("/upload/url")
async def upload_url(request: URLRequest):
    """
    Load a website.

    Steps
    -----
    1. Receive URL
    2. Read webpage
    3. Return preview
    """

    documents = load_url(request.url)

    return {
        "status": "success",
        "url": request.url,
        "documents": len(documents),
        "preview": documents[0].page_content[:300]
        if documents else ""
    }