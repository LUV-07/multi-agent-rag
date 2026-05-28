"""
test_setup.py — Quick validation that everything is installed and configured.
Run: python test_setup.py
"""
import sys
import os

print("=" * 55)
print("  Multi-Agent RAG — Setup Validation")
print("=" * 55)

errors = []
warnings = []

# ── 1. Python version ──────────────────────────────────────
print("\n[1/8] Python version...", end=" ")
if sys.version_info < (3, 9):
    errors.append(f"Python 3.9+ required, got {sys.version}")
    print("❌ FAIL")
else:
    print(f"✅ {sys.version.split()[0]}")

# ── 2. Env file ────────────────────────────────────────────
print("[2/8] .env file...", end=" ")
if os.path.exists(".env"):
    print("✅ Found")
else:
    warnings.append(".env file missing. Copy .env.example → .env and add your Groq API key.")
    print("⚠️  Not found (copy .env.example → .env)")

# ── 3. Groq API key ────────────────────────────────────────
print("[3/8] Groq API key...", end=" ")
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GROQ_API_KEY", "")
if api_key and api_key != "your_groq_api_key_here":
    print("✅ Set")
else:
    warnings.append("GROQ_API_KEY not set. Get free key at https://console.groq.com")
    print("⚠️  Not configured")

# ── 4. Core imports ────────────────────────────────────────
print("[4/8] Core packages...", end=" ")
missing = []
packages = [
    ("streamlit", "streamlit"),
    ("groq", "groq"),
    ("faiss", "faiss-cpu"),
    ("fitz", "pymupdf"),
    ("docx", "python-docx"),
    ("sentence_transformers", "sentence-transformers"),
    ("numpy", "numpy"),
    ("dotenv", "python-dotenv"),
    ("langchain", "langchain"),
    ("tenacity", "tenacity"),
    ("loguru", "loguru"),
]
for mod, pkg in packages:
    try:
        __import__(mod)
    except ImportError:
        missing.append(pkg)

if missing:
    errors.append(f"Missing packages: {', '.join(missing)}\nRun: pip install -r requirements.txt")
    print(f"❌ Missing: {', '.join(missing)}")
else:
    print("✅ All installed")

# ── 5. FAISS ───────────────────────────────────────────────
print("[5/8] FAISS vector store...", end=" ")
try:
    import faiss
    import numpy as np
    dim = 64
    index = faiss.IndexFlatIP(dim)
    vecs = np.random.rand(3, dim).astype("float32")
    index.add(vecs)
    D, I = index.search(vecs[:1], 1)
    print("✅ Working")
except Exception as e:
    errors.append(f"FAISS test failed: {e}")
    print(f"❌ {e}")

# ── 6. Embedding model ─────────────────────────────────────
print("[6/8] Embedding model...", end=" ")
try:
    from sentence_transformers import SentenceTransformer
    # Just test import, don't download model here
    print("✅ sentence-transformers ready")
except Exception as e:
    errors.append(f"sentence-transformers failed: {e}")
    print(f"❌ {e}")

# ── 7. Streamlit ───────────────────────────────────────────
print("[7/8] Streamlit...", end=" ")
try:
    import streamlit as st
    print(f"✅ v{st.__version__}")
except Exception as e:
    errors.append(f"Streamlit import failed: {e}")
    print(f"❌ {e}")

# ── 8. Project structure ───────────────────────────────────
print("[8/8] Project files...", end=" ")
required_files = [
    "app.py", "config.py", "requirements.txt",
    "agents/orchestrator.py", "agents/ingestion_agent.py",
    "agents/retrieval_agent.py", "agents/qa_agent.py",
    "agents/summarizer_agent.py", "core/document_processor.py",
    "core/embeddings.py", "core/vector_store.py", "core/llm.py",
    "utils/chunker.py", "utils/validators.py",
    "ui/styles.py", "ui/components.py",
]
missing_files = [f for f in required_files if not os.path.exists(f)]
if missing_files:
    errors.append(f"Missing files: {', '.join(missing_files)}")
    print(f"❌ Missing: {len(missing_files)} files")
else:
    print(f"✅ All {len(required_files)} files present")

# ── Summary ────────────────────────────────────────────────
print("\n" + "=" * 55)
if errors:
    print("❌ ERRORS (must fix):")
    for e in errors:
        print(f"   • {e}")
if warnings:
    print("⚠️  WARNINGS (optional):")
    for w in warnings:
        print(f"   • {w}")

if not errors:
    print("🎉 Setup complete! Run: streamlit run app.py")
else:
    print("\n❌ Fix errors above, then run: streamlit run app.py")
print("=" * 55)
