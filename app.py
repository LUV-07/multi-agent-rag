"""
app.py — Multi-Agent RAG System
Run with: streamlit run app.py
"""

import os
import sys
import tempfile
import streamlit as st
from dotenv import load_dotenv

# Ensure local modules are discoverable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.styles import CUSTOM_CSS
from ui.components import (
    render_header, 
    render_chat_message,
    render_agent_status, 
    render_empty_state, 
    render_doc_info,
)

# App Configuration
st.set_page_config(
    page_title="Multi-Agent RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- State Management ---
def init_session():
    """Initializes global app state if not already set."""
    defaults = {
        "orchestrator": None,
        "chat_history": [],
        "document_loaded": False,
        "active_agents": {
            "Ingestion Agent": False,
            "Retrieval Agent": False,
            "QA Agent": False,
            "Summarizer Agent": False,
        },
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

def get_orchestrator():
    """Lazy initializer for the agent coordinator."""
    if st.session_state.orchestrator is None:
        from agents.orchestrator import Orchestrator
        st.session_state.orchestrator = Orchestrator()
    return st.session_state.orchestrator


# --- Sidebar Setup ---
with st.sidebar:
    st.markdown("## ⚙️ Setup")
    st.markdown("### 🔑 Groq API Key")
    st.caption("Get a free key at [console.groq.com](https://console.groq.com)")

    load_dotenv()
    api_key_input = st.text_input(
        "API Key",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        placeholder="gsk_...",
        label_visibility="collapsed",
    )

    if api_key_input:
        os.environ["GROQ_API_KEY"] = api_key_input

    api_key_set = bool(api_key_input.strip())
    st.divider()

    st.markdown("### 🤖 LLM Model")
    models = {
        "⚡ LLaMA 3.1 8B (fast)": "llama-3.1-8b-instant",
        "🧠 LLaMA 3.3 70B (best)": "llama-3.3-70b-versatile",
        "🔮 LLaMA 3.1 70B": "llama-3.1-70b-versatile",
        "💎 Gemma 2 9B": "gemma2-9b-it",
    }
    selected_label = st.selectbox("Model", list(models.keys()), label_visibility="collapsed")
    os.environ["LLM_MODEL"] = models[selected_label]
    st.divider()

    st.markdown("### 📄 Upload Document")
    uploaded_file = st.file_uploader(
        "Upload",
        type=["pdf", "docx", "txt", "md", "pptx", "xlsx", "html"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        if not api_key_set:
            st.error("⚠️ Please enter your Groq API key first.")
        elif st.button("🚀 Process Document", use_container_width=True):
            progress_bar = st.progress(0.0)
            status_text = st.empty()

            def progress_cb(msg: str, pct: float):
                progress_bar.progress(min(pct, 1.0))
                status_text.caption(msg)

            try:
                suffix = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                orch = get_orchestrator()

                if st.session_state.document_loaded:
                    orch.reset()
                    st.session_state.chat_history = []

                result = orch.ingest_document(tmp_path, progress_cb)

                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

                if result.get("status") == "success":
                    st.session_state.document_loaded = True
                    progress_bar.progress(1.0)
                    st.success(f"✅ Loaded! {result['chunks']} chunks indexed.")
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error during ingestion')}")

            except Exception as e:
                st.error(f"❌ Error: {e}")

    st.divider()
    render_agent_status(st.session_state.active_agents)
    st.divider()

    if st.session_state.document_loaded and st.session_state.orchestrator:
        render_doc_info(st.session_state.orchestrator.stats)
        if st.button("🗑️ Clear Document", use_container_width=True):
            st.session_state.orchestrator.reset()
            st.session_state.document_loaded = False
            st.session_state.chat_history = []
            st.session_state.active_agents = {k: False for k in st.session_state.active_agents}
            st.rerun()


# --- Main Application Area ---
render_header()

if not api_key_set:
    st.warning(
        "**Setup Required:** Enter your free Groq API key in the sidebar.\n\n"
        "👉 Get one at [console.groq.com](https://console.groq.com) — free, no credit card needed."
    )

tab_qa, tab_summary, tab_about = st.tabs(["💬 Ask Questions", "📋 Summarize", "ℹ️ About"])

# Q&A View
with tab_qa:
    if not st.session_state.document_loaded:
        render_empty_state()
    else:
        if not st.session_state.chat_history:
            st.markdown(
                '<div style="text-align:center; padding:2rem; color:#64748b; font-size:0.9rem;">'
                '💡 Ask any question about your document.'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            for msg in st.session_state.chat_history:
                render_chat_message(
                    role=msg["role"],
                    content=msg["content"],
                    sources=msg.get("sources", ""),
                    warning=msg.get("warning", ""),
                    confidence=msg.get("confidence", 1.0),
                )

        st.divider()
        
        with st.form(key="qa_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                user_question = st.text_input(
                    "Ask a question",
                    placeholder="e.g. What is the main topic of this document?",
                    label_visibility="collapsed",
                )
            with col2:
                ask_btn = st.form_submit_button("Ask →", use_container_width=True)

        if ask_btn and user_question.strip():
            orch = get_orchestrator()
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            st.session_state.active_agents["Retrieval Agent"] = True
            st.session_state.active_agents["QA Agent"] = True

            with st.spinner("🔍 Retrieving and answering..."):
                try:
                    result = orch.ask_question(user_question, stream=False)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result.get("answer", "No answer generated."),
                        "sources": result.get("sources", ""),
                        "warning": result.get("warning", ""),
                        "confidence": result.get("confidence", 0.8),
                    })
                except Exception as e:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"❌ Error: {e}",
                        "sources": "",
                        "warning": "",
                        "confidence": 0.0,
                    })

            st.session_state.active_agents["Retrieval Agent"] = False
            st.session_state.active_agents["QA Agent"] = False
            st.rerun()

# Document Summarization View
with tab_summary:
    if not st.session_state.document_loaded:
        render_empty_state()
    else:
        st.markdown("### Document Summary")
        col1, col2 = st.columns([3, 1])
        
        summary_labels = {
            "comprehensive": " Comprehensive (Overview + Key Points + Conclusion)",
            "brief": " Brief (3-5 sentences)",
            "bullet_points": "• Bullet Points (8-12 key points)",
            "key_facts": " Key Facts & Data Only",
        }
        
        with col1:
            summary_type = st.selectbox(
                "Summary type",
                options=list(summary_labels.keys()),
                format_func=lambda x: summary_labels[x],
            )
        with col2:
            st.write("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
            summarize_btn = st.button("Generate →", use_container_width=True)

        if summarize_btn:
            orch = get_orchestrator()
            st.session_state.active_agents["Summarizer Agent"] = True

            with st.spinner("📝 Generating summary..."):
                try:
                    result = orch.summarize_document(summary_type=summary_type, stream=False)
                    summary_text = result.get("summary", "Failed to generate summary.")

                    st.markdown(f'<div class="summary-output">{summary_text}</div>', unsafe_allow_html=True)
                    st.download_button(
                        "⬇️ Download Summary",
                        data=summary_text,
                        file_name=f"summary_{summary_type}.txt",
                        mime="text/plain",
                    )
                    st.caption(
                        f"Generated from {result.get('chunk_count', 0)} chunks · "
                        f"{result.get('context_chars', 0):,} characters processed"
                    )
                except Exception as e:
                    st.error(f"Summary error: {e}")
                    if "api_key" in str(e).lower() or "groq_api_key" in str(e).lower():
                        st.info("💡 Check that your Groq API key is entered correctly in the sidebar.")

            st.session_state.active_agents["Summarizer Agent"] = False

# Technical Specifications View
with tab_about:
    st.markdown("""
## 🧠 Multi-Agent RAG System

**100% free** Retrieval-Augmented Generation — no OpenAI, no paid APIs.

---

### 🤖 Agent Architecture

| Agent | Role |
|-------|------|
| **Orchestrator** | Routes tasks, coordinates all agents |
| **Ingestion Agent** | Parses documents, chunks, embeds |
| **Retrieval Agent** | Semantic search over vector store |
| **QA Agent** | Answers strictly from retrieved context |
| **Summarizer Agent** | Creates structured summaries |

---

### 🆓 Free Stack

| Component | Tool | Cost |
|-----------|------|------|
| LLM | Groq API (LLaMA 3 / Mixtral) | **FREE** |
| Embeddings | HuggingFace all-MiniLM-L6-v2 | **FREE** |
| Vector DB | FAISS (local) | **FREE** |
| Frontend | Streamlit | **FREE** |

---

### 🛡️ Anti-Hallucination

1. Context-only prompting — LLM never uses outside knowledge
2. Source citations on every answer
3. Post-generation grounding check
4. Confidence score displayed visually
5. Honest "I don't know" when context is insufficient
6. Temperature = 0 for deterministic responses

---

### 📁 Supported Formats
PDF · DOCX · TXT · Markdown · PPTX · XLSX · HTML
    """)