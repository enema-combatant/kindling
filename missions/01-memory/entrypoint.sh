#!/bin/bash
set -e

echo "Waiting for Ollama..."
until curl -sf http://${OLLAMA_BASE_URL:-ollama:11434}/api/tags > /dev/null 2>&1; do
    sleep 2
done
echo "Ollama is ready."

# Pull embedding model if needed
if [ "${KINDLING_PROVIDER:-ollama}" = "ollama" ]; then
    EMBED_MODEL="${KINDLING_EMBED_MODEL:-nomic-embed-text}"
    echo "Ensuring embedding model '$EMBED_MODEL' is available..."
    curl -sf "http://${OLLAMA_BASE_URL:-ollama:11434}/api/show" \
        -d "{\"name\": \"$EMBED_MODEL\"}" > /dev/null 2>&1 \
        || curl -sf "http://${OLLAMA_BASE_URL:-ollama:11434}/api/pull" \
            -d "{\"name\": \"$EMBED_MODEL\", \"stream\": false}"
    echo "Embedding model ready."
fi

# Ingest sample docs on first run
python ingest.py

# Start the search interface
exec python search.py
