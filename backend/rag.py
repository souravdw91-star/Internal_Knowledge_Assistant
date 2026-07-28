from langchain_community.vectorstores import FAISS
from langchain_google_genai import (
    GoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain.prompts import ChatPromptTemplate

from backend.config import GOOGLE_API_KEY


def ask_question(question: str):

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2-preview",
        google_api_key=GOOGLE_API_KEY
    )

    vector_store = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 5}
    )

    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    prompt = ChatPromptTemplate.from_template(
            """
            You are an enterprise Internal Knowledge Assistant.

            Rules:

            1. Answer ONLY using the provided context.
            2. Do not use outside knowledge.
            3. If the answer isn't present, say:
            "I couldn't find this information in the uploaded documents."
            4. Keep answers concise but complete.
            5. If appropriate, use bullet points.
            6. Do not fabricate facts.

            Context:
            {context}

            Question:
            {question}

            Answer:
            """
            )

    chain = (
        prompt
        | GoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GOOGLE_API_KEY
        )
    )

    response = chain.invoke(
        {
            "context": context,
            "question": question
        }
    )

    return response, docs