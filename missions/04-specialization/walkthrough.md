# Mission 04 — Specialization: Walkthrough

## The Big Picture

Specialization is not fine-tuning. Fine-tuning retrains the model's weights — expensive, slow, and requires ML expertise. Specialization via RAG customization achieves domain expertise through three levers you already understand:

1. **Corpus curation** — what the expert knows
2. **System prompt engineering** — how the expert behaves
3. **Automated testing** — whether the expert is correct

This is the same pattern as deploying a specialized service: same base image, different configuration, different data. The model is the hardware. Your domain directory is the firmware.

## Step 1: Corpus Curation

Open `domains/networking/corpus/network-troubleshooting.txt`. This is the expert's knowledge base — everything it can reference when answering questions.

The quality of your expert depends entirely on the quality of this corpus. Garbage in, garbage out — just like a database.

### What makes a good corpus document?

- **Specific and factual.** "Check the link light" beats "there might be connectivity issues."
- **Structured for retrieval.** One topic per paragraph. The chunker splits on size, so keep related information close together.
- **Complete coverage.** If a topic isn't in the corpus, the expert can't answer questions about it. Missing documents create knowledge gaps.

Open `app/corpus_builder.py` and trace the flow:

```python
documents = load_corpus(corpus_dir)     # Read all .txt/.md files
chunks = chunk_text(doc["content"])      # Split into ~500 char pieces
vectors = embed([chunk])                 # Convert to vectors
collection.add(...)                      # Store in domain-specific collection
```

Each domain gets its own ChromaDB collection (named in `prompts.yaml`). This isolation means a networking question only searches networking documents — it won't accidentally pull cooking recipes.

## Step 2: Domain Prompts

Open `domains/networking/prompts.yaml`:

```yaml
name: Network Troubleshooting Expert
system_prompt: |
  You are a senior network engineer specializing in enterprise infrastructure troubleshooting.
  When given a problem, systematically diagnose from layer 1 (physical) upward.
  Always suggest specific diagnostic commands.
  Base your answers ONLY on the provided context documents.
  Cite sources in [brackets].
greeting: "Network troubleshooting expert ready. Describe your issue."
collection_name: kindling_networking
```

This is the "firmware image." The `system_prompt` defines behavior:

- **Role**: "senior network engineer" — sets the expertise level and domain
- **Method**: "systematically diagnose from layer 1 upward" — defines the reasoning approach
- **Constraints**: "ONLY on the provided context" — prevents hallucination
- **Format**: "Cite sources in [brackets]" — ensures traceability

Open `app/domain_config.py` to see how this YAML becomes a Python dataclass. Open `app/app.py` to see how the system prompt replaces the generic one from Mission 02:

```python
domain = load_domain(DOMAIN_PATH)
# ...
messages = [
    {"role": "system", "content": domain.system_prompt},  # Domain-specific!
    {"role": "user", "content": f"Context documents:\n\n{context_block}\n\n---\n\nQuestion: {query}"},
]
```

Same RAG pipeline. Different system prompt. Different expert.

## Step 3: The Testing Loop

Open `domains/networking/eval_questions.yaml`:

```yaml
questions:
  - question: "A host can't reach the gateway. What should I check first?"
    expected_keywords: ["layer 2", "link light", "cable", "physical"]
    expected_source: "network-troubleshooting.txt"
```

Each test question defines:
- The question to ask
- Keywords that should appear in a correct answer
- The corpus document that should be retrieved

Open `app/evaluator.py` to see the testing flow:

1. Retrieve context from the domain's collection
2. Generate an answer using the domain's system prompt
3. Check if expected keywords appear in the answer
4. Check if the expected source was retrieved
5. Pass if >= 50% of keywords found AND the right source was retrieved

Click "Run Tests" in the UI to see results. The test panel shows pass/fail per question, with details about which keywords were found or missing.

## The Development Loop

This is how you iterate on a domain expert:

```
1. Write/update corpus documents
2. Rebuild corpus (restart container or run corpus_builder.py)
3. Run tests
4. If tests fail:
   a. Missing keywords? → Improve corpus content
   b. Wrong source retrieved? → Improve document structure
   c. Keywords present but answer is bad? → Tune system prompt
5. Repeat until pass rate is acceptable
```

This is exactly how you'd iterate on any service configuration: deploy, test, tune, repeat.
