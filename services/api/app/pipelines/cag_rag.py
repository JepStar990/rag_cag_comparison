from app.utils.cache import Cache
from app.utils.embeddings import embed_query
from app.utils.vector import search_chunks
from app.utils.llm import chat_completion
from app.utils.similarity import cosine
from app.utils.reranker_client import rerank

SYSTEM_PROMPT = "You are a helpful assistant. Answer using ONLY provided context. Cite source ids."
cache = Cache()

def build_prompt(query: str, passages: list[dict]) -> str:
    ctx = "\n".join([f"[{p['id']}] {p['text']}" for p in passages])
    return f"{SYSTEM_PROMPT}\n\n# Context\n{ctx}\n\n# Question\n{query}\n\n# Answer\n"

def cag_rag_answer(query: str, k: int, max_tokens: int, collection: str, sim_threshold: float):
    # 1) Safe answer cache
    ans = cache.get_answer(query)
    if ans:
        qvec = embed_query(query)
        if cosine(qvec, ans["qvec"]) >= sim_threshold:
            return {"pipeline": "CAG+RAG", "answer": ans["text"], "cached": True}

    # 2) Retrieval → rerank (with topk cache)
    topk_cached = cache.get_topk(query)
    if topk_cached:
        prelim = topk_cached
    else:
        qvec = embed_query(query)
        prelim = search_chunks(collection=collection, query_vec=qvec, limit=max(k*3, 24))
        cache.put_topk(query, prelim)

    ranked = rerank(query, prelim)
    topk = ranked[:k]

    # 3) Generation + write-back
    prompt = build_prompt(query, topk)
    answer = chat_completion(prompt, max_tokens=max_tokens)
    cache.put_answer(query, answer, embed_query(query))
    cites = [p["id"] for p in topk]
    return {"pipeline": "CAG+RAG", "answer": answer, "citations": cites, "cached": False, "reranked": True}
