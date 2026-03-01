# RAG vs CAG vs CAG+RAG Pipeline Comparison

## 📌 Project Overview
This project aims to **design, implement, and evaluate three AI pipelines** for question-answering:

1. **RAG (Retrieval-Augmented Generation)**  
   - Combines document retrieval with LLM generation for grounded answers.
2. **CAG (Cache-Augmented Generation)**  
   - Uses caching to speed up repeated queries and reduce latency.
3. **CAG+RAG (Integrated)**  
   - Combines retrieval and caching for optimal performance.

The goal is to **compare latency, accuracy, and cost** across these pipelines using diverse data sources.

---

## ✅ Objectives
- Build **three independent pipelines** and deploy them using **Docker**.
- Ingest heterogeneous data (PDF, DOCX, audio, video, images).
- Implement **vector database** for RAG pipelines using OSS tools.
- Add **multi-layer caching** for CAG pipelines.
- Conduct **User Acceptance Testing (UAT)** with real-world queries.
- Measure performance and quality metrics.

---

## 🏗 Architecture
### Common Ingestion Pipeline
- Extract text from PDFs/DOCX: **Apache Tika**
- OCR for images: **Tesseract**
- Audio/Video transcription: **Whisper**
- Store raw files in **MinIO** (object storage)
- Chunk and embed text using **BAAI/bge-m3** embeddings
- Store embeddings in **Qdrant** (vector DB)

### Pipelines
- **Pipeline A (RAG):** Retrieval → Rerank → Context → LLM → Answer
- **Pipeline B (CAG):** Cache → LLM → Answer
- **Pipeline C (CAG+RAG):** Cache → Retrieval → Rerank → Context → LLM → Answer → Cache

---

## 🛠 Tech Stack (Open Source)
- **Vector DB:** Qdrant or Milvus
- **Cache:** Redis Stack
- **LLM Serving:** vLLM (Llama 3 or Mistral)
- **Embeddings:** BAAI/bge-m3 (HuggingFace)
- **Object Storage:** MinIO
- **Parsing:** Apache Tika, Tesseract, Whisper
- **API Orchestration:** FastAPI
- **Deployment:** Docker Compose

---

## 📂 Folder Structure
```

rag\_cag\_comparison/
├── ingestion/         # Data ingestion scripts
├── pipelines/
│   ├── rag/           # RAG pipeline code
│   ├── cag/           # CAG pipeline code
│   └── cag\_rag/       # Integrated pipeline code
├── services/          # Dockerized services (LLM, embeddings, cache, etc.)
├── configs/           # Environment configs
├── docker/            # Dockerfiles and compose files
├── scripts/           # Utility scripts
├── data/              # Raw and processed data
├── notebooks/         # Experiments and UAT analysis
├── tests/             # Unit and integration tests
└── README.md

````

---

## 📊 Evaluation Metrics
- **Latency:** P50/P95 response times
- **Cache Efficiency:** hit rates for answers, retrieval, KV-prefill
- **Quality:** BLEU/ROUGE scores, human evaluation
- **Freshness:** stale answer incidents after index updates
- **Cost:** compute and storage footprint

---

## 🔍 Data Sources
- **Internal:** Company policies, reports, training videos
- **Public:**  
  - https://commoncrawl.org  
  - https://arxiv.org  
  - https://www.ted.com  
  - https://www.openslr.org/12/  
- **Synthetic:** Create sample FAQs and policy docs for controlled tests.

---

## 🚀 How to Run
1. Clone the repo:
   ```bash
   git clone https://github.com/JepStar990/rag_cag_comparison.git
   cd rag_cag_comparison

2.  Start services:
    ```bash
    docker-compose up -d
    ```
3.  Ingest data:
    ```bash
    curl -X POST http://localhost:8081/ingest -F "file=@sample.pdf"
    ```
4.  Query pipelines:
    ```bash
    curl -X POST http://localhost:8081/rag/answer -d '{"query": "What is our vacation policy?"}'
    ```

***

## ✅ Next Steps

*   Implement ingestion scripts.
*   Build baseline RAG pipeline.
*   Add CAG caching layer.
*   Integrate CAG+RAG pipeline.
*   Run UAT and compare metrics.

***

## 📜 License

MIT License

