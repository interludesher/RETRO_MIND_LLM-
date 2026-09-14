# RetroMind - AI Knowledge Base Assistant
## Late-1980s Synthwave RAG Platform with Groq / Claude AI Integration

---

## 1. Project Overview

**RetroMind** is a production-ready, client-deliverable Retrieval-Augmented Generation (RAG) Knowledge Base Assistant. It allows users to ingest documents (PDF, TXT, MD), convert text into semantic vector embeddings, perform similarity search via ChromaDB, and generate grounded answers using Groq API (or Anthropic Claude API) with strict anti-hallucination guardrails and sourced citations.

The user interface follows a late-1980s retro-computing/synthwave aesthetic featuring neon magenta/cyan visual accents, animated perspective grid floor, CRT scanline overlays, and monospace arcade typography.

---

## 2. Technology Stack

- **Backend**: Python 3.10+ (FastAPI, Pydantic, Uvicorn)
- **LLM Engine**: Groq API (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant`) & Anthropic Claude API (`claude-3-5-sonnet`)
- **Vector DB & Embeddings**: ChromaDB vector store with HuggingFace SentenceTransformers (`all-MiniLM-L6-v2`)
- **Relational Storage**: SQLite 3 (`retromind.db`) for chat session logs, document metadata, and citations
- **Frontend**: React + Vite SPA with custom 1980s synthwave CSS design system
- **Testing**: `pytest` unit & functional test suites

---

## 3. Environment Variables Configuration

Copy `.env.example` to `.env` and supply your credentials:

```bash
# LLM API Keys (Provide Groq or Anthropic Key)
GROQ_API_KEY=your_groq_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LLM Configuration
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.3-70b-versatile
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# RAG & Embedding Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=800
CHUNK_OVERLAP=150
VECTOR_DB_PATH=./data/chroma_db
SQLITE_DB_PATH=./data/retromind.db

# Server Settings
HOST=127.0.0.1
PORT=8000
```

---

## 4. Local Installation & Running Guide

### Step 1: Clone Repository & Setup Python Virtual Environment

```bash
# Create Python virtual environment
python -m venv .venv

# Activate Virtual Environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install Backend Dependencies
pip install -r requirements.txt
```

### Step 2: Setup Frontend Node Dependencies

```bash
cd frontend
npm install
cd ..
```

### Step 3: Launch System Services

#### Start Backend REST Server:
```bash
.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Start Frontend UI Development Server (in separate terminal):
```bash
cd frontend
npm run dev
```
Open your browser at `http://localhost:3000`.

---

## 5. Automated Test Suite Execution

Run the complete 14-test suite covering ingestion, vector storage, retrieval, LLM guardrails, and API endpoints:

```bash
.venv\Scripts\python -m pytest
```

---

## 6. REST API Specification

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/v1/health` | GET | System status and active LLM provider telemetry |
| `POST /api/v1/documents/upload` | POST | Upload and process PDF/TXT file into vector store |
| `GET /api/v1/documents` | GET | List all ingested knowledge base documents |
| `DELETE /api/v1/documents/{doc_id}` | DELETE | Purge document metadata and vector index |
| `POST /api/v1/chat/sessions` | POST | Initialize a new user chat session |
| `GET /api/v1/chat/sessions` | GET | List user chat sessions |
| `GET /api/v1/chat/sessions/{session_id}/messages` | GET | Retrieve message logs for a session |
| `DELETE /api/v1/chat/sessions/{session_id}` | DELETE | Delete session and history |
| `POST /api/v1/chat/query` | POST | RAG query pipeline (retrieval + LLM generation) |

---

