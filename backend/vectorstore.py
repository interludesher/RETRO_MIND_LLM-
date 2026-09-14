import os
import math
import shutil
import json
import uuid
from typing import List, Dict, Any, Optional
from backend.config import settings

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except ImportError:
    chromadb = None

class SimpleVectorEmbedder:
    """
    Deterministic feature vector embedder producing 384-dimensional
    normalized feature vectors.
    """
    def __init__(self, dim: int = 384):
        self.dim = dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        import hashlib
        words = text.lower().split()
        vec = [0.0] * self.dim
        
        for w in words:
            h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
            idx = h % self.dim
            val = ((h % 1000) + 1.0) / 1000.0
            vec[idx] += val

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        else:
            vec[0] = 1.0

        return vec

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 > 0 and norm2 > 0:
        return dot / (norm1 * norm2)
    return 0.0

class InMemoryVectorStore:
    """
    Fallback high-performance in-memory vector store for isolated unit tests
    or lightweight environments.
    """
    def __init__(self):
        self.records = []

    def add(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]):
        for i in range(len(ids)):
            # Remove any existing record with same ID
            self.records = [r for r in self.records if r["id"] != ids[i]]
            self.records.append({
                "id": ids[i],
                "document": documents[i],
                "metadata": metadatas[i],
                "embedding": embeddings[i]
            })

    def query(self, query_embeddings: List[List[float]], n_results: int = 4, where: Optional[Dict[str, Any]] = None, include: Optional[List[str]] = None):
        q_emb = query_embeddings[0]
        scored = []
        for r in self.records:
            if where:
                match = True
                for k, v in where.items():
                    if r["metadata"].get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            sim = cosine_similarity(q_emb, r["embedding"])
            dist = max(0.0, 1.0 - sim)
            scored.append((dist, r))

        scored.sort(key=lambda x: x[0])
        top_k = scored[:n_results]

        ids = [item[1]["id"] for item in top_k]
        docs = [item[1]["document"] for item in top_k]
        metas = [item[1]["metadata"] for item in top_k]
        dists = [item[0] for item in top_k]

        return {
            "ids": [ids],
            "documents": [docs],
            "metadatas": [metas],
            "distances": [dists]
        }

    def get(self, where: Dict[str, Any]):
        matched = []
        for r in self.records:
            match = True
            for k, v in where.items():
                if r["metadata"].get(k) != v:
                    match = False
                    break
            if match:
                matched.append(r["id"])
        return {"ids": matched}

    def delete(self, ids: List[str]):
        id_set = set(ids)
        self.records = [r for r in self.records if r["id"] not in id_set]

class VectorStoreManager:
    """
    Manages vector embeddings and document chunk storage in ChromaDB
    (or fallback vector memory store) for RetroMind RAG Knowledge Base.
    """

    def __init__(self, db_path: str = None, collection_name: str = "retromind_chunks"):
        self.db_path = db_path or settings.VECTOR_DB_PATH
        self.collection_name = collection_name
        os.makedirs(self.db_path, exist_ok=True)

        # 1. Initialize Embeddings
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embedding_function = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL
            )
        except Exception:
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings
                self.embedding_function = HuggingFaceEmbeddings(
                    model_name=settings.EMBEDDING_MODEL
                )
            except Exception:
                self.embedding_function = SimpleVectorEmbedder()

        # 2. Initialize Vector DB Client
        if chromadb is not None:
            try:
                self.chroma_client = chromadb.PersistentClient(
                    path=self.db_path,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
                self.collection = self.chroma_client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"description": "RetroMind Knowledge Vector Store"}
                )
            except Exception:
                self.chroma_client = None
                self.collection = InMemoryVectorStore()
        else:
            self.chroma_client = None
            self.collection = InMemoryVectorStore()

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        if not chunks:
            return 0

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk["id"])
            documents.append(chunk["text"])
            meta = {k: v for k, v in chunk["metadata"].items() if v is not None}
            metadatas.append(meta)

        embeddings = self.embedding_function.embed_documents(documents)

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        return len(ids)

    def search_similar_chunks(
        self, 
        query: str, 
        k: int = 4, 
        doc_id_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not query.strip():
            return []

        query_embedding = self.embedding_function.embed_query(query)
        
        where_filter = None
        if doc_id_filter:
            where_filter = {"doc_id": doc_id_filter}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        matching_chunks = []
        if results and results.get("ids") and results["ids"][0]:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for i in range(len(ids)):
                dist = float(distances[i])
                sim_score = round(1.0 / (1.0 + dist), 4)
                matching_chunks.append({
                    "chunk_id": ids[i],
                    "text": docs[i],
                    "metadata": metas[i],
                    "distance": dist,
                    "similarity_score": sim_score
                })

        return matching_chunks

    def delete_document_chunks(self, doc_id: str) -> int:
        try:
            existing = self.collection.get(where={"doc_id": doc_id})
            if existing and existing.get("ids"):
                ids_to_delete = existing["ids"]
                self.collection.delete(ids=ids_to_delete)
                return len(ids_to_delete)
            return 0
        except Exception:
            return 0

    def reset_collection(self):
        if self.chroma_client:
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name
            )
        else:
            self.collection = InMemoryVectorStore()
