# Embeddings as Hashing

*Content-addressable hashes that preserve semantic similarity.*

## The Infrastructure Mental Model

You already know hashing. SHA-256 takes any input and produces a fixed-length output. Two identical inputs always produce the same hash. But SHA-256 has a deliberate property: *similar inputs produce completely different hashes*. Change one bit, and the hash is unrecognizable.

**Embeddings are hashes that work the other way around.** They take any text and produce a fixed-length vector (a list of numbers, typically 384-1536 floats). But unlike SHA-256, *similar inputs produce similar outputs.* "The server is down" and "The machine has crashed" produce vectors that are close together in space. "I like pizza" produces a vector far away from both.

## The Technical Reality

An embedding model is a neural network trained on billions of text pairs. It learned which texts are semantically related and encodes that knowledge into the vector space. The result:

```
"The server is overloaded"     → [0.12, -0.45, 0.78, 0.33, ...]  (768 numbers)
"The machine has high load"    → [0.11, -0.44, 0.79, 0.31, ...]  (close!)
"I enjoy cooking pasta"        → [0.89, 0.12, -0.34, 0.67, ...]  (far away)
```

"Close" and "far" are measured using distance functions — cosine similarity (angle between vectors) or L2/Euclidean distance (straight-line distance). This is directly analogous to how you'd measure similarity between network traffic patterns or log signatures.

## Where the Analogy Holds

| Hashing | Embeddings |
|---------|-----------|
| Fixed-length output | Fixed-length output (384, 768, 1024 floats) |
| Deterministic (same input → same output) | Deterministic (same model + input → same vector) |
| Used for indexing and lookup | Used for indexing and search |
| Different algorithms (SHA-256, MD5) | Different models (nomic-embed-text, text-embedding-3-small) |
| Hash collisions are possible | Semantic overlap is expected and useful |

## Where the Analogy Breaks Down

- **Hashes are opaque.** You can't derive meaning from a SHA-256 output. Embedding dimensions *do* encode meaning — dimension 42 might loosely correlate with "technical content" — but the encoding is learned, not designed.
- **Hashes are designed for exact match.** Embeddings are designed for *approximate* match. The whole point is finding things that are similar but not identical.
- **Different embedding models produce incompatible vectors.** This is like having two hash functions — you can't compare a SHA-256 hash with an MD5 hash. If you embed with `nomic-embed-text` and search with `text-embedding-3-small`, you'll get garbage results. Pick a model and stick with it for a given index.

## Practical Implications

1. **Model choice is permanent for a given index.** Changing embedding models means re-embedding everything. Like changing your filesystem — you don't do it casually.
2. **Dimension count is your resolution.** 384 dimensions = lower resolution, faster, smaller. 1024 dimensions = higher resolution, slower, larger. Like choosing between 720p and 4K.
3. **Garbage in, garbage out.** Embedding "Chapter 1 Introduction The following section describes..." produces a vague vector. Embedding a clean, focused paragraph produces a precise one. Chunking strategy matters — see Mission 01.
4. **Embeddings are read-heavy.** You embed once (write), then search many times (read). Optimize for search latency, not embedding throughput. This is familiar — it's the same trade-off as building a database index.

## Try It Yourself

In Mission 01, you'll embed real documents and search them semantically. You'll see firsthand that "network connectivity issue" finds documents about "the link between the switches went down" — even though they share zero keywords.
