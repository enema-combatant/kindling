# Mission 04 — Extend

## Create Your Own Domain Expert

Copy the template and fill it in:

```bash
cp -r domains/template domains/cooking
# Edit domains/cooking/prompts.yaml
# Add .txt or .md files to domains/cooking/corpus/
# Add test questions to domains/cooking/eval_questions.yaml
```

Change the `DOMAIN_PATH` in `docker-compose.yml` and restart:

```yaml
environment:
  - DOMAIN_PATH=/app/domains/cooking
```

No code changes needed. The same app serves any domain.

## Multi-Domain Routing

Currently, the app serves one domain at a time. To support multiple domains simultaneously:

1. Load all domain configs at startup by scanning the `domains/` directory
2. Add a domain selector to the UI (dropdown or tabs)
3. Route queries to the correct collection based on the selected domain

A more advanced approach: **automatic domain detection**. Embed a short description of each domain, compare the user's query to each description, and route to the closest match. This is essentially a classifier built from embeddings.

```python
# Pseudocode for automatic routing
domain_descriptions = {
    "networking": embed(["Network troubleshooting, switches, routing, DNS"]),
    "cooking": embed(["Recipes, ingredients, cooking techniques"]),
}

query_vec = embed([user_query])
best_domain = max(domain_descriptions, key=lambda d: cosine_similarity(query_vec, domain_descriptions[d]))
```

## Custom Test Metrics

The built-in tester checks for keyword presence — simple but effective. You could extend it with:

**Semantic similarity scoring**: Instead of checking for exact keywords, embed both the expected answer and the actual answer, then compute cosine similarity. This catches paraphrasing.

**Source precision/recall**: Track not just whether the right source was retrieved, but whether irrelevant sources were excluded. A good retrieval system returns the right documents AND excludes the wrong ones.

**Response format validation**: Check that the answer follows the format specified in the system prompt (e.g., bullet points, specific structure, citation format).

## Adding New Domains

Good domain candidates have:

- **Structured reference material** — manuals, guides, procedures, FAQs
- **Testable answers** — questions with objectively correct answers
- **Bounded scope** — a domain that can be covered by 5-50 documents

Examples:
- **IT runbooks** — incident response procedures with specific steps
- **Product documentation** — user guides for internal tools
- **Compliance reference** — regulatory requirements with specific citations
- **Onboarding guides** — new hire FAQ with definitive answers

## Prompt Engineering Techniques

Try these variations in your `prompts.yaml`:

**Strict citation mode** — forces every claim to have a source:
```yaml
system_prompt: |
  Every factual claim must include [Source: filename] citation.
  If you cannot cite a source for a statement, do not make the statement.
```

**Step-by-step reasoning** — forces structured diagnostic flow:
```yaml
system_prompt: |
  For every question, respond with:
  1. LIKELY CAUSE: Most probable root cause based on context
  2. DIAGNOSTIC STEPS: Numbered commands to verify
  3. RESOLUTION: Fix for the confirmed cause
  4. SOURCES: Documents referenced
```

**Audience-aware** — adjusts language based on context:
```yaml
system_prompt: |
  Assess the technical level of the question.
  For basic questions, explain concepts simply.
  For advanced questions, be precise and assume expertise.
  Always include the relevant commands either way.
```
