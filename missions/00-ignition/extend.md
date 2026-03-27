# Mission 00 — Extend

Now that you have a working chat interface, try these modifications.

## Try a Different Model

Edit your `.env` file:

```bash
# Smaller and faster (good for CPU):
KINDLING_MODEL=llama3.2:1b

# Larger and smarter (needs more RAM/VRAM):
KINDLING_MODEL=qwen3:8b

# Code-focused:
KINDLING_MODEL=qwen2.5-coder:3b
```

Restart: `docker compose down && docker compose up`

Notice how different models have different personalities, speeds, and capabilities — same interface, different engine. Like swapping the backend behind a load balancer.

## Adjust Temperature

In `app/app.py`, try changing the temperature parameter:

```python
response = chat(messages, temperature=0.0)  # Deterministic
response = chat(messages, temperature=1.0)  # Creative/random
```

Ask the same question multiple times at each setting. At 0.0, responses are nearly identical. At 1.0, they vary significantly.

## Modify the System Prompt

The system prompt is your primary tuning lever. Try specialized personas:

```python
# Network troubleshooter
SYSTEM_PROMPT = """You are a senior network engineer. When users describe
problems, ask about the topology first, then suggest diagnostic commands.
Always specify which device to run commands on."""

# Socratic teacher
SYSTEM_PROMPT = """You are a patient teacher who never gives direct answers.
Instead, ask guiding questions that help the user discover the answer
themselves. Use analogies from everyday life."""
```

## Add Conversation History

The current implementation sends only one message at a time (no memory of previous messages). To add conversation history, modify `app.py` to maintain a message list:

```python
# Store conversation in session or in-memory list
conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

# In the chat endpoint, append the user message and response:
conversation.append({"role": "user", "content": user_message})
response = chat(conversation)
conversation.append({"role": "assistant", "content": response})
```

This lets the model reference earlier messages — the foundation for multi-turn conversation.

## Switch to a Cloud Provider

Change `.env` to use OpenAI or Groq:

```bash
KINDLING_PROVIDER=groq
GROQ_API_KEY=gsk_...
KINDLING_MODEL=llama-3.3-70b-versatile
```

Notice the speed difference. Groq runs a 70B model at 300+ tokens/second — much faster than local inference on most hardware. The trade-off: your data goes to a cloud API.
