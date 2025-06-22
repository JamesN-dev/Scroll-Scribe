"""Configuration factories for standardized crawl4ai components.

Provides factory functions for BrowserConfig and CrawlerRunConfig with:
- Browser singleton/session management fixes
- Performance-oriented defaults for scraping and processing
- Integrated logging and noise suppression

Note:
    These configuration utilities are shared by both LLM-based and fast processing pipelines.
"""

from crawl4ai import BrowserConfig, CacheMode, CrawlerRunConfig


def get_browser_config(headless: bool = True, verbose: bool = False) -> BrowserConfig:
    """Create and return a standardized BrowserConfig for crawl4ai.

    Args:
        headless (bool): Whether to run the browser in headless mode.
        verbose (bool): Enable verbose browser logging (not recommended for production).

    Returns:
        BrowserConfig: Configured browser settings for crawl4ai.
    """
    return BrowserConfig(
        # browser_mode="builtin",  # Temporarily disable - may force use_managed_browser=True
        headless=headless,
        verbose=verbose,
        use_managed_browser=False,  # Temporary fix for crawl4ai context.pages bug
    )


def silence_noisy_libraries():
    """Suppress excessive logging output from third-party libraries.

    This function configures logging levels and environment variables to minimize
    noise from libraries such as LiteLLM, httpx, and urllib3.
    """
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
    """Create an optimized CrawlerRunConfig for documentation URL processing.

    Args:
        session_id (str): Session ID for browser reuse and session management.
        args: Parsed command line arguments (from argparse) providing wait and timeout settings.

    Returns:
        CrawlerRunConfig: Configured instance with performance and content filtering optimizations.
    """
    return CrawlerRunConfig(
        session_id=session_id,
        cache_mode=CacheMode.DISABLED,
        wait_until=args.wait,
        page_timeout=args.timeout,
        verbose=False,
        stream=False,
        exclude_external_links=True,
        excluded_tags=["script", "style", "nav", "footer", "aside"],
        word_count_threshold=10,
    )
