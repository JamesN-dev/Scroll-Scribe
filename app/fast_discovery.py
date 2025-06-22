"""Fast, reliable internal link discovery for documentation sites using Crawl4AI.

Implements modern, high-performance URL discovery with browser automation and JavaScript support.
Fetches only internal documentation links, always using fresh content (no cache, no LLM).

Key features:
- Optimized for speed and accuracy on documentation sites
- No LLM required; always fetches live content
- Designed for use in --fast mode and as a drop-in replacement for legacy discovery
- Returns only internal links relevant for documentation scraping

Example:
    from fast_discovery import extract_links_fast
    links = extract_links_fast("https://docs.example.com/", verbose=True)
"""

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

from .utils.exceptions import InvalidUrlError, NetworkError
from .utils.logging import CleanConsole
from .utils.retry import retry_network


@retry_network
async def extract_links_fast(start_url: str, verbose: bool = False) -> set[str]:
    """
    Async fast link discovery using Crawl4AI.
    Returns a set of internal links (hrefs as strings).
    Always fetches fresh content (cache disabled).

    Args:
        start_url: The starting URL to scrape for links
        verbose: Enable verbose logging output

    Returns:
        Set of unique internal URLs found on the page

    Raises:
        InvalidUrlError: If the URL cannot be parsed or processed
        NetworkError: If the crawl fails due to network issues
    """
    console = CleanConsole()
    try:
        return await _extract_links_async(start_url, verbose)
    except Exception as e:
        # Map unexpected errors to appropriate ScrollScribe exceptions
        error_msg = str(e).lower()
        if any(term in error_msg for term in ["invalid", "parse", "malformed", "url"]):
            if verbose:
                console.print_error(f"URL parsing failed: {e}")
            raise InvalidUrlError(
                f"Could not process URL: {start_url}", url=start_url, parse_error=str(e)
            ) from e
        else:
            if verbose:
                console.print_error(f"Discovery network error: {e}")
            raise NetworkError(f"Discovery operation failed: {e}", url=start_url) from e


async def _extract_links_async(start_url: str, verbose: bool = False) -> set[str]:
    console = CleanConsole()

    if verbose:
        console.print_phase("DISCOVERY", f"Extracting links from {start_url}")

    config = CrawlerRunConfig(
        css_selector="a[href]",
        cache_mode=CacheMode.DISABLED,  # Always fetch fresh content
        excluded_tags=["script", "style", "img", "video", "nav", "footer", "aside"],
        word_count_threshold=0,
        exclude_external_links=True,
    )

    internal_links: set[str] = set()

    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(start_url, config=config)

            if not getattr(result, "success", False):
                error_msg = getattr(result, "error_message", "Unknown crawl error")
                if verbose:
                    console.print_error(
                        f"Discovery operation returned failure: {error_msg}"
                    )

                # Check if it's a URL-related error
                if any(
                    term in error_msg.lower()
                    for term in ["invalid", "malformed", "url", "domain"]
                ):
                    raise InvalidUrlError(
                        f"Invalid URL format: {start_url}",
                        url=start_url,
                        parse_error=error_msg,
                    )
                else:
                    raise NetworkError(
                        f"Discovery operation failed: {error_msg}", url=start_url
                    )

            # Extract links from result - safely access links attribute
            links_data = getattr(result, "links", {}) or {}
            internal_link_list = links_data.get("internal", [])

            if verbose:
                console.print_fetch_status(start_url, "fetched")

            # Process and filter links
            for link in internal_link_list:
                href = link.get("href")
                if href and isinstance(href, str):
                    # Strip fragments and normalize
                    clean_href = href.split("#")[0].strip()
                    if clean_href and clean_href != start_url:
                        internal_links.add(clean_href)

            if verbose:
                console.print_success(
                    f"Discovery completed: {len(internal_links)} unique internal links"
                )

    except (InvalidUrlError, NetworkError):
        # Re-raise our ScrollScribe exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e)
        if verbose:
            console.print_error(f"Unexpected error during discovery: {error_msg}")

        # Map to appropriate ScrollScribe exception
        if any(
            term in error_msg.lower()
            for term in ["timeout", "connection", "network", "dns"]
        ):
            raise NetworkError(
                f"Network error during discovery: {error_msg}", url=start_url
            ) from e
        elif any(
            term in error_msg.lower()
            for term in ["url", "parse", "invalid", "malformed"]
        ):
            raise InvalidUrlError(
                f"URL processing error: {start_url}",
                url=start_url,
                parse_error=error_msg,
            ) from e
        else:
            # Generic network error for other unexpected issues
            raise NetworkError(
                f"Discovery operation failed: {error_msg}", url=start_url
            ) from e

    return internal_links
