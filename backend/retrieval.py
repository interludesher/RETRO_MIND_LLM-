from typing import List, Dict, Any, Tuple, Optional
from backend.vectorstore import VectorStoreManager

class RetrievalEngine:
    """
    RAG Retrieval Engine: filters, formats, and ranks vector store matches
    for accurate context insertion into LLM prompts.
    """

    def __init__(self, vector_store: VectorStoreManager = None, min_similarity_score: float = 0.25):
        self.vector_store = vector_store or VectorStoreManager()
        self.min_similarity_score = min_similarity_score

    def retrieve_context(
        self, 
        query: str, 
        top_k: int = 4, 
        doc_id_filter: Optional[str] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Search vector store for relevant chunks, filter by similarity score threshold,
        and construct formatted prompt context string and citation array.

        Returns:
            Tuple[formatted_context_string, list_of_source_citations]
        """
        raw_chunks = self.vector_store.search_similar_chunks(
            query=query,
            k=top_k,
            doc_id_filter=doc_id_filter
        )

        filtered_chunks = [
            chunk for chunk in raw_chunks 
            if chunk["similarity_score"] >= self.min_similarity_score
        ]

        if not filtered_chunks:
            return "", []

        context_blocks = []
        citations = []

        for idx, chunk in enumerate(filtered_chunks, 1):
            meta = chunk["metadata"]
            filename = meta.get("filename", "Unknown Document")
            page_num = meta.get("page_number", 1)
            chunk_id = chunk["chunk_id"]
            doc_id = meta.get("doc_id", "")

            # Formatted context block for LLM prompt
            header = f"[DOCUMENT: {filename} | PAGE: {page_num} | REF_ID: {chunk_id}]"
            content = chunk["text"].strip()
            context_blocks.append(f"{header}\n{content}")

            # Structured citation for UI frontend display
            citations.append({
                "source_index": idx,
                "doc_id": doc_id,
                "chunk_id": chunk_id,
                "filename": filename,
                "page_number": page_num,
                "similarity_score": chunk["similarity_score"],
                "text_snippet": content[:200] + ("..." if len(content) > 200 else "")
            })

        formatted_context = "\n\n---\n\n".join(context_blocks)
        return formatted_context, citations
