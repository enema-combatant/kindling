"""
Mission 04 — Specialization: Corpus builder.

Ingests domain-specific documents into a named ChromaDB collection.
Each domain gets its own collection — like giving each department its own
database rather than sharing one big table.

Usage:
    python corpus_builder.py /path/to/domain/directory
"""

import hashlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import chromadb
from shared.provider import embed
from shared.config import get_config
from domain_config import load_domain


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks by character count.

    Same strategy as Mission 01 — simple, predictable, debuggable.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
    return chunks


def load_corpus(corpus_dir: str) -> list[dict]:
    """Load all .txt and .md files from the corpus directory."""
    docs = []
    if not os.path.exists(corpus_dir):
        return docs

    for filename in sorted(os.listdir(corpus_dir)):
        if filename.endswith((".txt", ".md")) and not filename.startswith((".", "README")):
            filepath = os.path.join(corpus_dir, filename)
            with open(filepath, "r") as f:
                content = f.read()
            if content.strip():
                docs.append({"filename": filename, "content": content})

    return docs


def build_corpus(domain_path: str) -> dict:
    """
    Build a domain-specific ChromaDB collection from corpus documents.

    Returns statistics about the ingestion.
    """
    config = get_config()
    domain = load_domain(domain_path)
    corpus_dir = os.path.join(domain_path, "corpus")

    documents = load_corpus(corpus_dir)
    if not documents:
        print(f"No documents found in {corpus_dir}. Skipping.")
        return {"chunks_indexed": 0, "documents_processed": 0, "avg_chunk_size": 0}

    # Each domain gets its own collection
    client = chromadb.PersistentClient(path=config.chroma_path)
    collection = client.get_or_create_collection(
        name=domain.collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    existing = set(collection.get()["ids"]) if collection.count() > 0 else set()

    total_chunks = 0
    new_chunks = 0
    chunk_sizes = []

    for doc in documents:
        print(f"  Processing: {doc['filename']}")
        chunks = chunk_text(doc["content"])

        for i, chunk in enumerate(chunks):
            total_chunks += 1
            chunk_sizes.append(len(chunk))

            # Deterministic ID scoped to this domain
            chunk_id = hashlib.sha256(
                f"{domain.collection_name}:{doc['filename']}:{i}:{chunk[:50]}".encode()
            ).hexdigest()[:16]

            if chunk_id in existing:
                continue

            vectors = embed([chunk])
            collection.add(
                ids=[chunk_id],
                embeddings=vectors,
                documents=[chunk],
                metadatas=[{"source": doc["filename"], "chunk_index": i}],
            )
            new_chunks += 1

    total_indexed = collection.count()
    avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0

    stats = {
        "domain": domain.name,
        "collection": domain.collection_name,
        "documents_processed": len(documents),
        "chunks_indexed": total_indexed,
        "new_chunks": new_chunks,
        "avg_chunk_size": round(avg_size),
    }

    print(f"  Domain: {domain.name}")
    print(f"  Collection: {domain.collection_name}")
    print(f"  Documents: {len(documents)}")
    print(f"  Chunks indexed: {total_indexed} ({new_chunks} new)")
    print(f"  Avg chunk size: {round(avg_size)} chars")

    return stats


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python corpus_builder.py <domain_path>")
        print("  e.g., python corpus_builder.py domains/networking")
        sys.exit(1)

    domain_path = sys.argv[1]
    if not os.path.isdir(domain_path):
        print(f"Error: {domain_path} is not a directory")
        sys.exit(1)

    print(f"Building corpus from: {domain_path}")
    stats = build_corpus(domain_path)
    print("Corpus build complete.")
