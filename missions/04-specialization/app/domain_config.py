"""
Mission 04 — Specialization: Domain configuration loader.

Reads prompts.yaml from a domain directory and returns a structured config.
This is the "firmware image" — it defines what the expert knows and how it behaves.
"""

import os
from dataclasses import dataclass

import yaml


@dataclass
class DomainConfig:
    """Configuration for a domain expert."""
    name: str
    system_prompt: str
    greeting: str
    collection_name: str


def load_domain(domain_path: str) -> DomainConfig:
    """
    Load domain configuration from prompts.yaml.

    Args:
        domain_path: Path to the domain directory (e.g., domains/networking/)

    Returns:
        DomainConfig with the domain's system prompt, greeting, and collection name.

    Raises:
        FileNotFoundError: If prompts.yaml doesn't exist in the domain directory.
        KeyError: If required fields are missing from prompts.yaml.
    """
    prompts_file = os.path.join(domain_path, "prompts.yaml")

    if not os.path.exists(prompts_file):
        raise FileNotFoundError(
            f"No prompts.yaml found in {domain_path}. "
            f"Copy domains/template/ as a starting point."
        )

    with open(prompts_file, "r") as f:
        data = yaml.safe_load(f)

    required_fields = ["name", "system_prompt", "greeting", "collection_name"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise KeyError(
            f"prompts.yaml is missing required fields: {', '.join(missing)}. "
            f"See domains/template/prompts.yaml for the expected format."
        )

    return DomainConfig(
        name=data["name"],
        system_prompt=data["system_prompt"].strip(),
        greeting=data["greeting"].strip(),
        collection_name=data["collection_name"],
    )
