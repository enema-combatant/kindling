"""
Mission 05 — Agents: Flask app with agent chat interface.

GET  /       — Agent chat UI with reasoning trace panel
POST /agent  — Run the agent loop, returns {answer, steps, iterations}
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, jsonify
from agent import run_agent

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("agent.html")


@app.route("/agent", methods=["POST"])
def agent_endpoint():
    """Run the agent control loop and return the full trace."""
    query = request.json.get("query", "")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        result = run_agent(query, max_iterations=10)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("  Kindling — Mission 05: Agents")
    print("  Open http://localhost:5005 in your browser")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5005, debug=False)
