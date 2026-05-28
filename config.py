import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- LLM Settings ---
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    LLM_TEMPERATURE = 0.0  # 0 = deterministic to prevent hallucination
    LLM_MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1024))

    # --- Embeddings & Vector Store ---
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    VECTOR_STORE_PATH = "./vector_store"
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 5))

    # --- Text Chunking ---
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

    # --- Application UI & Constraints ---
    APP_TITLE = os.getenv("APP_TITLE", "Multi-Agent RAG")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    MAX_FILE_SIZE_MB = 50
    ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt", ".md", ".pptx", ".xlsx", ".html")

    # --- Validation Guards ---
    SIMILARITY_THRESHOLD = 0.10  # Minimum score to accept a retrieved chunk
    MIN_CONTEXT_CHUNKS = 1        # Minimum chunks required to attempt an answer

    # --- Core Agent Prompts ---
    QA_SYSTEM_PROMPT = """You are a precise document analysis assistant. 
Your ONLY job is to answer questions using the provided document context.

STRICT RULES:
1. ONLY use information from the provided context — never use outside knowledge
2. If the answer is not in the context, say: "I don't have enough information in the document to answer this."
3. Always cite which part of the document supports your answer
4. Be concise and accurate
5. Never make up facts, statistics, or details not present in the context

Context from document:
{context}

Question: {question}

Answer (based strictly on the document context above):"""

    SUMMARY_SYSTEM_PROMPT = """You are a precise document summarizer.
Summarize the following document content accurately and comprehensively.

RULES:
1. Only summarize what is actually in the text — do not add outside information
2. Structure the summary with: Overview, Key Points, and Conclusion
3. Be factual and objective
4. If a section is unclear, say so rather than guess

Document content:
{context}

Provide a well-structured summary:"""

    CHUNK_RELEVANCE_PROMPT = """Given this question: "{question}"
And this document chunk: "{chunk}"

Rate how relevant this chunk is to answering the question.
Respond with ONLY a number from 0.0 to 1.0 (e.g., 0.8)"""

# Global configuration instance
config = Config()