import os
import subprocess
from pathlib import Path

def preload_models():
    """
    Downloads and prepares the embedding model before starting the server.
    This prevents timeouts and crashes on the first upload.
    """
    print("\n--- Pre-loading AI Embedding Model ---")
    print("This may take a few minutes on the first run as it downloads the model...")
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        from dotenv import load_dotenv
        
        load_dotenv() # Load .env to get the model name
        EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        
        if not EMBEDDING_MODEL:
            raise ValueError("EMBEDDING_MODEL not set in .env file.")

        HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={'device': 'cpu'})
        
        print("✅ AI Embedding Model is ready.")
    except Exception as e:
        print("\n--- ❌ ERROR DURING MODEL PRE-LOADING ---")
        import traceback
        traceback.print_exc()
        print("\nCould not download or load the AI model. Please check your internet connection and the model name in your .env file.")
        exit()

def run(cmd):
    """Runs a command."""
    print(f"\n=== Running: {cmd} ===")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except KeyboardInterrupt:
        print("\n\nUser interrupted the process. Shutting down.")

def main():
    """Main function to run the application."""
    preload_models()
    
    print("\n🚀 Starting Advanced AI Research Assistant v2.0...")
    api_dir = Path(__file__).resolve().parent / 'services' / 'langchain_api'
    command = f'uvicorn services.langchain_api.app:app --host 0.0.0.0 --port 8000 --reload --reload-dir "{api_dir}"'
    run(command)

if __name__ == "__main__":
    main()