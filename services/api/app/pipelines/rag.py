from app.utils.embeddings import embed_query
from app.utils.vector import search_chunks
from app.utils.llm import chat_completion

SYSTEM_PROMPT = "You are a helpful assistant. Answer using ONLY the provided context. Cite source ids."

def build_prompt(query: str, passages: list[dict]) -> str:
    ctx_lines = []
    for p in passages:
        ctx_lines.append(f"[{p['id']}] {p['text']}")
    ctx = "\n".join(ctx_lines[:10])  # safety cap
    return f"{SYSTEM_PROMPT}\n\n# Context\n{ctx}\n\n# Question\n{query}\n\n# Answer\n"

def rag_answer(query: str, k: int, max_tokens: int, collection: str):
    qvec = embed_query(query)
    passages = search_chunks(collection=collection, query_vec=qvec, limit=k)
    prompt = build_prompt(query, passages)
    answer = chat_completion(prompt, max_tokens=max_tokens)
    cites = [p["id"] for p in passages]
    return {"pipeline": "RAG", "answer": answer, "citations": cites, "k": k}
