# Mission 01 — Memory

*Embed your documents. Search by meaning, not keywords.*

**Time:** ~30 minutes
**Infra Analogy:** Building a search index — like Elasticsearch, but for meaning instead of keywords.
**Concepts:** [Embeddings as Hashing](../../concepts/embeddings-as-hashing.md), [Vectors as Indexes](../../concepts/vectors-as-indexes.md)

## What You'll Build

An embedding pipeline that converts documents into searchable vectors, stored in a vector database (ChromaDB). You'll ingest text files and search them semantically — "network connectivity problem" will find documents about "the link between switches went down" even though they share zero keywords.

```
┌─────────────┐     Chunk + Embed    ┌──────────────┐
│  Your Docs   │ ──────────────────→  │   ChromaDB    │
│  (text files)│                      │  (vectors)    │
└─────────────┘                      └──────┬───────┘
                                            │
┌─────────────┐     Semantic Search  ┌──────┴───────┐
│   Browser    │ ←──────────────────  │   Flask App   │
│  :5001       │ ──────────────────→  │  (search.py)  │
└─────────────┘     Query            └──────────────┘
```

## Quick Start

```bash
cd missions/01-memory
docker compose up
```

Open [http://localhost:5001](http://localhost:5001) to search. Sample documents are ingested automatically on first run.

## Adding Your Own Documents

Drop `.txt` or `.md` files into the `sample-docs/` directory and restart:

```bash
docker compose restart app
```

The ingest pipeline will process any new files it finds.

## Verify

```bash
./verify.sh
```

## Next Steps

- [Walkthrough](walkthrough.md) — understand every step of the pipeline
- [Extend](extend.md) — different embedding models, chunk sizes, distance metrics
- Ready for more? → [Mission 02 — Retrieval](../02-retrieval/)
