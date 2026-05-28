# 🧠 Multi-Agent RAG System

A lightweight, local Retrieval-Augmented Generation (RAG) app that lets you upload documents, ask questions, and generate structured summaries. The system coordinates multiple isolated agents to handle ingestion, context extraction, and validation completely locally or using free-tier cloud models.

---

## 🏗️ Project Directory Layout

```text
multi_agent_rag/
├── app.py                      # Main Streamlit UI entry point
├── config.py                   # Central settings, constraints, and prompts
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environmental variables
├── agents/
│   ├── orchestrator.py         # Coordinates state transitions and agent routing
│   ├── ingestion_agent.py      # Handles text layout parsing and payload building
│   ├── retrieval_agent.py      # Manages localized vector space querying
│   ├── qa_agent.py             # Focuses strictly on synthesis and citation extraction
│   └── summarizer_agent.py     # Builds map-reduce or targeted outline summaries
├── core/
│   ├── document_processor.py   # Extracts string payloads from PDF/DOCX/TXT/HTML
│   ├── embeddings.py           # Local inference for vector calculations
│   ├── vector_store.py         # Local instance manager for FAISS matrix indexing
│   └── llm.py                  # API orchestration for Groq backend endpoints
├── utils/
│   ├── chunker.py              # Smart paragraph splitting and token sliding windows
│   ├── validators.py           # Post-generation checks and grounding tests
│   └── logger.py               # Streamlined console and debugging output
└── ui/
    ├── components.py           # Modular layout components for chat tabs and states
    └── styles.py               # Theme variables and UI structural layout definitions