#!/usr/bin/env sh
# ==============================================================================
# ATLAS Banking Copilot — Ollama Model Cache Initializer (S20)
# Pulls required language & embedding models into named Docker volume.
# ==============================================================================
set -e

OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.2:3b}"
OLLAMA_EMBED_MODEL="${OLLAMA_EMBED_MODEL:-nomic-embed-text}"

echo "=========================================================="
echo "ATLAS Ollama Initializer starting..."
echo "Target Host:        ${OLLAMA_HOST}"
echo "LLM Model:          ${OLLAMA_MODEL}"
echo "Embedding Model:    ${OLLAMA_EMBED_MODEL}"
echo "=========================================================="

echo "Waiting for Ollama daemon to become healthy..."
MAX_RETRIES=30
RETRY_COUNT=0

until curl -s -f "${OLLAMA_HOST}/api/tags" > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
        echo "Error: Timed out waiting for Ollama service at ${OLLAMA_HOST}."
        exit 1
    fi
    echo "Waiting for Ollama to accept connections (${RETRY_COUNT}/${MAX_RETRIES})..."
    sleep 2
done

echo "Ollama is ready. Checking local model cache..."

# Check and pull main chat/reasoning LLM
if curl -s "${OLLAMA_HOST}/api/tags" | grep -q "\"name\":\"${OLLAMA_MODEL}"; then
    echo "Model '${OLLAMA_MODEL}' already exists in volume cache."
else
    echo "Pulling '${OLLAMA_MODEL}' from registry..."
    curl -s -X POST "${OLLAMA_HOST}/api/pull" -d "{\"name\": \"${OLLAMA_MODEL}\"}"
    echo "Model '${OLLAMA_MODEL}' successfully cached."
fi

# Check and pull embedding model
if curl -s "${OLLAMA_HOST}/api/tags" | grep -q "\"name\":\"${OLLAMA_EMBED_MODEL}"; then
    echo "Embedding model '${OLLAMA_EMBED_MODEL}' already exists in volume cache."
else
    echo "Pulling '${OLLAMA_EMBED_MODEL}' from registry..."
    curl -s -X POST "${OLLAMA_HOST}/api/pull" -d "{\"name\": \"${OLLAMA_EMBED_MODEL}\"}"
    echo "Embedding model '${OLLAMA_EMBED_MODEL}' successfully cached."
fi

echo "=========================================================="
echo "All required models are present and ready for inference."
echo "=========================================================="
exit 0
