# Mission 05 — Agents: Walkthrough

## The Control Loop

Open `app/agent.py` and find `run_agent()`. This is the entire agent — a while loop with an LLM deciding the control flow.

```python
for iteration in range(1, max_iterations + 1):
    # 1. OBSERVE + DECIDE — ask the LLM what to do
    raw = call_llm(messages, config)
    parsed = _parse_response(raw, provider)

    # 2. Did it produce a final answer?
    if not parsed["tool_calls"]:
        return {"answer": parsed["content"], "steps": steps, ...}

    # 3. ACT — execute the tool
    result = execute_tool(tool_name, tool_args)

    # 4. OBSERVE — feed the result back
    messages.append({"role": "user", "content": f"Tool result: {result}"})
```

That's the pattern. Observe, decide, act, observe. Same loop as a Kubernetes controller reconciling desired state with actual state. The LLM is the decision engine. The tools are the actuators.

## Tool Definitions — Your API Contracts

Look at `TOOL_DEFINITIONS` at the top of `agent.py`. Each tool is described in a JSON schema — like an OpenAPI spec or a protobuf definition. The LLM reads these descriptions and decides which tool to call with what arguments.

```python
{
    "type": "function",
    "function": {
        "name": "search_knowledge",
        "description": "Search the knowledge base for documents relevant to a query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
            },
            "required": ["query"],
        },
    },
}
```

The quality of tool descriptions directly affects agent behavior. Vague descriptions lead to wrong tool selection — exactly like a vague API doc leads developers to call the wrong endpoint.

## Tool Dispatch — The API Server

`execute_tool()` is a simple router. It maps tool names to Python functions:

```python
TOOL_DISPATCH = {
    "search_knowledge": search_knowledge,
    "web_fetch": web_fetch,
    "calculate": calculate,
    "read_file": read_file,
}
```

When the LLM decides to call `search_knowledge(query="DNS troubleshooting")`, the dispatch function routes that to the actual Python function. This is the "API server" in the control plane analogy.

## The Four Tools

### search_knowledge (tools/search_tool.py)

Reuses the ChromaDB collection from Mission 01-02. Embeds the query, finds nearest neighbors, returns formatted results with source attribution. This is the same retrieval step from Mission 02, now available as an agent tool.

### web_fetch (tools/web_tool.py)

Fetches a URL with safety constraints: only http/https, 10-second timeout, 2000-char response limit. The agent can pull information from the web when the knowledge base doesn't have the answer.

### calculate (tools/calc_tool.py)

Safe math using Python's `ast` module. The expression is parsed into an Abstract Syntax Tree and walked node-by-node — only numbers, arithmetic operators, and whitelisted functions (abs, round, sqrt, etc.) are allowed. Arbitrary code cannot execute.

### read_file (tools/file_tool.py)

Sandboxed file access — only reads from `/app/sample-docs/`. The path is resolved with `os.path.realpath()` to prevent directory traversal attacks (`../../etc/passwd`). This is RBAC for AI: the tool has minimum permissions.

## Sandboxing — Because Tools Have Real Effects

Every tool in this mission has constraints:

| Tool | Constraint | Why |
|------|-----------|-----|
| search_knowledge | Read-only vector DB | Can't modify indexed data |
| web_fetch | HTTP/HTTPS only, 10s timeout, 2000 chars | No internal network, no hangs, bounded output |
| calculate | AST whitelist only | No arbitrary code execution |
| read_file | /app/sample-docs/ only | No filesystem escape |

This is the principle of least privilege applied to AI tools. An agent with a `run_command` tool can run commands. An agent with a `write_file` tool can write files. Scope your tools carefully — exactly like you'd scope a service account.

## Provider Normalization

The `_parse_response()` function normalizes different provider response formats into a common shape:

```python
{"content": str | None, "tool_calls": [{"name": ..., "arguments": ...}]}
```

Ollama, OpenAI, and Anthropic all return tool calls differently. The normalization layer means the agent loop itself doesn't care which provider is active.

## When Things Go Wrong

Try these to see failure modes:

- Ask something the knowledge base can't answer — watch the agent search, find nothing useful, and admit it
- Ask the agent to fetch a nonexistent URL — the web tool returns an error, the agent adapts
- Ask an extremely complex multi-step question — watch the iteration count climb

The `max_iterations=10` guard prevents infinite loops. Without it, a confused agent could call tools forever, consuming API credits and never converging.

## The Reasoning Trace

The trace panel on the right side of the UI shows every tool call: which tool, what arguments, what result. This transparency is essential for debugging and trust. In production, you'd log this trace and potentially show it to power users. For learning, it's how you understand what the agent is actually doing versus what you think it's doing.
