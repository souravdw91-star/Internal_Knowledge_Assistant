# 📚 Internal Knowledge Assistant

A production-ready **Retrieval-Augmented Generation (RAG)** application built using **LangChain**, **Google Gemini**, **FAISS**, **Redis**, **FastAPI**, and **Vanilla JavaScript**.

The application allows users to upload PDF documents or index website URLs, builds a local vector database, and answers questions grounded strictly on the uploaded knowledge base instead of relying on the LLM's general knowledge.

---

# 🚀 Features

* 📄 Upload PDF documents
* 🌐 Index website URLs
* 🤖 Chat with your own documents
* 🔍 Retrieval-Augmented Generation (RAG)
* 🧠 Google Gemini LLM integration
* 📚 FAISS Vector Database
* ⚡ Redis-powered conversation memory
* 🚀 Redis response caching
* 📖 Source citations
* 💬 Multi-session chat support
* 📊 Health monitoring endpoints
* 📈 LangSmith tracing support
* 🌍 REST API using FastAPI
* 💻 Responsive frontend built with HTML, CSS and JavaScript

---

# 🏗️ Architecture

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
 Google Gemini Embeddings
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

# 📁 Project Structure

```text
Internal_Knowledge_Assistants/
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

# 🛠️ Tech Stack

| Category     | Technology              |
| ------------ | ----------------------- |
| Language     | Python 3.11+            |
| Backend      | FastAPI                 |
| Frontend     | HTML5, CSS3, JavaScript |
| LLM          | Google Gemini           |
| Framework    | LangChain               |
| Vector Store | FAISS                   |
| Embeddings   | Gemini Embeddings       |
| Memory       | Redis                   |
| Cache        | Redis                   |
| Monitoring   | LangSmith               |
| PDF Loader   | PyPDF                   |
| Web Loader   | BeautifulSoup4          |
| Environment  | python-dotenv           |

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/Internal_Knowledge_Assistants.git

cd Internal_Knowledge_Assistants
```

---

## 2. Create Virtual Environment

Windows

```bash
python -m venv .venv
```

Activate

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file.

Example:

```env
GOOGLE_API_KEY=YOUR_GEMINI_KEY

LANGCHAIN_API_KEY=YOUR_LANGSMITH_KEY

LANGCHAIN_PROJECT=Internal Knowledge Assistant

LANGCHAIN_TRACING_V2=true

REDIS_HOST=localhost
REDIS_PORT=6379

HOST=0.0.0.0
PORT=8000
DEBUG=True
```

---

# ▶️ Running the Project

## Start Redis

```bash
redis-server
```

---

## Run FastAPI

```bash
uvicorn backend.app:app --reload
```

Backend URL

```
http://localhost:8000
```

Swagger Documentation

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

## Run Frontend

Open

```
frontend/index.html
```

or serve using

```bash
python -m http.server
```

---

# 📄 Upload Workflow

1. Upload PDF
2. PDF is loaded
3. Text is cleaned
4. Text is chunked
5. Embeddings are generated
6. Stored inside FAISS
7. Retriever is created
8. User asks question
9. Relevant chunks retrieved
10. Gemini generates grounded response

---

# 🌐 Website Workflow

```text
Website URL

      │

      ▼

BeautifulSoup Loader

      ▼

Clean HTML

      ▼

Split into Chunks

      ▼

Embeddings

      ▼

FAISS

      ▼

Retriever

      ▼

Gemini Response
```

---

# 💬 API Endpoints

| Method | Endpoint                | Description           |
| ------ | ----------------------- | --------------------- |
| POST   | `/upload/pdf`           | Upload PDF            |
| POST   | `/upload/url`           | Index Website         |
| POST   | `/chat`                 | Ask Question          |
| GET    | `/session/new`          | Create Session        |
| GET    | `/history/{session_id}` | Conversation History  |
| GET    | `/health`               | Health Check          |
| GET    | `/stats`                | Statistics            |
| DELETE | `/cache`                | Clear Cache           |
| DELETE | `/memory/{session_id}`  | Clear Session Memory  |
| DELETE | `/knowledge-base`       | Delete FAISS Index    |
| POST   | `/reload`               | Reload Knowledge Base |

---

# 🧠 Retrieval Pipeline

```text
Question

   │

   ▼

Retriever

   │

   ▼

Relevant Chunks

   │

   ▼

Prompt Template

   │

   ▼

Gemini LLM

   │

   ▼

Answer + Sources
```

---

# 📊 LangSmith Monitoring

The project supports LangSmith tracing for:

* LLM Calls
* Prompt Execution
* Retriever Performance
* Token Usage
* Latency
* Chain Visualization
* Debugging
* Prompt Evaluation

Enable tracing by setting:

```env
LANGCHAIN_TRACING_V2=true
```

---

# 📦 Core Components

| Module         | Responsibility            |
| -------------- | ------------------------- |
| config.py      | Application configuration |
| loader.py      | Load PDFs and websites    |
| vectorstore.py | FAISS operations          |
| rag.py         | Retrieval pipeline        |
| memory.py      | Redis conversation memory |
| cache.py       | Redis cache               |
| routes.py      | API endpoints             |
| prompts.py     | Prompt templates          |
| utils.py       | Utility helpers           |
| app.py         | FastAPI application       |

---

# 🔒 Security Notes

* API keys are stored in `.env`
* `.env` should never be committed
* Uploaded documents remain local
* Vector database is stored locally
* Redis stores temporary chat history and cached responses

---

# 🚀 Future Enhancements

* Authentication & user management
* Multi-user document isolation
* Streaming LLM responses
* Hybrid search (Keyword + Vector)
* Multiple vector store support
* Document versioning
* OCR support for scanned PDFs
* Docker & Docker Compose deployment
* Cloud storage integration
* Kubernetes deployment

---

# 📸 Screenshots

Add screenshots here after running the application.

```text
docs/
├── home.png
├── upload.png
├── chat.png
└── sources.png
```

---

# 🤝 Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push to your branch.
5. Open a Pull Request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Sourav**

**Data Engineer | AI Engineer | LangChain Developer**

* 12+ years of experience in Data Engineering & ETL
* Passionate about Generative AI, RAG, LangChain, LLM Applications, and Intelligent Data Systems

---

# ⭐ Support

If you found this project helpful:

* ⭐ Star the repository
* 🍴 Fork the project
* 🐛 Report issues
* 💡 Suggest new features

Contributions and feedback are always welcome.
