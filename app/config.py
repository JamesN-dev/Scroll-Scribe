"""Configuration factories for crawl4ai components.

Provides standardized BrowserConfig and CrawlerRunConfig setup.
"""

from crawl4ai import BrowserConfig, CacheMode, CrawlerRunConfig


def get_browser_config(headless: bool = True, verbose: bool = False) -> BrowserConfig:
    """Get standardized browser configuration.

    Args:
        headless: Run browser in headless mode
        verbose: Enable verbose browser logging

    Returns:
        Configured BrowserConfig instance
    """
    return BrowserConfig(
        headless=headless,
        verbose=verbose,
        use_managed_browser=True,  # Enable session persistence
        user_data_dir="data/session/browser",  # Persistent browser data
        viewport_width=1920,
        viewport_height=1080,
    )


def get_processing_config(session_id: str, args) -> CrawlerRunConfig:
    """Get configuration for URL processing with session reuse.

    Args:
        session_id: Session ID for browser reuse
        args: Command line arguments (from argparse)

    Returns:
        Configured CrawlerRunConfig instance
    """
    return CrawlerRunConfig(
        session_id=session_id,  # Enable session reuse
        cache_mode=CacheMode.DISABLED,  # Fresh content for processing
        wait_until=args.wait,
        page_timeout=args.timeout,
        markdown_generator=None,  # type: ignore[arg-type]
        extraction_strategy=None,  # type: ignore[arg-type]
        verbose=args.verbose,
        stream=False,
    )
