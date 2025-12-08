
#!/usr/bin/env bash
set -e

API="http://localhost:8081"
DOCS_DIR="./ingestion/docs"
mkdir -p "$DOCS_DIR"

# --- Policy & Procedure docs ---
cat > "${DOCS_DIR}/policy_leave_2025.txt" <<'EOF'
Title: Leave Policy FY2025
Summary: Employees accrue 1.75 days per month. Carry-over capped at 10 days.
Details: Annual leave requests require manager approval at least 10 working days prior to the start date.
Citations: HR Handbook v2025 Section 4.2.
EOF

cat > "${DOCS_DIR}/policy_security_2025.txt" <<'EOF'
Title: Information Security Policy FY2025
Principles: Least privilege, MFA mandatory, data classification.
Controls: Encryption-at-rest (AES-256), transport TLS1.2+, quarterly audit.
Incident Response: Report within 24h via ServiceDesk.
EOF

# --- Meeting minutes / transcripts ---
cat > "${DOCS_DIR}/minutes_water_audit_jhb.txt" <<'EOF'
Meeting: Johannesburg Water Audit Review
Date: 2025-08-12
Actions:
- Install smart meters in Region A within Q1 FY2026
- Reduce NRW by 8% via pressure management
- Publish monthly leakage dashboard to Operations
EOF

# --- Product/Service FAQs ---
cat > "${DOCS_DIR}/faq_internal_tools.txt" <<'EOF'
Q: How do I request access to the analytics sandbox?
A: Submit a ticket in ServiceNow with manager approval. Provisioning SLA: 2 business days.
Q: Where do I find the data catalog?
A: Visit /data/catalog on the intranet.
EOF

# --- Synthetic knowledge article ---
cat > "${DOCS_DIR}/kb_cache_aug_gen.txt" <<'EOF'
Cache-Augmented Generation (CAG) improves latency by caching retrieval results, prompts, and answers.
Safe reuse requires similarity gating (e.g., cosine >= 0.92) and index/model version checks.
EOF

echo "📄 Created synthetic text files under ${DOCS_DIR}"

# Index every file directly
for f in "${DOCS_DIR}"/*.txt; do
  TEXT=$(cat "$f" | sed 's/"/\\"/g')
  DOC_ID=$(basename "$f")
  echo "Indexing $DOC_ID ..."
  curl -s -X POST "${API}/index" \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"${TEXT}\",\"doc_id\":\"${DOC_ID}\",\"source_uri\":\"synthetic\",\"chunk_size\":800,\"overlap\":100}" > /dev/null
done

echo "✅ Synthetic dataset indexed."
echo "Try queries:"
echo "curl -s -X POST ${API}/rag/answer -H 'Content-Type: application/json' -d '{\"query\":\"What does the leave policy say?\",\"k\":8,\"max_tokens\":200}' | jq"
echo "curl -s -X POST ${API}/cag/answer -H 'Content-Type: application/json' -d '{\"query\":\"Explain CAG safety gating\",\"max_tokens\":200}' | jq"
echo "curl -s -X POST ${API}/cag_rag/answer -H 'Content-Type: application/json' -d '{\"query\":\"What actions are in the Johannesburg water audit minutes?\",\"k\":8,\"max_tokens\":200}' | jq"
