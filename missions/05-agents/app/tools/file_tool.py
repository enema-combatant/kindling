"""
Agent tool: read_file — sandboxed file access.

ONLY reads files from /app/sample-docs/. Any path that tries to escape
the sandbox is rejected. This is the "RBAC for AI" principle — tools
should have the minimum permissions they need.
"""

import os

SANDBOX_DIR = "/app/sample-docs"
MAX_CHARS = 5000


def read_file(path: str) -> str:
    """
    Read a file from the sample-docs directory.

    The path is resolved relative to /app/sample-docs/ and checked
    to prevent directory traversal attacks (../../etc/passwd).
    Returns the file contents, truncated to 5000 characters.
    """
    if not path:
        return "Error: no path provided"

    # Resolve the full path and ensure it stays within the sandbox
    # os.path.realpath resolves symlinks and .. components
    full_path = os.path.realpath(os.path.join(SANDBOX_DIR, path))

    if not full_path.startswith(os.path.realpath(SANDBOX_DIR)):
        return f"Access denied: path escapes the sandbox directory. Only files in {SANDBOX_DIR} are accessible."

    if not os.path.exists(full_path):
        # List available files to help the LLM self-correct
        available = []
        if os.path.isdir(SANDBOX_DIR):
            available = sorted(os.listdir(SANDBOX_DIR))
        if available:
            return f"File not found: {path}. Available files: {', '.join(available)}"
        return f"File not found: {path}"

    if not os.path.isfile(full_path):
        return f"Not a file: {path}"

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read(MAX_CHARS + 1)

        if len(content) > MAX_CHARS:
            content = content[:MAX_CHARS]
            content += f"\n\n[Truncated at {MAX_CHARS} characters]"

        return content
    except UnicodeDecodeError:
        return f"Error: {path} is not a text file"
    except PermissionError:
        return f"Permission denied: cannot read {path}"
