from app.utils.cache import Cache
from app.utils.embeddings import embed_query
from app.utils.llm import chat_completion
from app.utils.similarity import cosine

SYSTEM_PROMPT = "You are a helpful assistant. If unsure, say you are not sure."

cache = Cache()

def cag_answer(query: str, max_tokens: int, sim_threshold: float):
    # Answer cache check
    cached = cache.get_answer(query)
    if cached:
        qvec = embed_query(query)
        if cosine(qvec, cached["qvec"]) >= sim_threshold:
            return {"pipeline": "CAG", "answer": cached["text"], "cached": True}

    # Miss path → call LLM
    prompt = f"{SYSTEM_PROMPT}\n\n# Question\n{query}\n\n# Answer:"
    answer = chat_completion(prompt, max_tokens=max_tokens)
    cache.put_answer(query, answer, embed_query(query))
    return {"pipeline": "CAG", "answer": answer, "cached": False}
