from typing import List
import numpy as np
from config import config
from utils.logger import get_logger

log = get_logger("embeddings")


class EmbeddingEngine:
    

    def __init__(self, model_name: str = config.EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None
        log.info(f"Embedding engine initialized with model: {model_name}")

    @property
    def model(self):
        """Lazy-load model on first use."""
        if self._model is None:
            log.info(f"Loading embedding model '{self.model_name}' (first run downloads ~90MB)...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            log.info("Embedding model loaded successfully.")
        return self._model

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embed a list of texts.
        Returns numpy array of shape (n_texts, embedding_dim).
        """
        if not texts:
            return np.array([])

        # Clean texts
        cleaned = [t.strip() for t in texts if t and t.strip()]
        if not cleaned:
            return np.array([])

        log.debug(f"Embedding {len(cleaned)} texts...")
        embeddings = self.model.encode(
            cleaned,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,  # Cosine similarity ready
        )
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string."""
        result = self.embed_texts([query])
        return result[0] if len(result) > 0 else np.array([])

    @property
    def embedding_dim(self) -> int:
        """Return the embedding dimension of the loaded model."""
        return self.model.get_sentence_embedding_dimension()
