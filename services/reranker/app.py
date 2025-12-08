from fastapi import FastAPI
from pydantic import BaseModel
import os
from sentence_transformers import CrossEncoder

model_id = os.getenv("RERANKER_MODEL_ID", "BAAI/bge-reranker-v2-m3")
model = CrossEncoder(model_id)
app = FastAPI(title="Reranker Service")

class Item(BaseModel):
    id: str
    text: str

class RerankRequest(BaseModel):
    query: str
    items: list[Item]

@app.post("/rerank")
def rerank(req: RerankRequest):
    pairs = [(req.query, it.text) for it in req.items]
    scores = model.predict(pairs).tolist()
    ranked = sorted(
        [{"id": it.id, "text": it.text, "score": s} for it, s in zip(req.items, scores)],
        key=lambda x: x["score"],
        reverse=True
    )
    return {"ranked": ranked}
