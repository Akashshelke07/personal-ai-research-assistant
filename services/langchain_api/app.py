import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pyttsx3

load_dotenv()

ROOT = os.getcwd()
CHROMA_DIR = os.getenv("CHROMA_DIR")
MODEL_PATH = os.getenv("LLM_MODEL_PATH")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME")

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import GPT4All

app = FastAPI(title="Personal AI Research Assistant (Local)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskReq(BaseModel):
    query: str
    k: int = 4

class SpeakReq(BaseModel):
    text: str

@app.post("/speak")
def speak(req: SpeakReq):
    try:
        engine = pyttsx3.init()
        engine.say(req.text)
        engine.runAndWait()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/ask")
def ask(req: AskReq):
    # This is the fix for the "meta tensor" error.
    model_kwargs = {'device': 'cpu'}
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs=model_kwargs
    )
    
    db = Chroma(
        persist_directory=CHROMA_DIR, 
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    docs = db.similarity_search(req.query, k=req.k)
    if not docs:
        return {"answer": "No documents / context found for your query."}

    context = "\n\n".join(d.page_content for d in docs)
    system_prompt = "You are a helpful assistant. Use ONLY the context to answer the user's question. If the answer is not in context, say you don't know."
    prompt = f"{system_prompt}\n\nCONTEXT:\n{context}\n\nQuestion: {req.query}\nAnswer:"

    # The modern GPT4All constructor is simple.
    llm_params = { "model": MODEL_PATH }

    try:
        llm = GPT4All(**llm_params)
        answer = llm.invoke(prompt)
    except Exception as e:
        return {"answer": f"[LLM load error: {e}]"}

    return {"answer": answer, "sources": [getattr(d, "metadata", {}) for d in docs]}