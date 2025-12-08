import os, requests

EMB_URL = os.getenv("EMB_URL", "http://embeddings:80")

def embed_texts(texts: list[str]) -> list[list[float]]:
    r = requests.post(f"{EMB_URL}/embeddings", json={"input": texts, "model": "BAAI/bge-m3"})
    r.raise_for_status()
    data = r.json()["data"]
    return [item["embedding"] for item in data]

def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
