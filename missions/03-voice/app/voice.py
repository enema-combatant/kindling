"""
Mission 03 — Voice: Speech-to-text and text-to-speech integration.

Two pipelines:
  STT: Audio bytes → Whisper API → text
  TTS: Text → Piper (Wyoming protocol via wyoming package) → WAV audio bytes
"""

import asyncio
import os

import requests
from wyoming.audio import AudioChunk, AudioStop
from wyoming.client import AsyncClient
from wyoming.tts import Synthesize


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


async def _tts_async(text: str, host: str, port: int) -> bytes:
    """Send a synthesize request to Piper via the Wyoming protocol."""
    async with AsyncClient(host, port) as client:
        await client.write_event(Synthesize(text=text).event())

        audio_bytes = b""
        while True:
            event = await asyncio.wait_for(client.read_event(), timeout=30)
            if event is None:
                break
            if AudioChunk.is_type(event.type):
                chunk = AudioChunk.from_event(event)
                audio_bytes += chunk.audio
            elif AudioStop.is_type(event.type):
                break

    return audio_bytes


def text_to_speech(text: str) -> bytes:
    """
    Convert text to speech audio using Piper via Wyoming protocol.

    Uses the wyoming Python package to communicate with the Piper
    Wyoming server over TCP. Returns raw PCM audio bytes.
    """
    piper_host = os.environ.get("PIPER_HOST", "piper")
    piper_port = int(os.environ.get("PIPER_PORT", "10200"))

    return asyncio.run(_tts_async(text, piper_host, piper_port))
