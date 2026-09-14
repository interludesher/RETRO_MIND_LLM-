import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert data["system"] == "RETROMIND AI KNOWLEDGE CORE"

def test_chat_session_lifecycle():
    # 1. Create session
    create_res = client.post("/api/v1/chat/sessions", json={"title": "Test Matrix Thread"})
    assert create_res.status_code == 200
    session = create_res.json()
    session_id = session["id"]
    assert session["title"] == "Test Matrix Thread"

    # 2. List sessions
    list_res = client.get("/api/v1/chat/sessions")
    assert list_res.status_code == 200
    sessions = list_res.json()
    assert any(s["id"] == session_id for s in sessions)

    # 3. Delete session
    del_res = client.delete(f"/api/v1/chat/sessions/{session_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "DELETED"

def test_upload_and_query_flow():
    # 1. Create a session first
    session_res = client.post("/api/v1/chat/sessions", json={"title": "Ingestion Session"})
    session_id = session_res.json()["id"]

    # 2. Upload sample document
    sample_content = b"RetroMind project spec: Security protocol operates on port 8000 using SQLite database."
    files = {"file": ("project_spec.txt", sample_content, "text/plain")}
    upload_res = client.post("/api/v1/documents/upload", files=files)
    assert upload_res.status_code == 200
    doc_info = upload_res.json()["document"]
    doc_id = doc_info["id"]

    # 3. Query RAG pipeline
    query_payload = {
        "session_id": session_id,
        "query": "What port does the security protocol operate on?"
    }
    query_res = client.post("/api/v1/chat/query", json=query_payload)
    assert query_res.status_code == 200
    data = query_res.json()
    assert "answer" in data
    assert "sources" in data
    assert len(data["sources"]) > 0
    assert data["sources"][0]["filename"] == "project_spec.txt"

    # 4. Fetch session message history
    history_res = client.get(f"/api/v1/chat/sessions/{session_id}/messages")
    assert history_res.status_code == 200
    messages = history_res.json()
    assert len(messages) == 2 # 1 user query + 1 assistant answer

    # Clean up document
    client.delete(f"/api/v1/documents/{doc_id}")
    client.delete(f"/api/v1/chat/sessions/{session_id}")
