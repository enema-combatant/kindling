# Concepts — AI Through an Infrastructure Lens

These documents translate AI concepts into infrastructure language. They're not dumbed down — they're translated from one technical domain to another.

You don't need to read these front-to-back. Each mission links to the relevant concepts when they come up. Come here when you want to understand *why* something works, not just *how* to make it work.

| Concept | AI Term | Your Term |
|---------|---------|-----------|
| [Embeddings as Hashing](embeddings-as-hashing.md) | Vector embeddings | Content-addressable hashes |
| [Vectors as Indexes](vectors-as-indexes.md) | Vector databases, HNSW | B-tree indexes, query planners |
| [RAG as Query Pipeline](rag-as-query-pipeline.md) | Retrieval-augmented generation | `SELECT` with semantic `WHERE` |
| [Tokens as Packets](tokens-as-packets.md) | Tokenization, context windows | MTU, fragmentation, buffers |
| [Prompts as Configs](prompts-as-configs.md) | System prompts, few-shot | Service configuration files |
| [Agents as Control Planes](agents-as-control-planes.md) | Agent loops, tool calling | Kubernetes reconciliation |

## A Note on Analogies

Every analogy breaks down eventually. These are designed to give you the right *intuition*, not a mathematically rigorous mapping. When you hit the edges where the analogy stops working, that's when you're learning the genuinely new parts of AI — the parts that don't have infrastructure equivalents. That's the good stuff.
