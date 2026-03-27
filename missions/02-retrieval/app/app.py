"""
Mission 02 — Retrieval: RAG chat interface with citations.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, Response, stream_with_context, jsonify
from rag import retrieve, augment, generate_stream

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/ask", methods=["POST"])
def ask():
    """RAG query with streaming response."""
    query = request.json.get("query", "")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Step 1 & 2: Retrieve and augment
    chunks = retrieve(query, top_k=4)
    messages = augment(query, chunks)

    # Return sources immediately, then stream the answer
    def generate():
        # Send sources first as a JSON event
        yield f"event: sources\ndata: {json.dumps(chunks)}\n\n"

        # Stream the answer (JSON-encode to handle newlines in SSE)
        for token in generate_stream(messages):
            yield f"data: {json.dumps(token)}\n\n"
        yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
    )


if __name__ == "__main__":
    print("=" * 50)
    print("  Kindling — Mission 02: Retrieval")
    print("  Open http://localhost:5002 in your browser")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5002, debug=False)
