import uuid
import os
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        RecursiveCharacterTextSplitter = None

from backend.config import settings

class StandaloneTextSplitter:
    """
    Self-contained recursive text splitter fallback.
    Splits text recursively by paragraphs, sentences, words, and characters.
    """
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
        
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            
            if end < text_len:
                # Find best separator to break at
                break_point = -1
                for sep in self.separators:
                    if sep:
                        pos = text.rfind(sep, start, end)
                        if pos > start:
                            break_point = pos + len(sep)
                            break
                if break_point != -1:
                    end = break_point

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start pointer forward considering overlap
            next_start = end - self.chunk_overlap
            if next_start <= start:
                next_start = end
            start = next_start

        return chunks

class DocumentChunker:
    """
    Handles document parsing, text extraction, and text chunking
    for RetroMind RAG Knowledge Base.
    """

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        if RecursiveCharacterTextSplitter is not None:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                is_separator_regex=False
            )
        else:
            self.text_splitter = StandaloneTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )

    def extract_text_from_txt(self, file_content: bytes, filename: str) -> List[Tuple[str, int]]:
        try:
            text = file_content.decode('utf-8')
        except UnicodeDecodeError:
            text = file_content.decode('latin-1', errors='replace')
        
        if not text.strip():
            raise ValueError(f"Document {filename} is empty or contains no readable text.")
            
        return [(text, 1)]

    def extract_text_from_pdf(self, file_content: bytes, filename: str) -> List[Tuple[str, int]]:
        import io
        pdf_file = io.BytesIO(file_content)
        try:
            reader = PdfReader(pdf_file)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF document {filename}: {str(e)}")

        pages_text = []
        for i, page in enumerate(reader.pages):
            extracted = page.extract_text()
            if extracted and extracted.strip():
                pages_text.append((extracted, i + 1))

        if not pages_text:
            raise ValueError(f"PDF Document {filename} contains no extractable text.")

        return pages_text

    def process_document(
        self, 
        file_content: bytes, 
        filename: str, 
        doc_id: str = None
    ) -> Dict[str, Any]:
        if not doc_id:
            doc_id = f"doc_{uuid.uuid4().hex[:12]}"

        file_extension = os.path.splitext(filename)[1].lower()
        file_size = len(file_content)

        if file_extension in ['.txt', '.md', '.markdown', '.log', '.json', '.csv']:
            file_type = "text"
            extracted_pages = self.extract_text_from_txt(file_content, filename)
        elif file_extension == '.pdf':
            file_type = "pdf"
            extracted_pages = self.extract_text_from_pdf(file_content, filename)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Allowed formats: PDF, TXT, MD.")

        all_chunks = []
        chunk_counter = 0

        for page_text, page_num in extracted_pages:
            chunks = self.text_splitter.split_text(page_text)
            for chunk_text in chunks:
                if not chunk_text.strip():
                    continue
                
                chunk_id = f"{doc_id}_chunk_{chunk_counter}"
                chunk_metadata = {
                    "doc_id": doc_id,
                    "chunk_id": chunk_id,
                    "filename": filename,
                    "file_type": file_type,
                    "page_number": page_num,
                    "chunk_index": chunk_counter,
                    "char_count": len(chunk_text)
                }
                
                all_chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "metadata": chunk_metadata
                })
                chunk_counter += 1

        if not all_chunks:
            raise ValueError(f"No valid text chunks generated for document {filename}.")

        return {
            "doc_id": doc_id,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "chunk_count": len(all_chunks),
            "chunks": all_chunks
        }
