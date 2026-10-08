# 🧠 Multi-Agent RAG — Document Q&A & Summarization System

A modular **Retrieval-Augmented Generation (RAG)** system for document question answering, summarization, and key-information extraction.

The application allows users to upload documents, retrieve relevant content using semantic vector search, generate document-grounded answers through an LLM, inspect source information, and request document summaries through a Streamlit interface.

---

## ✨ Features

- 📄 **Multi-format document ingestion**
  - PDF
  - DOCX
  - TXT
  - Markdown
  - PPTX
  - XLSX
  - HTML

- 🔎 **Semantic document retrieval**
  - Sentence Transformer embeddings
  - FAISS vector search
  - Top-K configurable retrieval
  - Similarity-threshold filtering

- 🤖 **Multi-agent architecture**
  - Ingestion Agent
  - Retrieval Agent
  - QA Agent
  - Summarizer Agent
  - Custom Python Orchestrator

- 💬 **Document-grounded Q&A**
  - Answers generated using retrieved document context
  - Context-only prompting
  - Source information displayed with responses

- ✅ **Grounding validation**
  - Post-generation context-support check
  - Grounding score for the generated answer
  - Helps identify potentially unsupported responses

- 📝 **Document summarization**
  - Multiple summary modes
  - Document-level summaries
  - Key-information extraction

- 🖥️ **Interactive Streamlit interface**
  - Document upload
  - Question answering
  - Source inspection
  - Summarization

- 📦 **50 MB upload limit**

---

## 🏗️ Architecture

The system uses a modular four-agent architecture coordinated by a custom Python orchestrator.

```text
                     ┌─────────────────────┐
                     │    Streamlit UI     │
                     └──────────┬──────────┘
                                │
                  ┌─────────────▼─────────────┐
                  │   Python Orchestrator     │
                  └─────────────┬─────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
 ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
 │ Ingestion      │    │ Retrieval      │    │ Summarizer     │
 │ Agent          │    │ Agent          │    │ Agent          │
 └───────┬────────┘    └───────┬────────┘    └────────────────┘
         │                     │
         ▼                     ▼
   Document Processing     Semantic Search
         │                     │
         ▼                     ▼
     Embeddings              FAISS
         │                     │
         └──────────┬──────────┘
                    ▼
             ┌───────────────┐
             │    QA Agent   │
             └───────┬───────┘
                     │
                     ▼
                Groq LLM
                     │
                     ▼
             Grounding Check
                     │
                     ▼
               Answer + Sources
```

The ingestion flow extracts document text, performs paragraph-aware chunking, generates embeddings, and stores them in FAISS. Questions are embedded with the same Sentence Transformer model and matched against the indexed document chunks before being passed to the QA agent.

---

## 🔄 How It Works

### 1. Document Ingestion

```text
Document
   ↓
Validation
   ↓
Text Extraction
   ↓
Paragraph-aware Chunking
   ↓
Sentence Transformer
   ↓
Embedding Normalization
   ↓
FAISS Index
```

The ingestion pipeline preserves relevant source metadata such as page information where available. The resulting embeddings are normalized before being stored in FAISS for local similarity search.

---

### 2. Question Answering

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
Top-K Relevant Chunks
      ↓
QA Agent
      ↓
Groq LLM
      ↓
Grounding Validation
      ↓
Answer + Sources
```

The Retrieval Agent searches the FAISS index for the most relevant chunks. The QA Agent then receives the user's question together with the retrieved context and generates a document-grounded response.

---

## 🤖 Multi-Agent Design

### 1. Ingestion Agent

Responsible for:

- Validating uploaded documents
- Extracting text
- Chunking content
- Generating embeddings
- Indexing document chunks in FAISS

### 2. Retrieval Agent

Responsible for:

- Embedding the user's query
- Searching the FAISS vector store
- Applying similarity filtering
- Returning the most relevant chunks

### 3. QA Agent

Responsible for:

- Receiving the user question
- Receiving retrieved document context
- Generating a grounded response using the Groq LLM
- Returning answer content for grounding validation

### 4. Summarizer Agent

Responsible for:

- Generating summaries from indexed document content
- Supporting different summarization modes
- Extracting important information from documents

### Orchestrator

The custom Python Orchestrator coordinates the document ingestion, retrieval, question answering, and summarization workflows.

---

## 🔍 Embeddings & Vector Retrieval

The system uses:

```text
Model: all-MiniLM-L6-v2
```

Embedding pipeline:

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

Both document chunks and user queries are embedded using the same Sentence Transformer model.

The normalized vectors are stored in FAISS and searched using inner-product similarity, providing cosine-similarity-style semantic retrieval. The number of retrieved chunks and similarity threshold are configurable.

---

## ✂️ Chunking Strategy

The document processor uses **paragraph-aware, word-based chunking**.

### Default configuration

| Parameter | Value |
|---|---:|
| Chunk size | 512 words |
| Chunk overlap | 200 words |
| Default retrieved chunks | 5 |
| Maximum upload size | 50 MB |

Paragraph-aware splitting attempts to preserve logical document structure while the overlap helps maintain contextual continuity between neighboring chunks.

---

## ✅ Grounding Validation

After the QA Agent generates an answer, the system performs a lightweight post-generation grounding check.

```text
Retrieved Context
       +
Generated Answer
       ↓
Context Support Check
       ↓
Grounding Score
```

The grounding score estimates how strongly the generated answer is supported by the retrieved document context.

This mechanism is intended as a **lightweight context-support check**, not as a formal guarantee that an answer is completely hallucination-free.

---

## 📚 Supported Documents

The ingestion pipeline currently supports:

- `.pdf`
- `.docx`
- `.txt`
- `.md`
- `.pptx`
- `.xlsx`
- `.html`

Maximum upload size: **50 MB**.

### Note

Text-heavy documents generally produce better results.

Scanned PDFs without an extractable text layer require OCR before their content can be processed effectively.

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| Frontend | Streamlit |
| LLM API | Groq |
| LLM Models | LLaMA / Gemma |
| Embeddings | Sentence Transformers |
| Embedding Model | `all-MiniLM-L6-v2` |
| Vector Search | FAISS |
| Orchestration | Custom Python Orchestrator |
| PDF Processing | PyMuPDF |
| DOCX Processing | python-docx |
| PPTX Processing | python-pptx |
| Excel Processing | openpyxl |
| HTML Processing | BeautifulSoup |
| Text Processing | LangChain |
| Configuration | python-dotenv |

Embeddings and vector search run locally, while LLM inference is performed through the Groq API.

---

## 📁 Project Structure

```text
multi-agent-rag/
│
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── test_setup.py
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
├── ui/
│
└── utils/
    ├── text_splitter.py
    └── helpers.py
```

### Important Modules

**`app.py`**  
Streamlit application and user interface.

**`agents/orchestrator.py`**  
Coordinates ingestion, retrieval, question answering, and summarization.

**`agents/ingestion_agent.py`**  
Processes uploaded documents and indexes their content.

**`agents/retrieval_agent.py`**  
Performs semantic retrieval against FAISS.

**`agents/qa_agent.py`**  
Generates document-grounded responses using the configured Groq model.

**`agents/summarizer_agent.py`**  
Generates document summaries.

**`core/document_processor.py`**  
Extracts and prepares text from supported formats.

**`core/embeddings.py`**  
Generates Sentence Transformer embeddings.

**`core/vector_store.py`**  
Handles FAISS indexing, similarity search, and persistence.

**`core/llm_engine.py`**  
Handles Groq API communication and model configuration.

**`utils/text_splitter.py`**  
Implements paragraph-aware chunking.

The repository's current structure and module responsibilities are documented in the project itself.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/LUV-07/multi-agent-rag.git
cd multi-agent-rag
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Groq API key

Create a `.env` file from the provided template:

```bash
cp .env.example .env
```

Then add:

```env
GROQ_API_KEY=your_key_here
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

These are the repository's current setup and execution steps.

---

## 🖥️ Usage

1. Launch the Streamlit application.
2. Upload a supported document.
3. Wait for text extraction, chunking, embedding, and indexing.
4. Ask a question about the document.
5. Review the generated answer.
6. Inspect the retrieved source information.
7. Use the summarization functionality when a document-level summary is required.

---

## 💬 Example Questions

```text
What is the main argument of this paper?

List all the dates and deadlines mentioned.

What does the author recommend in the conclusion?

Summarize section 3.

What are the main risks or limitations mentioned?

What evidence does the document provide for this claim?
```

---

## 🔐 Environment Variables

| Variable | Description | Default |
|---|---|---:|
| `GROQ_API_KEY` | Groq API key required for LLM inference | Required |
| `CHUNK_SIZE` | Maximum configured chunk size | `512` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |
| `TOP_K_RESULTS` | Number of retrieved chunks | `5` |
| `SIMILARITY_THRESHOLD` | Minimum retrieval similarity | Configurable |

These settings are exposed through the application's configuration system.

---

## ⚠️ Known Limitations

- Text-heavy documents generally produce better results than scanned or image-only documents.
- Scanned PDFs without an extractable text layer require OCR.
- Large documents may require additional processing time during initial indexing.
- Answer quality depends on retrieval quality and the selected LLM.
- The grounding mechanism is a lightweight context-support check rather than a formal hallucination detector.
- LLM inference requires access to the configured Groq API.
- Very similar chunks may sometimes produce redundant retrieval results.

---

## 🚀 Future Improvements

Potential improvements include:

- Hybrid keyword + semantic retrieval
- Retrieval reranking
- Automated RAG evaluation using Recall@K, MRR, and answer relevance
- More advanced grounding and faithfulness evaluation
- Conversation-aware retrieval
- Improved OCR support for scanned documents
- FastAPI REST API layer
- More sophisticated caching

These are intentionally listed as **future improvements rather than current features**, so the README does not overstate the current implementation.

---

## 🧩 Design Philosophy

The project focuses on keeping the RAG pipeline modular:

```text
Document Processing
        ↓
Embedding Generation
        ↓
Vector Retrieval
        ↓
Context Construction
        ↓
LLM Generation
        ↓
Grounding Validation
        ↓
Source-aware Response
```

Each stage is separated into dedicated modules and agents, making the system easier to extend, debug, and evaluate.

---

## 📄 License

MIT License.
