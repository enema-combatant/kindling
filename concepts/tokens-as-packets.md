# Tokens as Packets

*MTU, fragmentation, context windows as buffer sizes.*

## The Infrastructure Mental Model

You understand packets. Data is broken into fixed-size units for transmission. There's an MTU (Maximum Transmission Unit) that limits packet size. If your data exceeds the MTU, it gets fragmented. Buffers hold packets in transit, and when a buffer fills up, packets get dropped.

**Tokens are the packets of language models.** Text is broken into tokens — subword units that the model processes one at a time. The context window is the buffer. When it fills up, content gets dropped (truncated). Understanding tokenization helps you predict costs, manage context, and avoid silent truncation.

## What Is a Token?

A token is a chunk of text — roughly 3-4 characters or 0.75 words in English. The model doesn't see characters or words; it sees tokens. A tokenizer converts text to token IDs before processing and back after generation.

```
"The server is experiencing high latency"
→ ["The", " server", " is", " experiencing", " high", " latency"]
→ [791, 3847, 374, 25051, 1579, 38698]
= 6 tokens (from ~42 characters)
```

Some words are single tokens ("the", "server"). Uncommon words get split into subword tokens ("experiencing" might become "exp" + "eriencing"). Technical jargon, code, and non-English text use more tokens per character.

**Rule of thumb:** 1 token ≈ 4 characters ≈ 0.75 words. A typical paragraph is 50-100 tokens.

## The Context Window — Your Buffer

| Network Concept | LLM Equivalent |
|----------------|---------------|
| Buffer size | Context window (4K, 8K, 32K, 128K tokens) |
| Packet | Token |
| MTU | Maximum token length per piece |
| Buffer overflow → packet drop | Context overflow → truncation |
| Bandwidth (packets/sec) | Token throughput (tokens/sec) |
| Latency (time to first byte) | Time to first token (TTFT) |
| Payload vs. header | User content vs. system prompt overhead |

The context window holds *everything*: system prompt, conversation history, retrieved documents (in RAG), and the generated response. It's a shared buffer. If your system prompt uses 500 tokens and your retrieved documents use 2,000, you have `window_size - 2500` tokens left for conversation and response.

## Fragmentation and Chunking

When you ingest documents for RAG (Mission 02), you break them into chunks — fragments sized to fit efficiently in the context window. This is directly analogous to packet fragmentation:

- **Chunk too large:** Fewer chunks fit in context. You get more complete sections but fewer of them.
- **Chunk too small:** More chunks fit, but each one lacks surrounding context. Like tiny packets with proportionally large headers.
- **Sweet spot:** 200-500 tokens per chunk. Enough context to be meaningful, small enough to fit 3-5 in a prompt.

## Cost — Metering by the Token

Cloud providers charge per token (input + output). This is bandwidth billing:

| Concept | Network | LLM |
|---------|---------|-----|
| Metering unit | Bytes transferred | Tokens processed |
| Pricing | $/GB | $/1M tokens |
| Input vs. output | Upload vs. download | Input tokens vs. output tokens |
| Cost optimization | Compress payload, cache | Shorter prompts, cache responses |

**Cost awareness matters.** A 10-document RAG query with a 2,000-token context costs ~10x more than a simple "hello" prompt. When you're prototyping, use a local model (Ollama) to avoid surprise bills.

## Throughput and Latency

LLM inference has two phases:

1. **Prefill** — Process all input tokens at once (like establishing a connection)
2. **Decode** — Generate output tokens one at a time (like streaming a response)

**Time to first token (TTFT)** = prefill time. Longer prompts = longer TTFT.
**Tokens per second (t/s)** = decode speed. Depends on model size and hardware.

| Hardware | Typical Speed | Analogy |
|----------|--------------|---------|
| CPU only | 5-15 t/s | Dial-up |
| Consumer GPU (RTX 3060) | 30-60 t/s | Broadband |
| Data center GPU (A100) | 100-200 t/s | Fiber |
| Cloud API (Groq) | 300-800 t/s | CDN edge |

## Practical Implications

1. **Monitor your token budget.** In RAG, track how many tokens your retrieved chunks consume. Leave room for the response. It's buffer management.
2. **Shorter prompts are cheaper and faster.** Every token in your system prompt is "overhead" on every request. Keep system prompts lean.
3. **Local models are free but slower.** Cloud APIs are fast but metered. Choose based on your use case — same as choosing between on-prem and cloud compute.
4. **Token counts vary by model.** Different models use different tokenizers. The same text might be 100 tokens for one model and 120 for another. Like different network protocols having different header overhead.

## Try It Yourself

In every mission, you'll work with tokens implicitly. Mission 00 shows you raw token throughput (watch the generation speed). Mission 01 introduces chunking. Mission 02 makes context window management explicit when you see how many chunks fit alongside your prompt.
