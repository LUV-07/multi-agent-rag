import os
import json
import pickle
from typing import List, Dict, Tuple, Optional
import numpy as np
from config import config
from utils.logger import get_logger

log = get_logger("vector_store")


class VectorStore:
    """
    Local FAISS vector store for storing and retrieving document chunks.
    Persists to disk automatically.
    """

    def __init__(self, store_path: str = config.VECTOR_STORE_PATH):
        self.store_path = store_path
        self.index = None
        self.chunks: List[Dict] = []       # Raw chunk data
        self.embeddings: Optional[np.ndarray] = None
        self._dim: Optional[int] = None
        os.makedirs(store_path, exist_ok=True)

    def add_chunks(self, chunks: List[Dict], embeddings: np.ndarray) -> None:
        """
        Add chunks and their embeddings to the store.
        chunks: list of {text, metadata} dicts
        embeddings: numpy array of shape (n_chunks, dim)
        """
        try:
            import faiss
        except ImportError:
            raise ImportError("Install FAISS: pip install faiss-cpu")

        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) count mismatch.")

        embeddings = embeddings.astype(np.float32)
        dim = embeddings.shape[1]

        if self.index is None:
            # Create new index
            self._dim = dim
            self.index = faiss.IndexFlatIP(dim)  # Inner product (for normalized vecs = cosine sim)
            log.info(f"Created new FAISS index (dim={dim})")
        elif dim != self._dim:
            raise ValueError(f"Embedding dimension mismatch: store={self._dim}, new={dim}")

        self.index.add(embeddings)
        self.chunks.extend(chunks)

        # Track embeddings for optional reranking
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])

        log.info(f"Added {len(chunks)} chunks. Total: {len(self.chunks)}")

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = config.TOP_K_RESULTS,
        threshold: float = config.SIMILARITY_THRESHOLD,
    ) -> List[Dict]:
        """
        Search for the most similar chunks to a query embedding.
        Returns list of {text, metadata, score} dicts.
        """
        if self.index is None or len(self.chunks) == 0:
            log.warning("Vector store is empty — no results.")
            return []

        query = query_embedding.astype(np.float32).reshape(1, -1)
        k = min(top_k, len(self.chunks))

        scores, indices = self.index.search(query, k)
        scores = scores[0]
        indices = indices[0]

        results = []
        for score, idx in zip(scores, indices):
            if idx < 0 or idx >= len(self.chunks):
                continue
            if float(score) < threshold:
                log.debug(f"Chunk {idx} below threshold ({score:.3f} < {threshold})")
                continue

            chunk = self.chunks[idx].copy()
            chunk["score"] = float(score)
            results.append(chunk)

        log.info(f"Retrieved {len(results)} chunks above threshold ({threshold})")
        return results

    def clear(self) -> None:
        """Clear all stored chunks and index."""
        self.index = None
        self.chunks = []
        self.embeddings = None
        self._dim = None
        log.info("Vector store cleared.")

    def save(self, name: str = "default") -> None:
        """Persist the vector store to disk."""
        try:
            import faiss
        except ImportError:
            return

        if self.index is None:
            return

        index_path = os.path.join(self.store_path, f"{name}.index")
        chunks_path = os.path.join(self.store_path, f"{name}.chunks.pkl")

        faiss.write_index(self.index, index_path)
        with open(chunks_path, "wb") as f:
            pickle.dump({"chunks": self.chunks, "dim": self._dim}, f)

        log.info(f"Vector store saved to {self.store_path}/{name}.*")

    def load(self, name: str = "default") -> bool:
        """Load vector store from disk. Returns True if successful."""
        try:
            import faiss
        except ImportError:
            return False

        index_path = os.path.join(self.store_path, f"{name}.index")
        chunks_path = os.path.join(self.store_path, f"{name}.chunks.pkl")

        if not os.path.exists(index_path) or not os.path.exists(chunks_path):
            return False

        self.index = faiss.read_index(index_path)
        with open(chunks_path, "rb") as f:
            data = pickle.load(f)
            self.chunks = data["chunks"]
            self._dim = data["dim"]

        log.info(f"Loaded vector store: {len(self.chunks)} chunks from {self.store_path}/{name}.*")
        return True

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)

    @property
    def is_ready(self) -> bool:
        return self.index is not None and len(self.chunks) > 0
