"""
Agent tool: search_knowledge — query the vector database.

Reuses the ChromaDB collection built by Mission 01's ingest pipeline.
This is the same retrieval step from Mission 02, wrapped as a tool.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import chromadb
from shared.provider import embed
from shared.config import get_config


def search_knowledge(query: str, top_k: int = 3) -> str:
    """
    Search the kindling_docs collection for chunks relevant to the query.

    Returns formatted text with source attribution and similarity scores.
    """
    config = get_config()
    client = chromadb.PersistentClient(path=config.chroma_path)

    try:
        collection = client.get_collection(name="kindling_docs")
    except Exception:
        return "No documents indexed yet. Run the ingest pipeline first."

    if collection.count() == 0:
        return "Knowledge base is empty. No documents have been ingested."

    query_vector = embed([query])[0]

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    if not results["ids"][0]:
        return f"No results found for query: {query}"

    # Format results for the LLM to read
    parts = []
    for i in range(len(results["ids"][0])):
        source = results["metadatas"][0][i].get("source", "unknown")
        similarity = round(1 - results["distances"][0][i], 4)
        text = results["documents"][0][i]
        parts.append(f"[Source: {source}, Similarity: {similarity}]\n{text}")

    return "\n\n---\n\n".join(parts)
