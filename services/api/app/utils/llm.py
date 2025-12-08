import os, requests

LLM_URL = os.getenv("LLM_URL", "http://vllm:8000")

def chat_completion(prompt: str, max_tokens: int = 256) -> str:
    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "stream": False
    }
    r = requests.post(f"{LLM_URL}/v1/chat/completions", json=payload, timeout=None)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()
