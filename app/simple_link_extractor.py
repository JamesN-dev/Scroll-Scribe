#!/usr/bin/env python3
"""
Simple link extractor for documentation websites.
This script uses requests and BeautifulSoup to extract all links from a documentation website.
"""

import argparse
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from pathlib import Path
from rich.console import Console

# Initialize console for output
console = Console()


def extract_links(url, verbose=False):
    """Extract all links from a URL."""
    console.print(f"[cyan][INFO] Fetching URL: {url}[/cyan]")

    # Get the base URL for filtering
    try:
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        if verbose:
            console.print(f"[magenta][DEBUG] Base URL: {base_url}[/magenta]")
    except Exception as e:
        console.print(
            f"[bold red][ERROR] Could not parse domain from URL: {url} - {e}[/bold red]"
        )
        return set()

    # Fetch the page
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red][ERROR] Failed to fetch URL: {e}[/bold red]")
        return set()

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    if verbose:
        console.print(
            f"[magenta][DEBUG] Page title: {soup.title.string if soup.title else 'No title'}[/magenta]"
        )

    # Find all links
    all_links = soup.find_all("a")
    if verbose:
        console.print(f"[magenta][DEBUG] Found {len(all_links)} total links[/magenta]")

    # Filter links to only include documentation links (not external links)
    doc_links = set()
    for link in all_links:
        href = link.get("href")
        if not href:
            continue

        # Skip anchors and external links
        if href.startswith("#"):
            continue

        # Convert relative URLs to absolute
        absolute_url = urljoin(url, href)

        # Only include links from the same domain
        link_domain = urlparse(absolute_url).netloc
        if link_domain == urlparse(url).netloc:
            doc_links.add(absolute_url)
        elif verbose:
            console.print(
                f"[magenta][DEBUG] Skipping external link: {absolute_url}[/magenta]"
            )

    if verbose:
        console.print(
            f"[magenta][DEBUG] Found {len(doc_links)} internal links[/magenta]"
        )

    return doc_links


def setup_argparse():
    """Sets up and parses command-line arguments for link extraction."""
    parser = argparse.ArgumentParser(
        description="Extract links from documentation websites.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "start_url",
        help="The starting URL to scrape for links (e.g., 'https://docs.example.com/').",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        required=True,
        help="Path to the output text file to save discovered URLs (e.g., 'output/discovered_urls.txt').",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args()


def main(args):
    """Main function."""
    # Extract links
    console.print("[cyan][INFO] Starting Link Extraction...[/cyan]")
    console.print(f"[cyan][INFO] Start URL:[/cyan] {args.start_url}")
    console.print(f"[cyan][INFO] Output File:[/cyan] {args.output_file}")

    found_urls = extract_links(args.start_url, args.verbose)

    # Save discovered URLs
    if found_urls:
        console.print(
            f"\n[cyan][INFO] Found {len(found_urls)} unique URLs. Saving to file...[/cyan]"
        )
        output_filepath = Path(args.output_file)
        try:
            output_filepath.parent.mkdir(parents=True, exist_ok=True)
            output_filepath.write_text(
                "\n".join(sorted(list(found_urls))), encoding="utf-8"
            )
            console.print(f"[green][SUCCESS] Saved URLs to:[/green] {output_filepath}")
        except IOError as e:
            console.print(
                f"[bold red][ERROR] Failed to write output file {output_filepath}: {e}[/bold red]"
            )
            return 1
        except Exception as e:
            console.print(
                f"[bold red][ERROR] Unexpected error saving file: {e}[/bold red]"
            )
            return 1
    else:
        console.print("[yellow][WARN] No valid URLs were extracted to save.[/yellow]")

    console.print("[cyan][INFO] Link Extraction finished.[/cyan]")
    return 0


if __name__ == "__main__":
    args = setup_argparse()
    sys.exit(main(args))
