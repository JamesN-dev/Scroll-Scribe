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
    links: list[str] = await extract_links_fast("https://docs.example.com/", verbose=True)
"""

from pathlib import Path

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from rich.console import Console

from app.utils.error_classification import classify_error_type
from app.utils.exceptions import InvalidUrlError, NetworkError
from app.utils.logging import CleanConsole
from app.utils.retry import retry_network
from app.utils.url_helpers import clean_url_for_display


@retry_network
async def extract_links_fast(start_url: str, verbose: bool = False) -> list[str]:
    """
    Async fast link discovery using Crawl4AI.
    Returns an ordered list of internal links (hrefs as strings).
    Always fetches fresh content (cache disabled).

    Args:
        start_url: The starting URL to scrape for links
        verbose: Enable verbose logging output

    Returns:
        Ordered list of unique internal URLs found on the page

    Raises:
        InvalidUrlError: If the URL cannot be parsed or processed
        NetworkError: If the crawl fails due to network issues
    """
    console = CleanConsole()
    try:
        return await _extract_links_async(start_url, verbose)
    except Exception as e:
        # Map unexpected errors to appropriate ScrollScribe exceptions
        error_type = classify_error_type(str(e))

        if error_type == "url_error":
            if verbose:
                console.print_error(f"URL parsing failed: {e}")
            raise InvalidUrlError(
                f"Could not process URL: {start_url}", url=start_url, parse_error=str(e)
            ) from e
        else:
            if verbose:
                console.print_error(f"Discovery network error: {e}")
            raise NetworkError(f"Discovery operation failed: {e}", url=start_url) from e


async def _extract_links_async(start_url: str, verbose: bool = False) -> list[str]:
    """Internal async function to extract links using ordered duplicate-free approach.

    Args:
        start_url: The starting URL to scrape for links
        verbose: Enable verbose logging output

    Returns:
        Ordered list of unique internal URLs found on the page

    Raises:
        InvalidUrlError: If the URL cannot be parsed or processed
        NetworkError: If the crawl fails due to network issues
    """
    console = CleanConsole()

    if verbose:
        console.print_phase(
            "DISCOVERY", f"Extracting links from {clean_url_for_display(start_url)}"
        )

    config = CrawlerRunConfig(
        css_selector="a[href]",
        cache_mode=CacheMode.DISABLED,  # Always fetch fresh content
        excluded_tags=["script", "style", "img", "video", "nav", "footer", "aside"],
        word_count_threshold=0,
        exclude_external_links=True,
    )

    seen: set[str] = set()
    ordered_links: list[str] = []

    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(start_url, config=config)

            if not getattr(result, "success", False):
                error_msg = getattr(result, "error_message", "Unknown crawl error")
                if verbose:
                    console.print_error(
                        f"Discovery operation returned failure: {error_msg}"
                    )

                # Use unified error classification
                error_type = classify_error_type(error_msg)

                if error_type == "url_error":
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
                    if (
                        clean_href
                        and clean_href != start_url
                        and clean_href not in seen
                    ):
                        seen.add(clean_href)
                        ordered_links.append(clean_href)

            if verbose:
                console.print_success(
                    f"Discovery completed: {len(ordered_links)} unique internal links"
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

    return ordered_links


def save_links_to_file(
    links: list[str], output_file: str, verbose: bool = False
) -> None:
    """Save discovered links to a text file.

    Args:
        links: Ordered list of URLs to save
        output_file: Path to output file
        verbose: Enable verbose logging
    """
    console = Console()

    if not links:
        if verbose:
            console.print("[yellow][WARN] No valid URLs to save.[/yellow]")
        return

    if verbose:
        console.print(
            f"\n[cyan][INFO] Found {len(links)} unique URLs. Saving...[/cyan]"
        )

    out_path: Path = Path(output_file)
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(links), encoding="utf-8")
        if verbose:
            console.print(f"[green][SUCCESS] Saved to {out_path}[/green]")
    except Exception as e:
        console.print(
            f"[bold red][ERROR] Could not write file {out_path}: {e}[/bold red]"
        )
        raise
