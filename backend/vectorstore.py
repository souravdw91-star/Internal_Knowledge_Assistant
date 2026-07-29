"""
vectorstore.py

Creates, updates, loads and searches the FAISS vector database.
"""

from pathlib import Path
from typing import List, Optional
import time

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from backend.config import (
    GOOGLE_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    FAISS_INDEX_PATH,
    TOP_K,
)
from backend.utils import LOGGER


class VectorStoreManager:
    """Handles all FAISS vector store operations."""

    def __init__(self):

        self.index_path = Path(FAISS_INDEX_PATH)

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=GEMINI_EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY,
        )

        self.vectorstore: Optional[FAISS] = None

    # -----------------------------------------------------
    # Create Vector Store
    # -----------------------------------------------------

    def create(self, documents: List[Document]) -> FAISS:
        """
        Create a new FAISS index.
        """

        LOGGER.info("Creating FAISS index...")

        batch_size = 100
        first_batch = documents[:batch_size]

        # Initialize FAISS with first batch (with retry)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.vectorstore = FAISS.from_documents(
                    documents=first_batch,
                    embedding=self.embeddings,
                )
                break
            except Exception as ex:
                err_str = str(ex).lower()
                if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
                    if attempt < max_retries - 1:
                        LOGGER.warning(f"Rate limit hit during index creation. Retrying in 30 seconds (Attempt {attempt+1}/{max_retries})...")
                        time.sleep(30.0)
                        continue
                raise

        remaining = documents[batch_size:]
        if remaining:
            LOGGER.info(f"Adding remaining {len(remaining)} chunks in batches of {batch_size}...")
            for i in range(0, len(remaining), batch_size):
                time.sleep(1.0)
                batch_docs = remaining[i:i+batch_size]
                
                # Retry loop for batch addition
                for attempt in range(max_retries):
                    try:
                        self.vectorstore.add_documents(batch_docs)
                        break
                    except Exception as ex:
                        err_str = str(ex).lower()
                        if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
                            if attempt < max_retries - 1:
                                LOGGER.warning(f"Rate limit hit during batch addition. Retrying in 30 seconds (Attempt {attempt+1}/{max_retries})...")
                                time.sleep(30.0)
                                continue
                        raise

        self.save()

        LOGGER.info("FAISS index created successfully.")

        return self.vectorstore

    # -----------------------------------------------------
    # Add Documents
    # -----------------------------------------------------

    def add_documents(
        self,
        documents: List[Document],
    ):
        """
        Add new documents into the existing FAISS index.
        """

        if self.vectorstore is None:

            self.load()

        if self.vectorstore is None:

            self.create(documents)

            return

        LOGGER.info(
            f"Adding {len(documents)} chunks to vector database in batches..."
        )

        batch_size = 100
        max_retries = 3
        for i in range(0, len(documents), batch_size):
            if i > 0:
                time.sleep(1.0)
            batch_docs = documents[i:i+batch_size]
            
            # Retry loop for batch addition
            for attempt in range(max_retries):
                try:
                    self.vectorstore.add_documents(batch_docs)
                    break
                except Exception as ex:
                    err_str = str(ex).lower()
                    if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
                        if attempt < max_retries - 1:
                            LOGGER.warning(f"Rate limit hit during batch addition. Retrying in 30 seconds (Attempt {attempt+1}/{max_retries})...")
                            time.sleep(30.0)
                            continue
                    raise

        self.save()

        LOGGER.info("Vector database updated.")

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    def save(self):
        """
        Save FAISS index locally.
        """

        if self.vectorstore is None:
            return

        self.index_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.vectorstore.save_local(
            folder_path=str(self.index_path)
        )

        LOGGER.info(
            f"Vector database saved to {self.index_path}"
        )

    # -----------------------------------------------------
    # Load
    # -----------------------------------------------------

    def load(self) -> Optional[FAISS]:
        """
        Load an existing FAISS index.
        """

        if not self.exists():

            LOGGER.warning("FAISS index not found.")

            return None

        try:

            self.vectorstore = FAISS.load_local(
                folder_path=str(self.index_path),
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True,
            )

            LOGGER.info("FAISS index loaded.")

            return self.vectorstore

        except Exception as e:

            LOGGER.exception(e)

            return None

    # -----------------------------------------------------
    # Delete
    # -----------------------------------------------------

    def delete_index(self):
        """
        Delete the local FAISS index.
        """

        if not self.index_path.exists():
            return

        for file in self.index_path.iterdir():
            file.unlink()

        LOGGER.info("FAISS index deleted.")

        self.vectorstore = None

    # -----------------------------------------------------
    # Similarity Search
    # -----------------------------------------------------

    def similarity_search(
        self,
        query: str,
        k: int = TOP_K,
    ) -> List[Document]:
        """
        Perform similarity search.
        """

        if self.vectorstore is None:

            self.load()

        if self.vectorstore is None:

            raise RuntimeError(
                "Vector database has not been created."
            )

        return self.vectorstore.similarity_search(
            query=query,
            k=k,
        )

    # -----------------------------------------------------
    # Similarity Search With Score
    # -----------------------------------------------------

    def similarity_search_with_score(
        self,
        query: str,
        k: int = TOP_K,
    ):
        """
        Retrieve documents with similarity score.
        """

        if self.vectorstore is None:

            self.load()

        if self.vectorstore is None:

            raise RuntimeError(
                "Vector database has not been created."
            )

        return self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
        )

    # -----------------------------------------------------
    # Retriever
    # -----------------------------------------------------

    def as_retriever(
        self,
        k: int = TOP_K,
    ):
        """
        Return LangChain Retriever.
        """

        if self.vectorstore is None:

            self.load()

        if self.vectorstore is None:

            raise RuntimeError(
                "Vector database has not been created."
            )

        return self.vectorstore.as_retriever(
            search_kwargs={
                "k": k,
            }
        )

    # -----------------------------------------------------
    # Document Count
    # -----------------------------------------------------

    def document_count(self) -> int:
        """
        Return total number of indexed chunks.
        """

        if self.vectorstore is None:

            self.load()

        if self.vectorstore is None:
            return 0

        try:

            return self.vectorstore.index.ntotal

        except Exception:

            return 0

    # -----------------------------------------------------
    # Check Index
    # -----------------------------------------------------

    def exists(self) -> bool:
        """
        Check whether a FAISS index exists.
        """

        return (
            self.index_path.exists()
            and (self.index_path / "index.faiss").exists()
            and (self.index_path / "index.pkl").exists()
        )

    # -----------------------------------------------------
    # Reset
    # -----------------------------------------------------

    def reset(self):
        """
        Remove current vector database and start fresh.
        """

        self.delete_index()

        self.vectorstore = None