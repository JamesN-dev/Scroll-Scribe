# ScrollScribe

**ScrollScribe** turns grabs docs and converts into local clean Markdown using browser automation and LLM filtering, perfect for building RAG datasets.

<!-- markdownlint-disable MD004 MD007 MD041 -->
<!-- toc-ignore-start -->

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Step 1: Extracting Links from a Documentation Homepage](#step-1-extracting-links-from-a-documentation-homepage)
  - [Step 2: Scraping URLs to Markdown](#step-2-scraping-urls-to-markdown)
  - [Arguments](#arguments)
    - [Positional](#positional)
    - [Options](#options)
- [Output](#output)
- [Notes](#notes)
- [Acknowledgments](#acknowledgments)

<!-- toc-ignore-end -->

ScrollScribe leverages `crawl4ai`'s browser automation capabilities to fetch HTML content and then utilizes an LLM (Language Model) via `crawl4ai`'s `LLMContentFilter` to intelligently extract the main content from the HTML, excluding common boilerplate like navigation, footers, and ads, before outputting Markdown.

---

## Features

* Extracts internal links from a single documentation page using `simple_link_extractor.py`.
* Reads target URLs from a text file, one URL per line (only the first URL per line is used).
* Uses `crawl4ai` for robust, asynchronous scraping with Playwright.
* Applies `LLMContentFilter` to intelligently parse HTML and extract clean, focused Markdown content.
* Fully configurable via CLI: specify the LLM model, API key environment variable, and base URL (OpenRouter by default).
* Supports adjustable page load timeouts and wait conditions.
* Outputs each successfully processed page as a standalone `.md` file in the specified directory.
* Provides a full CLI experience with colored console feedback and error reporting via `rich`.

---

## Prerequisites

* Python 3.10+ (3.12+ recommended)
* `uv` (or `pip`) Python package manager.
* An API key for your chosen LLM provider (e.g., OpenRouter, OpenAI) accessible as an environment variable.

---

## Installation

1. **Clone the repository (if applicable) or place the scripts in your project directory.**
2. **Create and activate a virtual environment:**
    ```bash
    uv venv
    source .venv/bin/activate
    # Or: python -m venv .venv && source .venv/bin/activate
    ```
3. **Install required libraries using `uv`:**
    ```bash
    uv add crawl4ai rich python-dotenv litellm requests beautifulsoup4
    ```
    *(Note: `litellm` is used internally by `LLMContentFilter` for making LLM calls).*
4. **Run Crawl4AI setup to install Playwright browsers and verify your environment:**
    ```bash
    crawl4ai-setup
    ```
    *This command installs necessary Playwright browsers and performs environment checks.*
5. **(Optional) Run Diagnostics:**
    ```bash
    crawl4ai-doctor
    ```
    *This checks compatibility and verifies the installation.*

---

## Configuration

1. **Create a `.env` file** in the project root directory (where you run the script from).
2. **Add your LLM API key** to the `.env` file. The script defaults to looking for `OPENROUTER_API_KEY`. If you use a different provider/key, ensure the corresponding environment variable is set and use the `--api-key-env` argument when running the script. You might also need to adjust `--model` and `--base-url`.
    ```dotenv
    # Example .env file for OpenRouter
    OPENROUTER_API_KEY="your_openrouter_api_key_here"

    # Example for OpenAI (use with --model openai/gpt-4o --api-key-env OPENAI_API_KEY --base-url "")
    # OPENAI_API_KEY="your_openai_api_key_here"
    ```

---

## Usage

### Step 1: Extracting Links from a Documentation Homepage

Use `simple_link_extractor.py` to crawl a documentation homepage or index and extract all internal links. The output is a `.txt` file with one URL per line.

**Command Structure:**
```bash
uv run app/simple_link_extractor.py <start_url> -o <output_link_file.txt> [-v]
```

**Arguments:**
- `start_url` (positional): The starting URL to scrape for links (e.g., `https://docs.example.com/`).
- `-o`, `--output-file` (required): Path to the output text file to save discovered URLs (e.g., `output/discovered_urls.txt`).
- `-v`, `--verbose` (optional): Enable verbose logging.

**Example:**
```bash
uv run app/simple_link_extractor.py https://docs.example.com/ -o data/doc_links.txt -v
```

---

### Step 2: Scraping URLs to Markdown

Use the main app (`scrollscribe.py`) to process the list of URLs generated in Step 1. This script reads the `.txt` file, scrapes each URL, and outputs cleaned Markdown files.

**Command Structure:**
```bash
uv run app/scrollscribe.py <input_file.txt> [OPTIONS]
```

### Arguments

#### Positional

- **`input_file`**  
  Path to the text file containing URLs (typically the output from Step 1).

#### Options

- **`-o`, `--output-dir`**  
  Directory to save filtered Markdown files.  
  *Default:* `output_llm_filtered_markdown`

- **`-t`, `--timeout`**  
  Page load timeout in milliseconds.  
  *Default:* `60000`

- **`--wait`**  
  Playwright `wait_until` state that defines when a page is considered loaded.  
  *Options:* `load`, `domcontentloaded`, `networkidle`  
  *Default:* `networkidle`

- **`--model`**  
  LLM model identifier to use for filtering.  
  *Default:* `openrouter/openrouter/optimus-alpha`

- **`--api-key-env`**  
  Name of the environment variable containing your LLM API key.  
  *Default:* `OPENROUTER_API_KEY`

- **`--base-url`**  
  Base URL for the LLM API.  
  *Default:* `https://openrouter.ai/api/v1`

- **`--max-tokens`**  
  Maximum number of output tokens to allow in the LLM's response.  
  *Default:* `4096`

- **`-v`, `--verbose`**  
  Enable verbose logging.  
  *Default:* `False`

- **`-h`, `--help`**  
  Show help message and exit.

**Examples:**
```bash
# Basic usage: process the generated link file using default settings
uv run app data/doc_links.txt

# Specify output directory and longer timeout
uv run app data/doc_links.txt -o output/my_docs_markdown -t 90000

# Use a different model and enable verbose logging
uv run app data/doc_links.txt -o output/my_docs_claude -t 60000 --model openrouter/openrouter/optimus-alpha -v
```

---

## Output

The script automatically creates the specified output directory if it doesn’t exist. Inside this directory, it saves one `.md` file for each URL that was successfully fetched and processed by the LLMContentFilter. The filename is based on the URL path (e.g., `page_012_api_arun.md`). These files contain the cleaned Markdown content intended for RAG ingestion.

---

## Notes

- The `simple_link_extractor.py` script uses `rich` for colored console output.
  
- Speed: The main script makes an LLM call for every URL, so processing time depends on the number of URLs, page complexity, network speed, and the chosen LLM's response time.
  
- API Keys: You can set multiple API keys inside your .env and select between them using --api-key-env. Ensure the correct API key environment variable is set in your `.env` file and matches the `--api-key-env` argument (or its default). Simply leave this argument out if you just want to use the default (default: OPENROUTER_API_KEY).
  
- Errors: Check the console output for warnings (e.g., skipped lines, empty filter results) or errors (e.g., fetch failures, LLM API errors).

---

## Acknowledgments

ScrollScribe is built on top of [`crawl4ai`](https://github.com/unclecode/crawl4ai), an excellent library by [@unclecode](https://github.com/unclecode) for browser automation and LLM-powered content filtering.

Big ups to the crawl4ai team for building such a solid foundation... this project wouldn’t exist without it.
