# Ollama — Local Inference

*Free. Private. No account required.*

## Why Ollama?

Ollama runs language models on your own hardware. Your data never leaves your machine. There's no API key, no billing, no rate limits. It handles GPU detection, model downloading, and serving automatically.

**Trade-off:** Slower than cloud APIs (especially on CPU-only machines), but free and private.

## Setup

### Option A: Kindling Handles It (Recommended)

The Docker Compose files in each mission include an Ollama service. Just run:

```bash
cd missions/00-ignition
docker compose up
```

Ollama will start automatically and pull the required models on first run.

### Option B: Install Locally

If you want Ollama available system-wide (not just in Docker):

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from https://ollama.ai/download

# Pull the default models
ollama pull llama3.2:3b       # Chat model (~2 GB)
ollama pull nomic-embed-text   # Embedding model (~275 MB)
```

Then update `.env` to point to your local instance:

```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434  # macOS/Windows
OLLAMA_BASE_URL=http://172.17.0.1:11434            # Linux
```

## Configuration

```bash
# .env
KINDLING_PROVIDER=ollama
KINDLING_MODEL=llama3.2:3b
KINDLING_EMBED_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://ollama:11434    # Default (Docker Compose)
```

## Model Recommendations

| Your Hardware | Chat Model | Size | Speed |
|--------------|-----------|------|-------|
| CPU only, 8 GB RAM | `llama3.2:1b` | 1.3 GB | 5-10 t/s |
| CPU only, 16 GB RAM | `llama3.2:3b` | 2.0 GB | 8-15 t/s |
| GPU (6+ GB VRAM) | `llama3.2:3b` | 2.0 GB | 30-60 t/s |
| GPU (8+ GB VRAM) | `qwen3:8b` | 4.9 GB | 20-40 t/s |
| GPU (16+ GB VRAM) | `mistral:7b` | 4.1 GB | 40-80 t/s |
| GPU (24+ GB VRAM) | `llama3.1:13b` | 7.9 GB | 25-50 t/s |

The embedding model (`nomic-embed-text`) runs well on CPU. It's small (275 MB) and fast.

## GPU Acceleration

Ollama detects NVIDIA GPUs automatically if you have:
- NVIDIA drivers installed on the host
- `nvidia-container-toolkit` installed (for Docker GPU passthrough)

For Docker Compose, GPU access is configured in the mission's `docker-compose.yml`:

```yaml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

**No GPU? No problem.** Everything works on CPU — just slower. Start with `llama3.2:1b` for the fastest CPU experience.

## Verifying Ollama Is Working

```bash
# If running via Docker Compose:
docker compose exec ollama ollama list

# If running locally:
ollama list
curl http://localhost:11434/api/tags
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "model not found" | Run `ollama pull llama3.2:3b` (or use Docker Compose which pulls automatically) |
| Slow on CPU | Switch to `llama3.2:1b` — smaller and faster |
| Out of memory | Use a smaller model or increase Docker's memory limit |
| Can't connect from Docker | Check `OLLAMA_BASE_URL` — use `host.docker.internal` on macOS/Windows |
