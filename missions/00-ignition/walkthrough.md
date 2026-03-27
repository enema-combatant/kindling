# Mission 00 — Ignition: Walkthrough

This walkthrough explains what happens at each step when you run Mission 00.

## Step 1: Start the Stack

```bash
docker compose up
```

**What happens:**
1. Docker pulls the Ollama image (a model inference server — think of it as a database server for AI models)
2. Docker builds the Flask app container from the Dockerfile
3. Ollama starts and exposes port 11434 (its REST API)
4. The app's `entrypoint.sh` waits for Ollama to be healthy, then pulls the model
5. Flask starts on port 5000

**First run takes 2-5 minutes** (downloading the ~2 GB model). Subsequent runs start in seconds because the model is cached in a Docker volume.

## Step 2: Open the Chat Interface

Navigate to [http://localhost:5000](http://localhost:5000).

You'll see a minimal chat interface. It's deliberately simple — no React, no build step, no framework. Just HTML, CSS, and vanilla JavaScript. You can read every line in `app/templates/index.html`.

## Step 3: Send a Message

Type something and press Enter (or click Send).

**What happens under the hood:**

1. JavaScript sends a `POST /stream` request with your message as JSON
2. Flask's `/stream` endpoint builds a **messages array**:
   ```python
   [
       {"role": "system", "content": "You are a helpful AI assistant..."},
       {"role": "user", "content": "your message here"}
   ]
   ```
3. The provider module (`shared/provider.py`) sends this to Ollama's `/api/chat` endpoint
4. Ollama processes the tokens through the neural network and generates a response
5. Tokens stream back one at a time via Server-Sent Events (SSE)
6. JavaScript appends each token to the message bubble as it arrives

**Watch the response appear word by word.** That's tokens being generated sequentially — each one takes a few milliseconds on GPU, tens of milliseconds on CPU. This is the "decode" phase described in [Tokens as Packets](../../concepts/tokens-as-packets.md).

## Step 4: Understand the System Prompt

Open `app/app.py` and look at `SYSTEM_PROMPT`:

```python
SYSTEM_PROMPT = """You are a helpful AI assistant. You give clear, concise answers.
If you don't know something, say so — don't make things up."""
```

This is the model's configuration. It's sent with every request, before your message. Try changing it:

```python
SYSTEM_PROMPT = """You are a grumpy sysadmin who answers questions
reluctantly and always complains about users."""
```

Restart the app (`docker compose restart app`) and ask the same question. Same model, different behavior — just like changing a service config.

See [Prompts as Configs](../../concepts/prompts-as-configs.md) for more.

## Step 5: Verify

```bash
./verify.sh
```

This sends test requests to both the standard and streaming endpoints and checks for coherent responses. If all three tests pass, Mission 00 is complete.

## What You Just Did

- **Deployed a model server** (Ollama) — the AI equivalent of deploying a database
- **Built a service layer** (Flask app) — that translates user requests into API calls
- **Configured behavior** (system prompt) — without changing any code
- **Observed streaming** (SSE) — tokens arriving like packets

You now have a working AI service running on your hardware. In Mission 01, you'll give it a memory.
