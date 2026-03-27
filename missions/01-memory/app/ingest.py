"""
Mission 01 — Memory: Document ingestion pipeline.

This script:
1. Reads text files from sample-docs/
2. Splits them into chunks (like packet fragmentation)
3. Embeds each chunk into a vector (like computing a hash)
4. Stores the vectors in ChromaDB (like inserting into an index)

No magic — you can read every line.
"""

import hashlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import chromadb
from shared.provider import embed
from shared.config import get_config


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks by character count.

    This is the simplest chunking strategy — split by size with overlap.
    The overlap ensures context isn't lost at chunk boundaries, like
    overlapping network segments ensuring continuous coverage.

    chunk_size: ~500 chars ≈ 100-125 tokens ≈ a solid paragraph.
    overlap: ~50 chars so adjacent chunks share a sentence boundary.
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


def load_documents(docs_dir: str) -> list[dict]:
    """Load all .txt and .md files from a directory."""
    docs = []
    for filename in sorted(os.listdir(docs_dir)):
        if filename.endswith((".txt", ".md")) and not filename.startswith("README"):
            filepath = os.path.join(docs_dir, filename)
            with open(filepath, "r") as f:
                content = f.read()
            docs.append({"filename": filename, "content": content})
    return docs


def main():
    config = get_config()
    docs_dir = os.environ.get("DOCS_DIR", "/app/sample-docs")

    if not os.path.exists(docs_dir) or not os.listdir(docs_dir):
        print("No documents found in sample-docs/. Skipping ingestion.")
        return

    # Connect to ChromaDB (persistent storage)
    client = chromadb.PersistentClient(path=config.chroma_path)
    collection = client.get_or_create_collection(
        name="kindling_docs",
        metadata={"hnsw:space": "cosine"},  # cosine similarity — direction, not magnitude
    )

    # Check what's already ingested
    existing = set(collection.get()["ids"]) if collection.count() > 0 else set()

    documents = load_documents(docs_dir)
    new_chunks = 0

    for doc in documents:
        print(f"Processing: {doc['filename']}")
        chunks = chunk_text(doc["content"])

        for i, chunk in enumerate(chunks):
            # Deterministic ID — same content always gets same ID (idempotent)
            chunk_id = hashlib.sha256(f"{doc['filename']}:{i}:{chunk[:50]}".encode()).hexdigest()[:16]

            if chunk_id in existing:
                continue

            # Embed the chunk — this is the "hashing" step
            vectors = embed([chunk])

            collection.add(
                ids=[chunk_id],
                embeddings=vectors,
                documents=[chunk],
                metadatas=[{"source": doc["filename"], "chunk_index": i}],
            )
            new_chunks += 1

    total = collection.count()
    print(f"Ingestion complete: {new_chunks} new chunks added. Total: {total} chunks indexed.")


if __name__ == "__main__":
    main()
