import os, requests

RERANKER_URL = os.getenv("RERANKER_URL", "http://reranker:7002")

def rerank(query: str, passages: list[dict]) -> list[dict]:
    """
    Passages: [{"id": "...", "text": "..."}]
    Returns ranked list with scores desc.
    """
    payload = {"query": query, "items": [{"id": p["id"], "text": p["text"]} for p in passages]}
    r = requests.post(f"{RERANKER_URL}/rerank", json=payload, timeout=None)
    r.raise_for_status()
    return r.json()["ranked"]
