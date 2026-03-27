# OpenAI — Cloud API

*Best-in-class models. Pay-per-token.*

## Setup

1. Create an account at [platform.openai.com](https://platform.openai.com)
2. Generate an API key at [API Keys](https://platform.openai.com/api-keys)
3. Add credits (minimum $5 to start)

## Configuration

```bash
# .env
KINDLING_PROVIDER=openai
KINDLING_MODEL=gpt-4o-mini
KINDLING_EMBED_MODEL=text-embedding-3-small
OPENAI_API_KEY=sk-...
```

## Model Recommendations

| Model | Best For | Cost (per 1M tokens) |
|-------|---------|---------------------|
| `gpt-4o-mini` | Best value — fast, cheap, good quality | $0.15 input / $0.60 output |
| `gpt-4o` | Maximum quality | $2.50 input / $10.00 output |
| `text-embedding-3-small` | Embeddings (1536 dims) | $0.02 |
| `text-embedding-3-large` | High-quality embeddings (3072 dims) | $0.13 |

**Start with `gpt-4o-mini`.** It's fast, cheap, and good enough for all missions. The complete mission set costs roughly $0.50-2.00 in API credits.

## Cost Estimation

| Mission | Estimated Cost |
|---------|---------------|
| 00 — Ignition | $0.01-0.05 |
| 01 — Memory (embedding 50 docs) | $0.01 |
| 02 — Retrieval (10 RAG queries) | $0.05-0.10 |
| 03 — Voice | $0.05-0.10 (STT/TTS are local, only chat uses API) |
| 04 — Specialization | $0.10-0.50 (evaluation runs many queries) |
| 05 — Agents | $0.10-0.50 (multi-step tool calling) |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| 401 Unauthorized | Check your API key in `.env` |
| 429 Rate Limited | Wait and retry, or add payment method for higher limits |
| Billing not set up | Add credits at platform.openai.com/account/billing |
