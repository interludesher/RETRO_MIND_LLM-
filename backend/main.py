from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os

from backend.config import settings
from backend.ingestion import DocumentChunker
from backend.vectorstore import VectorStoreManager
from backend.retrieval import RetrievalEngine
from backend.llm import LLMEngine
from backend.database import DatabaseManager

app = FastAPI(
    title="RetroMind RAG AI Knowledge Base API",
    description="Late-1980s Retro AI Knowledge Base Assistant with Vector Search and Grounded LLM",
    version="1.0.0"
)

# Enable CORS for frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared Service Singletons
db_manager = DatabaseManager()
chunker = DocumentChunker()
vector_store = VectorStoreManager()
retrieval_engine = RetrievalEngine(vector_store=vector_store)
llm_engine = LLMEngine()

# --- Pydantic API Models ---

class SessionCreateRequest(BaseModel):
    title: Optional[str] = "Retro Matrix Session"

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str

class QueryRequest(BaseModel):
    session_id: str = Field(..., description="ID of active chat session")
    query: str = Field(..., description="User question or query text")
    doc_id_filter: Optional[str] = Field(None, description="Optional document filter")

class QueryResponse(BaseModel):
    session_id: str
    message_id: str
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    timestamp: str

# --- REST Endpoints ---

@app.get("/api/v1/health")
def health_check():
    """
    System status and component telemetry check.
    """
    return {
        "status": "ONLINE",
        "system": "RETROMIND AI KNOWLEDGE CORE",
        "llm_provider": settings.LLM_PROVIDER,
        "vector_store": "ChromaDB Persistent Store",
        "database": "SQLite Relational Storage"
    }

@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload, chunk, embed, and index a PDF or TXT document into RetroMind knowledge matrix.
    """
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="Invalid uploaded file name.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        # Step 1: Chunk document text
        processed = chunker.process_document(content, filename)
        doc_id = processed["doc_id"]

        # Step 2: Index chunks in ChromaDB
        indexed_count = vector_store.add_chunks(processed["chunks"])

        # Step 3: Record metadata in SQLite
        doc_record = db_manager.insert_document(
            doc_id=doc_id,
            filename=processed["filename"],
            file_type=processed["file_type"],
            file_size=processed["file_size"],
            chunk_count=indexed_count
        )

        return {
            "status": "SUCCESS",
            "message": f"Document {filename} ingested into knowledge matrix.",
            "document": doc_record
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")

@app.get("/api/v1/documents")
def list_documents():
    """
    List all ingested knowledge documents.
    """
    return db_manager.list_documents()

@app.delete("/api/v1/documents/{doc_id}")
def delete_document(doc_id: str):
    """
    Delete document metadata and remove all associated vectors from ChromaDB.
    """
    doc = db_manager.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found.")

    # Remove from vector store
    vector_store.delete_document_chunks(doc_id)

    # Remove from SQLite
    db_manager.delete_document(doc_id)

    return {
        "status": "DELETED",
        "doc_id": doc_id,
        "message": f"Document {doc.get('filename')} purged from memory matrix."
    }

@app.post("/api/v1/chat/sessions", response_model=SessionResponse)
def create_chat_session(payload: SessionCreateRequest):
    """
    Initialize a new user chat session.
    """
    title = payload.title or "Retro Matrix Session"
    session = db_manager.create_session(title=title)
    return session

@app.get("/api/v1/chat/sessions", response_model=List[SessionResponse])
def list_chat_sessions():
    """
    Retrieve all user chat sessions.
    """
    return db_manager.list_sessions()

@app.get("/api/v1/chat/sessions/{session_id}/messages")
def get_session_messages(session_id: str):
    """
    Fetch message log history for a specific chat session.
    """
    session = db_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    return db_manager.get_session_messages(session_id)

@app.delete("/api/v1/chat/sessions/{session_id}")
def delete_chat_session(session_id: str):
    """
    Delete chat session and associated messages.
    """
    session = db_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    db_manager.delete_session(session_id)
    return {"status": "DELETED", "session_id": session_id}

@app.post("/api/v1/chat/query", response_model=QueryResponse)
def query_rag_pipeline(payload: QueryRequest):
    """
    RAG Pipeline Core Endpoint:
    1. Validate session existence.
    2. Save user query message to SQLite history.
    3. Retrieve relevant document context from ChromaDB.
    4. Generate grounded LLM response (Groq/Claude).
    5. Save assistant answer and citations to SQLite history.
    6. Return grounded response with citations.
    """
    session = db_manager.get_session(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {payload.session_id} not found.")

    query_text = payload.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    # 1. Save user query message
    db_manager.add_message(
        session_id=payload.session_id,
        role="user",
        content=query_text
    )

    # 2. Retrieve prior session chat history for continuity
    history = db_manager.get_session_messages(payload.session_id)

    # 3. Perform semantic retrieval from ChromaDB
    context, citations = retrieval_engine.retrieve_context(
        query=query_text,
        top_k=4,
        doc_id_filter=payload.doc_id_filter
    )

    # 4. Generate grounded LLM response
    answer = llm_engine.generate_answer(
        query=query_text,
        context=context,
        chat_history=history
    )

    # 5. Save assistant response with citations to SQLite
    assistant_msg = db_manager.add_message(
        session_id=payload.session_id,
        role="assistant",
        content=answer,
        sources=citations
    )

    return {
        "session_id": payload.session_id,
        "message_id": assistant_msg["id"],
        "query": query_text,
        "answer": answer,
        "sources": citations,
        "timestamp": assistant_msg["timestamp"]
    }
