"""
Mission 04 — Specialization: Domain accuracy testing.

Runs a set of test questions against the domain RAG pipeline and checks
whether expected keywords appear in the answers. This is your acceptance
test suite -- change the prompt, re-run, see if accuracy improves.

Think of it as a network test suite: ping tests verify reachability,
these tests verify your expert answers correctly.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import yaml
import chromadb
from shared.provider import chat, embed
from shared.config import get_config
from domain_config import load_domain


def load_test_questions(domain_path: str) -> list[dict]:
    """Load test questions from the YAML file."""
    questions_file = os.path.join(domain_path, "eval_questions.yaml")

    if not os.path.exists(questions_file):
        return []

    with open(questions_file, "r") as f:
        data = yaml.safe_load(f)

    return data.get("questions", [])


def retrieve_for_test(query: str, collection_name: str, top_k: int = 4) -> list[dict]:
    """Retrieve context chunks from the domain's collection."""
    config = get_config()
    client = chromadb.PersistentClient(path=config.chroma_path)

    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        return []

    query_vector = embed([query])[0]
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i].get("source", "unknown"),
            "similarity": round(1 - results["distances"][0][i], 4),
        })

    return chunks


def run_tests(domain_path: str) -> dict:
    """
    Run all test questions and return results.

    For each question:
    1. Retrieve context from the domain collection
    2. Generate an answer using the domain system prompt
    3. Check if expected keywords appear in the answer
    4. Check if the expected source was retrieved

    Returns a dict with pass/fail counts and per-question details.
    """
    domain = load_domain(domain_path)
    questions = load_test_questions(domain_path)

    if not questions:
        return {
            "domain": domain.name,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "results": [],
            "error": "No test questions found. Add them to eval_questions.yaml.",
        }

    results = []
    passed = 0
    failed = 0

    for q in questions:
        question = q["question"]
        expected_keywords = [kw.lower() for kw in q.get("expected_keywords", [])]
        expected_source = q.get("expected_source", "")

        # Retrieve context
        chunks = retrieve_for_test(question, domain.collection_name)

        # Build augmented prompt with domain system prompt
        context_parts = []
        for chunk in chunks:
            context_parts.append(f"[Source: {chunk['source']}]\n{chunk['text']}")
        context_block = "\n\n---\n\n".join(context_parts)

        messages = [
            {"role": "system", "content": domain.system_prompt},
            {"role": "user", "content": f"Context documents:\n\n{context_block}\n\n---\n\nQuestion: {question}"},
        ]

        # Generate answer
        try:
            answer = chat(messages)
        except Exception as e:
            answer = f"Error: {e}"

        answer_lower = answer.lower()

        # Check keywords
        found_keywords = [kw for kw in expected_keywords if kw in answer_lower]
        missing_keywords = [kw for kw in expected_keywords if kw not in answer_lower]

        # Check source retrieval
        retrieved_sources = [chunk["source"] for chunk in chunks]
        source_found = expected_source in retrieved_sources if expected_source else True

        # Pass if at least half the keywords are found and the source was retrieved
        keyword_pass = len(found_keywords) >= len(expected_keywords) / 2
        test_passed = keyword_pass and source_found

        if test_passed:
            passed += 1
        else:
            failed += 1

        results.append({
            "question": question,
            "passed": test_passed,
            "answer_excerpt": answer[:200],
            "expected_keywords": expected_keywords,
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
            "expected_source": expected_source,
            "source_found": source_found,
            "retrieved_sources": retrieved_sources,
        })

    return {
        "domain": domain.name,
        "total": len(questions),
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / len(questions) * 100, 1) if questions else 0,
        "results": results,
    }
