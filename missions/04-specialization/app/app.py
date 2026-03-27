"""
Mission 04 — Specialization: Domain expert chat interface.

Same RAG pipeline as Mission 02, but configured by a domain's prompts.yaml.
The system prompt, collection, and greeting all come from the domain config —
not hardcoded. Change the domain, change the expert.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, Response, stream_with_context, jsonify

import chromadb
from shared.provider import chat, stream, embed
from shared.config import get_config
from domain_config import load_domain
from evaluator import run_tests

app = Flask(__name__)

DOMAIN_PATH = os.environ.get("DOMAIN_PATH", "/app/domains/networking")
domain = load_domain(DOMAIN_PATH)


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    """Retrieve chunks from the domain-specific collection."""
    config = get_config()
    client = chromadb.PersistentClient(path=config.chroma_path)
    collection = client.get_or_create_collection(
        name=domain.collection_name,
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
    """Build the prompt using the domain's system prompt."""
    context_parts = []
    for chunk in chunks:
        context_parts.append(f"[Source: {chunk['source']}]\n{chunk['text']}")
    context_block = "\n\n---\n\n".join(context_parts)

    messages = [
        {"role": "system", "content": domain.system_prompt},
        {"role": "user", "content": f"Context documents:\n\n{context_block}\n\n---\n\nQuestion: {query}"},
    ]

    return messages


@app.route("/")
def index():
    return render_template(
        "expert.html",
        domain_name=domain.name,
        greeting=domain.greeting,
    )


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    """RAG query using the domain's system prompt and collection."""
    query = request.json.get("query", "")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    chunks = retrieve(query, top_k=4)
    messages = augment(query, chunks)

    def generate():
        yield f"event: sources\ndata: {json.dumps(chunks)}\n\n"

        for token in stream(messages):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
    )


@app.route("/evaluate", methods=["GET"])
def evaluate():
    """Run the domain evaluation suite and return results."""
    results = run_tests(DOMAIN_PATH)
    return jsonify(results)


if __name__ == "__main__":
    print("=" * 50)
    print(f"  Kindling — Mission 04: Specialization")
    print(f"  Domain: {domain.name}")
    print(f"  Open http://localhost:5004 in your browser")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5004, debug=False)
