#!/usr/bin/env bash
# =====================================================================
# Personal AI Research Assistant (FREE / LOCAL)
# One-shot scaffolder: folders, code, requirements, README, and model.
# Works on Windows (Git Bash), macOS, and Linux.
# =====================================================================
set -euo pipefail

echo "📦 Scaffolding project..."

# --- FOLDERS ----------------------------------------------------------
mkdir -p data chroma_db models
mkdir -p services/ingestion services/langchain_api services/tts services/web
# ensure importable packages
touch services/__init__.py services/ingestion/__init__.py services/langchain_api/__init__.py services/tts/__init__.py

# --- .ENV EXAMPLE -----------------------------------------------------
cat > .env.example <<'ENV'
# Local paths (no paid keys needed)
CHROMA_DIR=./chroma_db
LLM_MODEL_PATH=./models/gpt4all-model.bin
ENV

# --- .GITIGNORE -------------------------------------------------------
cat > .gitignore <<'GI'
.venv/
__pycache__/
*.pyc
chroma_db/
models/*.bin
.env
GI

# --- README -----------------------------------------------------------
cat > README.md <<'MD'
# Personal AI Research Assistant (Free & Local)

## What this does
1) **Ingestion**: Reads files in `data/` (.txt, .md, .pdf), splits into chunks, builds **embeddings**, and persists them to **ChromaDB** in `chroma_db/`.
2) **Query**: Semantic search retrieves the most relevant chunks and passes them to a **local GPT4All LLM** → grounded answers.
3) **(Optional) Voice**: Local TTS speaks the answer.

## Quick Start (Git Bash / macOS / Linux)
```bash
python -m venv .venv

# Windows (Git Bash):
source .venv/Scripts/activate

# macOS/Linux:
# source .venv/bin/activate

# Install requirements
pip install -r services/ingestion/requirements.txt
pip install -r services/langchain_api/requirements.txt
pip install -r services/tts/requirements.txt

# Put a couple .txt/.md/.pdf files into ./data
python services/ingestion/ingest.py

# Start the API
uvicorn services.langchain_api.app:app --host 0.0.0.0 --port 8000 --reload

# Ask a question
curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"What is this project?"}'
