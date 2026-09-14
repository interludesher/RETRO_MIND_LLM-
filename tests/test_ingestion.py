import pytest
from backend.ingestion import DocumentChunker

def test_extract_txt_document():
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    sample_text = "RetroMind is a RAG application. " * 10
    file_bytes = sample_text.encode('utf-8')
    
    result = chunker.process_document(file_bytes, "test_file.txt", doc_id="doc_test_1")
    
    assert result["doc_id"] == "doc_test_1"
    assert result["filename"] == "test_file.txt"
    assert result["file_type"] == "text"
    assert result["chunk_count"] > 1
    assert len(result["chunks"]) == result["chunk_count"]
    assert result["chunks"][0]["metadata"]["doc_id"] == "doc_test_1"
    assert result["chunks"][0]["metadata"]["page_number"] == 1

def test_empty_document_handling():
    chunker = DocumentChunker()
    empty_bytes = b"   "
    with pytest.raises(ValueError, match="is empty or contains no readable text"):
        chunker.process_document(empty_bytes, "empty.txt")

def test_unsupported_file_format():
    chunker = DocumentChunker()
    dummy_bytes = b"test content"
    with pytest.raises(ValueError, match="Unsupported file format"):
        chunker.process_document(dummy_bytes, "image.png")

def test_chunk_metadata_structure():
    chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    text = "Line 1: High latency systems.\nLine 2: Vector memory database."
    result = chunker.process_document(text.encode('utf-8'), "guide.md")
    
    first_chunk = result["chunks"][0]
    assert "id" in first_chunk
    assert "text" in first_chunk
    assert "metadata" in first_chunk
    assert first_chunk["metadata"]["filename"] == "guide.md"
    assert first_chunk["metadata"]["chunk_index"] == 0
