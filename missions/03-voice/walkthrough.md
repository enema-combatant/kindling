# Mission 03 — Voice: Walkthrough

## The Audio Pipeline

Voice adds two services to the existing RAG pipeline:

```
Browser Mic → WebM audio → Flask /ask-voice
                               ↓
                          Whisper (STT) → "What causes high CPU?"
                               ↓
                          RAG Pipeline (from Mission 02)
                               ↓
                          "Based on the documents, high CPU is caused by..."
                               ↓
                          Piper (TTS) → WAV audio
                               ↓
                          Browser plays audio
```

### Whisper — Speech to Text

[Faster-whisper](https://github.com/SYSTRAN/faster-whisper) is an optimized version of OpenAI's Whisper model. It runs on CPU and transcribes audio with surprisingly good accuracy. The server exposes an OpenAI-compatible API:

```
POST /v1/audio/transcriptions
Content-Type: multipart/form-data
Body: audio file (WAV, WebM, etc.)
Response: {"text": "transcribed text here"}
```

The `base.en` model is ~150 MB and handles conversational English well. Larger models (`small`, `medium`) improve accuracy at the cost of speed and memory.

### Piper — Text to Speech

[Piper](https://github.com/rhasspy/piper) is a fast, lightweight text-to-speech engine. It uses the Wyoming protocol (a simple TCP protocol for voice services) and produces natural-sounding speech. The `lessac-medium` voice is a good default — clear and not robotic.

## Understanding the Flow

Open `app/voice.py` and trace through:

1. **`speech_to_text()`** sends audio bytes to Whisper's REST API and gets text back
2. **`text_to_speech()`** sends text to Piper via Wyoming protocol and gets WAV audio back

The main `app.py` connects these to the RAG pipeline from Mission 02:

```python
question = speech_to_text(audio_bytes)   # Ears
result = rag_query(question)             # Brain (Mission 02)
tts_audio = text_to_speech(result)       # Mouth
```

Same system, new interface. The RAG pipeline doesn't know or care whether the question came from a keyboard or a microphone.
