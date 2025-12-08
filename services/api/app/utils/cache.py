import os, json, hashlib
from redis import Redis

def qh(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:32]

class Cache:
    def __init__(self):
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.r = Redis.from_url(url, decode_responses=True)
        self.idx_ver = os.getenv("INDEX_VERSION", "1")
        self.model_ver = "llm_v1"
        self.t_topk = 600       # 10 min
        self.t_answer = 86400   # 24 h

    def _k(self, kind: str, q: str):
        return f"{kind}::{qh(q)}::{self.idx_ver}"

    def get_topk(self, query: str):
        val = self.r.get(self._k("topk", query))
        return json.loads(val) if val else None

    def put_topk(self, query: str, passages: list[dict]):
        self.r.setex(self._k("topk", query), self.t_topk, json.dumps(passages))

    def get_answer(self, query: str):
        val = self.r.get(self._k("answer", query))
        return json.loads(val) if val else None

    def put_answer(self, query: str, text: str, qvec: list[float]):
        payload = {"text": text, "qvec": qvec, "model_ver": self.model_ver, "idx_ver": self.idx_ver}
        self.r.setex(self._k("answer", query), self.t_answer, json.dumps(payload))
