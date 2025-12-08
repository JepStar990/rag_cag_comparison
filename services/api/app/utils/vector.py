import os, uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue, PayloadSchemaType
)

QDRANT_URL = os.getenv("VECTOR_DB_URL", "http://qdrant:6333")
COLLECTION = os.getenv("INDEX_COLLECTION", "ai_chunks_bge")

client = QdrantClient(url=QDRANT_URL)

def ensure_collection(collection: str):
    dim = int(os.getenv("EMBEDDING_DIM", "1024"))  # bge-m3 is 1024
    existing = client.get_collections()
    names = [c.name for c in existing.collections]
    if collection not in names:
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
    # Explicit payload indexes
    for field, schema in [("doc_id", PayloadSchemaType.KEYWORD),
                          ("index_version", PayloadSchemaType.INTEGER)]:
        try:
            client.create_payload_index(collection_name=collection, field_name=field, field_schema=schema)
        except Exception:
            pass

def upsert_chunks(collection: str, chunks: list[dict], vectors: list[list[float]], index_version: int):
    points = []
    for i, ch in enumerate(chunks):
        payload = {
            "doc_id": ch["doc_id"],
            "text": ch["text"],
            "source_uri": ch.get("source_uri", ch["doc_id"]),
            "index_version": index_version,
        }
        points.append(PointStruct(id=str(uuid.uuid4()), vector=vectors[i], payload=payload))
    client.upsert(collection_name=collection, points=points)

def search_chunks(collection: str, query_vec: list[float], limit: int = 8, index_version: int | None = None):
    q_filter = None
    if index_version is not None:
        q_filter = Filter(should=[FieldCondition(key="index_version", match=MatchValue(value=index_version))])

    # ✅ Correct method name for current qdrant-client
    res = client.search_points(
        collection_name=collection,
        query_vector=query_vec,
        limit=limit,
        query_filter=q_filter
    )

    return [{"id": str(p.id), "text": p.payload.get("text", ""), "doc_id": p.payload.get("doc_id")} for p in res]
