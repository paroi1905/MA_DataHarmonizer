import os
import json
import asyncio
from typing import List, Optional
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

from rag import create_rag_chain, get_vectorstore, RateLimitedEmbeddings
from ingest import run_ingestion_pipeline, ingest_single_file
from semantic import RateLimitedEmbeddings

load_dotenv()

app = FastAPI(title="RAG Ingestion Framework")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Schema Definitions ===
class QueryRequest(BaseModel):
    question: str

class Source(BaseModel):
    company: str
    year: int
    file: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float

class IngestRequest(BaseModel):
    files: List[str] = []

# === Global Pipeline Initializer ===
rag_pipeline = None

@app.on_event("startup")
def startup_event():
    global rag_pipeline
    rag_pipeline = create_rag_chain()


# === API Endpoints ===

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG Pipeline not initialized.")
    try:
        return rag_pipeline(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# === Documents Tab Endpoints ===

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in (".pdf", ".json"):
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
        file_path = os.path.join(DATA_DIR, file.filename)
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        saved_files.append(file.filename)
    return {"uploaded_files": saved_files}

@app.post("/ingest")
async def ingest_documents(req: IngestRequest):
    if req is None or not req.files:
        raise HTTPException(status_code=400, detail="No files specified for ingestion")

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    file_paths = [os.path.join(data_dir, f) for f in req.files]
    missing = [f for f, p in zip(req.files, file_paths) if not os.path.exists(p)]
    if missing:
        raise HTTPException(status_code=400, detail=f"Files not found: {missing}")

    LOG_STEPS = [
        "Receiving documents",
        "Extracting financial data",
        "Creating Unified Document Model",
        "Splitting into semantic chunks",
        "Storing chunks in database",
    ]

    executor = ThreadPoolExecutor(max_workers=1)

    async def event_stream():
        global rag_pipeline
        loop = asyncio.get_running_loop()

        for step in LOG_STEPS:
            yield f"STEP:{step}\n"
            await asyncio.sleep(0.8)

        for fp in file_paths:
            yield f"FILE:{os.path.basename(fp)}\n"
            await loop.run_in_executor(executor, ingest_single_file, fp)

        rag_pipeline = create_rag_chain()
        yield "DONE\n"

    return StreamingResponse(event_stream(), media_type="text/plain")

@app.get("/documents")
async def list_documents():
    try:
        embeddings = RateLimitedEmbeddings(chunk_size=50)
        vectorstore = get_vectorstore(embeddings)
        collection_data = vectorstore.get(include=["metadatas"])
        metadatas = collection_data.get("metadatas", [])
    except Exception:
        return []

    seen = set()
    documents = []
    for meta in metadatas:
        if meta is None:
            continue
        filename = meta.get("file", "")
        if filename in seen:
            continue
        seen.add(filename)
        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        documents.append({
            "company": meta.get("company", "Unknown"),
            "year": meta.get("year", 0),
            "file": filename,
            "format": ext if ext in ("pdf", "json") else "pdf",
        })
    return documents


# === Frontend Directory Serving ===
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "static")

@app.get("/")
def serve_frontend_index():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Frontend not found."}

@app.get("/{filename}")
def serve_frontend_assets(filename: str):
    file_path = os.path.join(frontend_dir, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")
