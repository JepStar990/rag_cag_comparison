# OpenAI-compatible CPU server using llama.cpp
FROM ghcr.io/abetlen/llama-cpp-python:server

# Small helper tools
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

# ✅ Download a CPU-friendly GGUF model (3B instruct, quantized)
# Adjust if you prefer a different model; Q4_K_M is a good latency/quality trade-off.
RUN mkdir -p /models && \
    wget -O /models/llama-3.2-3b-instruct-q4_k_m.gguf \
      https://huggingface.co/lmstudio-community/Meta-Llama-3.2-3B-Instruct-GGUF/resolve/main/Meta-Llama-3.2-3B-Instruct-Q4_K_M.gguf

# Default server args: OpenAI compatible, port 8000, 4K context
ENV LLAMA_CPP_SERVER_ARGS="--model /models/llama-3.2-3b-instruct-q4_k_m.gguf --host 0.0.0.0 --port 8000 --chat_format openai --n_ctx 4096"

EXPOSE 8000
CMD ["python", "-m", "llama_cpp.server"]
