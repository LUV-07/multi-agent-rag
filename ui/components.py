import streamlit as st


def render_header():
    st.markdown("""
    <div class="app-header">
        <div>
            <h1>🧠 Multi-Agent RAG</h1>
            <p>Upload a document · Ask questions · Get accurate, grounded answers</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card(label: str, value: str):
    st.markdown(f"""
    <div class="stat-card">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_chat_message(role: str, content: str, sources: str = "", warning: str = "", confidence: float = 1.0):
    icon = "👤" if role == "user" else "🤖"
    label = "You" if role == "user" else "RAG Assistant"

    st.markdown(f"""
    <div class="chat-message {role}">
        <div class="role-label">{icon} {label}</div>
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)

    if sources and role == "assistant":
        # Confidence bar color
        if confidence >= 0.7:
            bar_color = "#34d399"
        elif confidence >= 0.4:
            bar_color = "#fbbf24"
        else:
            bar_color = "#f87171"

        st.markdown(f"""
        <div class="sources-box">
            <div class="sources-header">📎 Sources</div>
            <pre style="margin:0; white-space:pre-wrap;">{sources}</pre>
            <div class="confidence-bar" style="margin-top:0.5rem;">
                <div class="confidence-fill" style="width:{confidence*100:.0f}%; background:{bar_color};"></div>
            </div>
            <div style="font-size:0.7rem; color:#64748b; margin-top:0.25rem;">
                Confidence: {confidence*100:.0f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    if warning:
        st.markdown(f'<div class="grounding-warning">{warning}</div>', unsafe_allow_html=True)


def render_agent_status(agents: dict):
    """Display which agents are active."""
    st.markdown("### 🤖 Agent Status")
    for name, is_active in agents.items():
        status = "active" if is_active else "idle"
        icon = "🟢" if is_active else "⚪"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">
            <span>{icon}</span>
            <span style="font-size:0.85rem; color:#e2e8f0;">{name}</span>
            <span class="agent-badge {status}">{status}</span>
        </div>
        """, unsafe_allow_html=True)


def render_empty_state():
    st.markdown("""
    <div style="
        text-align: center;
        padding: 3rem 2rem;
        background: #1a1d27;
        border: 2px dashed #2d3148;
        border-radius: 12px;
        margin: 1rem 0;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">📄</div>
        <div style="color: #94a3b8; font-size: 0.95rem;">
            No document loaded yet.<br>
            Upload a file in the sidebar to get started.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_doc_info(stats: dict):
    """Display document stats after ingestion."""
    st.markdown(f"""
    <div style="
        background: rgba(52, 211, 153, 0.08);
        border: 1px solid rgba(52, 211, 153, 0.3);
        border-radius: 10px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 1rem;
    ">
        <div style="color: #34d399; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.4rem;">
            ✅ Document Ready
        </div>
        <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.6;">
            📄 {stats.get('ingested_files', 0)} file(s) loaded<br>
            📦 {stats.get('total_chunks', 0):,} chunks indexed<br>
            💬 {stats.get('conversation_turns', 0)} questions asked
        </div>
    </div>
    """, unsafe_allow_html=True)
