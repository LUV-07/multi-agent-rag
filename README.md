<h1>#🧠 Multi-Agent RAG — Document Q&A System</h1>
 
Ask questions about any document and get accurate, cited answers powered by a multi-agent AI pipeline. Upload a PDF, DOCX, or TXT file and instantly chat with it — summarize it, extract key points, or ask anything specific.

---

## What it does

- **Upload any document** — PDF, DOCX, or plain text
- **Ask questions in natural language** — the system finds the most relevant parts of your document and answers based only on what's actually in it
- **Summarize** — get a full summary of any document in seconds
- **Extract key points** — pull out the most important facts and takeaways
- **Cited answers** — every response tells you which part of the document it came from
- **Semantic caching** — identical or very similar queries are cached so you don't waste API calls

---

## How it works

When you upload a document, it gets split into small chunks and converted into numerical embeddings using a local HuggingFace model. These embeddings are stored in ChromaDB on your machine.

When you ask a question, four agents work together:

```
Your Question
      ↓
Orchestrator Agent — figures out what you're asking (Q&A, summarize, key points)
      ↓
Retrieval Agent — searches ChromaDB for the most relevant chunks
      ↓
Reasoning Agent — thinks through the retrieved context step by step
      ↓
Generation Agent — writes the final answer with source citations
      ↓
Answer shown in Streamlit UI
```

---

## Tech stack

| Layer | Tool | Why |
|---|---|---|
| Frontend | Streamlit | Fast, clean UI with no frontend code |
| LLM | Gemini 1.5 Flash | Free tier — 1M tokens/day |
| Embeddings | sentence-transformers (HuggingFace) | Runs locally, completely free |
| Vector DB | ChromaDB | Local, persistent, no setup needed |
| Framework | LangChain | Agent orchestration and prompt management |
| Document parsing | PyMuPDF, python-docx | PDF and DOCX support |

**Total cost to run: $0** — everything except Gemini runs locally. Gemini's free tier gives you 15 requests/minute and 1 million tokens per day.

---

## Project structure

```
multi_agent_rag/
├── app.py                        # Streamlit frontend — run this
├── requirements.txt
├── .env.example                  # Copy this to .env and add your key
│
├── agents/
│   ├── orchestrator.py           # Routes queries to the right agent
│   ├── retrieval_agent.py        # Semantic search over your document
│   ├── reasoning_agent.py        # Chain-of-thought reasoning
│   └── generation_agent.py      # Final answer with citations
│
├── core/
│   ├── document_processor.py    # Ingests and chunks documents
│   ├── embeddings.py            # HuggingFace embedding generation
│   ├── vector_store.py          # ChromaDB interface
│   └── prompt_templates.py      # All LangChain prompts
│
├── utils/
│   ├── text_splitter.py         # Semantic chunking logic
│   └── helpers.py               # Utility functions
│
└── config/
    └── settings.py              # Config loaded from .env
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/multi-agent-rag.git
cd multi-agent-rag
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get your free Gemini API key

Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey), sign in with your Google account, and create a key. It takes about 30 seconds.

### 4. Set up your environment

```bash
cp .env.example .env
```

Open `.env` and paste your key:

```
GEMINI_API_KEY=your_key_here
```

### 5. Run the app

```bash
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`.

---

## Usage

1. Open the app in your browser
2. Upload a PDF, DOCX, or TXT file using the sidebar
3. Wait a few seconds while the document is processed and indexed
4. Start asking questions in the chat box
5. Use the **Summarize** or **Key Points** buttons for instant one-click analysis
6. Expand the **Sources** section under any answer to see exactly which part of the document was used

---

## Example queries

- *"What is the main argument of this paper?"*
- *"List all the dates and deadlines mentioned."*
- *"What does the author recommend in the conclusion?"*
- *"Summarize section 3."*
- *"Are there any risks or limitations mentioned?"*

---

## Environment variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key (required) |
| `CHUNK_SIZE` | Token size per document chunk (default: 500) |
| `CHUNK_OVERLAP` | Overlap between chunks (default: 50) |
| `TOP_K_RESULTS` | Number of chunks retrieved per query (default: 5) |
| `CACHE_SIMILARITY_THRESHOLD` | Cosine similarity above which a cached answer is reused (default: 0.95) |

---

## Known limitations

- Works best with text-heavy documents — scanned image PDFs without OCR won't be indexed properly
- Very large documents (100+ pages) may take 30–60 seconds to process on first upload
- Gemini free tier has a rate limit of 15 requests per minute — if you hit it, just wait a moment and retry

---

## Built with

- [LangChain](https://langchain.com)
- [Google Gemini](https://aistudio.google.com)
- [ChromaDB](https://www.trychroma.com)
- [Streamlit](https://streamlit.io)
- [sentence-transformers](https://www.sbert.net)

---

## License

MIT — free to use, modify, and distribute.
