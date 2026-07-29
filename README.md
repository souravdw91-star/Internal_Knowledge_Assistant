# 📚 Internal Knowledge Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangChain-Enabled-1C3C3C?style=for-the-badge" alt="LangChain">
  <img src="https://img.shields.io/badge/Google_Gemini-API-4285F4?style=for-the-badge&logo=google" alt="Google Gemini">
  <img src="https://img.shields.io/badge/Redis-Cache%20%26%20Memory-DC382D?style=for-the-badge&logo=redis" alt="Redis">
  <img src="https://img.shields.io/badge/FAISS-VectorStore-76B900?style=for-the-badge" alt="FAISS">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

---

A production-ready **Retrieval-Augmented Generation (RAG)** application built using **LangChain**, **Google Gemini**, **FAISS**, **Redis**, **FastAPI**, and **Vanilla JavaScript**.

The application allows users to upload PDF documents or index website URLs, builds a local vector database, and answers questions grounded strictly on the uploaded knowledge base instead of relying on the LLM's general knowledge.

---

## 🚀 Features

* 📄 **Resilient PDF Upload**: Batches documents in chunks of 100 with automatic 30s retry loops to safely bypass free-tier Gemini API 429 rate limits.
* 🌐 **Website Indexing**: Ingests and chunks HTML content from web URLs.
* 🤖 **Multi-Purpose Conversation**: Seamlessly handles greetings, small talk, and introductions (e.g. *"Hi my name is Sourav"*) conversationally.
* 🧠 **Direct LLM Fallback**: Chat with the assistant immediately before uploading any document, falling back directly to the LLM when no FAISS index exists.
* 📚 **Vector Store & Grounded RAG**: Strict document QA matching using FAISS Vector Database and Gemini Embeddings.
* 🔍 **Document Synonym Mapping**: Maps queries referring to *"the book"*, *"the PDF"*, or *"the document"* to summarize or answer about the context.
* 🌍 **General Knowledge Fallback**: Falls back to the LLM's general knowledge when queries go beyond document context, with **smart citation filtering** (clearing citations for off-context answers).
* ⚡ **Redis Memory & Cache**: Uses Redis for chat history serialization and prompt caching, featuring a fully functional cache-clear endpoint.
* 💻 **Obsidian Dark Glass UI**: Redesigned from scratch with custom neon gradients, glassmorphic layout elements, and inline **marked.js** markdown rendering.
* 📈 **LangSmith Tracing**: Integrated tracing for latency, token counts, and chain visualizations.

---

## 🏗️ Architecture

```text
                    +-----------------------+
                    |      User Browser     |
                    +----------+------------+
                               |
                               |
                               ▼
                    HTML / CSS / JavaScript
                               |
                               ▼
                      FastAPI REST Backend
                               |
         +---------------------+---------------------+
         |                     |                     |
         ▼                     ▼                     ▼
  Document Loader        Conversation         Redis Cache
 (PDF / Website)            Memory
         |                     |
         +----------+----------+
                    |
                    ▼
           Text Chunking
                    |
                    ▼
 Log-scaled Gemini Embeddings
                    |
                    ▼
             FAISS Vector DB
                    |
                    ▼
        LangChain Retrieval Chain
                    |
                    ▼
         Google Gemini LLM
                    |
                    ▼
             Final Response
```

---

## 📁 Project Structure

```text
Internal_Knowledge_Assistant/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── routes.py
│   ├── rag.py
│   ├── loader.py
│   ├── vectorstore.py
│   ├── prompts.py
│   ├── cache.py
│   ├── memory.py
│   └── utils.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── uploads/
├── faiss_index/
├── .env
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Language** | Python 3.11+ |
| **Backend** | FastAPI |
| **Frontend** | HTML5, CSS3, JavaScript (marked.js) |
| **LLM** | Google Gemini |
| **Framework** | LangChain |
| **Vector Store** | FAISS |
| **Embeddings** | Gemini Embeddings |
| **Memory** | Redis |
| **Cache** | Redis |
| **Monitoring** | LangSmith |
| **PDF Loader** | PyPDF |
| **Web Loader** | BeautifulSoup4 |
| **Environment** | python-dotenv |

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/Internal_Knowledge_Assistants.git
cd Internal_Knowledge_Assistants
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=YOUR_GEMINI_KEY

LANGCHAIN_API_KEY=YOUR_LANGSMITH_KEY
LANGCHAIN_PROJECT=Internal Knowledge Assistant
LANGCHAIN_TRACING_V2=true

REDIS_HOST=localhost
REDIS_PORT=6379

HOST=127.0.0.1
PORT=8000
DEBUG=True
```

> [!WARNING]
> Never commit your `.env` file to version control. Ensure it is listed in your `.gitignore`.

---

## ▶️ Running the Project

### 1. Start Redis
Ensure Redis is running locally:
```bash
redis-server
```

### 2. Run FastAPI Server
```bash
uvicorn backend.app:app --reload
```

* **Backend URL**: [http://localhost:8000](http://localhost:8000)
* **Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 3. Open Frontend Dashboard
Open `frontend/index.html` in your browser, or serve it using Python:
```bash
python -m http.server
```

---

## 📄 Upload & Retrieval Workflows

### Upload & Index Workflow
1. Upload PDF / website URL.
2. Text content is extracted & cleaned.
3. Split into Recursive Character chunks.
4. Gemini embeds chunks in batches of 100 (handles 429 retries).
5. FAISS index created and stored locally.

### Retrieval Pipeline
```text
Question ──► Retriever ──► Relevant Chunks ──► Prompt Template ──► Gemini LLM ──► Answer + Sources
```

---

## 💬 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/api/upload/pdf` | Upload PDF and run chunk indexer |
| **POST** | `/api/upload/url` | Ingest and index Website URL |
| **POST** | `/api/chat` | Chat with RAG (or conversation fallback) |
| **GET** | `/api/session/new` | Start a new session session ID |
| **GET** | `/api/history/{session_id}` | Retrieve chat history of a session |
| **GET** | `/api/health` | Check backend service health status |
| **GET** | `/api/stats` | Retrieve index & token database stats |
| **DELETE** | `/api/cache` | Flush Redis cache |
| **DELETE** | `/api/memory/{session_id}` | Clear conversation memory of session |
| **DELETE** | `/api/knowledge-base` | Purge local FAISS index files |
| **POST** | `/api/reload` | Force reload of FAISS database |

---

## 📊 LangSmith Monitoring

Traces are automatically published for:
* LLM calls and latency.
* Prompt template variables.
* Retriever search efficiency.
* Token count evaluations.

Enable monitoring by checking the environment flags in your `.env`:
```env
LANGCHAIN_TRACING_V2=true
```

---

## 🔒 Security Notes

* API keys are kept strictly local in the `.env` file.
* Uploaded documents are saved under the local `./uploads` directory.
* The FAISS vector database operates completely offline on your disk under `./faiss_index`.
* Redis caches and session histories are volatile and stored locally.

---

## 🚀 Future Enhancements

* Authentication & user account levels.
* Multi-tenant document database isolation.
* Streaming responses using SSE.
* Hybrid keyword-vector search.
* OCR support for scanned documents.
* Dockerized compose configurations.

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 👨‍💻 Author

**Sourav**  
*Data Engineer | AI Engineer*

---

## ⭐ Support

If you found this project helpful:
* ⭐ **Star** the repository
* 🍴 **Fork** the project
* 🐛 **Report** issues or suggest features
