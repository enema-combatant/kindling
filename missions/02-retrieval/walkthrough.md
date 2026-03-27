# Mission 02 — Retrieval: Walkthrough

## The Big Picture

RAG is a three-step pipeline. Open `app/rag.py` and follow along — it's ~60 lines.

### Step 1: Retrieve (`retrieve()`)

```python
query_vector = embed([query])[0]
results = collection.query(query_embeddings=[query_vector], n_results=top_k)
```

Your question is embedded into a vector (same model used for documents), then the vector database returns the top-k most similar chunks. This is a database lookup — fast and deterministic.

### Step 2: Augment (`augment()`)

```python
messages = [
    {"role": "system", "content": RAG_SYSTEM_PROMPT},
    {"role": "user", "content": f"Context documents:\n\n{context_block}\n\nQuestion: {query}"},
]
```

The retrieved chunks are formatted into a prompt. The system prompt instructs the LLM to base its answer on the context and cite sources. The user message includes both the context and the question.

This is the "enrichment" step — you're augmenting the user's bare question with authoritative data, exactly like a query service enriching a request with data from multiple backends.

### Step 3: Generate (`generate()`)

```python
return chat(messages)
```

The LLM reads the context + question and produces a grounded answer. Because the relevant documents are literally in the prompt, the LLM doesn't need to rely on its training data — it can cite what it sees.

## What Makes This Work

The quality of RAG depends on the quality of retrieval. If the right documents aren't retrieved, the LLM can't produce a good answer. This is why Mission 01 (embeddings + search) matters — it's the foundation that Mission 02 builds on.

## Try These Queries

- "What should I do when a container keeps restarting?" — Should pull from container-operations.txt
- "How do I protect my network from intruders?" — Should pull from security-fundamentals.txt
- "What causes slow database performance?" — Should pull from server-administration.txt (swap, disk)
- "How do I debug DNS issues?" — Should pull from network-troubleshooting.txt

Notice the sources panel on the right — it shows exactly which chunks were retrieved and how similar they were to your query. This transparency is intentional. In production, you'd hide this from users. In learning, it's essential for understanding what's happening.
