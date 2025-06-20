#!/usr/bin/env python3
"""
Simple link extractor for documentation websites.
This script uses requests and BeautifulSoup to extract all unique internal documentation links from a given URL,
stripping off any `#` fragments for deduplication.
"""

import argparse
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich_argparse import RichHelpFormatter

# Initialize console for output
console: Console = Console()


def extract_links(url: str, verbose: bool = False) -> set[str]:
    """Extract all unique internal documentation links from a URL, stripping #anchors."""
    console.print(f"[cyan][INFO] Fetching URL: {url}[/cyan]")

    # Determine base domain
    try:
        base_domain: str = urlparse(url).netloc
        if verbose:
            console.print(f"[magenta][DEBUG] Base domain: {base_domain}[/magenta]")
    except Exception as e:
        console.print(
            f"[bold red][ERROR] Could not parse domain from URL: {url} - {e}[/bold red]"
        )
        return set()

    # Fetch the page
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red][ERROR] Failed to fetch URL: {e}[/bold red]")
        return set()

    # Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")
    if verbose:
        title: str | None = soup.title.string if soup.title else "No title"
        console.print(f"[magenta][DEBUG] Page title: {title}[/magenta]")

    # Collect and dedupe internal links
    all_links = soup.find_all("a")
    if verbose:
        console.print(f"[magenta][DEBUG] Found {len(all_links)} total links[/magenta]")

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


def setup_argparse() -> argparse.Namespace:
    """Set up and parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Extract links from documentation websites.\n\n"
            "Example:\n  uv run simple_link_extractor.py https://docs.example.com/ -o data/doc_links.txt -v"
        ),
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "start_url",
        type=str,
        help="The starting URL to scrape for links (e.g., 'https://docs.example.com/').",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        required=True,
        help="Path to the output file for saving discovered URLs.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> int:
    """Main entry point."""
    console.print("[cyan][INFO] Starting Link Extraction...[/cyan]")
    console.print(f"[cyan][INFO] Start URL:[/cyan] {args.start_url}")
    console.print(f"[cyan][INFO] Output File:[/cyan] {args.output_file}")

    found_urls: set[str] = extract_links(args.start_url, args.verbose)

    if found_urls:
        console.print(
            f"\n[cyan][INFO] Found {len(found_urls)} unique URLs. Saving...[/cyan]"
        )
        out_path: Path = Path(args.output_file)
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text("\n".join(sorted(found_urls)), encoding="utf-8")
            console.print(f"[green][SUCCESS] Saved to {out_path}[/green]")
        except Exception as e:
            console.print(
                f"[bold red][ERROR] Could not write file {out_path}: {e}[/bold red]"
            )
            return 1
    else:
        console.print("[yellow][WARN] No valid URLs extracted.[/yellow]")

    console.print("[cyan][INFO] Extraction finished.[/cyan]")
    return 0


if __name__ == "__main__":
    args = setup_argparse()
    sys.exit(main(args))
