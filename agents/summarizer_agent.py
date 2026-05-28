"""
agents/summarizer_agent.py — Document summarization agent
Responsibility: Generate accurate, structured summaries of documents.
"""
from typing import List, Dict, Generator
from core.llm import LLMEngine
from config import config
from utils.logger import get_logger

log = get_logger("summarizer_agent")


class SummarizerAgent:
    """
    Agent that summarizes documents accurately using retrieved chunks.
    Anti-hallucination: Only summarizes actual document content.
    """

    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine

    def summarize(self, chunks: List[Dict], summary_type: str = "comprehensive") -> Dict:
        """
        Summarize document content.
        summary_type: "comprehensive" | "brief" | "bullet_points" | "key_facts"
        """
        if not chunks:
            return {
                "summary": "No document content available to summarize. Please upload a document first.",
                "chunk_count": 0,
                "summary_type": summary_type,
            }

        context_string = self._build_summary_context(chunks)

        prompt = self._build_prompt(context_string, summary_type)

        log.info(f"Summarizing {len(chunks)} chunks (type: {summary_type})")

        summary = self.llm.generate(prompt)

        log.info(f"Summary generated: {len(summary)} chars")

        return {
            "summary": summary,
            "chunk_count": len(chunks),
            "summary_type": summary_type,
            "context_chars": len(context_string),
        }

    def summarize_stream(
        self,
        chunks: List[Dict],
        summary_type: str = "comprehensive",
    ) -> Generator[str, None, None]:
        """Stream summary for real-time display."""
        if not chunks:
            yield "No document content available to summarize."
            return

        context_string = self._build_summary_context(chunks)
        prompt = self._build_prompt(context_string, summary_type)

        log.info(f"Streaming summary ({summary_type}) for {len(chunks)} chunks")

        for chunk in self.llm.stream(prompt):
            yield chunk

    def _build_summary_context(self, chunks: List[Dict], max_chars: int = 8000) -> str:
        """Build context string from chunks for summarization."""
        parts = []
        total = 0

        for chunk in chunks:
            text = chunk.get("text", "").strip()
            meta = chunk.get("metadata", {})
            page = meta.get("page", "")
            page_info = f" [p.{page}]" if page else ""

            entry = f"{text}{page_info}"

            if total + len(entry) > max_chars:
                remaining = max_chars - total
                if remaining > 100:
                    parts.append(entry[:remaining] + "...")
                break

            parts.append(entry)
            total += len(entry)

        return "\n\n".join(parts)

    def _build_prompt(self, context: str, summary_type: str) -> str:
        """Build the appropriate summarization prompt."""

        type_instructions = {
            "comprehensive": """Provide a comprehensive summary with:
1. **Overview**: What this document is about (2-3 sentences)
2. **Key Points**: Main topics, arguments, or findings (bullet points)
3. **Details**: Important specifics, data, or examples
4. **Conclusion**: Final thoughts or conclusions from the document""",

            "brief": """Provide a brief 3-5 sentence summary covering:
- What the document is about
- The most important information
- Key conclusions""",

            "bullet_points": """Provide ONLY a bullet-point summary:
- List the 8-12 most important points from the document
- Each bullet should be a complete, informative sentence
- Order from most to least important""",

            "key_facts": """Extract ONLY the key facts, data, and statistics from the document:
- Numbers, dates, statistics
- Names of people, places, organizations
- Specific claims or findings
- Present as a structured fact list""",
        }

        instruction = type_instructions.get(summary_type, type_instructions["comprehensive"])

        return f"""{config.SUMMARY_SYSTEM_PROMPT.format(context=context)}

Summary type requested: {summary_type}

{instruction}

Remember: Only include information actually present in the document text above."""
