# Agents as Control Planes

*The Kubernetes reconciliation loop: observe, decide, act, observe.*

## The Infrastructure Mental Model

A Kubernetes controller watches the desired state (manifests) and the actual state (cluster). When they diverge, it takes action to reconcile: create a pod, scale a deployment, restart a container. Then it observes again. This is a **control loop** — an infinite cycle of observe → decide → act → observe.

**An AI agent is the same pattern with an LLM as the decision engine.** The agent observes (reads the user's request + available information), decides (the LLM chooses what to do), acts (calls a tool — searches a database, runs a calculation, fetches a URL), and observes the result. It repeats until the task is complete.

```
Kubernetes Controller:          AI Agent:
  Watch desired state             Read user query
  Compare to actual state         Assess what information is needed
  Take corrective action          Call a tool (search, calculate, fetch)
  Observe result                  Read tool output
  Repeat until converged          Repeat until answer is complete
```

## The Agent Loop

```python
# This is ~30 lines of actual code. No framework magic.

while not done:
    # 1. OBSERVE — what does the LLM see?
    response = llm.chat(
        messages=conversation + tool_results,
        tools=available_tools          # like available API endpoints
    )

    # 2. DECIDE — does it want to call a tool?
    if response.has_tool_call:
        tool_name = response.tool_call.name       # "search_docs"
        tool_args = response.tool_call.arguments   # {"query": "CPU tuning"}

        # 3. ACT — execute the tool
        result = execute_tool(tool_name, tool_args)

        # 4. OBSERVE — feed result back
        tool_results.append(result)

    else:
        # LLM is done — it has a final answer
        done = True
        final_answer = response.content
```

That's it. An agent is a while loop with an LLM deciding the control flow.

## Tool Definitions — Your API Contracts

Tools are defined as structured descriptions — like API endpoint documentation or function signatures. The LLM reads these definitions and decides which tool to call, with what arguments.

```json
{
    "name": "search_knowledge_base",
    "description": "Search the vector database for documents relevant to a query",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "top_k": {
                "type": "integer",
                "description": "Number of results to return",
                "default": 5
            }
        },
        "required": ["query"]
    }
}
```

This is an API contract. The LLM is the client. Your tool executor is the server. The JSON schema is the interface definition — like an OpenAPI spec or a protobuf definition.

## The Analogy in Detail

| Control Plane Concept | Agent Equivalent |
|----------------------|-----------------|
| Controller | Agent loop |
| Decision engine | LLM |
| API server | Tool executor |
| Custom Resource Definition | Tool definition (JSON schema) |
| Watch/list | Conversation history + tool results |
| Reconciliation action | Tool call |
| Convergence (desired = actual) | Final answer produced |
| Operator pattern | Specialized agent (domain expert + tools) |
| RBAC / permissions | Tool sandboxing |
| Backoff / retry | Max iterations / error handling |

## Multi-Step Reasoning

The power of agents comes from **chaining**. A single question might require multiple tool calls:

```
User: "What's the average response time of our top 3 most-queried endpoints?"

Agent thinking:
  1. I need to find the top 3 endpoints → call search_knowledge_base("most queried API endpoints")
  2. Got endpoint names. Now I need response times → call search_knowledge_base("response time /api/users")
  3. And the other two → call search_knowledge_base("response time /api/orders")
  4. Now I have the data → call calculator("average", [45, 120, 78])
  5. Average is 81ms → compose final answer with citations
```

Each step observes the result of the previous step and decides the next action. The LLM is the orchestrator — like a CI/CD pipeline that conditionally runs stages based on previous stage outputs.

## Sandboxing — Because Tools Have Real Effects

An agent with a `write_file` tool can write files. An agent with a `run_command` tool can run commands. This is powerful and dangerous — exactly like giving a service account broad permissions.

**Sandbox your tools:**
- File tools should only access a designated directory
- Network tools should respect timeouts and allowlists
- Destructive actions should require confirmation
- All tool executions should be logged

This is RBAC for AI. The principle of least privilege applies exactly as you'd expect.

## When Agents Go Wrong

| Failure Mode | Infra Equivalent | Mitigation |
|-------------|-----------------|------------|
| Infinite loop (agent keeps calling tools without converging) | Restart loop, reconciliation storm | Max iterations limit |
| Wrong tool selection | Calling the wrong API endpoint | Better tool descriptions, fewer tools |
| Hallucinated tool arguments | Malformed API request | Input validation in tool executor |
| Context window exhaustion | Buffer overflow from too many results | Summarize intermediate results |
| Cascading tool failures | Dependency failure cascade | Error handling, circuit breaker pattern |

## Practical Implications

1. **Start with few tools.** 3-5 well-defined tools beat 20 vague ones. The LLM selects better when choices are clear.
2. **Tool descriptions are critical.** The LLM reads them to decide what to call. Vague descriptions → wrong tool selection. Write them like API docs.
3. **Set a max iteration limit.** Agents can loop. A hard cap (10-15 iterations) prevents runaway costs and infinite loops.
4. **Log everything.** Every tool call, every argument, every result. This is your audit trail — essential for debugging and trust.
5. **The agent framework is ~200 lines.** Don't reach for LangChain. The loop is simple. Keeping it visible lets you debug it.

## Try It Yourself

In Mission 05, you'll build an agent with 4 tools: search (your knowledge base from Mission 01-02), web fetch, calculator, and file access. You'll see the reasoning trace — every decision the LLM makes and every tool it calls — displayed in the UI.
