import os, requests

# Provider switch is kept for flexibility; default to Ollama
EMB_PROVIDER = os.getenv("EMB_PROVIDER", "ollama")  # "ollama" only now
OLLAMA_URL = os.getenv("LLM_URL", "http://ollama:11434")
OLLAMA_EMB_MODEL = os.getenv("OLLAMA_EMB_MODEL", "nomic-embed-text")

def _ollama_embed(texts: list[str]) -> list[list[float]]:
    vecs = []
    for t in texts:
        r = requests.post(f"{OLLAMA_URL}/api/embeddings", json={"model": OLLAMA_EMB_MODEL, "prompt": t})
        r.raise_for_status()
        vecs.append(r.json()["embedding"])
    return vecs

def embed_texts(texts: list[str]) -> list[list[float]]:
    # We only support Ollama in this setup
    return _ollama_embed(texts)

def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
