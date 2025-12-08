# %% [markdown]
# # Evaluation: RAG vs CAG vs CAG+RAG (CPU, Ollama)
# Measures latency (P50/P95), simple quality proxies, and saves raw results.

# %%
import time, statistics, json, requests
API = "http://localhost:8081"

QUERIES = [
    {"q": "What does the leave policy say?", "k": 8},
    {"q": "Explain CAG safety gating", "k": 8},
    {"q": "What actions are in the Johannesburg water audit minutes?", "k": 8},
    {"q": "How do I request analytics sandbox access?", "k": 8},
    {"q": "Summarize information security controls", "k": 8},
]

def call(endpoint, payload):
    t0 = time.perf_counter()
    r = requests.post(f"{API}{endpoint}", json=payload, timeout=None)
    dt = (time.perf_counter() - t0) * 1000.0
    r.raise_for_status()
    return dt, r.json()

# %% Warmup to populate caches
for q in QUERIES:
    _ = call("/cag/answer", {"query": q["q"], "max_tokens": 160})
    _ = call("/cag_rag/answer", {"query": q["q"], "k": q["k"], "max_tokens": 160})

# %%
results = {"RAG": [], "CAG": [], "CAG+RAG": []}

for q in QUERIES:
    dt, data = call("/rag/answer", {"query": q["q"], "k": q["k"], "max_tokens": 160})
    results["RAG"].append({"query": q["q"], "latency_ms": dt, "answer": data["answer"], "cites": data.get("citations", [])})

    dt, data = call("/cag/answer", {"query": q["q"], "max_tokens": 160})
    results["CAG"].append({"query": q["q"], "latency_ms": dt, "answer": data["answer"], "cached": data.get("cached", False)})

    dt, data = call("/cag_rag/answer", {"query": q["q"], "k": q["k"], "max_tokens": 160})
    results["CAG+RAG"].append({"query": q["q"], "latency_ms": dt, "answer": data["answer"],
                               "cites": data.get("citations", []), "cached": data.get("cached", False)})

def summarize_latencies(name):
    lat = [x["latency_ms"] for x in results[name]]
    lat_sorted = sorted(lat)
    p95 = lat_sorted[int(max(0, len(lat)*0.95 - 1))] if lat else None
    return {
        "pipeline": name,
        "count": len(lat),
        "p50_ms": statistics.median(lat) if lat else None,
        "p95_ms": p95,
        "avg_ms": statistics.mean(lat) if lat else None,
    }

summary = [summarize_latencies(n) for n in ["RAG", "CAG", "CAG+RAG"]]
print(json.dumps(summary, indent=2))

EXPECT = {
    "What does the leave policy say?": ["accrue", "1.75", "carry-over", "10"],
    "Explain CAG safety gating": ["similarity", "0.92", "index", "version"],
    "What actions are in the Johannesburg water audit minutes?": ["smart meters", "Q1", "NRW", "8%", "leakage"],
    "How do I request analytics sandbox access?": ["ServiceNow", "manager", "SLA", "2"],
    "Summarize information security controls": ["least privilege", "MFA", "AES-256", "TLS"],
}

def quality_score(answer: str, expected: list[str]) -> float:
    a_low = answer.lower()
    hits = sum(1 for kw in expected if kw.lower() in a_low)
    return hits / max(1, len(expected))

quality = []
for name in ["RAG", "CAG", "CAG+RAG"]:
    scores = []
    for item in resultsqs = EXPECT.get(item["query"], [])
        scores.append(quality_score(item["answer"], qs))
    quality.append({"pipeline": name, "avg_quality": round(statistics.mean(scores), 3)})

print(json.dumps(quality, indent=2))

with open("evaluation_results.json", "w") as f:
    json.dump({"summary": summary, "quality": quality, "raw": results}, f, indent=2)
print("Saved evaluation_results.json")
