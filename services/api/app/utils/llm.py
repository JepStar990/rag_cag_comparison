import os, requests

LLM_URL = os.getenv("LLM_URL", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b-instruct")

def chat_completion(prompt: str, max_tokens: int = 256) -> str:
    """
    Calls Ollama /api/chat using a single-turn system+user structure.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "options": {
            "temperature": 0.2,
            "num_predict": max_tokens,
            "top_p": 0.95
        },
        "stream": False
    }
    r = requests.post(f"{LLM_URL}/api/chat", json=payload, timeout=None)
    r.raise_for_status()
    data = r.json()
    return data["message"]["content"].strip()
