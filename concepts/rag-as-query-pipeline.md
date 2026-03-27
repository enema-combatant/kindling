# RAG as Query Pipeline

*`SELECT` with a semantic `WHERE` clause.*

## The Infrastructure Mental Model

You've built query services. A user sends a request, your service checks a data store, enriches the raw data, formats a response, and sends it back. The data store doesn't generate the answer — it provides the facts. Your service layer does the synthesis.

**RAG (Retrieval-Augmented Generation) is exactly this pattern.** The user asks a question. Your system retrieves relevant documents from a vector database. Those documents are injected into the LLM's prompt as context. The LLM generates an answer grounded in those documents — not from its training data alone.

```
Traditional:  User → Query Service → Database → Format → Response
RAG:          User → RAG Pipeline  → Vector DB → LLM   → Response
```

The LLM is the formatting/synthesis layer. The vector database is the data store. The RAG pipeline is the query service that connects them.

## The Pipeline in Detail

```
1. QUERY      User asks: "What causes high CPU on the load balancer?"
                ↓
2. EMBED      Convert the question to a vector (same model used for documents)
                ↓
3. RETRIEVE   Search vector DB for top-k similar document chunks
              Returns: [chunk_1 about CPU tuning, chunk_2 about LB health, chunk_3 about process limits]
                ↓
4. AUGMENT    Build a prompt:
              "Using ONLY the following context, answer the user's question.
               Context:
               [chunk_1]
               [chunk_2]
               [chunk_3]
               Question: What causes high CPU on the load balancer?"
                ↓
5. GENERATE   LLM reads the context + question, produces a grounded answer
                ↓
6. CITE       Attach source references so the user can verify
```

Steps 2-3 are your database query. Step 4 is your query result enrichment. Step 5 is your response formatting. Step 6 is your audit trail.

## Why Not Just Ask the LLM Directly?

LLMs have training data cutoffs and will confidently fabricate answers about topics they don't know. This is called **hallucination** — the AI equivalent of a service returning cached stale data and claiming it's fresh.

RAG solves this the same way you'd solve stale cache problems: **go to the source of truth.** By retrieving current, authoritative documents and injecting them into the prompt, you ground the LLM's response in real data. It can still hallucinate, but now it has the right material in front of it — and you can verify by checking the citations.

## The Analogy in Detail

| Query Service | RAG Pipeline |
|--------------|-------------|
| User request | User question |
| SQL `WHERE` clause | Vector similarity search |
| `JOIN` across tables | Retrieving from multiple collections |
| Result formatting | LLM synthesis |
| Query timeout | Token limit / context window |
| Cache layer | Pre-computed embeddings |
| Index miss (full scan) | Low similarity scores (poor retrieval) |
| Source attribution | Citation with chunk references |

## The Context Window Problem

An LLM's context window is its buffer. Like a network buffer, it has a fixed size (4K, 8K, 32K, 128K tokens). Everything — system prompt, retrieved documents, conversation history, and the generated response — must fit in this buffer.

This means you can't just dump your entire knowledge base into the prompt. You need to be selective: retrieve the most relevant chunks, truncate if necessary, and prioritize quality over quantity. It's capacity planning for AI.

**Rule of thumb:** Retrieve 3-5 chunks of 200-500 tokens each. This leaves room for the system prompt and response while providing enough context for a good answer.

## Quality Levers

| Lever | Effect | Analogy |
|-------|--------|---------|
| **Chunk size** | Smaller = more precise, less context. Larger = more context, less precise. | Row size in a database — normalize for precision, denormalize for speed |
| **Top-k** | More results = more context but more noise | Query result limit — too many joins slow you down |
| **Similarity threshold** | Filter out low-confidence matches | Query optimizer cost threshold |
| **Reranking** | Re-score retrieved chunks with a more expensive model | Multi-stage query: fast index scan, then detailed evaluation |
| **System prompt** | Instruct the LLM how to use the context | Service configuration |

## Try It Yourself

In Mission 02, you'll build a complete RAG pipeline. You'll ingest your own documents, ask questions about them, and see the LLM answer with citations — grounded in your data, not its training set.
