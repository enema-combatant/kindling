# Prompts as Configs

*System prompts are service configuration files.*

## The Infrastructure Mental Model

Every service you deploy has a configuration file. Nginx has `nginx.conf`. PostgreSQL has `postgresql.conf`. Kubernetes has manifests. The config defines behavior: what the service does, how it responds, what limits it respects. Change the config, change the behavior — without changing the code.

**System prompts are configuration files for LLMs.** They define the model's persona, behavior constraints, output format, and domain focus. The same model with different system prompts behaves like different services — a support agent, a code reviewer, a medical triage assistant — just as the same Nginx binary serves different sites with different configs.

## The Anatomy of a System Prompt

```yaml
# Think of this as service.conf for your LLM

# Identity — who is this service?
role: "You are a network troubleshooting assistant for enterprise environments."

# Constraints — what are the operational boundaries?
rules:
  - "Only answer questions about networking."
  - "If you don't know, say so. Never guess at IP addresses or configs."
  - "Always ask for the device type and OS before troubleshooting."

# Behavior — how should it respond?
format: "Use bullet points for steps. Include the command to run."
tone: "Professional but concise. Skip pleasantries."

# Context — what does it know about the environment?
environment:
  - "We run Cisco Catalyst switches and Juniper SRX firewalls."
  - "VLANs: 10=mgmt, 20=servers, 30=users, 100=IoT"
  - "DNS: 10.1.1.53 and 10.1.1.54"
```

In practice, this becomes a text block:

```
You are a network troubleshooting assistant for enterprise environments.

Rules:
- Only answer questions about networking.
- If you don't know, say so. Never guess at IP addresses or configurations.
- Always ask for the device type and OS before troubleshooting.

Response format: Use bullet points for steps. Include the command to run.
Tone: Professional but concise. Skip pleasantries.

Environment context:
- Cisco Catalyst switches and Juniper SRX firewalls
- VLANs: 10=mgmt, 20=servers, 30=users, 100=IoT
- DNS: 10.1.1.53 and 10.1.1.54
```

## The Analogy in Detail

| Config File Concept | System Prompt Equivalent |
|-------------------|------------------------|
| Server block / virtual host | Role definition ("You are a...") |
| Access control rules | Behavioral constraints ("Never...", "Always...") |
| Response headers | Output format instructions |
| Upstream / backend config | Domain context and environment info |
| Include directives | Multi-section prompt organization |
| Config reload (no restart) | Changing the prompt between requests |
| Config inheritance | Base prompt + per-request additions |

## Few-Shot Examples — Config Templates

Sometimes you want the model to follow a specific pattern. **Few-shot examples** are like config templates — you show the model input/output pairs, and it mimics the pattern:

```
Given a log line, extract the severity and message.

Example:
Input: "2024-03-15 14:22:01 ERROR Connection refused to 10.1.1.50:5432"
Output: {"severity": "ERROR", "message": "Connection refused to 10.1.1.50:5432"}

Example:
Input: "2024-03-15 14:22:05 WARN Disk usage at 89% on /data"
Output: {"severity": "WARN", "message": "Disk usage at 89% on /data"}

Now process this:
Input: "2024-03-15 14:23:11 CRITICAL OOM killer invoked for process nginx"
```

The model sees the pattern and follows it. This is the LLM equivalent of a Jinja2 template — you define the shape of the output by example.

## Temperature — Your Randomness Dial

| Temperature | Behavior | When to Use |
|------------|----------|-------------|
| 0.0 | Deterministic — same input, same output | Structured extraction, classification |
| 0.3-0.5 | Mostly consistent, slight variation | Technical Q&A, documentation |
| 0.7 | Balanced creativity and accuracy | General conversation (default) |
| 1.0+ | High creativity, less predictable | Brainstorming, creative writing |

This is analogous to jitter in load balancing. At 0.0, the same request always routes to the same backend. At 1.0, routing is randomized. Most production workloads want something in between.

## Practical Implications

1. **System prompts are your primary tuning lever.** Before fine-tuning, before RAG, before anything complex — try a better system prompt. It's the easiest and cheapest optimization, just like tuning a config file is cheaper than rewriting code.
2. **Be specific about what NOT to do.** Models follow positive instructions well but benefit from explicit negative constraints. "Never reveal internal IP addresses" is as important as "provide troubleshooting steps."
3. **Test your prompts like configs.** A bad system prompt causes bad behavior — reliably. Build test cases (known questions with expected answers) and validate after prompt changes. Mission 04 teaches this.
4. **Version control your prompts.** They're configs. They should be in git. Track changes, review diffs, roll back when something breaks.

## Try It Yourself

Every mission uses system prompts. Mission 00 starts with a simple one. By Mission 04, you'll build domain-specific prompt configurations and test them systematically.
