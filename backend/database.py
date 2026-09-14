import sqlite3
import json
import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.config import settings

class DatabaseManager:
    """
    SQLite Relational Storage Manager for RetroMind.
    Stores document metadata, chat session logs, and message histories.
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.SQLITE_DB_PATH
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """
        Initialize database schema tables.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Documents Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                chunk_count INTEGER NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Chat Sessions Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Chat Messages Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources_json TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
            );
            """)
            conn.commit()

    # --- Document Metadata Operations ---

    def insert_document(self, doc_id: str, filename: str, file_type: str, file_size: int, chunk_count: int) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO documents (id, filename, file_type, file_size, chunk_count, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_id, filename, file_type, file_size, chunk_count, now))
            conn.commit()
            return {
                "id": doc_id,
                "filename": filename,
                "file_type": file_type,
                "file_size": file_size,
                "chunk_count": chunk_count,
                "uploaded_at": now
            }

    def list_documents(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_document(self, doc_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
            return cursor.rowcount > 0

    # --- Chat Session & History Operations ---

    def create_session(self, title: str = "Retro Session") -> Dict[str, Any]:
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_sessions (id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (session_id, title, now, now))
            conn.commit()
            return {
                "id": session_id,
                "title": title,
                "created_at": now,
                "updated_at": now
            }

    def list_sessions(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat_sessions ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_session(self, session_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0

    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        sources: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        sources_json = json.dumps(sources) if sources else None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_messages (id, session_id, role, content, sources_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, session_id, role, content, sources_json, now))

            # Update session updated_at timestamp
            cursor.execute("UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (now, session_id))
            conn.commit()

            return {
                "id": message_id,
                "session_id": session_id,
                "role": role,
                "content": content,
                "sources": sources or [],
                "timestamp": now
            }

    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC
            """, (session_id,))
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                msg = dict(row)
                msg["sources"] = json.loads(msg["sources_json"]) if msg.get("sources_json") else []
                msg.pop("sources_json", None)
                messages.append(msg)
            return messages
