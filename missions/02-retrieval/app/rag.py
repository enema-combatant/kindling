"""
Mission 02 — Retrieval: The RAG pipeline.

This is the core of retrieval-augmented generation in ~60 lines.
No framework. No magic. Just: retrieve, augment, generate.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import chromadb
from shared.provider import chat, stream, embed
from shared.config import get_config

# The RAG system prompt — instructs the model to use context, cite sources,
# and admit when it doesn't know. This is your "service configuration."
RAG_SYSTEM_PROMPT = """You are a knowledgeable assistant that answers questions using the provided context documents.

Rules:
- Base your answer ONLY on the provided context. If the context doesn't contain enough information, say so.
- Cite your sources by referencing the document name in brackets, e.g. [network-troubleshooting.txt].
- Be concise and direct. Infrastructure professionals don't need fluff.
- If multiple sources are relevant, synthesize them into a coherent answer.
- Never make up information that isn't in the context."""


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    """
    Step 1: RETRIEVE — search the vector database for relevant chunks.

    This is the "database query" step. We embed the user's question using
    the same model that was used to embed the documents, then find the
    nearest neighbors in vector space.
    """
    config = get_config()
    client = chromadb.PersistentClient(path=config.chroma_path)
    collection = client.get_or_create_collection(
        name="kindling_docs",
        metadata={"hnsw:space": "cosine"},
    )

    query_vector = embed([query])[0]

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i].get("source", "unknown"),
            "similarity": round(1 - results["distances"][0][i], 4),
        })

    return chunks


def augment(query: str, chunks: list[dict]) -> list[dict]:
    """
    Step 2: AUGMENT — build the prompt with retrieved context.

    This is where we construct the "enriched request" — injecting the
    retrieved documents into the prompt so the LLM can use them as
    context for its answer.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[Source: {chunk['source']}]\n{chunk['text']}")

    context_block = "\n\n---\n\n".join(context_parts)

    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": f"Context documents:\n\n{context_block}\n\n---\n\nQuestion: {query}"},
    ]

    return messages


def generate(messages: list[dict]) -> str:
    """
    Step 3: GENERATE — the LLM reads the context and produces a grounded answer.
    """
    return chat(messages)


def generate_stream(messages: list[dict]):
    """Step 3 (streaming variant) — tokens arrive as they're generated."""
    return stream(messages)


def rag_query(query: str, top_k: int = 4) -> dict:
    """
    The complete RAG pipeline: retrieve → augment → generate.

    Returns the answer and the source chunks used to generate it.
    """
    # 1. Retrieve relevant chunks
    chunks = retrieve(query, top_k=top_k)

    # 2. Build the augmented prompt
    messages = augment(query, chunks)

    # 3. Generate the answer
    answer = generate(messages)

    return {
        "answer": answer,
        "sources": chunks,
        "query": query,
    }
