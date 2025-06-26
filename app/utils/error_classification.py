"""Error classification utilities for consistent exception handling."""

from typing import Literal

ErrorType = Literal["url_error", "network_error"]


def classify_error_type(error_msg: str) -> ErrorType:
    """
    Classify error message to determine appropriate exception type.

    This function provides consistent error classification across the application,
    ensuring that similar errors are always handled the same way.

    Args:
        error_msg: The error message to classify

    Returns:
        "url_error" for URL/parsing related issues
        "network_error" for network/connection issues
    """
    error_msg_lower = error_msg.lower()

    # URL-related error indicators
    url_error_terms = [
        "invalid",
        "malformed",
        "url",
        "domain",
        "parse",
        "format",
        "scheme",
        "hostname",
        "path",
        "query",
    ]

    # Network-related error indicators
    network_error_terms = [
        "connection",
        "timeout",
        "network",
        "dns",
        "ssl",
        "certificate",
        "refused",
        "unreachable",
        "socket",
        "http",
        "status",
        "response",
    ]

    # Check URL errors first (more specific)
    if any(term in error_msg_lower for term in url_error_terms):
        return "url_error"
    elif any(term in error_msg_lower for term in network_error_terms):
        return "network_error"
    else:
        # Default to network error for unknown issues
        # This is safer as network errors are more common and expected
        return "network_error"


def should_retry_error(error_msg: str) -> bool:
    """
    Determine if an error should be retried based on its type.

    Args:
        error_msg: The error message to analyze

    Returns:
        True if the error might be transient and worth retrying
    """
    error_type = classify_error_type(error_msg)

    # URL errors are usually permanent (malformed URLs won't fix themselves)
    if error_type == "url_error":
        return False

    # Network errors might be transient
    error_msg_lower = error_msg.lower()

    # Don't retry permanent network errors
    permanent_network_errors = [
        "404",
        "not found",
        "forbidden",
        "unauthorized",
        "certificate",
        "ssl",
        "dns",
        "host not found",
    ]

    if any(term in error_msg_lower for term in permanent_network_errors):
        return False

    # Retry other network errors (timeouts, connection issues, etc.)
    return True
