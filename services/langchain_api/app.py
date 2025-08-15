import os
import sys
import json
import uuid
import tempfile
import traceback
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from starlette.staticfiles import StaticFiles
from pdf2image import convert_from_path
import pytesseract

# --- .ENV LOADING ---
try:
    project_root = Path(__file__).resolve().parents[2]
    env_path = project_root / '.env'
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path)
except Exception as e:
    print(f"ERROR: Failed to load .env file: {e}", file=sys.stderr)

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# --- LangChain Imports ---
from langchain_community.llms import Ollama
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- App Setup ---
app = FastAPI(title="AI Research Assistant v3.0 (Stable)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

document_cache = {}

# --- Pydantic Models ---
class UploadResponse(BaseModel):
    session_id: str
    filename: str

class AnalyzeRequest(BaseModel):
    session_id: str

class ChatHistory(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    query: str
    history: List[ChatHistory] = Field(default_factory=list)

# --- Core Logic ---
def get_analysis_prompts():
    return {
        "Title": "What is the full title of this paper?",
        "Authors": "List all authors.",
        "Year": "What is the publication year?",
        "Journal": "What is the journal or conference name?",
        "Abstract": "Summarize the abstract.",
        "Research Gap": "What specific research gap does this study fill?",
        "Methodology": "Briefly describe the study's methodology.",
        "Key Findings": "Summarize the main results in bullet points.",
        "Limitations": "What were the study's limitations?",
        "Conclusion": "Summarize the paper's main conclusion."
    }

async def stream_analysis(full_text: str, llm: Ollama):
    prompts = get_analysis_prompts()
    for key, question in prompts.items():
        prompt = f"Based on the text of a research paper provided below, answer the question.\n\nQuestion: {question}\n\nText:\n---\n{full_text}\n---\n\nAnswer:"
        response_content = ""
        async for chunk in llm.astream(prompt):
            response_content += chunk
        yield f"data: {json.dumps({'key': key, 'value': response_content.strip()})}\n\n"

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        print("Loading PDF with PyPDFLoader...")
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()

        # Check if text extraction failed (likely image-based PDF)
        if not docs or not any(doc.page_content.strip() for doc in docs):
            print("No text extracted with PyPDFLoader, attempting OCR...")
            try:
                # Convert PDF to images
                images = convert_from_path(tmp_path)
                extracted_text = ""
                for image in images:
                    # Extract text from each image using Tesseract
                    text = pytesseract.image_to_string(image)
                    extracted_text += text + "\n\n"
                
                if not extracted_text.strip():
                    raise HTTPException(
                        status_code=400,
                        detail="Could not extract text from the PDF even with OCR. Please ensure the PDF contains readable content."
                    )

                # Create a LangChain document from OCR-extracted text
                from langchain_core.documents import Document
                docs = [Document(page_content=extracted_text, metadata={"source": file.filename})]
            except Exception as ocr_error:
                os.unlink(tmp_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"OCR failed: {str(ocr_error)}. Please use a text-based PDF or ensure Tesseract is properly installed."
                )

        os.unlink(tmp_path)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = text_splitter.split_documents(docs)
        
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={'device': 'cpu'})
        vector_store = Chroma.from_documents(chunks, embeddings)

        session_id = str(uuid.uuid4())
        document_cache[session_id] = {
            "db": vector_store,
            "full_text": "\n\n".join(doc.page_content for doc in docs)
        }
        
        print(f"Document processed successfully. Session ID: {session_id}")
        return {"session_id": session_id, "filename": file.filename}

    except HTTPException as http_exc:
        print(f"HTTP Exception: {http_exc.detail}", file=sys.stderr)
        raise http_exc
    except Exception as e:
        tb_str = traceback.format_exc()
        print(f"--- ❌ FATAL ERROR DURING UPLOAD ---\n{tb_str}", file=sys.stderr)
        return JSONResponse(
            status_code=500,
            content={"detail": f"An internal server error occurred: {e}"}
        )

@app.post("/analyze")
async def analyze_paper(req: AnalyzeRequest):
    if req.session_id not in document_cache:
        raise HTTPException(status_code=404, detail="Invalid session")
    cached_data = document_cache[req.session_id]
    llm = Ollama(model=LLM_MODEL_NAME)
    return StreamingResponse(stream_analysis(cached_data["full_text"], llm), media_type="text/event-stream")

@app.post("/chat")
async def chat_with_document(req: ChatRequest):
    if req.session_id not in document_cache:
        raise HTTPException(status_code=404, detail="Invalid session")
    async def stream_generator():
        try:
            vector_store = document_cache[req.session_id]["db"]
            llm = Ollama(model=LLM_MODEL_NAME)
            retriever = vector_store.as_retriever(search_kwargs={"k": 4})
            relevant_docs = retriever.invoke(req.query)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            history_str = "\n".join([f"{h.role}: {h.content}" for h in req.history])
            system_prompt = "You are an expert research assistant. Answer the user's question based on the provided context from the research paper and the conversation history. If the answer isn't in the context, say so."
            prompt = f"{system_prompt}\n\nCONVERSATION HISTORY:\n{history_str}\n\nCONTEXT FROM DOCUMENT:\n{context}\n\nUSER QUESTION:\n{req.query}\n\nANSWER:"
            async for chunk in llm.astream(prompt):
                yield f"data: {json.dumps({'token': chunk})}\n\n"
            yield f"event: end\ndata: [DONE]\n\n"
        except Exception as e:
            error_msg = f"Error during chat: {e}"
            print(error_msg, file=sys.stderr)
            traceback.print_exc()
            yield f"event: error\ndata: {json.dumps({'error': error_msg})}\n\n"
    return StreamingResponse(stream_generator(), media_type="text/event-stream")

# --- Static File Serving ---
web_files_path = project_root / "services" / "web"
@app.get("/")
async def read_index():
    return FileResponse(web_files_path / "index.html")

app.mount("/static", StaticFiles(directory=web_files_path), name="static")