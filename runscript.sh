#!/bin/bash

# ScrollScribe Runner Script
# This script allows you to configure ScrollScribe arguments to scrape web content
# (specifically designed for documentation sites) and convert it into Markdown
# via LLM-based filtering. By default, ScrollScribe is set to use
# Google Gemini 2.0 Flash Exp(Free), mostly because its free. But I suggest using
# Mistral AI's Codestral 2501 for the best markdown output for the price.
# Generally will cost you $0.005-$0.01 per page using Codestral 2501.

# Suggested Free Models
# --model openrouter/google/gemini-2.0-flash-exp:free

# Suggested Paid Models(Budget Friendly)
# --model openrouter/mistralai/codestral-2501

# Customize the arguments within the CMD variable below as needed.

# --- Key Parameters for scrollscribe.py (set in CMD below) ---
#   <input_file>: Path to the text file containing URLs (required positional).
#   --model: LLM model for filtering.
#   --max-tokens: Max tokens allowed in LLM output.
#   --start-at <number>: Start processing at this index in the URL list (0-based).
#   --timeout: Page load timeout in ms.
#   --wait: Browser wait condition ('load', 'domcontentloaded', 'networkidle').
#   -o: Output directory where Markdown files will be saved.
#   -v: Enable verbose logging (INFO level) for the script.
#   -p: Provide a custom LLM prompt string.
#   --api-key-env: Name of the env var that stores your API key.
#   --base-url: Custom API base URL for the LLM provider.
# --- (No special flags for this script itself anymore) ---

# --- Define ScrollScribe Command ---
# Edit the arguments below for your desired run
uv run python -m app process https://gofastmcp.com/getting-started/welcome -o output/fastmcp_scrape \
  -v \
  --model openrouter/mistralai/codestral-2501 \
  --wait domcontentloaded \
  --timeout 60000 \
  --max-tokens 10192 \
  --api-key-env OPENROUTER_API_KEY




# --- Notes ---
# Adjust input and output paths in CMD as needed.
# Ensure your API key is set using the specified environment variable, or loaded via .env.
# To save output to a file, use shell redirection: ./runscript.sh > output.log 2>&1
