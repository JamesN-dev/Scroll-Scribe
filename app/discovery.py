"""URL discovery for documentation websites.

DEPRECATED: This module is deprecated. Use fast_discovery.py instead.
The extract_links() function in this file uses slow requests+BeautifulSoup.
Use extract_links_fast() from fast_discovery.py for modern crawl4ai-based discovery.

Extracted from simple_link_extractor.py with @retry_network decorator added.
"""

from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from rich.console import Console

from .utils.exceptions import InvalidUrlError, NetworkError
from .utils.retry import retry_network


@retry_network
def extract_links(url: str, verbose: bool = False) -> set[str]:
    """Extract all unique internal documentation links from a URL, stripping #anchors.

    DEPRECATED: Use extract_links_fast() from fast_discovery.py instead.
    This function is slow and uses legacy requests+BeautifulSoup approach.

    Args:
        url: The starting URL to scrape for links
        verbose: Enable verbose logging output

    Returns:
        Set of unique internal URLs found on the page

    Raises:
        InvalidUrlError: If the URL cannot be parsed
        NetworkError: If the HTTP request fails
    """
    console = Console()

    if verbose:
        console.print(f"[cyan][INFO] Fetching URL: {url}[/cyan]")

    # Determine base domain
    try:
        base_domain: str = urlparse(url).netloc
        if verbose:
            console.print(f"[magenta][DEBUG] Base domain: {base_domain}[/magenta]")
    except Exception as e:
        raise InvalidUrlError(
            f"Could not parse domain from URL: {url} - {e}", url=url
        ) from e

    # Fetch the page
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise NetworkError(f"Failed to fetch URL: {e}", url=url) from e

    # Parse HTML
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        if verbose:
            title: str | None = soup.title.string if soup.title else "No title"
            console.print(f"[magenta][DEBUG] Page title: {title}[/magenta]")

        # Collect and dedupe internal links
        all_links = soup.find_all("a")
        if verbose:
            console.print(
                f"[magenta][DEBUG] Found {len(all_links)} total links[/magenta]"
            )

        doc_links: set[str] = set()
        seen_bases: set[str] = set()

        for link in all_links:
            href: str | None = link.get("href")  # type: ignore
            if not href or href.startswith("#"):
                continue

            # Resolve relative URLs
            absolute_url: str = urljoin(url, href)
            parsed = urlparse(absolute_url)

            # Skip external domains
            if parsed.netloc != base_domain:
                if verbose:
                    console.print(
                        f"[magenta][DEBUG] Skipping external: {absolute_url}[/magenta]"
                    )
                continue

            # Strip fragment (#anchor)
            base_url: str = absolute_url.split("#")[0]

            if base_url not in seen_bases:
                seen_bases.add(base_url)
                doc_links.add(base_url)

        if verbose:
            console.print(
                f"[magenta][DEBUG] Found {len(doc_links)} internal links[/magenta]"
            )

        return doc_links

    except Exception as e:
        # Convert any other errors to our exception types
        raise NetworkError(f"Failed to extract links from {url}: {e}", url=url) from e


def save_links_to_file(
    links: set[str], output_file: str, verbose: bool = False
) -> None:
    """Save discovered links to a text file.

    Args:
        links: Set of URLs to save
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
        out_path.write_text("\n".join(sorted(links)), encoding="utf-8")
        if verbose:
            console.print(f"[green][SUCCESS] Saved to {out_path}[/green]")
    except Exception as e:
        console.print(
            f"[bold red][ERROR] Could not write file {out_path}: {e}[/bold red]"
        )
        raise
