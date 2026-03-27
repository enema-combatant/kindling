"""
Agent tool: web_fetch — retrieve content from a URL.

Safety constraints:
- Only http/https URLs allowed
- 10-second timeout
- Response truncated to 2000 characters
- No authentication headers sent
"""

from urllib.parse import urlparse

import requests


def web_fetch(url: str) -> str:
    """
    Fetch the text content of a web page.

    Returns the first 2000 characters of the response body.
    """
    # Validate URL scheme
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return f"Refused: only http/https URLs are allowed, got '{parsed.scheme}'"

    if not parsed.netloc:
        return "Invalid URL: no hostname found"

    try:
        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Kindling-Agent/0.1"},
            allow_redirects=True,
        )
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        return f"Timeout: {url} did not respond within 10 seconds"
    except requests.exceptions.ConnectionError:
        return f"Connection error: could not reach {url}"
    except requests.exceptions.HTTPError as e:
        return f"HTTP error {e.response.status_code}: {url}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"

    # Return text content, truncated
    content = resp.text[:2000]
    if len(resp.text) > 2000:
        content += f"\n\n[Truncated — full response was {len(resp.text)} characters]"

    return content
