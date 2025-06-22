"""Configuration factories for crawl4ai components.

Provides standardized BrowserConfig and CrawlerRunConfig setup with:
- Browser singleton issue fixes
- Performance optimizations
- Clean logging integration
"""

from crawl4ai import BrowserConfig, CacheMode, CrawlerRunConfig


def get_browser_config(headless: bool = True, verbose: bool = False) -> BrowserConfig:
    """Get browser configuration (prefer builtin mode for best performance).

    Args:
        headless: Run browser in headless mode
        verbose: Enable verbose browser logging (not recommended)

    Returns:
        Configured BrowserConfig instance
    """
    return BrowserConfig(
        # browser_mode="builtin",  # Temporarily disable - may force use_managed_browser=True
        headless=headless,
        verbose=verbose,
        use_managed_browser=False,  # Temporary fix for crawl4ai context.pages bug
    )


def silence_noisy_libraries():
    """Silence the most obnoxious library logging using correct APIs."""
    import logging
    import os

    # LiteLLM - only method that actually works
    os.environ["LITELLM_LOG"] = "ERROR"  # Still shows errors, suppresses cost spam

    # Standard logging for actually noisy libraries
    noisy_loggers = [
        "litellm",
        "litellm.cost_calculator",
        "litellm.utils",
        "httpx",
        "urllib3",
    ]

    for logger_name in noisy_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.ERROR)  # Only show errors
        if "litellm" in logger_name:
            logger.disabled = True  # Nuclear option for litellm


def get_processing_config(session_id: str, args) -> CrawlerRunConfig:
    """Get optimized configuration for URL processing.

    Args:
        session_id: Session ID for browser reuse
        args: Command line arguments (from argparse)

    Returns:
        Configured CrawlerRunConfig instance with performance optimizations
    """
    return CrawlerRunConfig(
        session_id=session_id,  # Enable session reuse
        cache_mode=CacheMode.DISABLED,  # Fresh content for processing
        wait_until=args.wait,
        page_timeout=args.timeout,
        markdown_generator=None,  # type: ignore[arg-type]
        extraction_strategy=None,  # type: ignore[arg-type]
        verbose=False,  # Always disable to reduce noise
        stream=False,
        # Performance optimizations
        exclude_external_links=True,
        excluded_tags=["script", "style", "nav", "footer", "aside"],
        word_count_threshold=10,  # Lower threshold for faster processing
    )
