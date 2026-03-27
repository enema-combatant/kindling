#!/bin/bash
set -e

echo "Waiting for Ollama..."
until curl -sf http://${OLLAMA_BASE_URL:-ollama:11434}/api/tags > /dev/null 2>&1; do
    sleep 2
done
echo "Ollama is ready."

if [ "${KINDLING_PROVIDER:-ollama}" = "ollama" ]; then
    for MODEL_VAR in KINDLING_MODEL KINDLING_EMBED_MODEL; do
        MODEL="${!MODEL_VAR:-}"
        [ -z "$MODEL" ] && continue
        echo "Ensuring model '$MODEL' is available..."
        curl -sf "http://${OLLAMA_BASE_URL:-ollama:11434}/api/show" \
            -d "{\"name\": \"$MODEL\"}" > /dev/null 2>&1 \
            || curl -sf "http://${OLLAMA_BASE_URL:-ollama:11434}/api/pull" \
                -d "{\"name\": \"$MODEL\", \"stream\": false}"
    done
    echo "Models ready."
fi

# Ingest documents (reuses Mission 01's pipeline)
python ingest.py

exec python app.py
