# ScrollScribe

**ScrollScribe** grabs docs and converts them into clean local Markdown using browser automation and LLM filtering, perfect for building RAG datasets.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Step 1: Extracting Links](#step-1-extracting-links)
  - [Step 2: Scraping URLs to Markdown](#step-2-scraping-urls-to-markdown)
  - [Runner Script](#runner-script)
- [Arguments](#arguments)
  - [Positional](#positional)
  - [Options](#options)
- [Output](#output)
- [Notes](#notes)
- [Acknowledgments](#acknowledgments)

---

## Features

- Extracts internal links from a documentation homepage using `simple_link_extractor.py`.
- Reads target URLs from a text file and scrapes HTML to Markdown via `LLMContentFilter`.
- Uses `crawl4ai`'s Playwright-based crawler for robust asynchronous scraping.
- Applies intelligent LLM filtering to extract only core content, excluding boilerplate.
- Fully configurable via CLI: model, API key variable, base URL, timeouts, and more.
- Supports colored console output and debug logging via `rich`.
- Includes a convenient `runscript.sh` for standard workflows and debug handling.

---

## Prerequisites

- Python 3.10+ (3.12+ recommended)
- `uv` (or `pip`) Python package manager
- Playwright browsers (installed via `crawl4ai-setup`)
- An LLM API key (e.g., OpenRouter) available as an environment variable

---

## Installation

1. Clone or download this repository.
2. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   uv add crawl4ai rich python-dotenv litellm requests beautifulsoup4
   ```
4. Install Playwright browsers:
   ```bash
   crawl4ai-setup
   ```
5. (Optional) Run diagnostics:
   ```bash
   crawl4ai-doctor
   ```

---

## Configuration

Create a `.env` file in the project root and add your API key:

```dotenv
# Default expects OPENROUTER_API_KEY
OPENROUTER_API_KEY="your_openrouter_api_key_here"
```

If you use a different provider or variable name, pass `--api-key-env` to the script.

---

## Usage

### Step 1: Extracting Links

Use `simple_link_extractor.py` to crawl a homepage and extract links into a text file:

```bash
uv run app/simple_link_extractor.py <start_url> -o <output_links.txt> [-v]
```

### Step 2: Scraping URLs to Markdown

Process the list of URLs and convert to Markdown:

```bash
uv run app/scrollscribe.py <input_links.txt> [OPTIONS]
```

### Runner Script

A helper script `runscript.sh` is provided for common workflows:

```bash
./runscript.sh [--debug]
```

- Sets `PYTHON_FORCE_COLOR=1` to preserve colors
- Uses defaults for model, timeouts, and output directory
- If `--debug` is passed, debug output is logged to `output/llm_debug.log` via `tee`

---

## Arguments

### Positional

- `input_file`  
  Path to the text file containing URLs (one per line).

### Options

- `-o, --output-dir`  
  Directory to save Markdown files (default: `output_llm_filtered_markdown`).
- `--start-at`  
  Zero-based index in the URL list to start processing (default: `0`).
- `-p, --prompt`  
  Custom LLM instruction prompt (default: built-in converter prompt).
- `-t, --timeout`  
  Page load timeout in ms (default: `60000`).
- `-w, --wait`  
  Playwright wait state: `load`, `domcontentloaded`, `networkidle` (default: `networkidle`).
- `--model`  
  LLM model identifier (default: `openrouter/google/gemini-2.0-flash-exp:free`).
- `--api-key-env`  
  Environment variable for the API key (default: `OPENROUTER_API_KEY`).
- `--base-url`  
  Base URL for the LLM API (default: `https://openrouter.ai/api/v1`).
- `--max-tokens`  
  Max tokens for LLM output (default: `8192`).
- `-v, --verbose`  
  Enable verbose logging.
- `--debug`  
  Enable internal LLM debug tracing and rich-logged output.

---

## Output

The script creates the output directory if needed and writes one `.md` file per URL, named `page_XXX_<slug>.md`, containing the cleaned Markdown.

---

## Notes

- Color output requires a terminal that supports ANSI; piping or redirecting may disable colors.
- Debug logs funnel through `rich.logging.RichHandler` and are captured when `--debug` is used.
- File numbering properly accounts for `--start-at`.
- Custom prompts override the default converter instruction entirely.

---

## Acknowledgments

Built on top of [`crawl4ai`](https://github.com/unclecode/crawl4ai) by @unclecode, leveraging its powerful browser automation and LLM filtering capabilities.

---

