# Mission 04 — Specialization

*Build a domain expert from your own knowledge base.*

**Time:** 1-2 hours
**Infra Analogy:** Flashing custom firmware — same hardware, specialized behavior. Like loading a custom IOS image onto a switch — the silicon is identical, but the feature set changes completely.
**Concepts:** [Prompts as Configs](../../concepts/prompts-as-configs.md), [RAG as Query Pipeline](../../concepts/rag-as-query-pipeline.md)

## What You'll Build

A domain-specific AI expert that answers questions using your curated knowledge base. Not fine-tuning (retraining the model) — RAG customization (controlling what it knows and how it responds). You'll:

1. **Curate a corpus** — select and organize domain documents
2. **Write a domain prompt** — the system prompt that defines expert behavior
3. **Evaluate accuracy** — automated tests that verify your expert answers correctly

```
┌──────────────┐   prompts.yaml    ┌──────────────┐
│   Domain     │ ────────────────→  │   Expert     │
│  Directory   │                    │   Chat UI    │
│              │   corpus/*.txt     │   :5004      │
│  networking/ │ ────────────────→  │              │
│  cooking/    │                    │  ┌────────┐  │
│  legal/      │   eval_questions   │  │Evaluate│  │
│  your-own/   │ ────────────────→  │  └────────┘  │
└──────────────┘                    └──────┬───────┘
                                           │
                                    ┌──────▼───────┐
                                    │   ChromaDB   │
                                    │  (per-domain │
                                    │  collection) │
                                    └──────────────┘
```

The same model, the same RAG pipeline, the same infrastructure — different behavior entirely. Just like flashing different firmware onto identical hardware.

## Quick Start

```bash
cd missions/04-specialization
docker compose up
```

Open [http://localhost:5004](http://localhost:5004). The networking domain expert is loaded by default.

## Verify

```bash
./verify.sh
```

## How It Works

Each **domain directory** contains three things:

| File | Purpose |
|------|---------|
| `prompts.yaml` | System prompt, greeting, collection name — the "firmware image" |
| `corpus/` | Domain documents — the knowledge base |
| `eval_questions.yaml` | Test questions with expected answers — your acceptance tests |

To create a new domain expert, copy `domains/template/`, fill in the files, and restart. No code changes needed.

## Next Steps

- [Walkthrough](walkthrough.md) — understand corpus curation, domain prompts, and the evaluation loop
- [Extend](extend.md) — multi-domain routing, custom metrics, adding new domains
- Ready for more? → [Mission 05 — Agents](../05-agents/)
