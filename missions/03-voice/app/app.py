"""
Mission 03 — Voice: RAG with speech input/output.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, jsonify, send_file
import io

from rag import rag_query
from voice import speech_to_text, text_to_speech

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("voice.html")


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Convert uploaded audio to text."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    audio_file = request.files["audio"]
    audio_bytes = audio_file.read()

    text = speech_to_text(audio_bytes)
    return jsonify({"text": text})


@app.route("/ask-voice", methods=["POST"])
def ask_voice():
    """Full voice pipeline: transcribe → RAG → TTS."""
    # Allow text override from the typed input fallback
    text_override = request.form.get("text_override", "").strip()

    if text_override:
        question = text_override
    elif "audio" in request.files:
        audio_bytes = request.files["audio"].read()
        if len(audio_bytes) == 0:
            return jsonify({"error": "No audio recorded"}), 400
        question = speech_to_text(audio_bytes)
    else:
        return jsonify({"error": "No audio or text provided"}), 400

    if not question:
        return jsonify({"error": "Could not understand audio"}), 400

    # Step 2: RAG query
    result = rag_query(question)

    # Step 3: Text to speech
    try:
        tts_audio = text_to_speech(result["answer"])
        has_audio = len(tts_audio) > 0
    except Exception:
        tts_audio = b""
        has_audio = False

    return jsonify({
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"],
        "has_audio": has_audio,
    })


@app.route("/speak", methods=["POST"])
def speak():
    """Convert text to speech audio."""
    text = request.json.get("text", "")
    if not text:
        return jsonify({"error": "No text"}), 400

    audio_bytes = text_to_speech(text)
    return send_file(
        io.BytesIO(audio_bytes),
        mimetype="audio/wav",
        download_name="response.wav",
    )


if __name__ == "__main__":
    print("=" * 50)
    print("  Kindling — Mission 03: Voice")
    print("  Open http://localhost:5003 in your browser")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5003, debug=False)
