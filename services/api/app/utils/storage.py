import os, io
from minio import Minio

MINIO_ENDPOINT = f"{os.getenv('MINIO_ENDPOINT', 'minio')}:{os.getenv('MINIO_PORT', '9000')}"
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "ai-data")

client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

def ensure_bucket():
    found = client.bucket_exists(MINIO_BUCKET)
    if not found:
        client.make_bucket(MINIO_BUCKET)

def put_object(name: str, data: bytes):
    ensure_bucket()
    client.put_object(MINIO_BUCKET, name, io.BytesIO(data), length=len(data))
