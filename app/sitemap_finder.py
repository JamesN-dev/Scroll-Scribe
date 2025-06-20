import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import ParseError

# --- Google SERP link cleaning helper ---
import re
from urllib.parse import unquote, urlparse


def extract_google_link(google_href: str) -> str | None:
    m = re.search(r"[?&]q=(https?%3A%2F%2F[^&]+)", google_href)
    if not m:
        return None
    target = unquote(m.group(1))
    parsed = urlparse(target)
    return parsed._replace(query="", fragment="").geturl()


try:
    # Import specific types for checking
    from bs4 import BeautifulSoup, Tag

    BS4_AVAILABLE = True
except ImportError:
    BeautifulSoup = None  # Define as None if import fails
    Tag = None  # Define as None if import fails
    BS4_AVAILABLE = False

from urllib.parse import urljoin, urlparse

import requests
from rich.console import Console
from rich_argparse import RichHelpFormatter

# --- Console and Colors ---
console: Console = Console(highlight=False)

clr_p1_hdr = "bold bright_cyan"
clr_p1_info = "deep_sky_blue1"
clr_p1_url = "dodger_blue1"
clr_p2_hdr = "bold orange1"
clr_p2_info = "dark_orange"
clr_p2_url = "gold1"
clr_p3_hdr = "bold chartreuse1"
clr_p3_info = "spring_green1"
clr_p3_url = "green1"
clr_p4_hdr = "bold medium_purple1"
clr_p4_info = "purple"
clr_p5_hdr = "bold bright_blue"
clr_p5_info = "turquoise2"
clr_p5_url = "cyan1"
clr_scrape_hdr = "bold magenta1"
clr_scrape_info = "hot_pink3"
clr_scrape_url = "medium_purple2"
clr_success = "bold bright_green"
clr_error = "bold red"
clr_warn = "bold yellow"
clr_dim = "dim"

# --- Global Settings ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
SITEMAP_NS = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
}  # Namespace needed for XML parsing

# --- Sitemap Mode Functions ---


def find_and_extract_sitemap_urls(start_url_input: str) -> list[str] | None:
    """Finds and extracts page URLs from website sitemaps."""
    sitemaps_to_process: set[str] = set()
    processed_sitemaps: set[str] = set()
    final_sitemap_files: set[str] = set()
    extracted_page_urls: set[str] = set()

    try:
        start_url = start_url_input
        if not start_url.endswith("/robots.txt"):
            start_url = start_url.rstrip("/") + "/robots.txt"
        robots_url = start_url
        base_url: str = robots_url.replace("/robots.txt", "")

        console.print(
            f"\n[{clr_p1_hdr}]--- Phase 1: Checking robots.txt ---[/{clr_p1_hdr}]"
        )
        console.print(
            f"[{clr_p1_info}]Attempting to fetch:[/] [{clr_p1_url}]{robots_url}[/]"
        )

        try:
            response = requests.get(robots_url, timeout=10, headers=HEADERS)
            if response.status_code == 200:
                console.print(
                    f"[{clr_success}][+] Found robots.txt (Status: {response.status_code})[/{clr_success}]"
                )
                lines: list[str] = response.text.splitlines()
                robots_sitemaps = {
                    line.partition(":")[2].strip()
                    for line in lines
                    if line.strip().lower().startswith("sitemap:")
                }
                if robots_sitemaps:
                    console.print(
                        f"[{clr_p1_info}]-> Found {len(robots_sitemaps)} sitemap links listed in robots.txt:[/{clr_p1_info}]"
                    )
                    for sitemap_url in robots_sitemaps:
                        console.print(f"  [{clr_p1_url}]-> {sitemap_url}[/]")
                    sitemaps_to_process.update(robots_sitemaps)
                    console.print(
                        f"[{clr_p1_info}][+] Added {len(robots_sitemaps)} URL(s) from robots.txt to the processing queue.[/{clr_p1_info}]"
                    )
                else:
                    console.print(
                        f"[{clr_p1_info}][-] No 'Sitemap:' directives found in robots.txt.[/{clr_p1_info}]"
                    )
            elif response.status_code == 404:
                console.print(
                    f"[{clr_warn}][!] robots.txt not found at {robots_url} (Status: 404)[/{clr_warn}]"
                )
            else:
                console.print(
                    f"[{clr_error}][X] Failed to fetch {robots_url} (Status: {response.status_code})[/{clr_error}]"
                )
        except requests.exceptions.RequestException as e:
            console.print(
                f"[{clr_error}][X] Network Error fetching {robots_url}: {e}[/{clr_error}]"
            )

        console.print(
            f"\n[{clr_p2_hdr}]--- Phase 2: Guessing Common Sitemap Paths ---[/{clr_p2_hdr}]"
        )
        console.print(
            f"[{clr_p2_info}]Using base URL for guessing:[/] [{clr_p2_url}]{base_url}[/]"
        )
        COMMON_SITEMAP_PATHS = [
            "/sitemap.xml",
            "/sitemap_index.xml",
            "/sitemap.xml.gz",
            "/sitemap_index.xml.gz",
            "/sitemap-index.xml",
            "/sitemap_news.xml",
            "/sitemap-products.xml",
            "/sitemap_products_1.xml",
            "/sitemap_1.xml",
            "/sitemap_0.xml",
            "/sitemap.php",
            "/sitemap.txt",
            "/gss/sitemap.xml",
            "/post-sitemap.xml",
            "/page-sitemap.xml",
            "/category-sitemap.xml",
        ]
        guesses_added_count = 0
        for path in COMMON_SITEMAP_PATHS:
            guess_url = base_url.rstrip("/") + path
            if (
                guess_url in sitemaps_to_process
                or guess_url in processed_sitemaps
                or guess_url in final_sitemap_files
            ):
                console.print(
                    f"  [{clr_dim}]Skipping guess (already found/processed): {guess_url}[/{clr_dim}]"
                )
                continue
            try:
                console.print(f"  [{clr_dim}]Trying guess: {guess_url}[/{clr_dim}]")
                head_response = requests.head(
                    guess_url, timeout=3, headers=HEADERS, allow_redirects=True
                )
                if head_response.status_code == 200:
                    content_type = head_response.headers.get("content-type", "").lower()
                    if "xml" in content_type or "text" in content_type:
                        console.print(
                            f"  [{clr_success}][+] Guess successful (HEAD):[/] [{clr_p2_url}]{guess_url}[/]"
                        )
                        sitemaps_to_process.add(guess_url)
                        guesses_added_count += 1
                    else:
                        console.print(
                            f"  [{clr_warn}][!] Guess OK but invalid Content-Type ({content_type}) for {guess_url}. Skipping.[/{clr_warn}]"
                        )
            except requests.exceptions.Timeout:
                console.print(
                    f"  [{clr_warn}]Timeout on guess: {guess_url}[/{clr_warn}]",
                    style=clr_dim,
                )
            except requests.exceptions.RequestException:
                pass
        if guesses_added_count > 0:
            console.print(
                f"[{clr_p2_info}][+] Added {guesses_added_count} potential URL(s) from guessing to the processing queue.[/{clr_p2_info}]"
            )
        else:
            console.print(
                f"[{clr_p2_info}][-] No additional potential sitemaps found via guessing.[/{clr_p2_info}]"
            )

        console.print(
            f"\n[{clr_p3_hdr}]--- Phase 3: Processing Sitemap Queue ({len(sitemaps_to_process)} URLs initially) ---[/{clr_p3_hdr}]"
        )
        while sitemaps_to_process:
            sitemap_url = sitemaps_to_process.pop()
            if sitemap_url in processed_sitemaps:
                continue

            console.print(
                f"\n[{clr_p3_info}]Processing URL from queue:[/] [{clr_p3_url}]{sitemap_url}[/]"
            )
            processed_sitemaps.add(sitemap_url)

            try:
                sitemap_response = requests.get(
                    sitemap_url, timeout=15, headers=HEADERS
                )
                sitemap_response.raise_for_status()
                content_type = sitemap_response.headers.get("content-type", "").lower()
                is_xml = "xml" in content_type
                is_text = "text" in content_type
                is_gzipped = sitemap_url.endswith(".gz")

                if is_gzipped:
                    console.print(
                        f"  [{clr_warn}][!] Found gzipped sitemap. Parsing .gz not implemented. Adding URL directly to final sitemap list.[/{clr_warn}]"
                    )
                    final_sitemap_files.add(sitemap_url)
                    continue

                if not is_xml and not is_text:
                    console.print(
                        f"  [{clr_warn}][!] Content-Type ({content_type}) is not XML/text. Skipping parse.[/{clr_warn}]"
                    )
                    continue

                try:
                    console.print(f"  [{clr_p3_info}]Parsing XML content...[/]")
                    root = ET.fromstring(sitemap_response.content)
                    tag_name = root.tag

                    if tag_name.endswith("sitemapindex"):
                        console.print(
                            f"  [{clr_p3_info}][+] Detected Sitemap Index file.[/{clr_p3_info}]"
                        )
                        found_in_index = 0
                        for sitemap_node in root.findall("sm:sitemap", SITEMAP_NS):
                            loc_node = sitemap_node.find("sm:loc", SITEMAP_NS)
                            if loc_node is not None and loc_node.text:
                                nested_url = loc_node.text.strip()
                                if (
                                    nested_url not in processed_sitemaps
                                    and nested_url not in sitemaps_to_process
                                ):
                                    console.print(
                                        f"    [{clr_p3_url}]-> Found nested URL: {nested_url}[/]"
                                    )
                                    sitemaps_to_process.add(nested_url)
                                    found_in_index += 1
                                else:
                                    console.print(
                                        f"    [{clr_dim}]Skipping nested URL (already processed/queued): {nested_url}[/{clr_dim}]"
                                    )
                        if found_in_index > 0:
                            console.print(
                                f"  [{clr_p3_info}][+] Added {found_in_index} nested URL(s) back to the processing queue.[/{clr_p3_info}]"
                            )
                        else:
                            console.print(
                                f"  [{clr_warn}][!] Index file contained no new sitemap URLs.[/{clr_warn}]"
                            )

                    elif tag_name.endswith("urlset"):
                        console.print(
                            f"  [{clr_success}][+] Detected URL Set (Final Sitemap). Adding URL to final sitemap list.[/{clr_success}]"
                        )
                        final_sitemap_files.add(sitemap_url)
                    else:
                        console.print(
                            f"  [{clr_warn}][!] Unknown XML root tag <{tag_name}>. Skipping.[/{clr_warn}]"
                        )

                except ParseError as e_xml:
                    console.print(
                        f"  [{clr_error}][X] XML Parse Error: {e_xml}[/{clr_error}]"
                    )

            except requests.exceptions.Timeout:
                console.print(
                    f"  [{clr_error}][X] Timeout fetching this sitemap URL.[/{clr_error}]"
                )
            except requests.exceptions.HTTPError as e_http:
                console.print(
                    f"  [{clr_error}][X] HTTP Error fetching this sitemap URL: {e_http.response.status_code}[/{clr_error}]"
                )
            except requests.exceptions.RequestException as e_req:
                console.print(
                    f"  [{clr_error}][X] Request Error fetching this sitemap URL: {e_req}[/{clr_error}]"
                )

        console.print(
            f"\n[{clr_p4_hdr}]--- Phase 4: Finalizing Sitemap Files ---[/{clr_p4_hdr}]"
        )
        if not final_sitemap_files:
            console.print(
                f"[{clr_warn}][!] No final sitemap files (<urlset>) were identified in Phase 3.[/{clr_warn}]"
            )
            return None
        else:
            console.print(
                f"[{clr_p4_info}][+] Identified {len(final_sitemap_files)} final sitemap file(s) to extract URLs from:[/{clr_p4_info}]"
            )
            for fsf in sorted(list(final_sitemap_files)):
                console.print(f"  [{clr_p4_info}]-> {fsf}[/]")

        console.print(
            f"\n[{clr_p5_hdr}]--- Phase 5: Extracting URLs from Final Sitemaps ---[/{clr_p5_hdr}]"
        )
        for sitemap_file_url in final_sitemap_files:
            console.print(
                f"\n[{clr_p5_info}]Extracting from:[/] [{clr_p5_url}]{sitemap_file_url}[/]"
            )

            if sitemap_file_url.endswith(".gz"):
                console.print(
                    f"  [{clr_warn}][!] Skipping extraction for gzipped file (not implemented).[/{clr_warn}]"
                )
                continue

            try:
                sitemap_response = requests.get(
                    sitemap_file_url, timeout=15, headers=HEADERS
                )
                sitemap_response.raise_for_status()

                content_type = sitemap_response.headers.get("content-type", "").lower()
                if "xml" not in content_type and "text" not in content_type:
                    console.print(
                        f"  [{clr_warn}][!] Content-Type ({content_type}) is not XML/text. Cannot extract URLs.[/{clr_warn}]"
                    )
                    continue

                try:
                    root = ET.fromstring(sitemap_response.content)
                    tag_name = root.tag
                    urls_found_in_file = 0

                    if tag_name.endswith("urlset"):
                        for url_node in root.findall("sm:url", SITEMAP_NS):
                            loc_node = url_node.find("sm:loc", SITEMAP_NS)
                            if loc_node is not None and loc_node.text:
                                page_url = loc_node.text.strip()
                                if page_url:
                                    extracted_page_urls.add(page_url)
                                    urls_found_in_file += 1
                        console.print(
                            f"  [{clr_success}][+] Extracted {urls_found_in_file} page URLs from this file.[/{clr_success}]"
                        )
                    else:
                        console.print(
                            f"  [{clr_warn}][!] Expected <urlset> but found <{tag_name}>. Cannot extract URLs.[/{clr_warn}]"
                        )

                except ParseError as e_xml:
                    console.print(
                        f"  [{clr_error}][X] XML Parse Error during extraction: {e_xml}[/{clr_error}]"
                    )

            except requests.exceptions.Timeout:
                console.print(
                    f"  [{clr_error}][X] Timeout fetching this sitemap file for extraction.[/{clr_error}]"
                )
            except requests.exceptions.HTTPError as e_http:
                console.print(
                    f"  [{clr_error}][X] HTTP Error fetching this sitemap file for extraction: {e_http.response.status_code}[/{clr_error}]"
                )
            except requests.exceptions.RequestException as e_req:
                console.print(
                    f"  [{clr_error}][X] Request Error fetching this sitemap file for extraction: {e_req}[/{clr_error}]"
                )

        final_list = sorted(list(extracted_page_urls))
        return final_list if final_list else None

    except Exception as e:
        console.print(
            f"[{clr_error}][X] An unexpected critical error occurred in sitemap discovery/extraction: {e}[/{clr_error}]"
        )
        return None


# --- Scrape Mode Function ---


def scrape_single_page_links(
    start_url: str,
    verbose: bool = False,
    external: bool = False,
    clean_google: bool = False,
) -> list[str] | None:
    """Fetches a single HTML page and extracts internal links (optionally external links, optionally cleans Google SERP links)."""
    if not BS4_AVAILABLE:
        console.print(
            f"[{clr_error}][X] Error: BeautifulSoup4 (bs4) is required for '--mode scrape' but is not installed.[/{clr_error}]"
        )
        console.print(
            f"[{clr_error}]Please install it: pip install beautifulsoup4[/{clr_error}]"
        )
        return None

    console.print(
        f"\n[{clr_scrape_hdr}]--- Scrape Mode: Extracting Links from Single Page ---[/{clr_scrape_hdr}]"
    )
    console.print(
        f"[{clr_scrape_info}]Fetching HTML page:[/] [{clr_scrape_url}]{start_url}[/]"
    )

    try:
        base_domain: str = urlparse(start_url).netloc
        if verbose:
            console.print(
                f"[{clr_dim}]Base domain determined: {base_domain}[/{clr_dim}]"
            )
    except Exception as e:
        console.print(
            f"[{clr_error}][X] Could not parse domain from URL: {start_url} - {e}[/{clr_error}]"
        )
        return None

    try:
        response = requests.get(start_url, timeout=30, headers=HEADERS)
        response.raise_for_status()
        console.print(
            f"[{clr_success}][+] Successfully fetched page (Status: {response.status_code})[/{clr_success}]"
        )
    except requests.exceptions.RequestException as e:
        console.print(f"[{clr_error}][X] Failed to fetch URL: {e}[/{clr_error}]")
        return None

    try:
        console.print(f"[{clr_scrape_info}]Parsing HTML using BeautifulSoup...[/]")
        # Ensure BeautifulSoup is available before using it
        if BeautifulSoup is None:
            raise ImportError(
                "BeautifulSoup is required but was not imported successfully."
            )

        soup = BeautifulSoup(response.text, "html.parser")
        if verbose:
            title_tag = soup.title
            title: str | None = title_tag.string if title_tag else "No title"
            console.print(f"[{clr_dim}]Page title: {title}[/{clr_dim}]")

        all_links = soup.find_all("a")
        console.print(
            f"[{clr_scrape_info}]Found {len(all_links)} total <a> tags on the page.[/{clr_scrape_info}]"
        )

        scraped_urls: set[str] = set()
        seen_bases: set[str] = set()
        external_count = 0
        fragment_count = 0
        internal_count = 0

        for link in all_links:
            # Check if 'link' is a Tag object before calling .get()
            if Tag is not None and isinstance(link, Tag):
                # Explicitly cast the result of get() to satisfy Pyright
                href_value = link.get("href")
                href: str | None = None
                if isinstance(href_value, str):
                    href = href_value
                elif isinstance(
                    href_value, list
                ):  # Handle case where href might be a list (unlikely but possible)
                    href = href_value[0] if href_value else None
            else:
                # Skip if link is not a Tag object (e.g., NavigableString)
                continue

            if not href:
                continue
            if href.startswith("#"):
                fragment_count += 1
                continue

            # Google SERP cleaning logic
            if external and clean_google and "google.com/url" in href:
                clean = extract_google_link(href)
                if clean:
                    if clean not in seen_bases:
                        seen_bases.add(clean)
                        scraped_urls.add(clean)
                    continue

            absolute_url: str = urljoin(start_url, href)
            parsed = urlparse(absolute_url)
            base_url_no_fragment: str = absolute_url.split("#")[0]

            if parsed.netloc != base_domain:
                external_count += 1
                if external:
                    if base_url_no_fragment not in seen_bases:
                        seen_bases.add(base_url_no_fragment)
                        scraped_urls.add(base_url_no_fragment)
                        if verbose:
                            console.print(
                                f"  [{clr_scrape_url}]-> Found external: {base_url_no_fragment}[/]"
                            )
                else:
                    if verbose:
                        console.print(
                            f"  [{clr_dim}]Skipping external: {absolute_url}[/{clr_dim}]"
                        )
                    continue
            else:
                if base_url_no_fragment not in seen_bases:
                    seen_bases.add(base_url_no_fragment)
                    scraped_urls.add(base_url_no_fragment)
                    internal_count += 1
                    if verbose:
                        console.print(
                            f"  [{clr_scrape_url}]-> Found internal: {base_url_no_fragment}[/]"
                        )
                elif verbose:
                    console.print(
                        f"  [{clr_dim}]Skipping duplicate internal base: {base_url_no_fragment}[/{clr_dim}]"
                    )

        console.print(
            f"[{clr_scrape_info}]Extraction Summary: Found {internal_count} unique internal URLs (skipped {external_count} external, {fragment_count} fragment-only links).[/{clr_scrape_info}]"
        )

        final_list = sorted(list(scraped_urls))
        return final_list if final_list else None

    except Exception as e:
        console.print(
            f"[{clr_error}][X] Error during HTML parsing or link extraction: {e}[/{clr_error}]"
        )
        return None


# --- Main Execution Logic ---


def setup_argparse() -> argparse.Namespace:
    """Sets up and parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Discover URLs via sitemap analysis or single-page scraping.\n\n"
            "Sitemap Mode (default):\n"
            "  Finds sitemaps via robots.txt/guessing, processes indexes, extracts all page URLs.\n"
            "  Example: python url_finder.py https://www.example.com output_sitemap_urls.txt\n\n"
            "Scrape Mode:\n"
            "  Scrapes a single HTML page for internal links.\n"
            "  Example: python url_finder.py --mode scrape https://www.example.com/about output_scraped_links.txt"
        ),
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "start_url",
        type=str,
        help="The starting URL (domain for sitemap mode, specific page for scrape mode).",
    )
    parser.add_argument(
        "output_file",
        type=str,
        help="Path to the output file for saving discovered URLs.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["sitemap", "scrape"],
        default="sitemap",
        help="Operation mode: 'sitemap' (default) or 'scrape'.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging (currently affects scrape mode more).",
    )
    parser.add_argument(
        "--external",
        action="store_true",
        help="Also capture external links (default is only internal links).",
    )
    parser.add_argument(
        "--clean-google",
        action="store_true",
        help="Extract and clean real URLs from Google SERP redirect links.",
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> int:
    """Main entry point determining execution flow based on mode."""
    console.print(
        f"[{clr_p4_info}]Starting URL Discovery (Mode: {args.mode})...[/{clr_p4_info}]"
    )
    console.print(f"[{clr_p4_info}]Input URL:[/] {args.start_url}")
    console.print(f"[{clr_p4_info}]Output File:[/] {args.output_file}")

    found_urls: list[str] | None = None

    if args.mode == "sitemap":
        found_urls = find_and_extract_sitemap_urls(args.start_url)
        output_type = "page URLs from sitemaps"
    elif args.mode == "scrape":
        found_urls = scrape_single_page_links(
            args.start_url,
            args.verbose,
            args.external,
            args.clean_google,
        )
        output_type = (
            "internal links scraped from page"
            if not args.external
            else "links scraped from page (including external)"
        )
    else:
        console.print(
            f"[{clr_error}][X] Invalid mode specified: {args.mode}[/{clr_error}]"
        )
        return 1

    if found_urls:
        console.print(
            f"\n[{clr_p4_info}]Found {len(found_urls)} unique {output_type}. Saving...[/{clr_p4_info}]"
        )
        out_path: Path = Path(args.output_file)
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text("\n".join(found_urls), encoding="utf-8")
            console.print(
                f"[{clr_success}]Saved successfully to {out_path}[/{clr_success}]"
            )
        except Exception as e:
            console.print(
                f"[{clr_error}][X] Could not write output file {out_path}: {e}[/{clr_error}]"
            )
            return 1
    else:
        console.print(
            f"\n[{clr_warn}][!] No valid URLs found for mode '{args.mode}'.[/{clr_warn}]"
        )

    console.print(f"[{clr_p4_info}]Discovery finished.[/{clr_p4_info}]")
    return 0


if __name__ == "__main__":
    try:
        arguments = setup_argparse()
        if arguments.mode == "scrape" and not BS4_AVAILABLE:
            console.print(
                f"[{clr_error}][X] Error: '--mode scrape' requires BeautifulSoup4 (bs4), which is not installed.[/{clr_error}]"
            )
            console.print(
                f"[{clr_error}]Please install it: pip install beautifulsoup4[/{clr_error}]"
            )
            sys.exit(1)

        exit_code = main(arguments)
        raise SystemExit(exit_code)
    except Exception as main_err:
        console.print(
            f"[{clr_error}]A critical error occurred: {main_err}[/{clr_error}]"
        )
        raise SystemExit(1) from main_err
