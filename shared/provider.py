"""
Kindling — Unified LLM/Embedding Provider Abstraction

Switch providers by setting KINDLING_PROVIDER in your .env file.
All missions import from here. No mission code touches provider APIs directly.

Supported providers:
  - ollama:    Local inference via Ollama (free, GPU optional)
  - openai:    OpenAI API (gpt-4o-mini, text-embedding-3-small, etc.)
  - anthropic: Anthropic API (claude-sonnet, etc.) — embeddings fall back to Ollama
  - groq:      Groq API (fast cloud inference) — embeddings fall back to Ollama
"""

import json
import os
from typing import Iterator

import requests

from .config import get_config

# ---------------------------------------------------------------------------
# Public API — these are what missions import
# ---------------------------------------------------------------------------


def chat(messages: list[dict], **kwargs) -> str:
    """Send a chat completion request. Returns the assistant's response text."""
    config = get_config()
    provider = _PROVIDERS[config.provider]
    return provider.chat(messages, config, **kwargs)


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts. Returns a list of float vectors."""
    config = get_config()
    # Anthropic and Groq don't offer embeddings — fall back to Ollama
    if config.provider in ("anthropic", "groq"):
        return _OllamaProvider.embed(texts, config)
    provider = _PROVIDERS[config.provider]
    return provider.embed(texts, config)


def stream(messages: list[dict], **kwargs) -> Iterator[str]:
    """Stream a chat completion. Yields text chunks as they arrive."""
    config = get_config()
    provider = _PROVIDERS[config.provider]
    return provider.stream(messages, config, **kwargs)


# ---------------------------------------------------------------------------
# Provider Implementations
# ---------------------------------------------------------------------------


class _OllamaProvider:
    """Local inference via Ollama REST API."""

    @staticmethod
    def chat(messages, config, **kwargs):
        resp = requests.post(
            f"{config.ollama_base_url}/api/chat",
            json={
                "model": config.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", config.temperature),
                    "num_predict": kwargs.get("max_tokens", config.max_tokens),
                },
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    @staticmethod
    def embed(texts, config):
        # Ollama /api/embed supports batch input — send all texts at once
        resp = requests.post(
            f"{config.ollama_base_url}/api/embed",
            json={"model": config.embed_model, "input": texts},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["embeddings"]

    @staticmethod
    def stream(messages, config, **kwargs):
        resp = requests.post(
            f"{config.ollama_base_url}/api/chat",
            json={
                "model": config.model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", config.temperature),
                    "num_predict": kwargs.get("max_tokens", config.max_tokens),
                },
            },
            stream=True,
            timeout=120,
        )
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                chunk = json.loads(line)
                if content := chunk.get("message", {}).get("content", ""):
                    yield content


class _OpenAIProvider:
    """OpenAI-compatible API (works with OpenAI, Azure OpenAI, etc.)."""

    @staticmethod
    def _headers(config):
        return {
            "Authorization": f"Bearer {config.openai_api_key}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def chat(messages, config, **kwargs):
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=_OpenAIProvider._headers(config),
            json={
                "model": config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", config.temperature),
                "max_tokens": kwargs.get("max_tokens", config.max_tokens),
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    @staticmethod
    def embed(texts, config):
        resp = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers=_OpenAIProvider._headers(config),
            json={"model": config.embed_model, "input": texts},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data["data"]]

    @staticmethod
    def stream(messages, config, **kwargs):
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=_OpenAIProvider._headers(config),
            json={
                "model": config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", config.temperature),
                "max_tokens": kwargs.get("max_tokens", config.max_tokens),
                "stream": True,
            },
            stream=True,
            timeout=60,
        )
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                text = line.decode("utf-8")
                if text.startswith("data: ") and text != "data: [DONE]":
                    chunk = json.loads(text[6:])
                    if delta := chunk["choices"][0].get("delta", {}).get("content"):
                        yield delta


class _AnthropicProvider:
    """Anthropic Messages API."""

    @staticmethod
    def _headers(config):
        return {
            "x-api-key": config.anthropic_api_key,
            "anthropic-version": "2025-01-01",
            "Content-Type": "application/json",
        }

    @staticmethod
    def chat(messages, config, **kwargs):
        # Anthropic separates system prompt from messages
        system = None
        filtered = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                filtered.append(msg)

        body = {
            "model": config.model,
            "messages": filtered,
            "temperature": kwargs.get("temperature", config.temperature),
            "max_tokens": kwargs.get("max_tokens", config.max_tokens),
        }
        if system:
            body["system"] = system

        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=_AnthropicProvider._headers(config),
            json=body,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]

    @staticmethod
    def stream(messages, config, **kwargs):
        system = None
        filtered = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                filtered.append(msg)

        body = {
            "model": config.model,
            "messages": filtered,
            "temperature": kwargs.get("temperature", config.temperature),
            "max_tokens": kwargs.get("max_tokens", config.max_tokens),
            "stream": True,
        }
        if system:
            body["system"] = system

        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=_AnthropicProvider._headers(config),
            json=body,
            stream=True,
            timeout=60,
        )
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                text = line.decode("utf-8")
                if text.startswith("data: "):
                    chunk = json.loads(text[6:])
                    if chunk.get("type") == "content_block_delta":
                        if delta := chunk.get("delta", {}).get("text"):
                            yield delta


class _GroqProvider:
    """Groq API — OpenAI-compatible with different base URL."""

    @staticmethod
    def _headers(config):
        return {
            "Authorization": f"Bearer {config.groq_api_key}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def chat(messages, config, **kwargs):
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=_GroqProvider._headers(config),
            json={
                "model": config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", config.temperature),
                "max_tokens": kwargs.get("max_tokens", config.max_tokens),
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    @staticmethod
    def stream(messages, config, **kwargs):
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=_GroqProvider._headers(config),
            json={
                "model": config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", config.temperature),
                "max_tokens": kwargs.get("max_tokens", config.max_tokens),
                "stream": True,
            },
            stream=True,
            timeout=60,
        )
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                text = line.decode("utf-8")
                if text.startswith("data: ") and text != "data: [DONE]":
                    chunk = json.loads(text[6:])
                    if delta := chunk["choices"][0].get("delta", {}).get("content"):
                        yield delta


# Provider registry
_PROVIDERS = {
    "ollama": _OllamaProvider,
    "openai": _OpenAIProvider,
    "anthropic": _AnthropicProvider,
    "groq": _GroqProvider,
}
