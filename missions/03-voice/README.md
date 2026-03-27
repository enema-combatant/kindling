# Mission 03 — Voice

*Give your AI ears and a mouth.*

**Time:** ~30 minutes
**Infra Analogy:** Adding a management console — same system, new interface. Like adding a web UI to a CLI tool.
**Concepts:** [Tokens as Packets](../../concepts/tokens-as-packets.md)

## What You'll Build

Voice input and output for your RAG system. Press a button, speak a question, hear a spoken answer — grounded in your documents. Under the hood:

```
🎤 Microphone → Whisper (STT) → RAG Pipeline → Piper (TTS) → 🔊 Speaker
```

Three services working together:
- **Whisper** (faster-whisper): Converts your speech to text
- **RAG**: Retrieves context and generates an answer (from Mission 02)
- **Piper**: Converts the text answer to spoken audio

## Quick Start

```bash
cd missions/03-voice
docker compose up
```

Open [http://localhost:5003](http://localhost:5003). Click the microphone button and speak.

## Verify

```bash
./verify.sh
```

## Next Steps

- [Walkthrough](walkthrough.md) — understand the audio pipeline
- [Extend](extend.md) — different voices, wake words, streaming
- Ready for more? → [Mission 04 — Specialization](../04-specialization/)
