# Mission 02 — Extend

## Tune the Retrieval

In `rag.py`, change `top_k` to see how the number of retrieved chunks affects answer quality:

```python
chunks = retrieve(query, top_k=2)   # Less context, more focused
chunks = retrieve(query, top_k=8)   # More context, more comprehensive but noisier
```

## Modify the System Prompt

The `RAG_SYSTEM_PROMPT` in `rag.py` controls how the LLM uses the context. Try:

```python
RAG_SYSTEM_PROMPT = """You are a concise technical writer.
Summarize the relevant information from the context in bullet points.
Always cite the source document. Maximum 5 bullet points."""
```

## Add Conversation History

The current pipeline handles single questions. To support follow-up questions, maintain a conversation list and pass it to the augment step. The LLM will use previous messages as additional context.

## Implement a Similarity Threshold

Filter out low-quality retrievals before sending them to the LLM:

```python
chunks = [c for c in chunks if c["similarity"] > 0.3]
```

If no chunks pass the threshold, respond with "I don't have relevant information in my documents" instead of letting the LLM guess.

## Add Your Own Documents

Drop domain-specific documents into `../01-memory/sample-docs/` and restart. The RAG pipeline immediately works with new content — no model changes needed.
