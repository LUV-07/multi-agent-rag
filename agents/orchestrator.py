"""
agents/orchestrator.py — Master orchestrator agent
"""
import os
from typing import Dict, List, Optional, Generator, Callable

from core.document_processor import DocumentProcessor
from core.embeddings import EmbeddingEngine
from core.vector_store import VectorStore
from core.llm import LLMEngine
from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.qa_agent import QAAgent
from agents.summarizer_agent import SummarizerAgent
from utils.chunker import TextChunker
from utils.validators import validate_question
from config import config
from utils.logger import get_logger

log = get_logger("orchestrator")


class Orchestrator:
    def __init__(self):
        log.info("Initialising Multi-Agent RAG Orchestrator...")

        self.document_processor = DocumentProcessor()
        self.embedding_engine = EmbeddingEngine()
        self.vector_store = VectorStore()
        self.chunker = TextChunker()

        # LLM is constructed fresh — reads API key from env at each call
        self.llm_engine = LLMEngine()

        self.ingestion_agent = IngestionAgent(
            document_processor=self.document_processor,
            embedding_engine=self.embedding_engine,
            vector_store=self.vector_store,
            chunker=self.chunker,
        )
        self.retrieval_agent = RetrievalAgent(
            embedding_engine=self.embedding_engine,
            vector_store=self.vector_store,
        )
        self.qa_agent = QAAgent(llm_engine=self.llm_engine)
        self.summarizer_agent = SummarizerAgent(llm_engine=self.llm_engine)

        self.ingested_files: List[str] = []
        self.conversation_history: List[Dict] = []
        log.info("Orchestrator ready.")

    # ── Public API ────────────────────────────────────────────

    def ingest_document(
        self,
        file_path: str,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> Dict:
        log.info(f"Ingesting {file_path}")
        try:
            result = self.ingestion_agent.ingest(file_path, progress_callback)
            self.ingested_files.append(file_path)
            return {"status": "success", **result}
        except Exception as e:
            log.error(f"Ingestion failed: {e}")
            return {"status": "error", "error": str(e)}

    def ask_question(self, question: str, stream: bool = False):
        is_valid, error_msg = validate_question(question)
        if not is_valid:
            if stream:
                def _g():
                    yield error_msg
                return _g()
            return {"answer": error_msg, "sources": "", "is_grounded": False}

        if not self.vector_store.is_ready:
            msg = "No document loaded. Please upload a document first."
            if stream:
                def _g():
                    yield msg
                return _g()
            return {"answer": msg, "sources": "", "is_grounded": True}

        chunks = self.retrieval_agent.retrieve(question)
        context_string = self.retrieval_agent.build_context_string(chunks)

        self.conversation_history.append({"role": "user", "content": question})

        if stream:
            return self.qa_agent.answer_stream(question, chunks, context_string)

        result = self.qa_agent.answer(question, chunks, context_string)
        result["retrieved_chunk_count"] = len(chunks)
        self.conversation_history.append({"role": "assistant", "content": result["answer"]})
        return result

    def summarize_document(self, summary_type: str = "comprehensive", stream: bool = False):
        if not self.vector_store.is_ready:
            msg = "No document loaded. Please upload a document first."
            if stream:
                def _g():
                    yield msg
                return _g()
            return {"summary": msg}

        chunks = self.retrieval_agent.retrieve_for_summary(max_chunks=20)
        log.info(f"Summarising {len(chunks)} chunks (type={summary_type})")

        if stream:
            return self.summarizer_agent.summarize_stream(chunks, summary_type)
        return self.summarizer_agent.summarize(chunks, summary_type)

    def reset(self) -> None:
        self.vector_store.clear()
        self.ingested_files.clear()
        self.conversation_history.clear()
        log.info("Orchestrator reset.")

    @property
    def is_ready(self) -> bool:
        return self.vector_store.is_ready

    @property
    def stats(self) -> Dict:
        return {
            "ingested_files": len(self.ingested_files),
            "file_names": [f.split("\\")[-1].split("/")[-1] for f in self.ingested_files],
            "total_chunks": self.vector_store.chunk_count,
            "conversation_turns": len([h for h in self.conversation_history if h["role"] == "user"]),
            "model": os.getenv("LLM_MODEL", config.LLM_MODEL),
            "embedding_model": config.EMBEDDING_MODEL,
        }
