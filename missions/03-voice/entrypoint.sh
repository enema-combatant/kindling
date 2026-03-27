#!/bin/bash
set -e

echo "Waiting for Ollama..."
until curl -sf ${OLLAMA_BASE_URL:-http://ollama:11434}/api/tags > /dev/null 2>&1; do
    sleep 2
done

if [ "${KINDLING_PROVIDER:-ollama}" = "ollama" ]; then
    for MODEL_VAR in KINDLING_MODEL KINDLING_EMBED_MODEL; do
        MODEL="${!MODEL_VAR:-}"
        [ -z "$MODEL" ] && continue
        echo "Ensuring model '$MODEL' is available..."
        curl -sf "${OLLAMA_BASE_URL:-http://ollama:11434}/api/show" \
            -d "{\"name\": \"$MODEL\"}" > /dev/null 2>&1 \
            || curl -sf "${OLLAMA_BASE_URL:-http://ollama:11434}/api/pull" \
                -d "{\"name\": \"$MODEL\", \"stream\": false}"
    done
fi

echo "Waiting for Whisper..."
until curl -sf ${WHISPER_URL:-http://whisper:8000}/health > /dev/null 2>&1; do
    sleep 3
done
echo "All services ready."

python ingest.py
exec python app.py
