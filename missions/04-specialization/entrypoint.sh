#!/bin/bash
set -e

echo "Waiting for Ollama..."
until curl -sf ${OLLAMA_BASE_URL:-http://ollama:11434}/api/tags > /dev/null 2>&1; do
    sleep 2
done
echo "Ollama is ready."

if [ "${KINDLING_PROVIDER:-ollama}" = "ollama" ]; then
    # Pull both chat and embedding models
    for MODEL_VAR in KINDLING_MODEL KINDLING_EMBED_MODEL; do
        MODEL="${!MODEL_VAR:-}"
        [ -z "$MODEL" ] && continue
        echo "Ensuring model '$MODEL' is available..."
        curl -sf "${OLLAMA_BASE_URL:-http://ollama:11434}/api/show" \
            -d "{\"name\": \"$MODEL\"}" > /dev/null 2>&1 \
            || curl -sf "${OLLAMA_BASE_URL:-http://ollama:11434}/api/pull" \
                -d "{\"name\": \"$MODEL\", \"stream\": false}"
    done
    echo "Models ready."
fi

# Ingest domain corpus into the domain-specific collection
DOMAIN_PATH="${DOMAIN_PATH:-/app/domains/networking}"
echo "Building corpus from $DOMAIN_PATH..."
python corpus_builder.py "$DOMAIN_PATH"

exec python app.py
