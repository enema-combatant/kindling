# Mission 01 — Memory: Walkthrough

## Step 1: Start the Stack

```bash
docker compose up
```

This starts Ollama and pulls the embedding model (`nomic-embed-text`, ~275 MB). Then the ingest script processes the sample documents.

## Step 2: Watch the Ingestion

In the logs, you'll see:

```
Processing: container-operations.txt
Processing: network-troubleshooting.txt
Processing: security-fundamentals.txt
Processing: server-administration.txt
Ingestion complete: 48 new chunks added. Total: 48 chunks indexed.
```

**What happened:**
1. Each document was split into ~500-character chunks (see `ingest.py:chunk_text()`)
2. Each chunk was sent to the embedding model, which returned a vector (a list of floats)
3. Each vector + its source text was stored in ChromaDB

This is the "build index" phase. Like building a B-tree index on a database column — it's a one-time cost that makes all future queries fast.

## Step 3: Search by Meaning

Open [http://localhost:5001](http://localhost:5001) and try these searches:

| Search Query | What You'd Expect |
|-------------|-------------------|
| "machine running out of memory" | Results about OOM killer, memory management, swap |
| "protecting against hackers" | Results about defense in depth, network segmentation |
| "service keeps crashing" | Results about restart policies, health checks, systemd |
| "slow network performance" | Results about duplex mismatch, signal quality, latency |

Notice: the search terms don't appear verbatim in the documents. "Machine running out of memory" finds text about "the OOM killer" and "physical memory is exhausted" because the embedding model understands these are semantically related.

**This is the key insight.** A keyword search for "machine running out of memory" would match *none* of those documents. Semantic search finds them because embeddings preserve meaning, not exact words.

## Step 4: Understand Similarity Scores

Each result shows a similarity percentage:
- **>70%**: Strong semantic match
- **40-70%**: Related but may not be exactly what you asked
- **<40%**: Weak match — the query and document are only loosely related

These correspond to cosine similarity between the query vector and document vectors. See [Embeddings as Hashing](../../concepts/embeddings-as-hashing.md) for why this works.

## Step 5: Add Your Own Documents

Drop any `.txt` or `.md` files into `sample-docs/` and restart:

```bash
docker compose restart app
```

The ingest script is idempotent — it skips chunks that are already indexed and only processes new ones.

## What You Just Did

- **Built an embedding pipeline** — text in, vectors out (like computing content hashes)
- **Created a vector index** — ChromaDB with HNSW for fast approximate nearest neighbor search
- **Experienced semantic search** — found documents by meaning, not keywords
- **Understood chunking** — why documents are split and how chunk size affects search quality
