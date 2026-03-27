#!/bin/bash
set -e

# Wait for Ollama to be ready
echo "Waiting for Ollama..."
until curl -sf ${OLLAMA_BASE_URL:-http://ollama:11434}/api/tags > /dev/null 2>&1; do
    sleep 2
done
echo "Ollama is ready."

# Pull the model if not already present (only for Ollama provider)
if [ "${KINDLING_PROVIDER:-ollama}" = "ollama" ]; then
    MODEL="${KINDLING_MODEL:-llama3.2:3b}"
    echo "Ensuring model '$MODEL' is available..."
    curl -sf "${OLLAMA_BASE_URL:-http://ollama:11434}/api/show" \
        -d "{\"name\": \"$MODEL\"}" > /dev/null 2>&1 \
        || curl -sf "${OLLAMA_BASE_URL:-http://ollama:11434}/api/pull" \
            -d "{\"name\": \"$MODEL\", \"stream\": false}"
    echo "Model '$MODEL' ready."
fi

# Start the Flask app
exec python app.py
