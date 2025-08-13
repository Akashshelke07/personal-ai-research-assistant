
Personal AI Research Assistant (Local)

This project is a powerful, 100% local AI research assistant that allows you to ask questions about your own documents. It uses a Retrieval-Augmented Generation (RAG) pipeline to provide accurate answers based solely on the content of the files you provide.

The entire system, from the database to the AI model, runs on your own machine, ensuring complete privacy and no reliance on paid API keys.

✨ Features

📚 Document Ingestion: Supports PDF (.pdf), Markdown (.md), and text (.txt) files.

🧠 Local Question-Answering: Uses a local Large Language Model (LLM) to understand and answer questions based on the ingested documents.

🌐 Simple Web Interface: Interact with your AI through an easy-to-use web UI.

🗣️ Text-to-Speech: Convert the AI's answers into spoken words with a single click.

🔒 Completely Private: All data and models are stored and run locally. Nothing ever leaves your machine.

⚙️ Extensible: Built with a modular service-based architecture, making it easy to add new features.

🛠️ Tech Stack

Backend: Python, FastAPI, Uvicorn

AI / ML:

Framework: LangChain

LLM: GPT4All (specifically configured for GGUF models like Mistral)

Embeddings: Sentence Transformers (via Hugging Face)

Core Library: PyTorch

Vector Database: ChromaDB

Text-to-Speech: pyttsx3

Frontend: Plain HTML, CSS, and JavaScript

📂 Project Structure
code
Code
download
content_copy
expand_less

personal-ai-research-assistant/
├── data/                  # <-- Place your .pdf and .txt files here
├── models/                # <-- Place your downloaded LLM model file here
├── services/
│   ├── ingestion/         # Handles document loading and database creation
│   ├── langchain_api/     # The main FastAPI backend
│   ├── tts/               # Text-to-speech service logic
│   └── web/               # Contains the HTML frontend
├── .env                   # Main configuration file (you must create this)
├── requirements.txt       # All Python dependencies
└── run_all.py             # Main script to start the application
🚀 Getting Started

Follow these steps to get your Personal AI Research Assistant running.

1. Clone the Repository
code
Bash
download
content_copy
expand_less
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END
git clone https://github.com/YourUsername/personal-ai-research-assistant.git
cd personal-ai-research-assistant
2. Set Up the Python Virtual Environment

It's highly recommended to use a virtual environment to keep dependencies isolated.

code
Bash
download
content_copy
expand_less
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END
# Create the virtual environment
python -m venv .venv

# Activate it (on Windows Git Bash)
source .venv/Scripts/activate
3. Install Dependencies

Install all the required Python packages from the requirements.txt file.

code
Bash
download
content_copy
expand_less
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END
pip install -r requirements.txt
4. Download the AI Model

This project requires a local LLM to generate answers. The model file is large and must be downloaded manually.

Download the following model:

Model: mistral-7b-openorca.Q4_0.gguf

Link: https://gpt4all.io/models/gguf/mistral-7b-openorca.Q4_0.gguf

Place the downloaded file inside the models/ directory.

5. Configure Your Environment

Create a file named .env in the main project directory. Copy the contents of .env.example into it, or use the template below. This file tells the application where to find the model.

File: .env

code
Env
download
content_copy
expand_less
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END
# --- ChromaDB Settings ---
CHROMA_DIR=./chroma_db
CHROMA_COLLECTION_NAME=personal_ai_research_assistant

# --- Embedding Model ---
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# --- Local LLM Settings ---
# This path MUST match the model you downloaded
LLM_MODEL_PATH=./models/mistral-7b-openorca.Q4_0.gguf
6. Ingest Your Documents

Place your .pdf, .txt, or .md files into the data/ directory. A sample_research.pdf is included.

Run the ingestion script. This will read your documents, process them, and store them in the chroma_db vector database.

code
Bash
download
content_copy
expand_less
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END
python services/ingestion/ingest.py
▶️ Running the Application

After completing the setup, you can run the main application using the run_all.py script. This will check if the database exists and then start the API server.

code
Bash
download
content_copy
expand_less
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END
python run_all.py

The terminal will show Uvicorn running on http://0.0.0.0:8000. Your assistant is now ready!

💡 How to Use
Web Interface (Recommended)

Open the index.html file located in services/web/ in your web browser. The easiest way is to use the Live Server extension in VS Code (right-click the file and select "Open with Live Server").

Type your question into the input box.

Click "Ask" to get a text answer.

Click "Speak Answer" to hear the response read aloud.

API (For Advanced Use)

You can also interact with the API directly. Here is an example using curl in a Git Bash terminal:

code
Bash
download
content_copy
expand_less
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END
curl -X POST "http://127.0.0.1:8000/ask" \
-H "Content-Type: application/json" \
-d '{"query": "What is the main topic of the sample research?"}'
