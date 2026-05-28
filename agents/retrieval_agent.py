"""
agents/retrieval_agent.py — Semantic retrieval agent
Responsibility: Find the most relevant chunks for a given query.
"""
from typing import List, Dict, Optional
from core.embeddings import EmbeddingEngine
from core.vector_store import VectorStore
from config import config
from utils.logger import get_logger

log = get_logger("retrieval_agent")


class RetrievalAgent:
    """
    Agent that performs semantic search over the vector store.
    Returns the most relevant document chunks for a query.
    """

    def __init__(
        self,
        embedding_engine: EmbeddingEngine,
        vector_store: VectorStore,
        top_k: int = config.TOP_K_RESULTS,
        threshold: float = config.SIMILARITY_THRESHOLD,
    ):
        self.embedder = embedding_engine
        self.vector_store = vector_store
        self.top_k = top_k
        self.threshold = threshold

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.
        Returns list of {text, metadata, score} sorted by relevance.
        """
        if not self.vector_store.is_ready:
            log.warning("Vector store is empty. Please ingest a document first.")
            return []

        if not query.strip():
            return []

        k = top_k or self.top_k

        # 1. Embed the query
        log.debug(f"Embedding query: '{query[:80]}...'")
        query_embedding = self.embedder.embed_query(query)

        if len(query_embedding) == 0:
            log.error("Failed to embed query.")
            return []

        # 2. Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=k,
            threshold=self.threshold,
        )

        # 3. Sort by score descending
        results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)

        log.info(f"Retrieved {len(results)} relevant chunks for query: '{query[:50]}'")

        # Log scores for debugging
        for i, r in enumerate(results):
            log.debug(f"  Chunk {i+1}: score={r.get('score', 0):.3f} | {r.get('text', '')[:60]}...")

        return results

    def retrieve_for_summary(self, max_chunks: int = 20) -> List[Dict]:
        """
        Retrieve a representative sample of chunks for document summarization.
        Spreads selection across the document (beginning, middle, end).
        """
        if not self.vector_store.is_ready:
            return []

        total = self.vector_store.chunk_count
        chunks = self.vector_store.chunks

        if total <= max_chunks:
            return chunks

        # Evenly sample across the document
        step = total // max_chunks
        sampled = [chunks[i] for i in range(0, total, step)][:max_chunks]

        log.info(f"Sampled {len(sampled)} chunks for summarization (from {total} total)")
        return sampled

    def build_context_string(
        self,
        chunks: List[Dict],
        max_chars: int = 6000,
    ) -> str:
        """
        Build a formatted context string from retrieved chunks.
        Respects max_chars to avoid LLM token limits.
        """
        if not chunks:
            return ""

        context_parts = []
        total_chars = 0

        for i, chunk in enumerate(chunks, 1):
            text = chunk.get("text", "").strip()
            meta = chunk.get("metadata", {})
            source = meta.get("source", "Document")
            page = meta.get("page", "")
            score = chunk.get("score", 0)

            page_info = f", p.{page}" if page else ""
            header = f"[Chunk {i} | {source}{page_info} | relevance: {score:.2f}]"
            chunk_str = f"{header}\n{text}"

            if total_chars + len(chunk_str) > max_chars:
                # Add partial if we have space
                remaining = max_chars - total_chars
                if remaining > 200:
                    context_parts.append(chunk_str[:remaining] + "...")
                break

            context_parts.append(chunk_str)
            total_chars += len(chunk_str)

        return "\n\n---\n\n".join(context_parts)
