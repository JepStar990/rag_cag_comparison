#!/usr/bin/env bash
set -e
docker compose pull || true
docker compose up -d
echo "✅ Services are starting... Visit:"
echo "• FastAPI:    http://localhost:8081/docs"
echo "• Qdrant:     http://localhost:6333/dashboard"
echo "• MinIO:      http://localhost:9001  (user/pass from .env)"
