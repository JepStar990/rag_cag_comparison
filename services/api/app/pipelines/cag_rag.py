from app.utils.cache import Cache
from app.utils.embeddings import embed_query, embed_texts
from app.utils.vector import search_chunks
from app.utils.llm import chat_completion
from app.utils.similarity import cosine

SYSTEM_PROMPT = "You are a helpful assistant. Answer using ONLY provided context. Cite source ids."

cache = Cache()

def build_prompt(query: str, passages: list[dict]) -> str:
    ctx = "\n".join([f"[{p['id']}] {p['text']}" for p in passages])
    return f"{SYSTEM_PROMPT}\n\n# Context\n{ctx}\n\n# Question\n{query}\n\n# Answer\n"

def cag_rag_answer(query: str, k: int, max_tokens: int, collection: str, sim_threshold: float):
    # Safe answer cache
    ans = cache.get_answer(query)
    if ans:
        qvec = embed_query(query)
        if cosine(qvec, ans["qvec"]) >= sim_threshold:
            return {"pipeline": "CAG+RAG", "answer": ans["text"], "cached": True}

    # Retrieval cache (top-k ids & payloads)
    topk = cache.get_topk(query)
    if not topk:
        qvec = embed_query(query)
        passages = search_chunks(collection=collection, query_vec=qvec, limit=k)
        cache.put_topk(query, passages)
    else:
        passages = topk

    prompt = build_prompt(query, passages)
    answer = chat_completion(prompt, max_tokens=max_tokens)
    cache.put_answer(query, answer, embed_query(query))
    cites = [p["id"] for p in passages]
    return {"pipeline": "CAG+RAG", "answer": answer, "citations": cites, "cached": False}
