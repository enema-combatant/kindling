# Vectors as Indexes

*B-trees to HNSW. Query planning to approximate nearest neighbor.*

## The Infrastructure Mental Model

You've built database indexes. A B-tree index on a `users` table lets you find a row by email in O(log n) time instead of scanning every row. The database maintains the index structure, and the query planner decides when to use it.

**A vector database is the same idea, applied to embeddings.** Instead of indexing rows by column values, it indexes documents by their semantic meaning (as encoded in embedding vectors). Instead of exact-match lookups (`WHERE email = 'foo@bar.com'`), it does nearest-neighbor lookups ("find the 5 documents most semantically similar to this query").

## How Vector Indexes Work

### The Naive Approach (Full Scan)

Compare your query vector against every stored vector using cosine similarity. Return the top-k. This works for small collections but scales linearly — O(n) per query. With a million documents, every search checks a million vectors.

This is the equivalent of a `SELECT * FROM docs ORDER BY similarity(query, embedding) LIMIT 5` with no index. It works. It's slow.

### HNSW — The Infrastructure-Friendly Index

Most vector databases use **HNSW** (Hierarchical Navigable Small World). Think of it as a skip list meets a graph:

- **Layer 0:** All vectors, densely connected to nearby neighbors
- **Layer 1:** A subset of vectors, sparsely connected (long-range links)
- **Layer 2:** An even sparser subset (highway links)
- **Top layer:** A handful of entry points

Search starts at the top layer and navigates downward, getting more precise at each level. It's like routing a packet: start with backbone routers (coarse), then regional (medium), then last-mile (precise).

**Key trade-off:** HNSW is *approximate*. It finds very good neighbors, but not guaranteed-best neighbors. In exchange, it runs in O(log n) instead of O(n). For 99% of use cases, "very good" is indistinguishable from "best."

## The Analogy in Detail

| Database Index | Vector Index |
|---------------|-------------|
| B-tree, hash index | HNSW, IVF, FLAT |
| Index on column values | Index on embedding vectors |
| Exact match (`WHERE x = y`) | Approximate nearest neighbor |
| Query planner chooses index | Distance metric chooses search strategy |
| Index rebuild after bulk insert | Index rebuild after bulk embed |
| Index size vs. query speed trade-off | ef_construction vs. recall trade-off |

## Distance Metrics (Your Query Operators)

| Metric | What It Measures | When to Use |
|--------|-----------------|-------------|
| **Cosine similarity** | Angle between vectors (direction) | Most text search — you care about meaning, not magnitude |
| **L2 (Euclidean)** | Straight-line distance | When magnitude matters (rare for text) |
| **Dot product** | Combined direction + magnitude | Normalized vectors (equivalent to cosine) |

Cosine similarity is the default for text search. It's like comparing the *shape* of two network traffic patterns regardless of volume.

## Practical Implications

1. **Collection = Table, Document = Row, Vector = Indexed Column.** The mental model maps directly.
2. **You still need metadata.** Vectors find semantically similar documents, but you often want to filter by date, source, category. Vector DBs support metadata filtering — it's the `WHERE` clause alongside the similarity search.
3. **Batch your inserts.** Embedding + indexing is write-heavy. Batch 100-1000 documents at a time, not one-by-one. Same as database bulk loading.
4. **Index parameters matter.** HNSW's `ef_construction` (build quality) and `ef_search` (search quality) trade build time against recall accuracy. Start with defaults, tune if needed.
5. **Memory is the bottleneck.** Vectors live in memory for fast search. 1M vectors at 768 dimensions = ~3 GB RAM. Plan your capacity like you'd plan database memory.

## ChromaDB — Your First Vector Database

Kindling uses **ChromaDB** — an embedded vector database (like SQLite for vectors). No server to manage, no ports to configure. It runs inside your application process and stores data to disk.

For production, you'd use Qdrant, Milvus, or Pinecone — the same way you'd graduate from SQLite to PostgreSQL. But for learning the concepts, ChromaDB removes all the operational overhead so you can focus on what matters.

## Try It Yourself

In Mission 01, you'll create a ChromaDB collection, embed documents into it, and run semantic searches. You'll see how the index returns relevant results even when query and document share no common words.
