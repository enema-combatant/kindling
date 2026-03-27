# Anthropic — Claude API

*Claude models. Pay-per-token.*

## Setup

1. Create an account at [console.anthropic.com](https://console.anthropic.com)
2. Generate an API key at [API Keys](https://console.anthropic.com/settings/keys)
3. Add credits (minimum $5 to start)

## Configuration

```bash
# .env
KINDLING_PROVIDER=anthropic
KINDLING_MODEL=claude-sonnet-4-20250514
ANTHROPIC_API_KEY=sk-ant-...

# Anthropic doesn't offer embeddings — Ollama handles them automatically
KINDLING_EMBED_MODEL=nomic-embed-text
```

**Note:** Anthropic doesn't provide an embedding API. Kindling automatically falls back to Ollama for embeddings (missions 01+). The Docker Compose files include Ollama as a sidecar service, so this is handled transparently.

## Model Recommendations

| Model | Best For | Cost (per 1M tokens) |
|-------|---------|---------------------|
| `claude-haiku-4-5-20251001` | Fast, cheap, good for simple tasks | $0.80 input / $4.00 output |
| `claude-sonnet-4-20250514` | Best balance of quality and speed | $3.00 input / $15.00 output |
| `claude-opus-4-20250514` | Maximum reasoning quality | $15.00 input / $75.00 output |

**Start with `claude-sonnet-4-20250514`.** It handles all missions well. For budget-conscious exploration, `claude-haiku-4-5-20251001` is fast and cheap.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| 401 Authentication error | Check your API key in `.env` |
| 429 Rate limited | Anthropic has per-minute rate limits — wait and retry |
| Embeddings not working | Ensure Ollama is running (Docker Compose handles this) |
