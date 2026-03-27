# Provider Guides

Kindling is provider-agnostic. You bring the model, we provide the missions.

## Quick Decision Matrix

| If you want... | Use | Cost | Setup Time |
|----------------|-----|------|------------|
| Zero dependencies, no account, full privacy | [Ollama](ollama.md) | Free | 5 min |
| Fast inference, free tier, don't mind cloud | [Groq](groq.md) | Free tier | 2 min |
| Best-in-class models, pay-per-use | [OpenAI](openai.md) | ~$0.01-0.10/query | 2 min |
| Claude models, pay-per-use | [Anthropic](anthropic.md) | ~$0.01-0.10/query | 2 min |

**Recommended starting point:** Ollama. It's free, local, and keeps your data on your machine.

## How Provider Switching Works

All missions read from one environment variable: `KINDLING_PROVIDER`. Set it in your `.env` file and every mission uses that provider automatically. No code changes needed.

```bash
# Switch from local to cloud in one line:
# Before:
KINDLING_PROVIDER=ollama

# After:
KINDLING_PROVIDER=openai
OPENAI_API_KEY=sk-...
KINDLING_MODEL=gpt-4o-mini
```

## Embedding Caveat

Some providers (Anthropic, Groq) don't offer embedding APIs. For these providers, Kindling automatically falls back to Ollama for embeddings. This means:

- You need Ollama installed even when using a cloud provider for chat (missions 01+)
- Or you can use OpenAI for both chat and embeddings

The Docker Compose files handle this automatically — Ollama runs as a sidecar service in every mission.
