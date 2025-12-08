from app.utils.embeddings import embed_query
from app.utils.vector import search_chunks
from app.utils.llm import chat_completion
from app.utils.reranker_client import rerank

SYSTEM_PROMPT = "You are a helpful assistant. Answer using ONLY the provided context. Cite source ids."

def build_prompt(query: str, passages: list[dict]) -> str:
    ctx_lines = [f"[{p['id']}] {p['text']}" for p in passages]
    ctx = "\n".join(ctx_lines[:10])
    return f"{SYSTEM_PROMPT}\n\n# Context\n{ctx}\n\n# Question\n{query}\n\n# Answer\n"

def rag_answer(query: str, k: int, max_tokens: int, collection: str):
    qvec = embed_query(query)
    prelim = search_chunks(collection=collection, query_vec=qvec, limit=max(k*3, 24))
    ranked = rerank(query, prelim)
    topk = ranked[:k]
    prompt = build_prompt(query, topk)
    answer = chat_completion(prompt, max_tokens=max_tokens)
    cites = [p["id"] for p in topk]
