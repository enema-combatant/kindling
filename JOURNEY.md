# The Journey

*How an infrastructure architect went from zero AI experience to deploying field-ready AI assistants in 84 days, partnering with an AI coding assistant.*

---

## Day 1 — "Help Me Delete Duplicate Files"

January 1, 2026. New Year's Day. I sat down at my z590 workstation — 64 GB RAM, an RTX 2080 Super I'd bought for gaming years ago, Fedora 42, three monitors — and opened a terminal.

I'd just installed Claude Code, Anthropic's AI coding assistant. I'd heard the hype about AI for months, watched colleagues use ChatGPT for email drafts, seen the demos of code generation. But I hadn't built anything with AI. I didn't know what an embedding was. I couldn't tell you the difference between a model and a checkpoint. My professional identity for decades had been infrastructure — networks, servers, firewalls, storage, PKI, the tangible systems that keep organizations running.

My first request to Claude Code was not grand:

> "I would like to remove duplicate files in my home directory. Can you help?"

It built me a deduplication tool with a CSV processor, a grouping algorithm, an interactive checkbox UI, and safety confirmations. It worked. My home directory went from 71% to 41% utilization. I said "Thanks" and closed the terminal.

That was the first 10 minutes. What followed was the most compressed learning experience of my career.

---

## The Infrastructure Instinct

When most people start learning AI, they open a Jupyter notebook and follow a tutorial about training a sentiment classifier on movie reviews. They learn about tensors, loss functions, backpropagation, and gradient descent. It's bottom-up: theory first, application later.

I did the opposite. I deployed first.

Within the first week, I had Ollama running local models, was doing security reconnaissance on a consumer drone's WiFi network, and had started building skills — structured knowledge files that codified what I was learning so I could reference it later. By the end of week two, I had 25 skills covering DNS, VPNs, PXE boot, container management, and firewall automation.

I wasn't learning AI. I was learning how to make AI useful for infrastructure work. The distinction matters.

**The infrastructure instinct is to deploy first, understand second.** You don't read the PostgreSQL source code before you `CREATE TABLE`. You don't study the Linux scheduler before you `systemctl start`. You stand up the service, poke at it, see what it does, learn its failure modes, and gradually build a mental model from operational experience.

This instinct turned out to be exactly right for AI.

---

## The Moment It Clicked

Three weeks in, I was building a knowledge preservation system — a project called ARC (Assisted Reconstitution of Civilization). The ambition was massive: a multi-terabyte corpus of human knowledge, indexed and searchable, deployable to hardware ranging from a Raspberry Pi to a server rack, designed to work offline in worst-case scenarios.

To make it searchable, I needed to understand embeddings. I read the docs. I read blog posts. I read papers. Nothing stuck until I reframed it:

**An embedding is a content-addressable hash that preserves semantic similarity.**

That's it. I already knew content-addressable storage. I already knew hashing. The difference is that SHA-256 is designed so similar inputs produce different hashes, while an embedding model is trained so similar inputs produce similar hashes. Once I had that frame, everything fell into place:

- A vector database is just an index, like a B-tree, but for these semantic hashes
- RAG is just a query service that does a lookup before generating a response
- A context window is just a buffer with a size limit
- Token throughput is just bandwidth
- A system prompt is just a config file

I wasn't learning a foreign discipline. I was translating my existing expertise into a new domain. The concepts mapped almost one-to-one.

This is the insight Kindling is built on. If you have infrastructure experience, you already have the mental models for AI. You just need the translation.

---

## The First Hundred Hours

The next four weeks were a sprint. With Claude Code as a full-time partner, I built:

- **56 skills** covering networking, hardware, security, containers, media archival, VoIP, and AI/ML
- **An enterprise-grade lab** with Active Directory, PKI (two-tier CA), SSO across 50 applications, SIEM, and automated monitoring
- **A credential vault** migrated from GPG-encrypted files to Vaultwarden with OIDC
- **A knowledge corpus** growing toward 190 GB across 25 domains

The pace was only possible because of the partnership model. Claude Code didn't just answer questions — it executed. I'd describe what I wanted, it would build it, I'd test it, we'd iterate. In one session, we might stand up a container stack, debug a VLAN issue, write a deployment script, and update documentation.

I was still making mistakes. On February 11, I put `StartLimitBurst` in the wrong systemd section and locked out an entire 75-container node. The next day, I wrapped Podman in `flock` and caused a lock stampede that required a hard reboot. Each failure taught me something that no tutorial would have covered, because these were operational failures — the kind you only discover by running real systems.

By the end of February, I had:
- 591 Claude Code sessions
- 10,748 individual interactions
- 98 active projects
- More infrastructure automation than most teams ship in a year

---

## Training My Own Model

The first major AI/ML milestone came with HALops — Heuristic AI for Lab Operations. I wanted a model that understood *my* lab, *my* conventions, *my* systems. Not a general assistant, but a specialist that could help manage my specific environment.

I built an end-to-end fine-tuning pipeline:

1. **Data collection:** Extracted 7,676 training examples from my own Claude Code sessions — six weeks of real lab operations work
2. **Training:** QLoRA (4-bit quantized low-rank adaptation) on Qwen2.5-7B, run on a rented A100 GPU via Vast.ai for about $0.70/hour
3. **Quantization:** Converted the 15 GB model to a 4.4 GB GGUF file that fits in my RTX 2080's 8 GB VRAM
4. **Deployment:** Local inference via Ollama at 30+ tokens per second

The model wasn't perfect — 78% task accuracy after adding RAG — but it was *mine*. It knew about my VLANs, my container naming conventions, my monitoring setup. The experience of training it taught me more about how language models work than any course could have.

**What I learned:** Fine-tuning is powerful but expensive and fiddly. For most use cases, good RAG with good prompts gets you 80% of the way there at 1% of the effort. Fine-tuning is for the last 20% — when you need the model to *think* differently, not just *know* differently.

---

## Scaling: 8.7 Million Vectors and the Lessons They Taught

The ARC knowledge corpus grew. 190 GB of documents across 25 domains: medical, legal, security, infrastructure, agriculture, energy. Over 8.7 million vectors indexed in Qdrant across six collections.

At this scale, things break in ways that don't show up in tutorials:

**The Dimension Chaos (March 2026).** I was building golden caches — pre-computed answer databases — for deployment on different hardware. I used 768-dimensional embeddings on my desktop, 384-dimensional on the phone, and accidentally mixed them. Silent failures everywhere. Semantic search returned garbage results, but no errors. The fix was strict dimensional discipline: every device gets one embedding model, one dimension, enforced at build time. This is analogous to mixing IPv4 and IPv6 without a transition mechanism — the packets arrive, they just don't mean anything.

**The SIMD Surprise (March 2026).** My lab servers run Xeon X5675 processors — Westmere architecture from 2010. When I migrated Qdrant to one of these servers, it crashed with SIGILL (illegal instruction). The vector quantization code assumed AVX2 (Haswell, 2013). I had to split the C compilation: SSE-only path for old instructions, AVX2 for modern CPUs, with runtime detection. This is a lesson no cloud tutorial teaches — when you run on real hardware, CPU microarchitecture matters.

**The Swap Catastrophe (March 2026).** Fedora enables 8 GB of zram swap by default. Qdrant's memory-mapped HNSW indexes combined with zram's compression overhead created a page fault storm. Five-minute loads became multi-hour hangs followed by OOM kills. The fix: disable all swap, set swappiness to 0. Swap is Qdrant's enemy. This is the kind of operational knowledge that only comes from running systems at scale on real infrastructure.

---

## Taking It to the Field

By mid-March, the lab was solid. But I had a harder question: could all of this work offline, on constrained hardware, in the field?

I built NOCLAW AI ASSIST — a voice-enabled AI assistant designed for two field platforms:
- A Panasonic Toughbook CF-31 from 2011 (32 GB DDR3L, Core i5, no GPU)
- A Google Pixel 7 Pro running GrapheneOS (12 GB LPDDR5, Tensor G2)

The constraints forced elegant design. I developed a 5-tier answer architecture:

| Tier | Method | Speed | Accuracy | Hallucination Risk |
|------|--------|-------|----------|-------------------|
| 0 | Structured database lookup | Instant | 100% | Zero |
| 1 | Pre-computed golden cache | Instant | 98% | Zero |
| 2 | Decision tree traversal | Fast | 95% | Zero |
| 3 | RAG-templated response | Seconds | 90% | Low |
| 4 | Full LLM generation | 10-60s | 60-70% | Higher |

Tiers 0-2 are deterministic — no LLM, no hallucination, no latency. They handle the common questions. Tier 3 adds light LLM synthesis over retrieved context. Tier 4 is the full generative pipeline for novel questions. The system tries each tier in order and only escalates when it can't answer confidently.

This architecture works because most questions in a domain have known answers. You don't need a 70-billion-parameter model to tell someone the safe water temperature for handwashing. You need a model for the edge cases — and by the time you get there, you've already exhausted the fast, reliable tiers.

The Toughbook runs SmolLM3-3B at 10-15 tokens per second, sustained, with no thermal throttling. The Pixel runs the same model at variable speeds (the big cores thermal-throttle under load, but the efficient cores are steady). Both connect via Reticulum mesh networking for low-bandwidth query relay when connectivity exists.

---

## The Partnership Model

This section is about the meta-skill — the one that made everything else possible.

Working with an AI coding assistant is not like using a search engine. It's not like pair programming with a human, either. It's a new kind of collaboration that requires learning its own set of skills:

**Be specific about what you want, vague about how to get there.** I learned to describe the desired outcome and constraints, then let Claude Code choose the implementation. "I need a container that serves embeddings via REST, handles 100 concurrent requests, and restarts on failure" is better than "write me a Dockerfile." The AI has a broader view of available tools and patterns than I do in any specific domain.

**Treat your context like a system.** Claude Code has a context window — a buffer. I learned to manage it like I manage any finite resource: keep important facts pinned (in CLAUDE.md files), organize knowledge into memory files, avoid dumping large files when a targeted excerpt would suffice. I built 45 topic files, 56 skills, and a structured memory system that persists across sessions.

**Fail fast and debug together.** Some of my best sessions started with something breaking. The Node2 lockout. The SIMD crash. The dimension chaos. Each failure became a teaching moment — for both of us. The AI remembered the lessons (via memory files), I remembered the operational context, and together we built guardrails that prevented recurrence.

**Document as you go.** By the end of 84 days, I had 91 CLAUDE.md files across my projects, each one a living operational manual. This wasn't extra work — it was integral to the workflow. The documentation made future sessions faster because the AI could read the project context and understand where things stood without re-exploring.

**Know when to lead and when to follow.** For infrastructure decisions — network design, security architecture, hardware selection — I led, and the AI implemented. For AI/ML decisions — embedding model selection, chunking strategy, agent loop design — the AI led, and I evaluated. The best results came from playing to our respective strengths.

---

## What I'd Tell Myself on Day 1

If I could go back to January 1, 2026 and give myself advice:

1. **Deploy first, understand second.** Your infrastructure instinct is right. Stand up the model, talk to it, see what it does. The theory will make sense once you've seen the system operate.

2. **AI concepts map to what you already know.** Embeddings are hashes. Vector databases are indexes. RAG is a query pipeline. Agents are control loops. Don't let unfamiliar terminology convince you this is a foreign discipline. It's not.

3. **Start with RAG, not fine-tuning.** RAG gets you 80% of the value at 1% of the effort. Fine-tuning is powerful but expensive, slow, and requires a lot of data. Most problems are solved by better retrieval and better prompts.

4. **The system prompt is your primary tuning lever.** Before you reach for anything complex, try a better prompt. Version control it. Test it. Iterate on it. It's the cheapest and fastest optimization available.

5. **Operational failures are your best teacher.** The lockouts, the crashes, the silent failures — these are where the real learning happens. Embrace them. Document them. Build guardrails for next time.

6. **The AI is a force multiplier, not a replacement.** I brought decades of infrastructure knowledge. Claude Code brought breadth across AI/ML, software patterns, and rapid implementation. Neither of us could have built what we built alone. The combination was the breakthrough.

7. **Just start.** Don't wait until you understand transformers, attention mechanisms, or loss functions. Don't take a course first. Don't read a textbook first. Open a terminal, deploy a model, and ask it a question. Everything else follows.

---

## The Numbers

| Metric | Value |
|--------|-------|
| Days elapsed | 84 |
| Sessions | 591 |
| Interactions | 10,748 |
| Projects built | 98 |
| Skills created | 96 (56 active, 40 consolidated) |
| Vectors indexed | 8,700,000+ |
| Corpus size | 190 GB |
| Containers deployed | 155+ |
| Models fine-tuned | 2 (HALops v1, v2) |
| Field devices deployed | 2 (Toughbook CF-31, Pixel 7 Pro) |
| Critical incidents survived | 7 (lockouts, NVMe failure, UPS failure, SIMD crash) |
| Man-years saved (estimated) | Several |

---

## What Kindling Is For

This repository is the distillation of that 84-day journey into something you can walk through in an afternoon. Each mission corresponds to a real phase of the learning arc:

| Mission | Phase It Captures |
|---------|------------------|
| 00 — Ignition | Day 1: deploy a model, send a prompt |
| 01 — Memory | Week 2: embeddings and vector search |
| 02 — Retrieval | Week 3: RAG pipeline |
| 03 — Voice | Week 5: voice interface (NOCLAW) |
| 04 — Specialization | Week 4: domain expertise (HALops, Archivist) |
| 05 — Agents | Week 7: tool-calling agents (ARC agent) |

The concepts documents capture the mental model translations that made everything click. The provider guides capture the pragmatic reality of choosing between local and cloud inference. The extensions point toward where the journey goes next: fine-tuning, multi-node, field deployment, mesh networking.

You don't have to follow my path exactly. You don't need a homelab with enterprise servers. You need a computer, Docker, and the willingness to start.

The rest, as I discovered, follows naturally.

---

*Built in partnership with [Claude Code](https://claude.ai/code) by Anthropic. The journey continues.*
