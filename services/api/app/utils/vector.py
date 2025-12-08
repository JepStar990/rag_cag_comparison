import os, uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

QDRANT_URL = os.getenv("VECTOR_DB_URL", "http://localhost:6333")
COLLECTION = os.getenv("INDEX_COLLECTION", "ai_chunks")

client = QdrantClient(url=QDRANT_URL)

def ensure_collection(collection: str):
    dim = int(os.getenv("EMBEDDING_DIM", "1024"))
    exist = client.get_collections()
    names = [c.name for c in exist.collections]
    if collection not in names:
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        client.create_payload_index(collection, field_name="doc_id")
        client.create_payload_index(collection, field_name="index_version")

def upsert_chunks(collection: str, chunks: list[dict], vectors: list[list[float]], index_version: int):
    points = []
    for i, ch in enumerate(chunks):
        pid = str(uuid.uuid4())
        payload = {
            "doc_id": ch["doc_id"],
            "text": ch["text"],
            "source_uri": ch.get("source_uri", ch["doc_id"]),
            "index_version": index_version,
        }
        points.append(PointStruct(id=pid, vector=vectors[i], payload=payload))
    client.upsert(collection_name=collection, points=points)

def search_chunks(collection: str, query_vec: list[float], limit: int = 8, index_version: int | None = None):
    flt = None
    if index_version:
        flt = Filter(should=[FieldCondition(key="index_version", match=MatchValue(value=index_version))])
    res = client.search(collection_name=collection, query_vector=query_vec, limit=limit, query_filter=flt)
    # map to simplified dicts
    out = []
    for p in res:
        out.append({"id": str(p.id), "text": p.payload.get("text", ""), "doc_id": p.payload.get("doc_id")})
    return out
