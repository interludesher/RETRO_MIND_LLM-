import pytest
import tempfile
import shutil
from backend.vectorstore import VectorStoreManager
from backend.retrieval import RetrievalEngine

@pytest.fixture
def temp_retrieval_engine():
    temp_dir = tempfile.mkdtemp()
    store = VectorStoreManager(db_path=temp_dir, collection_name="test_retrieval")
    
    chunks = [
        {
            "id": "c1",
            "text": "Cybernetic security protocol v3.4 requires two-factor authentication tokens.",
            "metadata": {"doc_id": "sec_doc", "filename": "security.pdf", "page_number": 4}
        },
        {
            "id": "c2",
            "text": "The retro terminal interface color palette uses neon magenta #ff007f and cyan #00ffff.",
            "metadata": {"doc_id": "ui_doc", "filename": "ui_spec.txt", "page_number": 1}
        }
    ]
    store.add_chunks(chunks)
    engine = RetrievalEngine(vector_store=store, min_similarity_score=0.1)
    yield engine
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_retrieve_matching_context(temp_retrieval_engine):
    context, citations = temp_retrieval_engine.retrieve_context("cybernetic security authentication", top_k=2)
    assert "[DOCUMENT: security.pdf" in context
    assert len(citations) >= 1
    assert citations[0]["filename"] == "security.pdf"
    assert citations[0]["page_number"] == 4

def test_retrieval_no_match_returns_empty(temp_retrieval_engine):
    # Set high threshold so no match is returned
    temp_retrieval_engine.min_similarity_score = 0.99
    context, citations = temp_retrieval_engine.retrieve_context("completely irrelevant query xyz", top_k=2)
    assert context == ""
    assert citations == []
