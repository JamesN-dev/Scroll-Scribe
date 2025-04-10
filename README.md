# ScrollScribe: URL List to Cleaned Markdown Scraper

ScrollScribe is a Python tool designed to read a list of URLs from a text file, scrape the content of each URL using `crawl4ai`, and generate cleaned Markdown output suitable for ingestion into RAG (Retrieval-Augmented Generation) systems or other text-processing pipelines.

It leverages `crawl4ai`'s browser automation capabilities to fetch HTML content and then utilizes an LLM (Language Model) via `crawl4ai`'s `LLMContentFilter` to intelligently extract the main content from the HTML, excluding common boilerplate like navigation, footers, and ads, before outputting Markdown.

## Features

* Reads target URLs from a specified input text file (one URL per line, finds first URL on line).
* Uses `crawl4ai` for robust, asynchronous web scraping.
* Employs `LLMContentFilter` to intelligently parse HTML and generate clean Markdown focused on main content.
* Configurable LLM endpoint (model, API key source, base URL) via command-line arguments (defaults to OpenRouter).
* Configurable page load timeout and wait conditions.
* Saves the generated Markdown for each successfully processed URL to a separate `.md` file.
* Handles basic error checking and provides console feedback via `rich`.

## Prerequisites

* Python 3.10+ (3.12+ recommended)
* `uv` (or `pip`) Python package manager.
* An API key for your chosen LLM provider (e.g., OpenRouter, OpenAI) accessible as an environment variable.

## Installation

1.  **Clone the repository (if applicable) or place the script (`main.py` or `scroll_scribe.py`) in your project directory.**
2.  **Create and activate a virtual environment:**
    ```bash
    # Navigate to your project directory
    uv venv
    source .venv/bin/activate
    # Or: python -m venv .venv && source .venv/bin/activate
    ```
3.  **Install required libraries using `uv`:**
    ```bash
    uv add crawl4ai rich python-dotenv litellm
    ```
    *(Note: `litellm` is used internally by `LLMContentFilter` for making LLM calls).*
4.  **Run Crawl4AI Setup (Installs Browsers & Checks):**
    ```bash
    # Run this one time after activating the environment
    crawl4ai-setup
    ```
    *This command installs necessary Playwright browsers and performs environment checks.*
5.  **(Optional) Run Diagnostics:**
    ```bash
    crawl4ai-doctor
    ```
    *This checks compatibility and verifies the installation.*

## Configuration

1.  **Create a `.env` file** in the project root directory (where you run the script from).
2.  **Add your LLM API key** to the `.env` file. The script defaults to looking for `OPENROUTER_API_KEY`. If you use a different provider/key, ensure the corresponding environment variable is set and use the `--api-key-env` argument when running the script. You might also need to adjust `--model` and `--base-url`.
    ```dotenv
    # Example .env file for OpenRouter
    OPENROUTER_API_KEY="your_openrouter_api_key_here"

    # Example for OpenAI (use with --model openai/gpt-4o --api-key-env OPENAI_API_KEY --base-url "")
    # OPENAI_API_KEY="your_openai_api_key_here"
    ```

## Usage

Run the script from your project's root directory, providing the path to your URL list file as the main argument.

```bash
# General format (assuming script saved as main.py in a 'scripts' subdir)
python scripts/main.py <path_to_input_file.txt> [OPTIONS]
Arguments (from python scripts/main.py -h):usage: main.py [-h] [-o OUTPUT_DIR] [-t TIMEOUT]
               [--wait {load,domcontentloaded,networkidle}] [--model MODEL]
               [--api-key-env API_KEY_ENV] [--base-url BASE_URL]
               [--max-tokens MAX_TOKENS] [-v]
               input_file

Scrape URLs from file to cleaned Markdown files using LLMContentFilter.

positional arguments:
  input_file            Path to the text file containing URLs.

options:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory to save filtered Markdown files. (default:
                        output_llm_filtered_markdown)
  -t TIMEOUT, --timeout TIMEOUT
                        Page load timeout in ms. (default: 60000)
  --wait {load,domcontentloaded,networkidle}
                        Playwright wait_until state. (default: networkidle)
  --model MODEL         LLM model identifier for filtering. (default:
                        openrouter/google/gemini-2.0-flash-001)
  --api-key-env API_KEY_ENV
                        Environment variable name for the LLM API key. (default:
                        OPENROUTER_API_KEY)
  --base-url BASE_URL   API Base URL for LLM. (default:
                        [https://openrouter.ai/api/v1](https://openrouter.ai/api/v1))
  --max-tokens MAX_TOKENS
                        Max output tokens for the LLM filtering. (default: 4096)
  -v, --verbose         Enable verbose logging. (default: False)

Examples:Basic Usage (Defaults: Gemini Flash via OpenRouter, output to output_llm_filtered_markdown/):# Assumes perfionAPIurls.txt is in a 'data' subdirectory
# Assumes script is named main.py and is in 'scripts' subdir
python scripts/main.py data/perfionAPIurls.txt
Specify Output Directory and Longer Timeout:python scripts/main.py data/perfionAPIurls.txt -o output/perfion_docs_filtered -t 90000
Use a Different Model (e.g., Claude Sonnet via OpenRouter) & Verbose:python scripts/main.py data/perfionAPIurls.txt -o output/perfion_claude -t 90000 --model openrouter/anthropic/claude-3-sonnet-20240229 -v
OutputThe script creates the specified output directory. Inside this directory, it saves one .md file for each URL that was successfully fetched and processed by the LLMContentFilter. The filename is based on the URL path (e.g., page_001_Perfion_API.md). These files contain the cleaned Markdown content intended for RAG ingestion.NotesSpeed: This script makes an LLM call for every URL, so processing time depends heavily on the number of URLs, page complexity, network speed, and the chosen LLM's response time.API Keys: Ensure the correct API key environment variable is set in your .env file and matches the --api-key-env argument (or its default).Errors: Check the console output for warnings (e.g., skipped lines, empty filter results) or errors (e.g., fetch failures, LLM API errors).