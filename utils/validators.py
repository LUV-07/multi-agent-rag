"""
utils/validators.py — Input validation & anti-hallucination checks
"""

import os
from typing import Tuple
from config import config
from utils.logger import get_logger

log = get_logger("validators")

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "each", "and", "or",
    "but", "if", "this", "that", "these", "those", "it", "its",
}

UNCERTAIN_PHRASES = [
    "i don't have enough information",
    "not mentioned in the document",
    "not in the context",
    "cannot find",
    "no information",
    "i don't know",
]


def validate_file(file_path: str) -> Tuple[bool, str]:
    """Basic file integrity, type, and size compliance checks."""
    if not os.path.exists(file_path):
        return False, "File not found."

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        allowed = ", ".join(config.ALLOWED_EXTENSIONS)
        return False, f"Unsupported file type '{ext}'. Allowed: {allowed}"

    size_mb = os.path.getsize(file_path) / (1024 ** 2)
    if size_mb > config.MAX_FILE_SIZE_MB:
        return False, f"File too large ({size_mb:.1f}MB). Max: {config.MAX_FILE_SIZE_MB}MB"

    return True, "OK"


def validate_question(question: str) -> Tuple[bool, str]:
    """Validates query length parameters before hitting the LLM wrapper."""
    query = question.strip()

    if not query:
        return False, "Please enter a question."
    if len(query) < 3:
        return False, "Question too short. Please be more specific."
    if len(query) > 1000:
        return False, "Question too long. Please keep it under 1000 characters."

    return True, "OK"


def check_answer_grounded(answer: str, context_chunks: list) -> Tuple[bool, float]:
    """
    Evaluates whether the generation relies strictly on provided context tokens.
    Returns boolean status alongside a normalized confidence score.
    """
    if not answer or not context_chunks:
        return False, 0.0

    answer_lower = answer.lower()
    
    # An honest refusal to answer is perfectly grounded
    if any(phrase in answer_lower for phrase in UNCERTAIN_PHRASES):
        return True, 1.0

    context_text = " ".join([c.get("text", "") for c in context_chunks]).lower()
    
    # Tokenize content excluding non-semantic filler words
    answer_words = {w for w in answer_lower.split() if w not in STOP_WORDS}
    context_words = {w for w in context_text.split() if w not in STOP_WORDS}

    if not answer_words:
        return True, 0.5

    overlap = answer_words.intersection(context_words)
    overlap_ratio = len(overlap) / len(answer_words)

    # 30% word match threshold to pass grounding evaluation
    is_grounded = overlap_ratio >= 0.3
    confidence = min(1.0, overlap_ratio * 1.5)

    if not is_grounded:
        log.warning(f"Grounding failure: score {overlap_ratio:.2f} implies likely hallucination")

    return is_grounded, confidence


def format_sources(chunks: list) -> str:
    """Aggregates chunk metadata matrices into human-readable reference tags."""
    if not chunks:
        return "No sources found."

    citations = []
    for idx, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        source_name = meta.get("source", "Unknown")
        page = meta.get("page", "")
        chunk_idx = meta.get("chunk_index", idx)

        page_str = f", Page {page}" if page else ""
        citations.append(f"[{idx}] {source_name}{page_str} (Chunk #{chunk_idx})")

    return "\n".join(citations)
