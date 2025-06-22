# 🚀 ScrollScribe V2 - AI-Powered Documentation Scraper

**Transform any documentation website into clean, filtered Markdown files using advanced LLM processing.**

ScrollScribe V2 is a high-performance, modular CLI tool that discovers URLs from documentation websites and converts them into clean, well-structured Markdown files using AI-powered content filtering. Unlike simple web scrapers, ScrollScribe uses Large Language Models to intelligently extract and format only the relevant documentation content.

## ✨ What's New in V2

### 🚀 Performance Improvements

- **2x Speed Boost**: Fixed duplicate fetching bug - no more redundant URL requests
- **Session Reuse**: _(Temporarily disabled due to a bug in crawl4ai; will be restored when upstream is fixed)_
- **Smart Retries**: Automatic retry handling with exponential backoff for rate limits
- **Memory Management**: Adaptive dispatcher prevents out-of-memory issues

### 🎯 New CLI Interface

- **Modular Commands**: Separate `discover`, `scrape`, and unified `process` commands
- **Better Error Handling**: Improved error messages and graceful failure handling
- **Flexible Usage**: Run discovery and scraping separately or as a unified pipeline

### 🏗️ Code Quality

- **Modular Architecture**: Clean separation of concerns across multiple files
- **Type Safety**: Full type annotations throughout the codebase
- **Robust Exception Handling**: Custom exception hierarchy with retry logic

---

> **Note:**
> Browser session reuse and Playwright-based browser management are temporarily disabled due to a bug in the crawl4ai dependency. These features will be restored as soon as the upstream fix is merged.

## 🎯 Key Features

- **🤖 AI-Powered Filtering**: Uses advanced LLMs (Mistral Codestral recommended) to extract only relevant documentation content
- **🔗 Smart URL Discovery**: Automatically finds and follows internal documentation links
- **📄 Clean Markdown Output**: Converts HTML to well-structured Markdown with proper formatting
- **⚡ High Performance**: Batch processing with intelligent rate limiting
- **🔄 Retry Logic**: Automatic handling of rate limits and network errors
- **📊 Rich Progress Display**: Real-time progress bars with ETA and processing rates
- **🎨 Beautiful Console Output**: Rich terminal interface with colored status messages

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ScrollScribe

# Install dependencies (using uv - recommended)
uv sync

# Or with pip
pip install -r requirements.txt
```

### Set up your API key

Create a `.env` file in the project root:

```bash
# .env
OPENROUTER_API_KEY="your-openrouter-api-key-here"
```

### Basic Usage

```bash
# Discover URLs from a documentation site
python -m app discover https://docs.example.com/ -o urls.txt

# Convert URLs to markdown using AI filtering
python -m app scrape urls.txt -o output/

# Unified pipeline (discover + scrape in one command)
python -m app process https://docs.example.com/ -o output/
```

## 📋 Command Reference

### `discover` - Extract URLs from documentation sites

```bash
python -m app discover <start_url> -o <output_file> [options]

# Example
python -m app discover https://docs.crawl4ai.com/ -o crawl4ai_urls.txt -v
```

**Options:**

- `-o, --output-file`: File to save discovered URLs (required)
- `-v, --verbose`: Enable verbose logging

### `scrape` - Convert URLs to filtered markdown

```bash
python -m app scrape <input_file> -o <output_dir> [options]

# Example
python -m app scrape urls.txt -o output/ --model openrouter/mistralai/codestral-2501 -v
```

**Options:**

- `--start-at N`: Start processing from URL index N (0-based)
- `-o, --output-dir`: Output directory for markdown files (required)
- `--fast`: Enable fast HTML→Markdown mode (50-200 docs/min, no LLM filtering)
- `--model`: LLM model for filtering (default: gemini-2.0-flash-exp:free)
- `--prompt`: Custom LLM filtering prompt
- `--timeout`: Page timeout in milliseconds (default: 60000)
- `--wait`: Page load condition (default: networkidle)
- `--api-key-env`: Environment variable for API key (default: OPENROUTER_API_KEY)
- `--base-url`: API base URL (default: https://openrouter.ai/api/v1)
- `--max-tokens`: Max LLM output tokens (default: 8192)
- `-v, --verbose`: Enable verbose logging

### `process` - Unified pipeline (discover + scrape)

```bash
python -m app process <start_url> -o <output_dir> [options]

# Example
python -m app process https://docs.example.com/ -o output/ --model openrouter/mistralai/codestral-2501
```

Accepts all the same options as `scrape` command.

## 🎨 Recommended Models

### 🆓 Free Models

- `openrouter/google/gemini-2.0-flash-exp:free` (default)
- `openrouter/meta-llama/llama-3.2-1b-instruct:free`

### 💰 Premium Models (Better Quality)

- `openrouter/mistralai/codestral-2501` ⭐ **Recommended for best markdown output**
- `openrouter/anthropic/claude-3-haiku`

**Cost**: Premium models typically cost $0.005-$0.01 per page using Codestral 2501.

## 📊 Performance Comparison

| Version | Pages/Min | Duplicate Fetching | Session Reuse | Error Handling |
| ------- | --------- | ------------------ | ------------- | -------------- |
| V1      | ~4.9      | ❌ Yes             | ❌ No         | ⚠️ Manual      |
| V2      | ~9.8+     | ✅ Fixed           | ✅ Yes        | ✅ Automatic   |

## ⚡ Fast Mode (NEW!)

ScrollScribe now offers a blazing-fast HTML→Markdown conversion mode that bypasses LLM processing entirely:

```bash
# Fast mode examples
python -m app scrape urls.txt -o output/ --fast
python -m app process https://docs.example.com/ -o output/ --fast
```

### Fast Mode Benefits

- **🚀 Speed**: 50-200 docs/minute (5-20x faster than LLM mode)
- **💰 Cost**: No API costs - completely free to run
- **🔋 Efficiency**: Uses crawl4ai's built-in markdown generation with smart content filtering
- **🎯 Quality**: PruningContentFilter removes navigation, footers, and low-value content

### When to Use Fast Mode

- **Large documentation sites** (hundreds or thousands of pages)
- **Budget-conscious projects** (no LLM API costs)
- **Quick content extraction** where perfect formatting isn't critical
- **Testing and development** workflows

### LLM vs Fast Mode Comparison

| Feature | LLM Mode | Fast Mode |
|---------|----------|-----------|
| Speed | ~10 docs/min | 50-200 docs/min |
| Cost | $0.005-$0.01/page | Free |
| Quality | Excellent | Good |
| API Required | Yes | No |
| Use Case | High-quality docs | Large-scale extraction |

## 🛠️ Advanced Usage

### Custom LLM Prompts

```bash
python -m app scrape urls.txt -o output/ --prompt "Extract only API documentation and code examples. Format as markdown with clear headings."
```

### Processing Large Sites

```bash
# Start from a specific URL index (useful for resuming)
python -m app scrape urls.txt -o output/ --start-at 50

# Use longer timeout for slow sites
python -m app scrape urls.txt -o output/ --timeout 120000
```

### Different API Providers

```bash
# Use different API key environment variable
python -m app scrape urls.txt -o output/ --api-key-env MISTRAL_API_KEY --base-url https://api.mistral.ai/v1
```

## 📁 Project Structure

```
ScrollScribe/
├── app/
│   ├── __main__.py          # Package entry point
│   ├── cli.py               # Command-line interface
│   ├── discovery.py         # URL discovery logic
│   ├── processing.py        # Core processing with performance fixes
│   ├── config.py            # Configuration factories
│   └── utils/               # Utilities (retry, exceptions)
├── archive/                 # Original V1 files
├── test_performance.py      # Performance testing script
└── README.md               # This file
```

## 🔧 Troubleshooting

### Common Issues

**API Key Not Found**

```bash
[ERROR] API key env var 'OPENROUTER_API_KEY' not found!
```

Solution: Create `.env` file with your API key or set the environment variable.

**Rate Limiting**

```bash
Rate limit error: Provider returned error 429
```

Solution: ScrollScribe automatically retries with exponential backoff. For persistent issues, try a different model or add your own API key to accumulate rate limits.

**Network Errors**

```bash
Failed on navigating: net::ERR_ABORTED
```

Solution: Some sites block automated requests. Try increasing timeout or using different wait conditions.

### Debug Mode

Enable verbose logging for detailed information:

```bash
python -m app scrape urls.txt -o output/ -v
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [crawl4ai](https://github.com/unclecode/crawl4ai) for web crawling
- Uses [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- LLM integration via [LiteLLM](https://github.com/BerriAI/litellm)

---

**ScrollScribe V2** - Transforming documentation, one page at a time. 🚀
