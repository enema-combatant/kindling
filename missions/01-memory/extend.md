# Mission 01 — Extend

## Try Different Chunk Sizes

Edit `app/ingest.py` and change the chunk parameters:

```python
chunks = chunk_text(doc["content"], chunk_size=200, overlap=25)   # Small chunks
chunks = chunk_text(doc["content"], chunk_size=1000, overlap=100)  # Large chunks
```

Delete the ChromaDB data and re-ingest:
```bash
docker compose down -v   # Remove volumes
docker compose up        # Re-ingest with new chunk sizes
```

Compare search quality. Smaller chunks are more precise but lose context. Larger chunks capture more context but may dilute the signal.

## Compare Embedding Models

If using Ollama, try a different embedding model:

```bash
# In .env:
KINDLING_EMBED_MODEL=all-minilm     # Smaller, faster, 384 dimensions
```

Re-ingest and compare. Different models produce vectors with different numbers of dimensions and different quality characteristics.

## Inspect the Vectors

Add a debug endpoint to `search.py` to see raw vectors:

```python
@app.route("/debug/vector", methods=["POST"])
def debug_vector():
    text = request.json.get("text", "")
    vector = embed([text])[0]
    return jsonify({
        "text": text,
        "dimensions": len(vector),
        "first_10": vector[:10],
        "magnitude": sum(v**2 for v in vector) ** 0.5,
    })
```

## Add Metadata Filtering

ChromaDB supports filtering by metadata alongside vector search:

```python
results = collection.query(
    query_embeddings=[query_vector],
    n_results=5,
    where={"source": "network-troubleshooting.txt"},  # Filter by source
)
```

This combines semantic search with structured filtering — the AI equivalent of `WHERE category = 'networking' ORDER BY similarity DESC`.
