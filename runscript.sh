#!/bin/bash

# ScrollScribe Runner Script
# This script uses ScrollScribe to scrape web content (e.g., Django docs) and convert it into Markdown via LLM-based filtering.
# Customize the arguments as needed for different content sources or models.

# --- Key Parameters ---
#   - `--model`: LLM model for filtering. If omitted, defaults to gemini-2.0-flash-exp (OpenRouter free tier).
#   - `--max-tokens`: Max tokens allowed in LLM output (default: 2048, or overridden by CLI).
#   - `--timeout`: Page load timeout in ms (default: 30000).
#   - `--wait`: Browser wait condition before scraping begins (e.g. 'networkidle').
#   - `-o`: Output directory where Markdown files will be saved.
#   - `-v`: Enable verbose logging.
#   - `--api-key-env`: Name of the env var that stores your API key (e.g. OPENROUTER_API_KEY).
#   - `--debug`: Triggers internal LLM tracing and logs model usage. Outputs log file if enabled.

# --- Define ScrollScribe Command ---
CMD="PYTHON_FORCE_COLOR=1 uv run app/scrollscribe.py \
  data/django_urls_example.txt \
  --start-at 56 \
  -o output/django_markdown \
  -v \
  --model openrouter/google/gemini-2.0-flash-exp:free \
  --max-tokens 8192 \
  --timeout 60000 \
  --wait networkidle \
  --api-key-env OPENROUTER_API_KEY"

# --- Optional: Enable LLM Debug Log Output ---
if [[ "$*" == *"--debug"* ]]; then
  LOG_PATH="output/llm_debug.log"
echo -e "\033[1;35m━━━━━━━━━━━━━━━━━━━━🧠 LLM DEBUG MODE: LOGGING TO $LOG_PATH ━━━━━━━━━━━━━━━━━━━━\033[0m"
  mkdir -p output
  CMD="$CMD 2>&1 | tee $LOG_PATH"
fi

# --- Run ScrollScribe ---
eval "$CMD"

# --- Notes ---
# Adjust input and output paths as needed.
# Ensure that your API key is set using the specified environment variable, or loaded via .env.