"""
utils/chunker.py — Smart text chunking with overlap
"""

from typing import List
from config import config
from utils.logger import get_logger

log = get_logger("chunker")


class TextChunker:
    """Splits text into overlapping segments to preserve contextual boundaries."""

    def __init__(
        self,
        chunk_size: int = config.CHUNK_SIZE,
        chunk_overlap: int = config.CHUNK_OVERLAP,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, metadata: dict = None) -> List[dict]:
        """Splits raw text string into chunks of words using a sliding window."""
        if not text or not text.strip():
            return []

        metadata = metadata or {}
        words = text.split()
        chunks = []
        
        idx = 0
        word_count = len(words)
        step = max(1, self.chunk_size - self.chunk_overlap)

        while idx < word_count:
            chunk_words = words[idx : idx + self.chunk_size]
            chunk_text = " ".join(chunk_words)

            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        **metadata,
                        "chunk_index": len(chunks),
                        "word_start": idx,
                        "word_end": idx + len(chunk_words),
                        "char_count": len(chunk_text),
                    },
                })
            
            idx += step

        log.debug(f"Created {len(chunks)} text chunks (size={self.chunk_size}, overlap={self.chunk_overlap})")
        return chunks

    def chunk_by_paragraph(self, text: str, metadata: dict = None) -> List[dict]:
        """Groups text by paragraph breaks first, breaking down oversized segments."""
        metadata = metadata or {}
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        all_chunks = []

        for p_idx, paragraph in enumerate(paragraphs):
            para_meta = {**metadata, "paragraph_index": p_idx}
            words = paragraph.split()

            # If paragraph fits comfortably inside standard window size
            if len(words) <= self.chunk_size:
                all_chunks.append({
                    "text": paragraph,
                    "metadata": {
                        **para_meta,
                        "chunk_index": len(all_chunks),
                        "char_count": len(paragraph),
                    },
                })
            else:
                # Sub-chunk oversized paragraphs to prevent loss of signal
                sub_chunks = self.chunk_text(paragraph, para_meta)
                all_chunks.extend(sub_chunks)

        log.debug(f"Paragraph parser: {len(paragraphs)} paragraphs converted to {len(all_chunks)} chunks")
        return all_chunks