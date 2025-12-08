from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os

from app.utils.storage import ensure_bucket, put_object
from app.utils.vector import ensure_collection
from app.utils.tika_client import extract_text_via_tika
from app.utils.embeddings import embed_texts
from app.utils.vector import upsert_chunks, search_chunks
from app.utils.cache import Cache
from app.utils.llm import chat_completion
from app.pipelines.rag import rag_answer
from app.pipelines.cag import cag_answer
from app.pipelines.cag_rag import cag_rag_answer

app = FastAPI(title="RAG vs CAG vs CAG+RAG API")

# --- Settings from env ---
COLLECTION = os.getenv("INDEX_COLLECTION", "ai_chunks")
INDEX_VERSION = int(os.getenv("INDEX_VERSION", "1"))
CACHE_SIM_THRESHOLD = float(os.getenv("CACHE_SIM_THRESHOLD", "0.92"))

# Ensure storage and vector collection
ensure_bucket()
ensure_collection(collection=COLLECTION)

cache = Cache()

class IndexRequest(BaseModel):
    text: str
    doc_id: str
    source_uri: str | None = None
    chunk_size: int = 800
    overlap: int = 100

class QueryRequest(BaseModel):
    query: str
    k: int = 8
    max_tokens: int = 256

@app.get("/health")
def health():
    return {"status": "ok", "index_version": INDEX_VERSION}

# ---- Ingestion endpoints ----
@app.post("/ingest")
async def ingest(file: UploadFile = File(...), source_uri: str = Form(None)):
    """
    Accepts files (pdf, docx, html, txt, images) and uses Tika to extract text.
    Audio/video are routed to ASR service.
    Stores raw file in MinIO, returns doc_id + text length.
    """
    fname = file.filename
    content = await file.read()
    # Store raw
    put_object(fname, content)
    # Decide extraction path
    media_lower = (fname or "").lower()
    if any(media_lower.endswith(ext) for ext in [".mp3", ".wav", ".m4a", ".mp4", ".mov", ".mkv"]):
        # Send to ASR microservice
        import httpx
        asr_url = os.getenv("ASR_URL", "http://asr:7001")
        files = {"file": (fname, content, file.content_type)}
        r = httpx.post(f"{asr_url}/transcribe", files=files, timeout=None)
        r.raise_for_status()
        text = r.json().get("text", "")
    else:
        text = extract_text_via_tika(content, fname)

    doc_id = fname
    return {"doc_id": doc_id, "source_uri": source_uri or fname, "chars": len(text), "preview": text[:4000]}

@app.post("/index")
def index_text(payload: IndexRequest):
    """
    Chunks text, embeds with embeddings service, and upserts to Qdrant.
    """
    text = payload.text.strip()
    if not text:
        return JSONResponse({"error": "empty text"}, status_code=400)

    # simple chunker
    chunks = []
    words = text.split()
    chunk_size = max(100, payload.chunk_size)
    overlap = max(0, min(payload.overlap, chunk_size // 2))
    step = chunk_size - overlap
    i = 0
    while i < len(words):
        chunk_words = words[i:i+chunk_size]
        chunk_text = " ".join(chunk_words)
        chunks.append({"doc_id": payload.doc_id, "text": chunk_text, "source_uri": payload.source_uri or payload.doc_id})
        i += step

    vectors = embed_texts([c["text"] for c in chunks])
    upsert_chunks(collection=COLLECTION, chunks=chunks, vectors=vectors, index_version=INDEX_VERSION)
    return {"upserted": len(chunks), "doc_id": payload.doc_id, "index_version": INDEX_VERSION}

# ---- Pipelines ----
@app.post("/rag/answer")
def rag_endpoint(req: QueryRequest):
    return rag_answer(req.query, k=req.k, max_tokens=req.max_tokens, collection=COLLECTION)

@app.post("/cag/answer")
def cag_endpoint(req: QueryRequest):
    return cag_answer(req.query, max_tokens=req.max_tokens, sim_threshold=CACHE_SIM_THRESHOLD)

@app.post("/cag_rag/answer")
def cag_rag_endpoint(req: QueryRequest):
    return cag_rag_answer(req.query, k=req.k, max_tokens=req.max_tokens,
                          collection=COLLECTION, sim_threshold=CACHE_SIM_THRESHOLD)

# ---- Admin ----
@app.post("/admin/bump_index")
def bump_index():
    """
    Invalidate caches by bumping INDEX_VERSION (restart container with new env),
    but we emulate here by telling clients to update.
    """
    return {"message": "To bump index version, update INDEX_VERSION env and restart api/vllm", "current": INDEX_VERSION}
