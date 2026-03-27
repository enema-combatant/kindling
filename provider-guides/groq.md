# Groq — Fast Cloud Inference

*Free tier. Blazing fast.*

## Why Groq?

Groq runs open-source models (Llama, Mixtral) on custom LPU hardware that's significantly faster than traditional GPU inference. They offer a generous free tier — perfect for learning.

**Trade-off:** Free tier has rate limits (30 requests/minute, 14,400/day). More than enough for working through missions.

## Setup

1. Create an account at [console.groq.com](https://console.groq.com)
2. Generate an API key at [API Keys](https://console.groq.com/keys)
3. That's it — free tier is automatic

## Configuration

```bash
# .env
KINDLING_PROVIDER=groq
KINDLING_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_...

# Groq doesn't offer embeddings — Ollama handles them automatically
KINDLING_EMBED_MODEL=nomic-embed-text
```

**Note:** Like Anthropic, Groq doesn't provide an embedding API. Ollama handles embeddings as a sidecar. This is configured automatically in Docker Compose.

## Model Recommendations

| Model | Best For | Speed |
|-------|---------|-------|
| `llama-3.1-8b-instant` | Fast, lightweight | 750+ t/s |
| `llama-3.3-70b-versatile` | Best quality on free tier | 300+ t/s |
| `mixtral-8x7b-32768` | Long context (32K tokens) | 400+ t/s |

**Start with `llama-3.3-70b-versatile`.** It's a 70B parameter model running at 300+ tokens/second — faster than most local setups with much larger models. Free.

## Rate Limits (Free Tier)

| Limit | Value |
|-------|-------|
| Requests per minute | 30 |
| Requests per day | 14,400 |
| Tokens per minute | 6,000 |

This is more than enough for all missions. If you hit limits during Mission 04 (evaluation runs many queries), add a short delay between requests.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| 401 Unauthorized | Check your API key in `.env` |
| 429 Rate limited | Wait 60 seconds — free tier has per-minute limits |
| Model not available | Check [Groq docs](https://console.groq.com/docs/models) for current model list |
| Embeddings not working | Ensure Ollama is running (Docker Compose handles this) |
