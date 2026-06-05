
CUSTOM_CSS = """
<style>
/* ── Google Font ─────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Root Variables ──────────────────────────────────── */
:root {
    --primary: #6366f1;
    --primary-light: #818cf8;
    --accent: #22d3ee;
    --success: #34d399;
    --warning: #fbbf24;
    --danger: #f87171;
    --bg-dark: #0f1117;
    --bg-card: #1a1d27;
    --bg-input: #242736;
    --border: #2d3148;
    --text: #e2e8f0;
    --text-muted: #94a3b8;
    --radius: 12px;
}

/* ── Global ──────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

.stApp {
    background: var(--bg-dark);
}

/* ── Hide default Streamlit elements ─────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; max-width: 1100px; }

/* ── Header banner ───────────────────────────────────── */
.app-header {
    background: linear-gradient(135deg, #1a1d27 0%, #1e2035 50%, #1a1d27 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.app-header h1 {
    font-size: 1.6rem;
    font-weight: 600;
    background: linear-gradient(90deg, var(--primary-light), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.app-header p {
    color: var(--text-muted);
    font-size: 0.875rem;
    margin: 0.2rem 0 0;
}

/* ── Sidebar ─────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-card);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--primary-light);
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* ── Cards ───────────────────────────────────────────── */
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
}
.stat-card .label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 500;
}
.stat-card .value {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--primary-light);
    font-family: 'DM Mono', monospace;
}

/* ── Chat messages ───────────────────────────────────── */
.chat-message {
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    border: 1px solid var(--border);
    line-height: 1.65;
}
.chat-message.user {
    background: linear-gradient(135deg, #1e2140 0%, #252944 100%);
    border-color: var(--primary);
    border-left: 3px solid var(--primary);
}
.chat-message.assistant {
    background: var(--bg-card);
    border-left: 3px solid var(--accent);
}
.chat-message .role-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.chat-message.user .role-label { color: var(--primary-light); }
.chat-message.assistant .role-label { color: var(--accent); }

/* ── Source citation box ─────────────────────────────── */
.sources-box {
    background: #141620;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-top: 0.75rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-muted);
}
.sources-box .sources-header {
    color: var(--warning);
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.4rem;
}

/* ── Warning / grounding alert ───────────────────────── */
.grounding-warning {
    background: rgba(251, 191, 36, 0.1);
    border: 1px solid rgba(251, 191, 36, 0.3);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: 0.82rem;
    color: var(--warning);
    margin-top: 0.5rem;
}

/* ── Confidence meter ────────────────────────────────── */
.confidence-bar {
    height: 4px;
    border-radius: 2px;
    background: var(--border);
    margin-top: 0.5rem;
    overflow: hidden;
}
.confidence-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.4s ease;
}

/* ── Upload zone ─────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--bg-card) !important;
    padding: 1rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--primary) !important;
}

/* ── Buttons ─────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--primary), #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.2rem !important;
    transition: opacity 0.2s, transform 0.1s !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Text inputs ─────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
}

/* ── Select box ──────────────────────────────────────── */
.stSelectbox > div > div {
    background: var(--bg-input) !important;
    border-color: var(--border) !important;
    border-radius: 8px !important;
}

/* ── Progress bar ────────────────────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
    border-radius: 4px !important;
}

/* ── Success/Error/Info boxes ────────────────────────── */
.stSuccess {
    background: rgba(52, 211, 153, 0.1) !important;
    border-color: var(--success) !important;
    color: var(--success) !important;
    border-radius: 8px !important;
}
.stError {
    background: rgba(248, 113, 113, 0.1) !important;
    border-color: var(--danger) !important;
    border-radius: 8px !important;
}
.stInfo {
    background: rgba(99, 102, 241, 0.1) !important;
    border-color: var(--primary) !important;
    border-radius: 8px !important;
}

/* ── Tab styling ─────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    color: var(--text-muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 6px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--primary) !important;
    color: white !important;
}

/* ── Agent status badge ──────────────────────────────── */
.agent-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.agent-badge.active {
    background: rgba(99, 102, 241, 0.2);
    color: var(--primary-light);
    border: 1px solid rgba(99, 102, 241, 0.4);
}
.agent-badge.idle {
    background: rgba(148, 163, 184, 0.1);
    color: var(--text-muted);
    border: 1px solid var(--border);
}

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-dark); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ── Summary output ──────────────────────────────────── */
.summary-output {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--success);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    line-height: 1.7;
    white-space: pre-wrap;
}
</style>
"""
