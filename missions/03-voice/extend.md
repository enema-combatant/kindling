# Mission 03 — Extend

## Try Different Voices

Piper supports many voices. Change the voice in `docker-compose.yml`:

```yaml
piper:
    command: --voice en_US-amy-medium        # Different speaker
    # command: --voice en_GB-alan-medium     # British accent
```

See available voices at: https://rhasspy.github.io/piper-samples/

## Use a Larger Whisper Model

For better transcription accuracy (at the cost of speed):

```yaml
whisper:
    environment:
      - WHISPER__MODEL=Systran/faster-whisper-small.en   # More accurate
```

## Add Streaming TTS

Instead of waiting for the full answer before speaking, you could:
1. Stream the LLM response (already working in Mission 02)
2. Buffer sentences
3. Send each sentence to Piper as it completes
4. Play audio segments back-to-back

This creates a more natural conversational flow where the AI starts speaking before it's done thinking.

## Implement Wake Words

Add always-on listening with a wake word (like "Hey Kindling"):
- Use [openWakeWord](https://github.com/dscripka/openWakeWord) for local wake word detection
- Only start the full pipeline when the wake word is detected
- This is how voice assistants work in practice
