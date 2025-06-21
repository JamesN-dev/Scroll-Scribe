"""Retry utilities for ScrollScribe.

Includes:
- Flexible retry factory: `retry_scrollscribe_operation`
- Convenience decorators: `@retry_llm`, `@retry_network`
- External-to-internal exception mapping: `map_external_exception`

Handles:
- ScrollScribeError types (RateLimitError, NetworkError, etc.)
- LiteLLM retryable exceptions (RateLimitError, APIConnectionError, etc.)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from litellm.exceptions import (
    APIConnectionError as LiteAPIConnectionError,
)
from litellm.exceptions import (
    ContextWindowExceededError as LiteContextError,
)
from litellm.exceptions import (
    RateLimitError as LiteRateLimitError,
)
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    stop_after_attempt,
)

# --- ScrollScribe exceptions ---
from app.utils.exceptions import (
    LLMError,
    NetworkError,
    RateLimitError,
    ScrollScribeError,
    get_retry_delay,
)

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Retry predicate
# ------------------------------------------------------------------------------


def is_scrollscribe_retryable(exception: BaseException) -> bool:
    if isinstance(exception, RateLimitError):
        return True
    if isinstance(exception, NetworkError) and exception.can_retry():
        return True
    if (
        isinstance(exception, LLMError)
        and not getattr(exception, "is_context_length_error", lambda: False)()
    ):
        return True
    if isinstance(exception, (LiteRateLimitError | LiteAPIConnectionError)):
        return True
    return False


# ------------------------------------------------------------------------------
# Wait strategy
# ------------------------------------------------------------------------------


def scrollscribe_wait_strategy(retry_state: RetryCallState) -> float:
    if retry_state.outcome and retry_state.outcome.exception():
        exc = retry_state.outcome.exception()
        if isinstance(exc, ScrollScribeError):
            return get_retry_delay(exc)
        elif isinstance(exc, LiteRateLimitError):
            return float(getattr(exc, "retry_after", 60))
        elif isinstance(exc, LiteAPIConnectionError):
            return float(2**retry_state.attempt_number)
    return 1.0


# ------------------------------------------------------------------------------
# Main Retry Decorator Factory
# ------------------------------------------------------------------------------


def retry_scrollscribe_operation(
    max_attempts: int = 3,
    initial_delay_sec: float = 1.0,
    max_delay_sec: float = 60.0,
    retry_on_exceptions: list[type[Exception]] | None = None,
    exception_mapping: dict[type[Exception], type[ScrollScribeError]] | None = None,
) -> Callable:
    """
    Returns a Tenacity-based retry decorator with ScrollScribe semantics.
    """

    if retry_on_exceptions is None:
        retry_on_exceptions = []

    def retry_condition(exception: BaseException) -> bool:
        if is_scrollscribe_retryable(exception):
            return True
        if exception_mapping:
            for ext_exc, mapped_exc in exception_mapping.items():
                if isinstance(exception, ext_exc):
                    try:
                        return is_scrollscribe_retryable(mapped_exc("test"))
                    except Exception:
                        return False
        if retry_on_exceptions:
            return isinstance(exception, tuple(retry_on_exceptions))
        return False

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=scrollscribe_wait_strategy,
        retry=retry_if_exception(retry_condition),
        reraise=True,
    )


# ------------------------------------------------------------------------------
# Sugar decorators for common use cases
# ------------------------------------------------------------------------------

retry_llm = retry_scrollscribe_operation(
    max_attempts=5,
    retry_on_exceptions=[
        RateLimitError,
        LLMError,
        LiteRateLimitError,
    ],
)

retry_network = retry_scrollscribe_operation(
    max_attempts=4,
    retry_on_exceptions=[
        NetworkError,
        LiteAPIConnectionError,
    ],
)


# ------------------------------------------------------------------------------
# External exception mapping helper
# ------------------------------------------------------------------------------


def map_external_exception(
    external_exc: Exception,
    scrollscribe_exception_type: type[ScrollScribeError],
    **kwargs: Any,
) -> ScrollScribeError:
    if not issubclass(scrollscribe_exception_type, ScrollScribeError):
        raise TypeError(  # type: ignore[unreachable]
            f"{scrollscribe_exception_type.__name__} must subclass ScrollScribeError"
        )

    mapped = kwargs.copy()

    if isinstance(external_exc, LiteRateLimitError):
        mapped.setdefault("retry_after", getattr(external_exc, "retry_after", None))
        mapped.setdefault("api_provider", getattr(external_exc, "llm_provider", None))

    elif isinstance(external_exc, LiteContextError):
        mapped.setdefault("model_name", getattr(external_exc, "model_name", None))
        mapped.setdefault("api_provider", getattr(external_exc, "llm_provider", None))

    elif isinstance(external_exc, LiteAPIConnectionError):
        mapped.setdefault("url", getattr(external_exc, "url", None))

    elif isinstance(external_exc, FileNotFoundError):
        mapped.setdefault("filepath", kwargs.get("filepath", ""))
        mapped.setdefault("operation", kwargs.get("operation", "read"))

    msg = f"{external_exc.__class__.__name__}: {str(external_exc)}"
    return scrollscribe_exception_type(msg, cause=external_exc, **mapped)
