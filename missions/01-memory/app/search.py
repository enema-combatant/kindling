"""
Mission 01 — Memory: Semantic search interface.

Search your embedded documents by meaning, not keywords.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, jsonify
import chromadb
from shared.provider import embed
from shared.config import get_config

app = Flask(__name__)


def get_collection():
    config = get_config()
    client = chromadb.PersistentClient(path=config.chroma_path)
    return client.get_or_create_collection(
        name="kindling_docs",
        metadata={"hnsw:space": "cosine"},
    )


@app.route("/")
def index():
    collection = get_collection()
    doc_count = collection.count()
    return render_template("search.html", doc_count=doc_count)


@app.route("/search", methods=["POST"])
def search():
    query = request.json.get("query", "")
    top_k = request.json.get("top_k", 5)

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Embed the query using the same model used for documents
    query_vector = embed([query])[0]

    # Search ChromaDB — this is the vector index lookup
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    # Format results
    formatted = []
    for i in range(len(results["ids"][0])):
        formatted.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i].get("source", "unknown"),
            "distance": round(results["distances"][0][i], 4),
            "similarity": round(1 - results["distances"][0][i], 4),  # cosine: 1 - distance = similarity
        })

    return jsonify({"results": formatted, "query": query})


if __name__ == "__main__":
    print("=" * 50)
    print("  Kindling — Mission 01: Memory")
    print("  Open http://localhost:5001 in your browser")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5001, debug=False)
