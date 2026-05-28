"""
agents/qa_agent.py — Question-answering agent
Responsibility: Answer questions strictly from retrieved context.
Anti-hallucination: Only uses retrieved document chunks.
"""
from typing import List, Dict, Generator, Optional
from core.llm import LLMEngine
from config import config
from utils.validators import check_answer_grounded, format_sources
from utils.logger import get_logger

log = get_logger("qa_agent")


class QAAgent:
    """
    Agent that answers questions based ONLY on retrieved document context.
    Implements strict anti-hallucination via:
    1. Context-only prompting
    2. Grounding checks on output
    3. Refusal when context is insufficient
    """

    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine

    def answer(
        self,
        question: str,
        context_chunks: List[Dict],
        context_string: str,
    ) -> Dict:
        """
        Answer a question using the provided context.
        Returns {answer, sources, is_grounded, confidence, warning}.
        """
        if not context_chunks:
            return {
                "answer": "I don't have enough information in the document to answer this question. Please upload a relevant document first.",
                "sources": "",
                "is_grounded": True,
                "confidence": 1.0,
                "warning": None,
            }

        # Build the prompt using config template
        prompt = config.QA_SYSTEM_PROMPT.format(
            context=context_string,
            question=question,
        )

        log.info(f"QA answering: '{question[:60]}...'")

        # Generate answer
        answer = self.llm.generate(prompt)

        # Anti-hallucination check
        is_grounded, confidence = check_answer_grounded(answer, context_chunks)
        sources = format_sources(context_chunks)

        warning = None
        if not is_grounded:
            warning = "⚠️ Low confidence: This answer may not be fully supported by the document. Please verify."
            log.warning(f"Potential hallucination detected (confidence={confidence:.2f})")

        log.info(f"Answer generated | grounded={is_grounded} | confidence={confidence:.2f}")

        return {
            "answer": answer,
            "sources": sources,
            "is_grounded": is_grounded,
            "confidence": confidence,
            "warning": warning,
        }

    def answer_stream(
        self,
        question: str,
        context_chunks: List[Dict],
        context_string: str,
    ) -> Generator[str, None, None]:
        """
        Stream answer tokens for real-time display in Streamlit.
        Yields string chunks.
        """
        if not context_chunks:
            yield "I don't have enough information in the document to answer this question."
            return

        prompt = config.QA_SYSTEM_PROMPT.format(
            context=context_string,
            question=question,
        )

        log.info(f"Streaming QA answer for: '{question[:60]}'")

        for chunk in self.llm.stream(prompt):
            yield chunk
