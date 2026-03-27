# Mission 05 — Extend

## Write a Custom Tool

Adding a tool is three steps:

### 1. Write the function

Create `app/tools/my_tool.py`:

```python
def list_files(directory: str = ".") -> str:
    """List files in the sample-docs directory."""
    import os
    safe_dir = "/app/sample-docs"
    files = os.listdir(safe_dir)
    return "\n".join(sorted(files))
```

### 2. Add the tool definition

In `agent.py`, add to `TOOL_DEFINITIONS`:

```python
{
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "List all available files in the document directory.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}
```

### 3. Register in dispatch

```python
from tools.my_tool import list_files

TOOL_DISPATCH = {
    ...
    "list_files": list_files,
}
```

That's it. Rebuild and the agent can use your new tool.

## Tool Design Guidelines

- **Descriptions matter more than code.** The LLM reads descriptions to decide when to call a tool. Write them like API docs — specific, with examples.
- **Fewer tools, better selection.** 3-5 well-defined tools beat 20 vague ones. The LLM makes better choices with fewer options.
- **Return useful errors.** When a tool fails, return a message the LLM can act on ("File not found, available files: a.txt, b.txt") instead of a generic exception.
- **Always sandbox.** File tools should be directory-scoped. Network tools should have timeouts and allowlists. Calculation tools should use AST parsing, not eval.

## Multi-Agent Patterns

The single-agent loop in this mission handles many tasks well. For complex workflows, you can compose agents:

### Router Agent

A "manager" agent decides which specialist to delegate to:

```python
def router_agent(query):
    """Decide which specialist agent handles this query."""
    category = classify(query)  # LLM classifies the query
    if category == "technical":
        return technical_agent(query)  # Has search + file tools
    elif category == "math":
        return math_agent(query)       # Has calculator only
    else:
        return general_agent(query)    # Has all tools
```

### Pipeline Agent

Agents in sequence, each refining the previous output:

```python
def pipeline(query):
    research = research_agent(query)     # Gather information
    analysis = analysis_agent(research)  # Analyze and structure
    summary = summary_agent(analysis)    # Produce final summary
    return summary
```

### Critic Agent

One agent generates, another evaluates:

```python
def generate_and_critique(query):
    answer = agent_a(query)
    critique = agent_b(f"Evaluate this answer for accuracy: {answer}")
    if "needs improvement" in critique.lower():
        answer = agent_a(f"Revise based on feedback: {critique}\n\nOriginal: {answer}")
    return answer
```

## MCP Servers — Standardized Tool Protocol

The Model Context Protocol (MCP) is an open standard for connecting AI models to external tools and data sources. Instead of defining tools inline in your agent code, MCP lets you run a separate "tool server" that any compatible agent can connect to.

The pattern is the same as this mission — tool definitions + execution — but with a network protocol between agent and tools. Think of it as microservices for agent tools: each MCP server provides a focused set of capabilities, and agents discover and use them dynamically.

To learn more, see the [MCP specification](https://modelcontextprotocol.io/).

## Ideas for Custom Tools

- **Database query tool** — Run read-only SQL against a SQLite database
- **Shell command tool** — Execute whitelisted commands (ls, ps, df) in a sandbox
- **Image description tool** — Send an image to a vision model, return the description
- **API client tool** — Call a REST API with structured parameters
- **Memory tool** — Let the agent save and recall facts across conversations

## Observability

In production, log every tool call with:
- Timestamp
- Tool name and arguments
- Result (or error)
- Latency
- Token count for the LLM call that triggered it

This is your audit trail. When an agent does something unexpected, the trace tells you exactly why — which tool it called, what it saw, and what it decided next.
