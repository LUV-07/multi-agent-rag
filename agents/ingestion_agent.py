"""
agents/ingestion_agent.py — Document ingestion agent
Responsibility: Load, parse, chunk, embed, and store documents.
"""
from typing import List, Dict, Callable, Optional
from core.document_processor import DocumentProcessor
from core.embeddings import EmbeddingEngine
from core.vector_store import VectorStore
from utils.chunker import TextChunker
from utils.validators import validate_file
from utils.logger import get_logger

log = get_logger("ingestion_agent")


class IngestionAgent:
    """
    Agent that handles the full document ingestion pipeline:
    1. Validate file
    2. Extract text (PDF/DOCX/TXT/etc.)
    3. Chunk text smartly
    4. Generate embeddings
    5. Store in vector DB
    """

    def __init__(
        self,
        document_processor: DocumentProcessor,
        embedding_engine: EmbeddingEngine,
        vector_store: VectorStore,
        chunker: TextChunker,
    ):
        self.processor = document_processor
        self.embedder = embedding_engine
        self.vector_store = vector_store
        self.chunker = chunker

    def ingest(
        self,
        file_path: str,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> Dict:
        """
        Full ingestion pipeline for a single document.
        Returns summary dict with stats.
        """

        def update(msg: str, pct: float):
            log.info(f"[{pct*100:.0f}%] {msg}")
            if progress_callback:
                progress_callback(msg, pct)

        # ── Step 1: Validate ──────────────────────────────────
        update("Validating file...", 0.05)
        is_valid, error_msg = validate_file(file_path)
        if not is_valid:
            raise ValueError(f"File validation failed: {error_msg}")

        # ── Step 2: Extract text ──────────────────────────────
        update("Extracting text from document...", 0.20)
        pages = self.processor.process(file_path)

        if not pages:
            raise ValueError("No text could be extracted from the document.")

        total_text = " ".join(p["text"] for p in pages)
        update(f"Extracted {len(pages)} pages ({len(total_text):,} chars)", 0.35)

        # ── Step 3: Chunk text ────────────────────────────────
        update("Splitting into chunks...", 0.45)
        all_chunks = []

        for page in pages:
            page_metadata = {
                "source": page.get("source", "unknown"),
                "page": page.get("page", 1),
                "total_pages": page.get("total_pages", 1),
            }
            chunks = self.chunker.chunk_by_paragraph(page["text"], page_metadata)
            all_chunks.extend(chunks)

        if not all_chunks:
            raise ValueError("Document produced no text chunks after processing.")

        update(f"Created {len(all_chunks)} chunks", 0.55)

        # ── Step 4: Generate embeddings ───────────────────────
        update("Generating embeddings (this may take a moment)...", 0.65)
        texts = [c["text"] for c in all_chunks]
        embeddings = self.embedder.embed_texts(texts)

        if len(embeddings) == 0:
            raise ValueError("Embedding generation failed.")

        update(f"Embedded {len(embeddings)} chunks (dim={embeddings.shape[1]})", 0.80)

        # ── Step 5: Store in vector DB ────────────────────────
        update("Storing in vector database...", 0.90)
        self.vector_store.add_chunks(all_chunks, embeddings)

        update("✅ Document ingested successfully!", 1.0)

        return {
            "file_path": file_path,
            "pages": len(pages),
            "chunks": len(all_chunks),
            "total_chars": len(total_text),
            "embedding_dim": int(embeddings.shape[1]),
            "vector_store_total": self.vector_store.chunk_count,
        }

    def ingest_multiple(
        self,
        file_paths: List[str],
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> List[Dict]:
        """Ingest multiple documents sequentially."""
        results = []
        n = len(file_paths)

        for i, file_path in enumerate(file_paths):
            log.info(f"Ingesting document {i+1}/{n}: {file_path}")

            def scoped_callback(msg, pct, i=i):
                overall = (i + pct) / n
                if progress_callback:
                    progress_callback(f"[{i+1}/{n}] {msg}", overall)

            try:
                result = self.ingest(file_path, scoped_callback)
                result["status"] = "success"
                results.append(result)
            except Exception as e:
                log.error(f"Failed to ingest {file_path}: {e}")
                results.append({
                    "file_path": file_path,
                    "status": "error",
                    "error": str(e),
                })

        return results
