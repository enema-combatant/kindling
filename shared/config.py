"""
Kindling — Environment-based Configuration

Reads settings from environment variables (loaded from .env by Docker Compose).
"""

import os
from dataclasses import dataclass, field


@dataclass
class KindlingConfig:
    provider: str = "ollama"
    model: str = "llama3.2:3b"
    embed_model: str = "nomic-embed-text"
    temperature: float = 0.7
    max_tokens: int = 2048

    # Provider-specific
    ollama_base_url: str = "http://ollama:11434"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    groq_api_key: str = ""

    # Storage
    chroma_path: str = "/data/chromadb"


def get_config() -> KindlingConfig:
    """Build config from environment variables."""
    return KindlingConfig(
        provider=os.getenv("KINDLING_PROVIDER", "ollama"),
        model=os.getenv("KINDLING_MODEL", "llama3.2:3b"),
        embed_model=os.getenv("KINDLING_EMBED_MODEL", "nomic-embed-text"),
        temperature=float(os.getenv("KINDLING_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("KINDLING_MAX_TOKENS", "2048")),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        chroma_path=os.getenv("CHROMA_PATH", "/data/chromadb"),
    )
