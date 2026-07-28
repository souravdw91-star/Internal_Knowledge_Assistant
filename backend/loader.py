"""
=========================================================
File: loader.py

Purpose
-------
This module is responsible ONLY for loading documents.

Responsibilities
----------------
1. Load PDF files
2. Load Website URLs

It DOES NOT:
-------------
❌ Create embeddings
❌ Split text
❌ Create FAISS
❌ Call Gemini

Those belong to other modules.
=========================================================
"""

# LangChain PDF Loader
from langchain_community.document_loaders import PyPDFLoader

# LangChain Website Loader
from langchain_community.document_loaders import WebBaseLoader


def load_pdf(file_path: str):
    """
    Load a PDF file and return LangChain Document objects.

    Parameters
    ----------
    file_path : str
        Path of the uploaded PDF.

    Returns
    -------
    list[Document]
        A list of LangChain Document objects.
        Each page becomes one Document.
    """

    # Create loader object
    loader = PyPDFLoader(file_path)

    # Read PDF
    documents = loader.load()

    return documents


def load_url(url: str):
    """
    Load a website.

    Parameters
    ----------
    url : str

    Returns
    -------
    list[Document]
    """

    loader = WebBaseLoader(url)

    documents = loader.load()

    return documents