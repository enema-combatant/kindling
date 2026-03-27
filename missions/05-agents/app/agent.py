"""
Mission 05 — Agents: The agent control loop.

This is the whole thing. An agent is a while loop with an LLM deciding the
control flow — like a Kubernetes controller reconciling state.

    while not done:
        response = llm(messages, tools)
        if response wants a tool call:
            result = execute_tool(name, args)
            messages.append(result)
        else:
            done = True  # LLM produced a final answer

No LangChain. No framework. ~150 lines of actual logic.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from shared.config import get_config

from tools.search_tool import search_knowledge
from tools.web_tool import web_fetch
from tools.calc_tool import calculate
from tools.file_tool import read_file

# ---------------------------------------------------------------------------
# Tool Definitions — these are the "API contracts" the LLM reads to decide
# which tool to call. Same format as OpenAI function calling.
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "Search the knowledge base for documents relevant to a query. Use this when you need to find information from the ingested documentation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query — describe what you're looking for",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default 3)",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch the text content of a web page by URL. Use this when you need to retrieve information from a specific URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch (must be http or https)",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression. Supports: +, -, *, /, ** (power), parentheses, and functions like abs(), round(), min(), max().",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate, e.g. '(120 * 0.8)' or 'round(2048 / 3, 2)'",
                    },
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the sample-docs directory. Use this to read specific documents when you know the filename.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Filename to read from the sample-docs directory, e.g. 'container-operations.txt'",
                    },
                },
                "required": ["path"],
            },
        },
    },
]

# Map tool names to functions
TOOL_DISPATCH = {
    "search_knowledge": search_knowledge,
    "web_fetch": web_fetch,
    "calculate": calculate,
    "read_file": read_file,
}


def execute_tool(name: str, args: dict) -> str:
    """
    Dispatch a tool call to the right function.

    This is the "API server" — it receives the LLM's request, routes it
    to the correct handler, and returns the result. Input validation and
    error handling happen here.
    """
    func = TOOL_DISPATCH.get(name)
    if not func:
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        result = func(**args)
        return result if isinstance(result, str) else json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"{name} failed: {str(e)}"})


def _call_ollama(messages: list[dict], config) -> dict:
    """Send a chat request to Ollama with tool definitions."""
    resp = requests.post(
        f"{config.ollama_base_url}/api/chat",
        json={
            "model": config.model,
            "messages": messages,
            "tools": TOOL_DEFINITIONS,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
            },
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def _call_openai_compatible(messages: list[dict], config, base_url: str, api_key: str) -> dict:
    """Send a chat request to an OpenAI-compatible API with tool definitions."""
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": config.model,
            "messages": messages,
            "tools": TOOL_DEFINITIONS,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def _call_anthropic(messages: list[dict], config) -> dict:
    """Send a chat request to Anthropic with tool definitions."""
    # Anthropic separates system from messages and uses a different tool format
    system = None
    filtered = []
    for msg in messages:
        if msg["role"] == "system":
            system = msg["content"]
        else:
            filtered.append(msg)

    # Convert tool definitions to Anthropic format
    tools = []
    for t in TOOL_DEFINITIONS:
        tools.append({
            "name": t["function"]["name"],
            "description": t["function"]["description"],
            "input_schema": t["function"]["parameters"],
        })

    body = {
        "model": config.model,
        "messages": filtered,
        "tools": tools,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }
    if system:
        body["system"] = system

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": config.anthropic_api_key,
            "anthropic-version": "2025-01-01",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def _parse_response(raw: dict, provider: str) -> dict:
    """
    Normalize provider responses into a common format:
      {
        "content": str | None,
        "tool_calls": [{"name": ..., "arguments": ..., "id": ...}],
        "raw_message": <provider-specific assistant message for appending to history>,
      }

    The raw_message is the provider's native assistant message structure.
    It must be appended to messages before tool results so the conversation
    history stays valid for the next API call.
    """
    if provider == "ollama":
        msg = raw.get("message", {})
        tool_calls = msg.get("tool_calls", [])
        if tool_calls:
            return {
                "content": None,
                "tool_calls": [
                    {
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"],
                        "id": None,  # Ollama doesn't use tool_call IDs
                    }
                    for tc in tool_calls
                ],
                "raw_message": msg,  # The full message dict with tool_calls
            }
        return {"content": msg.get("content", ""), "tool_calls": [], "raw_message": msg}

    elif provider == "openai":
        choice = raw["choices"][0]["message"]
        tool_calls = choice.get("tool_calls", [])
        if tool_calls:
            return {
                "content": None,
                "tool_calls": [
                    {
                        "name": tc["function"]["name"],
                        "arguments": json.loads(tc["function"]["arguments"]),
                        "id": tc["id"],  # Required for OpenAI tool results
                    }
                    for tc in tool_calls
                ],
                "raw_message": choice,  # The full message dict with tool_calls
            }
        return {"content": choice.get("content", ""), "tool_calls": [], "raw_message": choice}

    elif provider == "anthropic":
        content_blocks = raw.get("content", [])
        tool_calls = []
        text_parts = []
        for block in content_blocks:
            if block["type"] == "tool_use":
                tool_calls.append({
                    "name": block["name"],
                    "arguments": block["input"],
                    "id": block["id"],  # Required for Anthropic tool_result
                })
            elif block["type"] == "text":
                text_parts.append(block["text"])
        if tool_calls:
            return {
                "content": None,
                "tool_calls": tool_calls,
                "raw_message": content_blocks,  # The full content block list
            }
        return {
            "content": "\n".join(text_parts),
            "tool_calls": [],
            "raw_message": content_blocks,
        }

    return {"content": str(raw), "tool_calls": [], "raw_message": None}


def run_agent(query: str, max_iterations: int = 10) -> dict:
    """
    The agent control loop. This is the entire agent.

    1. Send messages + tool definitions to the LLM
    2. If the LLM returns a tool_call, execute it
    3. Append the tool result to messages
    4. Repeat until the LLM returns a text response or max_iterations
    5. Return {answer, steps, iterations}
    """
    config = get_config()
    provider = config.provider

    # Choose the right API caller
    call_llm = {
        "ollama": _call_ollama,
        "openai": lambda msgs, cfg: _call_openai_compatible(
            msgs, cfg, "https://api.openai.com/v1", cfg.openai_api_key),
        "anthropic": _call_anthropic,
        "groq": lambda msgs, cfg: _call_openai_compatible(
            msgs, cfg, "https://api.groq.com/openai/v1", cfg.groq_api_key),
    }[provider]

    # Conversation history — the LLM sees everything
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful agent with access to tools. Use them to answer "
                "the user's question. Call tools when you need information you don't "
                "have. When you have enough information, respond with a complete answer. "
                "Be concise and cite your sources when using search results."
            ),
        },
        {"role": "user", "content": query},
    ]

    steps = []  # Reasoning trace — every tool call logged

    for iteration in range(1, max_iterations + 1):
        # 1. OBSERVE + DECIDE — ask the LLM what to do
        raw = call_llm(messages, config)
        parsed = _parse_response(raw, provider)

        # 2. Check: did the LLM produce a final answer?
        if not parsed["tool_calls"]:
            return {
                "answer": parsed["content"] or "(No response from model)",
                "steps": steps,
                "iterations": iteration,
            }

        # 3. ACT — execute each tool call and feed results back
        #
        # First, append the assistant's response to preserve the tool_calls
        # in the conversation history. Each provider needs its own format.
        if provider == "ollama":
            messages.append(parsed["raw_message"])
        elif provider in ("openai", "groq"):
            messages.append(parsed["raw_message"])
        elif provider == "anthropic":
            messages.append({"role": "assistant", "content": parsed["raw_message"]})

        for tc in parsed["tool_calls"]:
            tool_name = tc["name"]
            tool_args = tc["arguments"]
            tool_id = tc["id"]

            result = execute_tool(tool_name, tool_args)

            steps.append({
                "tool": tool_name,
                "args": tool_args,
                "result": result[:500],  # Truncate for the trace display
            })

            # 4. OBSERVE — feed the result back in provider-native format
            if provider == "ollama":
                messages.append({
                    "role": "tool",
                    "content": str(result),
                })
            elif provider in ("openai", "groq"):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": str(result),
                })
            elif provider == "anthropic":
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": str(result),
                    }],
                })

    # Max iterations reached — return what we have
    return {
        "answer": "(Agent reached maximum iterations without a final answer. Here's what was gathered: "
        + "; ".join(s["result"][:100] for s in steps[-3:]) + ")",
        "steps": steps,
        "iterations": max_iterations,
    }
