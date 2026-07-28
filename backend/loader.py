"""
loader.py

Loads PDF or URL content and converts it into LangChain document chunks.
"""

from pathlib import Path
from typing import List

from langchain_community.document_loaders import (
    PyPDFLoader,
    WebBaseLoader,
)
from langchain_text_splitters  import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from backend.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    USER_AGENT,
)
from backend.utils import (
    LOGGER,
    is_valid_url,
)


class DocumentLoader:
    """Handles PDF/URL loading and document chunking."""

    def __init__(self):

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    def load_pdf(self, pdf_path: str) -> List[Document]:
        """
        Load a PDF.

        Parameters
        ----------
        pdf_path : str

        Returns
        -------
        List[Document]
        """

        try:

            pdf_path = Path(pdf_path)

            if not pdf_path.exists():
                raise FileNotFoundError(
                    f"PDF not found: {pdf_path}"
                )

            LOGGER.info(f"Loading PDF : {pdf_path.name}")

            loader = PyPDFLoader(str(pdf_path))

            documents = loader.load()

            for page in documents:

                page.metadata["source"] = pdf_path.name

                page.metadata["file_name"] = pdf_path.name

                page.metadata["file_type"] = "pdf"

            LOGGER.info(
                f"{len(documents)} pages loaded."
            )

            return documents

        except Exception as e:

            LOGGER.exception(e)

            raise

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    def load_url(self, url: str) -> List[Document]:
        """
        Load webpage.

        Parameters
        ----------
        url : str

        Returns
        -------
        List[Document]
        """

        if not is_valid_url(url):
            raise ValueError("Invalid URL.")

        try:

            LOGGER.info(f"Loading URL : {url}")

            loader = WebBaseLoader(
                web_paths=(url,),
                header_template={
                    "User-Agent": USER_AGENT
                },
            )

            documents = loader.load()

            for doc in documents:

                doc.metadata["source"] = url

                doc.metadata["file_name"] = url

                doc.metadata["file_type"] = "url"

            LOGGER.info(
                f"{len(documents)} webpage(s) loaded."
            )

            return documents

        except Exception as e:

            LOGGER.exception(e)

            raise

    # --------------------------------------------------------
    # Chunking
    # --------------------------------------------------------

    def split_documents(
        self,
        documents: List[Document],
    ) -> List[Document]:
        """
        Split documents into chunks.
        """

        chunks = self.text_splitter.split_documents(
            documents
        )

        for index, chunk in enumerate(chunks):

            chunk.metadata["chunk_id"] = index + 1

        LOGGER.info(
            f"{len(chunks)} chunks created."
        )

        return chunks

    # --------------------------------------------------------
    # Cleaning
    # --------------------------------------------------------

    @staticmethod
    def clean_documents(
        documents: List[Document],
    ) -> List[Document]:
        """
        Remove unnecessary whitespaces.
        """

        cleaned = []

        for doc in documents:

            text = (
                doc.page_content.replace("\t", " ")
                .replace("\r", " ")
                .replace("\x00", "")
            )

            text = " ".join(text.split())

            doc.page_content = text

            cleaned.append(doc)

        return cleaned

    # --------------------------------------------------------
    # Pipeline
    # --------------------------------------------------------

    def load_pdf_chunks(
        self,
        pdf_path: str,
    ) -> List[Document]:
        """
        PDF -> Clean -> Chunk
        """

        documents = self.load_pdf(pdf_path)

        documents = self.clean_documents(documents)

        return self.split_documents(documents)

    def load_url_chunks(
        self,
        url: str,
    ) -> List[Document]:
        """
        URL -> Clean -> Chunk
        """

        documents = self.load_url(url)

        documents = self.clean_documents(documents)

        return self.split_documents(documents)

    # --------------------------------------------------------
    # Generic Loader
    # --------------------------------------------------------

    def load(
        self,
        source: str,
    ) -> List[Document]:
        """
        Automatically detect input type.
        """

        if source.lower().startswith(
            (
                "http://",
                "https://",
            )
        ):
            return self.load_url_chunks(source)

        return self.load_pdf_chunks(source)