# Mission 05 — Agents

*Give your AI hands. A control plane — observe, decide, act, observe. Same loop as a Kubernetes controller.*

**Time:** ~1 hour
**Infra Analogy:** A control plane — the LLM is the decision engine in a reconciliation loop, calling tools until the task converges to a final answer.
**Concepts:** [Agents as Control Planes](../../concepts/agents-as-control-planes.md)

## What You'll Build

An AI agent with a tool-calling loop. The agent reads your question, decides which tool to call (search your knowledge base, fetch a URL, run a calculation, read a file), executes it, reads the result, and repeats until it has enough information to answer. You'll see every step in a reasoning trace panel — no black boxes.

```
                     ┌───────────────────────────────────────────┐
                     │            Agent Control Loop              │
                     │                                           │
┌──────────┐         │  ┌─────────┐   tool_call?   ┌─────────┐  │
│  Browser  │ query   │  │  Ollama  │ ───────────→  │  Tools   │  │
│  :5005    │ ──────→ │  │  (LLM)  │ ←───────────  │ Executor │  │
└──────────┘         │  └─────────┘   result       └─────────┘  │
     ↑               │       │                      ┌─────────┐  │
     │ answer +      │       │ text                  │ search  │  │
     │ trace         │       │ (done)                │ web     │  │
     └───────────────│───────┘                       │ calc    │  │
                     │                               │ file    │  │
                     └───────────────────────────────┴─────────┘
```

## Quick Start

```bash
cd missions/05-agents
docker compose up
```

Open [http://localhost:5005](http://localhost:5005). Try a multi-step question like: "What does the documentation say about container memory limits, and what's 80% of 120 gigabytes?"

## Try These Multi-Step Queries

- "Search for information about DNS troubleshooting and summarize the key steps" — single tool call
- "What's 2048 divided by 3, rounded to two decimal places?" — calculator tool
- "Search for container operations advice, then also search for security best practices, and combine them into a checklist" — multiple search calls
- "Read the file container-operations.txt and summarize the most important points" — file tool

## Verify

```bash
./verify.sh
```

## Next Steps

- [Walkthrough](walkthrough.md) — understand the control loop, tool definitions, and sandboxing
- [Extend](extend.md) — write your own tools, multi-agent patterns, MCP servers
