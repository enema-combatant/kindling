# Mission 00 — Ignition

*Deploy your first model. Send your first prompt. See it respond.*

**Time:** ~15 minutes
**Infra Analogy:** Provisioning your first server — you don't understand everything about it yet, but it's running and responding to requests.
**Concepts:** [Tokens as Packets](../../concepts/tokens-as-packets.md), [Prompts as Configs](../../concepts/prompts-as-configs.md)

## What You'll Build

A local chat interface backed by a real language model. You'll type a question, and an LLM running on your hardware (or a cloud API) will generate a response. No magic — just HTTP requests between a Flask app and an inference server.

```
┌──────────────┐     HTTP POST     ┌──────────────┐
│   Browser     │ ──────────────→  │   Flask App   │
│  localhost:5000│ ←──────────────  │   (app.py)    │
└──────────────┘     HTML          └──────┬───────┘
                                          │ HTTP POST /api/chat
                                          ▼
                                   ┌──────────────┐
                                   │    Ollama     │
                                   │  (or cloud)   │
                                   │   :11434      │
                                   └──────────────┘
```

## Quick Start

```bash
# From the kindling root:
cp .env.example .env          # if you haven't already
cd missions/00-ignition
docker compose up
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

First run will pull the model (~2 GB for llama3.2:3b). Subsequent starts are instant.

## Verify

```bash
./verify.sh
```

This sends a test prompt and checks for a coherent response.

## What's Happening

1. **Docker Compose** starts two containers: Ollama (the model server) and the Flask app.
2. **Ollama** downloads and loads the model into memory (GPU if available, CPU if not).
3. **Flask** serves a simple chat UI and proxies your messages to Ollama's REST API.
4. **The model** processes your tokens (see [Tokens as Packets](../../concepts/tokens-as-packets.md)) and generates a response, one token at a time.

Every response is streamed — you see tokens appear as they're generated, just like watching packets arrive.

## Next Steps

- [Walkthrough](walkthrough.md) — step-by-step with explanations at each stage
- [Extend](extend.md) — try different models, adjust temperature, modify the system prompt
- Ready for more? → [Mission 01 — Memory](../01-memory/)
