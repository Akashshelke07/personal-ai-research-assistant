# run_all.py
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"
DATA_DIR = BASE_DIR / "data"

# Read the model path from the .env file to check if it exists
MODEL_PATH_STR = os.getenv("LLM_MODEL_PATH")
if not MODEL_PATH_STR:
    print("❌ LLM_MODEL_PATH not set in .env file. Please check your .env file.")
    exit()

# Create the full, absolute path to the model
MODEL_PATH = BASE_DIR / MODEL_PATH_STR

def run(cmd, cwd=None):
    print(f"\n=== Running: {cmd} ===")
    subprocess.run(cmd, cwd=cwd, shell=True, check=True)

def ensure_ingestion():
    """Ensure Chroma DB exists by running ingestion if needed."""
    if not CHROMA_DIR.exists() or not any(CHROMA_DIR.iterdir()):
        if not DATA_DIR.exists() or not any(DATA_DIR.iterdir()):
            print(f"⚠️ No files in {DATA_DIR} — place some .pdf/.txt there first.")
            return False
        print("📦 Chroma DB missing — running ingestion...")
        run(f"python \"{BASE_DIR / 'services' / 'ingestion' / 'ingest.py'}\"")
    else:
        print("✅ Chroma DB already exists — skipping ingestion.")
    return True

def main():
    """Main function to run the application."""
    # Check if the model file actually exists at the configured path
    if not MODEL_PATH.exists():
        print(f"❌ Model not found at {MODEL_PATH}")
        print(f"Please ensure the path in your .env file is correct and the model file is present.")
        return

    # Run ingestion if needed
    if not ensure_ingestion():
        return

    # Start the FastAPI server
    print("\n🚀 Starting LangChain API...")
    run(f"uvicorn services.langchain_api.app:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    main()