#!/usr/bin/env bash
set -e
docker compose pull || true
docker compose up -d
echo "✅ Services are starting..."
echo "• API:        http://localhost:8081/docs"
echo "• Qdrant:     http://localhost:6333/dashboard"
echo "• MinIO:      http://localhost:9001 (login: from .env)"
echo "• Ollama:     http://localhost:11434/api/tags"
