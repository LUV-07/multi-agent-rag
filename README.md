# 🧠 Multi-Agent RAG — Document Q&A System

Ask questions about your documents and get **document-grounded answers with source information** through a modular multi-agent AI pipeline.

Upload a document, ask questions about its contents, generate summaries, or extract key information through a Streamlit-based interface.

---

## What it does

- **Upload documents** — PDF, DOCX, TXT, Markdown, PPTX, XLSX, and HTML
- **Ask questions in natural language** — retrieves the most relevant document chunks before generating an answer
- **Document-grounded Q&A** — answers are generated using the retrieved document context
- **Summarize documents** — generate summaries from the indexed document content
- **Extract key information** — use the summarization workflow to identify important information
- **Source information** — responses include the source/page information associated with retrieved chunks
- **Grounding validation** — performs a post-generation context-support check on generated answers
- **Local vector search** — uses FAISS for persistent local similarity search
- **Multiple LLM options** — supports selectable models through the Groq API

---

## How it works

The system uses a modular four-agent architecture coordinated by a custom Python orchestrator.

### Document ingestion

When a document is uploaded:

```text
Document
   ↓
Document Processor
   ↓
Text Extraction
   ↓
Paragraph-aware Chunking
   ↓
Sentence Transformer Embeddings
   ↓
FAISS Vector Store
```

The document processor extracts text while preserving relevant metadata such as page information. The text is divided into configurable chunks and converted into embeddings using a local Sentence Transformer model.

The embeddings are normalized and stored in FAISS for efficient similarity search.

### Question answering

When a user asks a question:

```text
User Question
      ↓
Orchestrator
      ↓
Retrieval Agent
      ↓
Question Embedding
      ↓
FAISS Similarity Search
      ↓
Relevant Document Chunks
      ↓
QA Agent
      ↓
Groq LLM
      ↓
Grounding Validation
      ↓
Answer + Sources
      ↓
Streamlit UI
```

The retrieval agent searches the FAISS index for relevant chunks. These chunks are then passed as context to the QA agent, which generates the answer through the configured Groq model.

A post-generation grounding check compares the generated response with the retrieved context to estimate how strongly the answer is supported by the available document evidence.

---

## Multi-Agent Architecture

The project contains four specialized agents:

### 1. Ingestion Agent

Responsible for preparing uploaded documents for retrieval.

```text
Document
   ↓
Validation
   ↓
Text Extraction
   ↓
Chunking
   ↓
Embedding Generation
   ↓
FAISS Indexing
```

### 2. Retrieval Agent

Responsible for finding relevant information from the indexed document.

```text
User Question
      ↓
Question Embedding
      ↓
FAISS Search
      ↓
Similarity Filtering
      ↓
Top-K Relevant Chunks
```

### 3. QA Agent

Responsible for generating document-grounded answers.

It receives:

```text
User Question
        +
Retrieved Context
        ↓
     Groq LLM
        ↓
Generated Answer
        ↓
Grounding Validation
```

The QA workflow is designed to restrict answers to the retrieved document context rather than relying on unrelated external knowledge.

### 4. Summarizer Agent

Responsible for generating document summaries from the retrieved document content.

It supports different summary modes through the application interface.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit | Interactive document upload, Q&A and summarization interface |
| LLM | Groq API | LLM inference |
| LLM Models | LLaMA / Gemma models | Answer and summary generation |
| Embeddings | Sentence Transformers | Local semantic embedding generation |
| Embedding Model | `all-MiniLM-L6-v2` | Converts document text and queries into vectors |
| Vector Search | FAISS | Local persistent similarity search |
| Orchestration | Custom Python Orchestrator | Coordinates the four agents |
| PDF Processing | PyMuPDF | PDF text extraction |
| DOCX Processing | python-docx | DOCX text extraction |
| Additional Formats | Markdown, PPTX, XLSX, HTML | Extended document ingestion |
| UI | Streamlit | Application interface |

The embeddings and vector search run locally. LLM inference is performed through the Groq API.

---

## Project Structure

```text
multi-agent-rag/
│
├── app.py
├── requirements.txt
├── .env.example
│
├── agents/
│   ├── orchestrator.py
│   ├── ingestion_agent.py
│   ├── retrieval_agent.py
│   ├── qa_agent.py
│   └── summarizer_agent.py
│
├── core/
│   ├── document_processor.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── llm_engine.py
│   └── prompt_templates.py
│
├── utils/
│   ├── text_splitter.py
│   └── helpers.py
│
└── config.py
```

### Important modules

**`app.py`**  
Streamlit application and user interface.

**`agents/orchestrator.py`**  
Coordinates ingestion, retrieval, question answering and summarization.

**`agents/ingestion_agent.py`**  
Processes uploaded documents and indexes their contents.

**`agents/retrieval_agent.py`**  
Performs semantic retrieval against the FAISS vector store.

**`agents/qa_agent.py`**  
Generates document-grounded answers using the configured Groq model.

**`agents/summarizer_agent.py`**  
Generates summaries from retrieved document content.

**`core/document_processor.py`**  
Extracts and prepares text from supported document formats.

**`core/embeddings.py`**  
Generates embeddings using Sentence Transformers.

**`core/vector_store.py`**  
Provides the FAISS vector-store implementation and persistence.

**`core/llm_engine.py`**  
Handles communication with the Groq API and configured LLM models.

**`utils/text_splitter.py`**  
Provides paragraph-aware text chunking.

**`config.py`**  
Stores application configuration and environment-based settings.

---

## Supported Documents

The current ingestion pipeline supports:

- PDF
- DOCX
- TXT
- Markdown (`.md`)
- PowerPoint (`.pptx`)
- Excel (`.xlsx`)
- HTML (`.html`)

The application supports document uploads up to **50 MB**.

Text-heavy documents generally provide the best results. Scanned PDFs that do not contain an extractable text layer require OCR before their contents can be effectively processed.

---

## Embedding and Retrieval

The project uses the Sentence Transformers model:

```text
all-MiniLM-L6-v2
```

The pipeline is:

```text
Document Chunk
      ↓
Sentence Transformer
      ↓
Embedding Vector
      ↓
Normalization
      ↓
FAISS
```

User questions are embedded using the same model and searched against the FAISS index.

The vector store uses normalized embeddings with inner-product search, providing cosine-similarity-style semantic retrieval.

The number of retrieved results and relevance threshold are configurable.

---

## Chunking

The document processor uses paragraph-aware, word-based chunking.

Current default configuration:

```text
Chunk Size   : 512
Chunk Overlap: 200
```

The overlap helps preserve contextual continuity between adjacent chunks.

Chunking is performed while retaining relevant document metadata so that retrieved content can be associated with its source information.

---

## Grounding Validation

After the QA agent generates an answer, the system performs a post-generation grounding check.

Conceptually:

```text
Retrieved Context
       +
Generated Answer
       ↓
Context Support Check
       ↓
Grounding Score
```

The resulting score indicates how strongly the generated answer is supported by the retrieved context.

This is a lightweight grounding mechanism and should not be interpreted as a formal guarantee that an answer is completely hallucination-free.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/LUV-07/multi-agent-rag.git
cd multi-agent-rag
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get a Groq API key

Create a Groq API key through the Groq developer platform.

### 4. Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Then add your API key:

```env
GROQ_API_KEY=your_key_here
```

### 5. Run the application

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

---

## Usage

1. Open the application in your browser.
2. Upload a supported document.
3. Wait while the document is extracted, chunked, embedded and indexed.
4. Ask questions about the document.
5. Review the generated answer and its source information.
6. Use the summarization functionality when a document-level summary is required.
7. Inspect the retrieved source information to understand which document content was used.

---

## Example Questions

```text
What is the main argument of this paper?

List all the dates and deadlines mentioned.

What does the author recommend in the conclusion?

Summarize section 3.

What are the main risks or limitations mentioned?

What evidence does the document provide for this claim?
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key required for LLM inference |
| `CHUNK_SIZE` | Maximum configured chunk size; default: 512 |
| `CHUNK_OVERLAP` | Chunk overlap; default: 200 |
| `TOP_K_RESULTS` | Number of chunks retrieved per query; default: 5 |
| `SIMILARITY_THRESHOLD` | Minimum retrieval similarity threshold |

---

## Known Limitations

- Text-heavy documents generally produce better results than scanned/image-only documents.
- Scanned PDFs without an extractable text layer require OCR.
- Large documents can require additional processing time during the first upload.
- Answer quality depends on the relevance of retrieved chunks and the selected LLM.
- The grounding check is a lightweight lexical/context-support mechanism rather than a formal hallucination detector.
- LLM inference requires access to the configured Groq API.
- Very similar or poorly separated chunks can sometimes result in redundant retrieval results.

---

## Future Improvements

Potential improvements to the current system include:

- Hybrid keyword + semantic retrieval
- Retrieval reranking
- Automated RAG evaluation using Recall@K, MRR and answer relevance
- More advanced grounding and faithfulness evaluation
- Conversation-aware retrieval
- Improved OCR support for scanned documents
- REST API layer using FastAPI
- More sophisticated caching mechanisms

---

## Built With

- [Groq API](https://groq.com/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [Streamlit](https://streamlit.io/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [LangChain](https://www.langchain.com/)

---

## License

MIT — free to use, modify, and distribute.
