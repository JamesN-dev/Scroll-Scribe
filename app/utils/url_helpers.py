"""URL processing utilities for Scroll-Scribe.

This module provides common URL manipulation functions used throughout
the application, reducing code duplication and ensuring consistency.
"""

import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from ..constants import (
    DEFAULT_EXTENSION,
    MAX_FILENAME_LENGTH,
    URL_DISPLAY_MAX_LENGTH,
    URL_DISPLAY_MAX_LENGTH_DETAILED,
)


def url_to_filename(
    url: str,
    index: int,
    extension: str = DEFAULT_EXTENSION,
    max_len: int = MAX_FILENAME_LENGTH,
) -> str:
    """Generate a safe, filesystem-friendly filename from a URL and index.

    This function parses the given URL and constructs a filename that is safe for most filesystems,
    using the URL path or netloc, sanitized and truncated as needed. The filename includes a
    zero-padded index for ordering and the specified file extension.

    Args:
        url (str): The source URL to convert into a filename.
        index (int): The index of the URL in the processing batch (used for ordering).
        extension (str, optional): The file extension to use (default: ".md").
        max_len (int, optional): Maximum length for the filename base (default: 100).

    Returns:
        str: A safe filename string suitable for saving the processed content.

    Notes:
        - If the URL cannot be parsed, a fallback filename using only the index is returned.
        - All unsafe filesystem characters are replaced with underscores.
    """
    try:
        parsed = urlparse(url)
        path_part: str = (
            parsed.path.strip("/") if parsed.path.strip("/") else parsed.netloc
        )
        safe_path: str = re.sub(r'[\\/:*?"<>|]+', "_", path_part)
        safe_path = re.sub(r"\s+", "_", safe_path)
        safe_path = safe_path[:max_len].rstrip("._")
        if not safe_path:
            safe_path = f"url_{index}"
        return f"{index:03d}_{safe_path}{extension}"
    except Exception:
        return f"{index:03d}{extension}"


def extract_keywords_from_url(url: str) -> list[str]:
    """Extract meaningful keywords from URL path."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    path = parsed.path
    # Split by common separators and filter meaningful words
    words = re.split(r"[/\-_.]", path.lower())
    keywords = [
        w
        for w in words
        if w
        and len(w) > 2
        and w
        not in [
            "com",
            "org",
            "www",
            "html",
            "htm",
            "php",
            "md",
            "pdf",
            "txt",
            "css",
            "js",
        ]
    ]
    return keywords[:5]


def get_url_depth(url: str) -> int:
    """Calculate URL depth in site hierarchy."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    path = parsed.path
    return len([p for p in path.split("/") if p])


def analyze_url_metadata(url: str, index: int) -> dict[str, Any]:
    """Extract all metadata from a URL."""
    from urllib.parse import urlparse

    return {
        "url": url,
        "path": urlparse(url).path,
        "depth": get_url_depth(url),
        "keywords": extract_keywords_from_url(url),
        "filename_part": get_url_filename_part(url),
        "md_filename": url_to_filename(url, index),
        "discovered_at": datetime.now().isoformat(),
    }


def clean_url_for_display(url: str, max_length: int = URL_DISPLAY_MAX_LENGTH) -> str:
    """
    Clean and truncate URL for display purposes.

    Removes protocol prefixes and truncates long URLs with ellipsis.

    Args:
        url: The URL to clean
        max_length: Maximum length for the cleaned URL

    Returns:
        Cleaned URL suitable for display
    """
    if not url:
        return ""

    # Remove protocol prefixes
    clean_url = url.replace("https://", "").replace("http://", "")

    # Truncate if too long
    if len(clean_url) > max_length:
        clean_url = clean_url[: max_length - 3] + "..."

    return clean_url


def clean_url_for_detailed_display(url: str) -> str:
    """
    Clean URL for detailed display contexts (allows longer URLs).

    Args:
        url: The URL to clean

    Returns:
        Cleaned URL suitable for detailed display
    """
    return clean_url_for_display(url, URL_DISPLAY_MAX_LENGTH_DETAILED)


def extract_domain(url: str) -> str:
    """
    Extract domain from URL for display purposes.

    Args:
        url: The URL to extract domain from

    Returns:
        Domain name or original URL if extraction fails
    """
    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        return parsed.netloc or url
    except Exception:
        return url


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs are from the same domain.

    Args:
        url1: First URL
        url2: Second URL

    Returns:
        True if URLs are from the same domain
    """
    try:
        from urllib.parse import urlparse

        domain1 = urlparse(url1).netloc.lower()
        domain2 = urlparse(url2).netloc.lower()
        return domain1 == domain2
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """
    Normalize URL for consistent processing.

    - Strips whitespace
    - Ensures lowercase scheme
    - Removes trailing slashes from domain-only URLs

    Args:
        url: The URL to normalize

    Returns:
        Normalized URL
    """
    if not url:
        return ""

    url = url.strip()

    try:
        from urllib.parse import urlparse, urlunparse

        parsed = urlparse(url)

        # Normalize scheme to lowercase
        scheme = parsed.scheme.lower() if parsed.scheme else ""

        # Remove trailing slash from domain-only URLs
        path = parsed.path
        if path == "/":
            path = ""

        # Reconstruct URL
        normalized = urlunparse(
            (
                scheme,
                parsed.netloc.lower(),
                path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )

        return normalized
    except Exception:
        return url


def get_url_filename_part(url: str) -> str:
    """
    Extract the filename-relevant part from a URL.

    Used for generating safe filenames from URLs.

    Args:
        url: The URL to extract filename part from

    Returns:
        String suitable for use in filename generation
    """
    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)

        # Use path if available, otherwise use domain
        if parsed.path and parsed.path != "/":
            # Remove leading/trailing slashes and use path
            path_part = parsed.path.strip("/")
            if path_part:
                return path_part

        # Fall back to domain
        return parsed.netloc or "unknown"

    except Exception:
        return "unknown"


def get_md_filename(url: str, index: int) -> str:
    """Generate numbered markdown filename from URL."""
    filename_part = get_url_filename_part(url)
    safe_filename = filename_part.replace("/", "_").replace("-", "_")
    return f"{index:03d}_{safe_filename}.md"


def make_absolute_url(base_url: str, relative_url: str) -> str:
    """
    Convert relative URL to absolute URL using base URL.

    Args:
        base_url: The base URL to resolve against
        relative_url: The relative URL to resolve

    Returns:
        Absolute URL, or relative_url if conversion fails
    """
    try:
        from urllib.parse import urljoin

        return urljoin(base_url, relative_url)
    except Exception:
        return relative_url
