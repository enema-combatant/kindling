# Mission 02 — Retrieval

*Ask your documents questions. Get cited answers.*

**Time:** ~45 minutes
**Infra Analogy:** A query service — your AI does a lookup before answering, like a DNS resolver checking its cache before going upstream.
**Concepts:** [RAG as Query Pipeline](../../concepts/rag-as-query-pipeline.md), [Tokens as Packets](../../concepts/tokens-as-packets.md)

## What You'll Build

A complete RAG (Retrieval-Augmented Generation) pipeline. You ask a question in natural language. The system retrieves relevant document chunks from the vector database, injects them into the LLM's prompt as context, and the LLM generates an answer grounded in your documents — with citations.

```
┌──────────┐   Question   ┌──────────────┐   Embed    ┌──────────┐
│  Browser  │ ──────────→  │   RAG Engine  │ ────────→  │ ChromaDB │
│  :5002    │              │   (rag.py)    │ ←────────  │ (vectors)│
└──────────┘              └──────┬───────┘  Top-k     └──────────┘
     ↑                           │
     │ Cited Answer              │ Context + Question
     │                           ▼
     │                    ┌──────────────┐
     └────────────────────│   Ollama     │
                          │  (or cloud)   │
                          └──────────────┘
```

## Quick Start

```bash
cd missions/02-retrieval
docker compose up
```

Open [http://localhost:5002](http://localhost:5002). The sample documents from Mission 01 are automatically ingested.

## Verify

```bash
./verify.sh
```

## Next Steps

- [Walkthrough](walkthrough.md) — see the retrieve → augment → generate pipeline step by step
- [Extend](extend.md) — reranking, hybrid search, custom system prompts
- Ready for more? → [Mission 03 — Voice](../03-voice/)
