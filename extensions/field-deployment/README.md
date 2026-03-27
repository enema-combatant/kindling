# Extension: Field Deployment

*Take your AI offline — laptop, phone, constrained hardware.*

**Status:** Roadmap (coming soon)

## What You'll Learn

- Deploying AI on resource-constrained hardware (laptop, phone, Raspberry Pi)
- sqlite-vec as a portable vector database (single file, no server)
- Offline-first architecture with graceful degradation
- Battery and thermal management for sustained inference
- The 5-tier answer architecture (deterministic tiers before LLM generation)

## Planned Contents

1. Replacing ChromaDB with sqlite-vec for single-file portability
2. Building a Termux deployment for Android phones
3. Creating a self-contained tarball for laptop deployment
4. Thermal throttling awareness and model selection
5. The tier architecture: structured lookup → golden cache → decision trees → RAG → full LLM
