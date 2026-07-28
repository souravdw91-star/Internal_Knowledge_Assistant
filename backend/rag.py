"""
rag.py

Retrieval-Augmented Generation pipeline.
"""

from typing import List, Dict

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.config import (
    GOOGLE_API_KEY,
    GEMINI_CHAT_MODEL,
    TEMPERATURE,
    TOP_P,
    MAX_OUTPUT_TOKENS,
    TOP_K,
)

from backend.prompts import (
    RAG_PROMPT,
    NO_CONTEXT_RESPONSE,
)

from backend.vectorstore import VectorStoreManager
from backend.utils import LOGGER


class RAGPipeline:
    """Main Retrieval-Augmented Generation pipeline."""

    def __init__(self):

        self.vectorstore = VectorStoreManager()

        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_CHAT_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )

        self.chain = None

    # ---------------------------------------------------------
    # Load Retriever
    # ---------------------------------------------------------

    def load_retriever(self):

        retriever = self.vectorstore.as_retriever(
            k=TOP_K
        )

        return retriever

    # ---------------------------------------------------------
    # Build RAG Chain
    # ---------------------------------------------------------

    def build_chain(self):

        retriever = self.load_retriever()

        document_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=RAG_PROMPT,
        )

        self.chain = create_retrieval_chain(
            retriever,
            document_chain,
        )

        LOGGER.info("RAG chain initialized.")

        return self.chain

    # ---------------------------------------------------------
    # Ensure Chain Exists
    # ---------------------------------------------------------

    def initialize(self):

        if self.chain is None:

            self.build_chain()

    # ---------------------------------------------------------
    # Retrieve Relevant Documents
    # ---------------------------------------------------------

    def retrieve_documents(
        self,
        question: str,
    ) -> List[Document]:

        retriever = self.load_retriever()

        documents = retriever.invoke(question)

        LOGGER.info(
            f"{len(documents)} document chunks retrieved."
        )

        return documents

    # ---------------------------------------------------------
    # Extract Sources
    # ---------------------------------------------------------

    @staticmethod
    def extract_sources(
        documents: List[Document],
    ) -> List[Dict]:

        sources = []

        seen = set()

        for doc in documents:

            metadata = doc.metadata

            source = metadata.get(
                "source",
                "Unknown"
            )

            page = metadata.get(
                "page",
                "-"
            )

            key = (source, page)

            if key in seen:
                continue

            seen.add(key)

            sources.append(
                {
                    "source": source,
                    "page": page,
                }
            )

        return sources

    # ---------------------------------------------------------
    # Check Knowledge Base
    # ---------------------------------------------------------

    def knowledge_base_exists(self) -> bool:

        return self.vectorstore.exists()

    # ---------------------------------------------------------
    # Number of Indexed Chunks
    # ---------------------------------------------------------

    def chunk_count(self) -> int:

        return self.vectorstore.document_count()

        # ---------------------------------------------------------
    # Query RAG Chain
    # ---------------------------------------------------------

    def ask(
        self,
        question: str,
    ) -> Dict:
        """
        Execute a RAG query.

        Returns
        -------
        {
            "answer": str,
            "sources": list
        }
        """

        self.initialize()

        if not self.knowledge_base_exists():

            return {
                "answer": "No knowledge base found. Please upload a document first.",
                "sources": [],
            }

        documents = self.retrieve_documents(question)

        if len(documents) == 0:

            return {
                "answer": NO_CONTEXT_RESPONSE,
                "sources": [],
            }

        response = self.chain.invoke(
            {
                "input": question
            }
        )

        answer = response.get(
            "answer",
            NO_CONTEXT_RESPONSE,
        )

        sources = self.extract_sources(
            documents
        )

        return {
            "answer": answer.strip(),
            "sources": sources,
        }

    # ---------------------------------------------------------
    # Search Only
    # ---------------------------------------------------------

    def search(
        self,
        question: str,
    ) -> List[Document]:
        """
        Returns retrieved chunks without invoking the LLM.
        Useful for debugging and LangSmith tracing.
        """

        return self.retrieve_documents(question)

    # ---------------------------------------------------------
    # Similarity Search With Score
    # ---------------------------------------------------------

    def search_with_score(
        self,
        question: str,
    ):
        """
        Returns retrieved chunks along with similarity scores.
        """

        return self.vectorstore.similarity_search_with_score(
            query=question,
            k=TOP_K,
        )

    # ---------------------------------------------------------
    # Preview Retrieved Context
    # ---------------------------------------------------------

    def preview_context(
        self,
        question: str,
    ) -> str:
        """
        Returns the retrieved context as plain text.
        Useful for debugging prompts.
        """

        documents = self.retrieve_documents(question)

        context = []

        for doc in documents:

            context.append(doc.page_content)

        return "\n\n".join(context)

    # ---------------------------------------------------------
    # Source Summary
    # ---------------------------------------------------------

    def source_summary(
        self,
        question: str,
    ) -> List[str]:
        """
        Returns only source names.
        """

        documents = self.retrieve_documents(question)

        sources = []

        seen = set()

        for doc in documents:

            source = doc.metadata.get(
                "source",
                "Unknown"
            )

            if source not in seen:

                seen.add(source)

                sources.append(source)

        return sources

    # ---------------------------------------------------------
    # Health Check
    # ---------------------------------------------------------

    def health(self) -> Dict:
        """
        Returns pipeline status.
        """

        return {
            "model": GEMINI_CHAT_MODEL,
            "vector_db": self.knowledge_base_exists(),
            "indexed_chunks": self.chunk_count(),
            "chain_ready": self.chain is not None,
        }

        # ---------------------------------------------------------
    # Chat Session
    # ---------------------------------------------------------

    def chat(
        self,
        question: str,
        memory=None,
        cache=None,
        session_id: str | None = None,
    ) -> Dict:
        """
        Chat entry point with optional Redis cache and memory.
        """

        try:

            # -------------------------
            # Cache Lookup
            # -------------------------

            if cache is not None:

                cached_response = cache.get(question)

                if cached_response:

                    LOGGER.info("Response served from cache.")

                    return cached_response

            # -------------------------
            # Query RAG
            # -------------------------

            response = self.ask(question)

            # -------------------------
            # Memory
            # -------------------------

            if memory is not None and session_id:

                memory.add_message(
                    session_id=session_id,
                    role="user",
                    content=question,
                )

                memory.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=response["answer"],
                )

            # -------------------------
            # Cache Save
            # -------------------------

            if cache is not None:

                cache.set(
                    question,
                    response,
                )

            return response

        except Exception as e:

            LOGGER.exception(e)

            return {
                "answer": "An unexpected error occurred while generating the response.",
                "sources": [],
            }

    # ---------------------------------------------------------
    # Reset Pipeline
    # ---------------------------------------------------------

    def reset(self):
        """
        Reset the current RAG chain.
        """

        self.chain = None

        LOGGER.info("RAG pipeline reset.")

    # ---------------------------------------------------------
    # Reload
    # ---------------------------------------------------------

    def reload(self):
        """
        Reload the vector database and rebuild the chain.
        """

        self.vectorstore.load()

        self.build_chain()

        LOGGER.info("RAG pipeline reloaded.")

    # ---------------------------------------------------------
    # Index Documents
    # ---------------------------------------------------------

    def index_documents(
        self,
        documents: List[Document],
    ):
        """
        Index newly loaded document chunks.
        """

        if not documents:
            return

        if self.vectorstore.exists():

            self.vectorstore.add_documents(
                documents
            )

        else:

            self.vectorstore.create(
                documents
            )

        self.reload()

    # ---------------------------------------------------------
    # Delete Knowledge Base
    # ---------------------------------------------------------

    def clear_knowledge_base(self):
        """
        Delete the FAISS index.
        """

        self.vectorstore.reset()

        self.reset()

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def stats(self):

        return {

            "indexed_chunks": self.chunk_count(),

            "knowledge_base": self.knowledge_base_exists(),

            "model": GEMINI_CHAT_MODEL,

            "retriever_k": TOP_K,

        }


# =========================================================
# Singleton
# =========================================================

rag_pipeline = RAGPipeline()