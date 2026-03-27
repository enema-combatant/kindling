# Kindling

*The infrastructure operator's path to practical AI.*

You know how to build systems. Now build intelligent ones.

---

## What Is This?

Kindling is a hands-on learning lab for infrastructure professionals who want to understand AI — not academically, but operationally. If you can deploy a service, configure a network, and read a log file, you already have the mental models you need. You just need the right translation.

This project grew from an 84-day partnership between a senior infrastructure architect and an AI coding assistant. Starting from "help me delete duplicate files," that journey produced 98 projects, 8.7 million indexed vectors, fine-tuned models, and AI assistants deployed to field hardware. The breakthrough insight: **AI is an infrastructure problem**, and the concepts map directly to things you already know.

Kindling makes that journey reproducible.

## How It Works

Kindling is organized as **missions** — each a standalone, working system that you build and run locally. Every mission produces a tangible artifact: a running service, a searchable knowledge base, a voice interface, an agent that takes actions. Not notebooks. Not theory. Running systems.

| Mission | You Build | Time | Infra Analogy |
|---------|-----------|------|---------------|
| [00 — Ignition](missions/00-ignition/) | Chat interface + local model | 15 min | Provisioning your first server |
| [01 — Memory](missions/01-memory/) | Embedding pipeline + vector search | 30 min | Building a search index |
| [02 — Retrieval](missions/02-retrieval/) | RAG pipeline over your documents | 45 min | Deploying a query service |
| [03 — Voice](missions/03-voice/) | Speech input/output for your AI | 30 min | Adding a management console |
| [04 — Specialization](missions/04-specialization/) | Domain-specific AI expert | 1-2 hr | Flashing custom firmware |
| [05 — Agents](missions/05-agents/) | Tool-calling AI with live actions | 1 hr | Building a control plane |

Run them in order for the guided path, or jump to what interests you.

## Quick Start

### Prerequisites

- **Docker** + **Docker Compose** v2 (the `docker compose` plugin, not legacy `docker-compose`)
- **16 GB RAM** (8 GB minimum with smaller models)
- **10 GB free disk** (models + containers)
- **GPU optional** — NVIDIA for acceleration, but everything works on CPU
- **macOS, Linux, or Windows** (WSL2)
- **For verify scripts:** `curl` and `python3` on the host

### 1. Clone and configure

```bash
git clone https://github.com/enema-combatant/kindling.git
cd kindling
cp .env.example .env
```

### 2. Choose your model provider

Edit `.env` to select a provider. The default is **Ollama** (free, local, no account needed):

```bash
KINDLING_PROVIDER=ollama
KINDLING_MODEL=llama3.2:3b
KINDLING_EMBED_MODEL=nomic-embed-text
```

See [Provider Guides](provider-guides/) for other options (OpenAI, Anthropic, Groq).

### 3. Launch your first mission

```bash
cd missions/00-ignition
docker compose up
```

Open `http://localhost:5000` and start talking to your AI.

### 4. Verify it works

```bash
./verify.sh
```

Every mission includes a smoke test that proves the system is functional.

## Bring Your Own Model

Kindling is provider-agnostic. Switch providers by changing one environment variable — no code changes.

| Provider | Cost | Latency | Setup |
|----------|------|---------|-------|
| [Ollama](provider-guides/ollama.md) | Free | Local (GPU fast, CPU slower) | Download + `ollama pull` |
| [Groq](provider-guides/groq.md) | Free tier | Fast (cloud) | API key |
| [OpenAI](provider-guides/openai.md) | Pay-per-token | Fast (cloud) | API key |
| [Anthropic](provider-guides/anthropic.md) | Pay-per-token | Fast (cloud) | API key |

## Understand, Don't Memorize

Each mission references [concept documents](concepts/) that translate AI ideas into infrastructure language:

- [Embeddings as Hashing](concepts/embeddings-as-hashing.md) — Content-addressable hashes that preserve semantic similarity
- [Vectors as Indexes](concepts/vectors-as-indexes.md) — B-trees to HNSW; query planning to approximate nearest neighbor
- [RAG as Query Pipeline](concepts/rag-as-query-pipeline.md) — `SELECT` with a semantic `WHERE` clause
- [Tokens as Packets](concepts/tokens-as-packets.md) — MTU, fragmentation, context windows as buffer sizes
- [Prompts as Configs](concepts/prompts-as-configs.md) — System prompts are service configuration files
- [Agents as Control Planes](concepts/agents-as-control-planes.md) — The Kubernetes reconciliation loop: observe, decide, act, observe

These aren't dumbed down. They're translated — from one technical domain to another.

## The Story Behind This

Read **[JOURNEY.md](JOURNEY.md)** — the narrative of how an infrastructure architect went from zero AI experience to deploying field-ready AI assistants in 84 days, partnering with an AI coding assistant. It covers the mental model shifts, the mistakes that taught the most, and the meta-skill of working with AI effectively.

## Go Deeper

After completing missions, [extensions](extensions/) take you further:

- **[Fine-Tuning](extensions/fine-tuning/)** — Train a model on your own data (QLoRA on cloud GPU)
- **[Security Hardening](extensions/security-hardening/)** — TLS, authentication, container isolation
- **[Monitoring](extensions/monitoring/)** — Prometheus metrics, health checks, Grafana dashboards
- **[Multi-Node](extensions/multi-node/)** — Distribute inference across machines
- **[Field Deployment](extensions/field-deployment/)** — Take it offline: laptop, phone, constrained hardware
- **[Mesh Sync](extensions/mesh-sync/)** — Offline synchronization via LoRa and mesh networks

## Philosophy

- **No magic.** Every mission shows the actual HTTP calls, the actual vector math, the actual prompt construction. When you understand the primitives, you can choose any framework later.
- **No notebooks.** Infrastructure people think in services, configs, and logs — not cells.
- **No framework tax.** No LangChain, no React, no build toolchains. Vanilla Python, vanilla HTML, readable by anyone.
- **No vendor lock-in.** Switch providers with one env var. Run everything locally if you want.
- **No "just trust me."** Every mission links to concept docs that explain *why* it works, in language you already speak.

## License

[MIT](LICENSE) — Use it, modify it, share it.

## Acknowledgments

This project was built in partnership with [Claude Code](https://claude.ai/code) by Anthropic. The entire journey — from first prompt to this repository — demonstrates what's possible when infrastructure expertise meets AI assistance. The best way to learn AI is to build things with it.
