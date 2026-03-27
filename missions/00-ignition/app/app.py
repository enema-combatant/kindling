"""
Mission 00 — Ignition: A minimal chat interface.

This is deliberately simple. No frameworks, no abstractions beyond the
provider module. You can read every line and understand what's happening.
"""

import sys
import os

# Add project root to path so we can import shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, Response, stream_with_context
from shared.provider import chat, stream as stream_chat

app = Flask(__name__)

# The system prompt — this is your "service configuration."
# Change it and the model's behavior changes. See concepts/prompts-as-configs.md
SYSTEM_PROMPT = """You are a helpful AI assistant. You give clear, concise answers.
If you don't know something, say so — don't make things up."""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    """Non-streaming chat — send a message, get a complete response."""
    user_message = request.json.get("message", "")
    if not user_message:
        return {"error": "No message provided"}, 400

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    response = chat(messages)
    return {"response": response}


@app.route("/stream", methods=["POST"])
def stream_endpoint():
    """Streaming chat — tokens arrive as they're generated."""
    user_message = request.json.get("message", "")
    if not user_message:
        return {"error": "No message provided"}, 400

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    def generate():
        for chunk in stream_chat(messages):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
    )


if __name__ == "__main__":
    print("=" * 50)
    print("  Kindling — Mission 00: Ignition")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False)
