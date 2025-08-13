

# Personal AI Research Assistant (Local)

A **100% local, privacy-focused AI research assistant** that can answer questions about your own documents using a **Retrieval-Augmented Generation (RAG)** pipeline.

All processing — including the database, vector search, and AI inference — happens **entirely on your machine**. No internet calls, no API keys, no data leaks.

---

## ✨ Features

* 📚 **Document Ingestion** — Supports **PDF (.pdf)**, **Markdown (.md)**, and **Text (.txt)** files.
* 🧠 **Local Question Answering** — Powered by a local LLM (no API needed).
* 🌐 **Simple Web Interface** — Easy-to-use browser UI.
* 🗣 **Text-to-Speech** — Convert answers to speech with one click.
* 🔒 **Completely Private** — Nothing leaves your machine.
* ⚙ **Extensible** — Modular, service-based architecture for easy feature additions.

---

## 🛠 Tech Stack

**Backend:** Python, FastAPI, Uvicorn
**AI / ML:** LangChain, GPT4All (GGUF models, e.g., Mistral), Sentence Transformers (Hugging Face), PyTorch
**Vector Database:** ChromaDB
**Text-to-Speech:** pyttsx3
**Frontend:** HTML, CSS, JavaScript

---

## 📂 Project Structure

```
personal-ai-research-assistant/
├── data/                  # Your .pdf, .md, and .txt files
├── models/                # Local LLM model file
├── services/
│   ├── ingestion/         # Document loading and database creation
│   ├── langchain_api/     # FastAPI backend
│   ├── tts/               # Text-to-speech logic
│   └── web/               # Frontend (HTML/CSS/JS)
├── .env                   # Configuration file (create this)
├── requirements.txt       # Python dependencies
└── run_all.py             # Main startup script
```

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YourUsername/personal-ai-research-assistant.git
cd personal-ai-research-assistant
```

### 2️⃣ Set Up a Virtual Environment

```bash
python -m venv .venv
# Activate (Windows Git Bash)
source .venv/Scripts/activate
# Activate (Linux/Mac)
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Download the AI Model

Download **mistral-7b-openorca.Q4\_0.gguf**:
🔗 [Download Link](https://gpt4all.io/models/gguf/mistral-7b-openorca.Q4_0.gguf)

Place it in the `models/` folder.

### 5️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```env
# --- ChromaDB Settings ---
CHROMA_DIR=./chroma_db
CHROMA_COLLECTION_NAME=personal_ai_research_assistant

# --- Embedding Model ---
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# --- Local LLM Settings ---
LLM_MODEL_PATH=./models/mistral-7b-openorca.Q4_0.gguf
```

### 6️⃣ Ingest Your Documents

Place `.pdf`, `.txt`, or `.md` files into `data/`. Then run:

```bash
python services/ingestion/ingest.py
```

---

## ▶ Running the Application

```bash
python run_all.py
```

This starts Uvicorn at **[http://0.0.0.0:8000](http://0.0.0.0:8000)**.

---

## 💡 Usage

### **Web Interface** (Recommended)

1. Open `services/web/index.html` in your browser.
2. Type a question and click **Ask**.
3. Click **Speak Answer** to hear it aloud.

*(Tip: In VS Code, right-click `index.html` → **Open with Live Server** for instant reload.)*

### **API**

Example using `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
-H "Content-Type: application/json" \
-d '{"query": "What is the main topic of the sample research?"}'
```

Do you want me to also **add screenshots and example outputs** so this README looks more appealing on GitHub?
