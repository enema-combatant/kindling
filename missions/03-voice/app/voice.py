"""
Mission 03 — Voice: Speech-to-text and text-to-speech integration.

Two pipelines:
  STT: Audio bytes → Whisper API → text
  TTS: Text → Piper (Wyoming protocol) → WAV audio bytes
"""

import io
import os
import struct
import socket

import requests


def speech_to_text(audio_bytes: bytes) -> str:
    """
    Convert speech audio to text using faster-whisper server.

    Sends raw audio to the Whisper OpenAI-compatible endpoint.
    Returns the transcribed text.
    """
    whisper_url = os.environ.get("WHISPER_URL", "http://whisper:8000")

    resp = requests.post(
        f"{whisper_url}/v1/audio/transcriptions",
        files={"file": ("audio.wav", audio_bytes, "audio/wav")},
        data={"model": "Systran/faster-whisper-base.en"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("text", "").strip()


def text_to_speech(text: str) -> bytes:
    """
    Convert text to speech audio using Piper via Wyoming protocol.

    Sends a synthesize request to Piper and returns WAV audio bytes.
    The Wyoming protocol is a simple TCP-based protocol for voice services.
    """
    piper_host = os.environ.get("PIPER_HOST", "piper")
    piper_port = int(os.environ.get("PIPER_PORT", "10200"))

    # Wyoming protocol: JSON-line messages over TCP
    import json

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((piper_host, piper_port))

    try:
        # Send synthesize request
        request_msg = {
            "type": "synthesize",
            "data": {"text": text},
        }
        msg_bytes = (json.dumps(request_msg) + "\n").encode("utf-8")
        header = struct.pack(">I", len(msg_bytes))
        sock.sendall(header + msg_bytes)

        # Read response — audio chunks followed by a sentinel
        audio_chunks = []
        while True:
            # Read 4-byte length header
            header_data = _recv_exact(sock, 4)
            if not header_data:
                break
            length = struct.unpack(">I", header_data)[0]

            # Read message body
            body = _recv_exact(sock, length)
            if not body:
                break

            msg = json.loads(body.decode("utf-8"))

            if msg.get("type") == "audio-chunk":
                # Audio data is base64-encoded in the payload
                import base64
                audio_data = base64.b64decode(msg["data"]["audio"])
                audio_chunks.append(audio_data)
            elif msg.get("type") == "audio-stop":
                break

        return b"".join(audio_chunks)

    finally:
        sock.close()


def _recv_exact(sock, n):
    """Receive exactly n bytes from a socket."""
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data
