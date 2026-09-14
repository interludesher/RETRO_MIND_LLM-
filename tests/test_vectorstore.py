import pytest
import os
import tempfile
import shutil
from backend.vectorstore import VectorStoreManager

@pytest.fixture
def temp_vector_store():
    temp_dir = tempfile.mkdtemp()
    store = VectorStoreManager(db_path=temp_dir, collection_name="test_collection")
    yield store
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_add_and_search_chunks(temp_vector_store):
    chunks = [
        {
            "id": "chunk_1",
            "text": "The RetroMind system utilizes a 1980s retro aesthetic with synthwave themes.",
            "metadata": {"doc_id": "doc_1", "filename": "specs.txt", "page_number": 1}
        },
        {
            "id": "chunk_2",
            "text": "Database operations are stored in SQLite retromind.db relational file.",
            "metadata": {"doc_id": "doc_2", "filename": "db_guide.txt", "page_number": 1}
        }
    ]

    added = temp_vector_store.add_chunks(chunks)
    assert added == 2

    # Perform similarity search
    results = temp_vector_store.search_similar_chunks("synthwave retro aesthetic", k=2)
    assert len(results) >= 1
    top_match = results[0]
    assert "RetroMind" in top_match["text"]
    assert top_match["metadata"]["doc_id"] == "doc_1"

def test_delete_document_chunks(temp_vector_store):
    chunks = [
        {
            "id": "c1",
            "text": "Document 1 chunk content.",
            "metadata": {"doc_id": "doc_delete_me", "filename": "file1.txt"}
        },
        {
            "id": "c2",
            "text": "Document 2 chunk content.",
            "metadata": {"doc_id": "doc_keep_me", "filename": "file2.txt"}
        }
    ]

    temp_vector_store.add_chunks(chunks)
    deleted_count = temp_vector_store.delete_document_chunks("doc_delete_me")
    assert deleted_count == 1

    remaining = temp_vector_store.search_similar_chunks("chunk content", k=5)
    doc_ids = [r["metadata"]["doc_id"] for r in remaining]
    assert "doc_delete_me" not in doc_ids
    assert "doc_keep_me" in doc_ids
