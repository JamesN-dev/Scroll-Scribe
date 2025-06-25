<p align="center">
  <img src="https://40gwsazwi1.ufs.sh/f/GNQKLEu6hrNnLVZuuzM7lFAhGirR1v0IKaEQxCWZNeDoBMOj" width="120" height="120" alt="ScrollScribe Logo">
</p>

<h1 align="center">ScrollScribe</h1>

<p align="center">
  <strong>CLI toolkit for ML engineers, developers, data scientists, and researchers.</strong>
</p>

<p align="center">
  Extract docs to Markdown • Generate rich CSV/JSON metadata • Prepare data for vector databases
</p>

<p align="center">
  <a href="https://github.com/unclecode/crawl4ai">
    <img src="https://img.shields.io/badge/Powered%20by-Crawl4AI-blue?style=for-the-badge&logo=python&logoColor=white" alt="Powered by Crawl4AI">
  </a>
  <a href="https://github.com/tiangolo/typer">
    <img src="https://img.shields.io/badge/CLI-Typer-orange?style=for-the-badge&logo=python&logoColor=white" alt="Built with Typer">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  </a>
  <a href="https://github.com/JamesN-dev/Scroll-Scribe/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
  </a>
</p>

<p align="center">
  <a href="#the-toolkit">Toolkit</a> |
  <a href="#what-scrollscribe-does">Features</a> |
  <a href="#installation">Installation</a> |
  <a href="#quick-start">Quick Start</a> |
  <a href="#processing-modes">Processing Modes</a> |
  <a href="#commands">Commands</a> |
  <a href="#troubleshooting">FAQ</a>
</p>

---

With ScrollScribe, you can build your own docs library in minutes. Automatically discover all pages on a documentation site and convert them to clean Markdown files—perfect for agentic workflows, custom search systems, or offline documentation.

---

## The Toolkit

### `discover` - URL Extraction + Metadata

Extract URLs with rich metadata (keywords, depth, timestamps) exported as TXT, CSV, or JSON.

### `scrape` - Page Processing

Process single pages or URL lists. Choose fast mode (500+ pages/min) or LLM mode (publication-ready Markdown).

### `process` - Unified Pipeline

Point and go: discover + scrape in one command. Fast for bulk extraction, LLM for high-quality output.

---

## ⚡ Processing Modes

### Fast Mode (`--fast`)

- Quickly converts large documentation sites—great for bulk extraction, drafts, or when you don’t need perfect formatting. No API key required.

### AI Mode (default, or `--no-fast`)

- Uses LLMs for the highest quality Markdown output—ideal for publishing, feeding into websites, or when you want perfectly structured docs. Requires an API key and takes longer per page.

---

## What ScrollScribe Does

1. **Discovers** URLs from documentation sites with rich metadata (keywords, depth, timestamps) - export as TXT, CSV, or JSON
2. **Processes** single pages or entire URL lists - choose fast mode (500+ pages/min) or LLM mode for publication-quality output
3. **Converts** HTML to clean Markdown with preserved formatting, code blocks, and working links
4. **Outputs** structured data perfect for AI agents, vector databases, or offline documentation

**Examples:**

- `scribe discover docs.fastapi.com -o urls.json` → Get 200+ URLs with metadata for analysis
- `scribe process docs.fastapi.com -o fastapi-docs/` → Get 200+ clean Markdown files
- `scribe scrape single-page.html -o output/` → Process just one page

---

## Installation

```bash
git clone https://github.com/your-username/scrollscribe
cd scrollscribe
uv sync  # or pip install -r requirements.txt
```

---

## Quick Start

### Basic Usage

```bash
# Convert entire documentation site to Markdown
scribe process https://docs.fastapi.com/ -o fastapi-docs/

# That's it! All pages are now in the fastapi-docs/ folder
```

### Set up API Key (Recommended)

For highest quality output, add your API key:

```bash
# Create .env file with your API key
echo "OPENROUTER_API_KEY=your-key-here" > .env

# Now uses best model by default (Codestral 2501)
scribe process https://docs.fastapi.com/ -o fastapi-docs/
```

## Processing Modes

ScrollScribe offers two processing modes depending on your needs:

| Feature           | **Fast Mode**                 | **AI Mode**                     |
| ----------------- | ----------------------------- | ------------------------------- |
| **Speed**         | 50-200 pages/minute           | 10-15 pages/minute              |
| **Cost**          | Free                          | ~$0.005 per page (Codestral)    |
| **Quality**       | Good - removes navigation/ads | Excellent - AI-filtered content |
| **API Key**       | Not required                  | Required                        |
| **Best For**      | Large sites, quick extraction | High-quality documentation      |
| **Default Model** | N/A                           | Codestral 2501                  |

### Fast Mode (No API Key Needed)

```bash
# Fast processing - no API key required
scribe process https://docs.fastapi.com/ -o fastapi-docs/ --fast
```

**Good for:**

- Large documentation sites (1000+ pages)
- Quick content extraction
- When you don't want to pay for API calls

### AI Mode (Default with API Key)

```bash
# Uses Codestral 2501 by default - best quality
scribe process https://docs.fastapi.com/ -o fastapi-docs/
```

**Good for:**

- High-quality documentation extraction (default mode)
- When clean formatting is important
- Feeding into other AI tools

## Commands

ScrollScribe has three main commands:

### `process` - Complete Pipeline (Most Common)

Convert an entire documentation site in one command:

```bash
# Discover all pages and convert them to Markdown
scribe process https://docs.fastapi.com/ -o fastapi-docs/
```

### `discover` - Find All Documentation Pages

Extract URLs from a site with optional metadata (useful for manual curation):

```bash
# Get simple list of URLs
scribe discover https://docs.fastapi.com/ -o urls.txt

# Get rich metadata with depth, keywords, and timestamps
scribe discover https://docs.fastapi.com/ -o urls.json

# Get CSV format for spreadsheet analysis
scribe discover https://docs.fastapi.com/ -o urls.csv
```

**Output Formats:**

- **`.txt`** - Simple URL list (default)
- **`.csv`** - Rich metadata in spreadsheet format with columns for depth, keywords, timestamps, and filenames
- **`.json`** - Same rich metadata as structured objects for programming

**JSON metadata example:**

```json
{
  "url": "https://docs.fastapi.com/tutorial/first-steps/",
  "path": "/tutorial/first-steps/",
  "depth": 2,
  "keywords": ["tutorial", "first", "steps"],
  "filename_part": "tutorial/first-steps",
  "discovered_at": "2025-06-24T19:43:27.627987"
}
```

**Why use discover separately?**

- **Manual curation**: Edit output files to remove pages you don't want
- **Planning**: See how many pages and site structure before processing
- **Analysis**: Use JSON metadata to understand site hierarchy and content types
- **Selective processing**: Only download the pages you actually need

### `scrape` - Convert to Markdown

Process URLs or a single page:

```bash
# Process a curated list of URLs
scribe scrape urls.txt -o fastapi-docs/

# Process a single page
scribe scrape https://docs.fastapi.com/tutorial/first-steps/ -o output/
```

**Smart input detection**: `scrape` automatically detects if you're giving it:

- A `.txt` file with URLs (one per line)
- A single webpage URL (`http://` or `https://`)

## API Keys & Models

**Default Model**: `openrouter/mistralai/codestral-2501` ⭐ (Best quality)

### Alternative Models

- `openrouter/google/gemini-2.0-flash-exp:free` (Free tier)
- `openrouter/anthropic/claude-3-haiku` (Fast premium)

### Setting API Key

```bash
# Setup: Add API keys to .env file
echo "OPENROUTER_API_KEY=your-openrouter-key" >> .env
echo "ANTHROPIC_API_KEY=your-anthropic-key" >> .env
echo "MISTRAL_API_KEY=your-mistral-key" >> .env

# Use default API key (OPENROUTER_API_KEY)
scribe process https://docs.example.com/ -o output/

# Use a different API key variable
scribe process https://docs.example.com/ -o output/ --api-key-env ANTHROPIC_API_KEY
```

### Changing Models

```bash
# Use a different model with its corresponding API key
scribe process https://docs.example.com/ -o output/ \
  --model openrouter/anthropic/claude-3-haiku \
  --api-key-env ANTHROPIC_API_KEY

# Use free model (still needs OpenRouter key)
scribe process https://docs.example.com/ -o output/ \
  --model openrouter/google/gemini-2.0-flash-exp:free
```

Get a free API key at [OpenRouter](https://openrouter.ai/).

## Workflow Examples

### Complete Workflow (Most Common)

```bash
# One command to rule them all
scribe process https://docs.fastapi.com/ -o fastapi-docs/
```

### Curated Workflow (Manual Selection)

```bash
# Step 1: Discover all pages
scribe discover https://docs.fastapi.com/ -o urls.txt

# Step 2: Edit urls.txt - remove pages you don't want
# Step 3: Process only the pages you kept
scribe scrape urls.txt -o fastapi-docs/
```

### Single Page

```bash
# Process just one specific page
scribe scrape https://docs.fastapi.com/tutorial/first-steps/ -o output/
```

### For Developers

- **Offline Documentation**: Work with docs without internet
- **AI Tools**: Feed clean docs into Claude, ChatGPT, or local AI
- **Documentation Search**: Build custom search for your team
- **Backup**: Archive documentation that might change or disappear

### For Teams

- **Internal Knowledge Base**: Convert internal wikis to searchable Markdown
- **Compliance**: Archive API documentation for regulatory requirements
- **Training Data**: Clean documentation for training custom models

### For Researchers

- **Literature Review**: Convert technical documentation for analysis
- **Comparative Studies**: Analyze documentation across different tools
- **Academic Research**: Study how projects document their APIs

## Advanced Usage

### Separate Discovery and Processing

```bash
# Step 1: Discover all URLs (fast)
scribe discover https://docs.fastapi.com/ -o urls.txt

# Step 2: Process URLs to Markdown
scribe scrape urls.txt -o fastapi-docs/
```

### Resume Processing

```bash
# Resume from the 50th page or URL #50 if processing was interrupted
scribe scrape urls.txt -o output/ --start-at 50
```

### Custom Settings

```bash
# Use different model with custom timeout
scribe process https://docs.example.com/ -o output/ \
  --model openrouter/anthropic/claude-3-haiku \
  --timeout 120000 \
  --verbose

# Use different API key variable
scribe process https://docs.example.com/ -o output/ \
  --api-key-env ANTHROPIC_API_KEY

# Combine custom model and API key variable
scribe process https://docs.example.com/ -o output/ \
  --model openrouter/mistralai/codestral-2501 \
  --api-key-env OPENROUTER_API_KEY \
  --verbose
```

## Output Structure

ScrollScribe saves one Markdown file per documentation page in the output folder you specify.
You choose the folder name—organize by language, project, or however you like.

```bash
scribe process https://docs.python.org/3/ -o python-docs/
scribe process https://developer.mozilla.org/en-US/docs/Web/JavaScript -o javascript-docs/
```

```
output/
├── python-docs/
│   ├── index.md                # Homepage
│   ├── getting-started.md      # Getting started guide
│   ├── ...                     # Other pages
├── javascript-docs/
    ├── index.md
    └── ...

```

Each file contains:

- Clean Markdown formatting
- Preserved code blocks and syntax highlighting
- Working internal links (converted to relative paths)
- Original page title as the filename

This flexible structure makes it easy to build your own docs library, organize by project or language, and prepare for **future features like serving docs with an MCP server**.

### Large Sites (Use Fast Mode)

```bash
# Large documentation sites - use fast mode for speed
scribe process https://docs.microsoft.com/en-us/azure/ -o azure-docs/ --fast
scribe process https://developer.mozilla.org/en-US/docs/ -o mdn-docs/ --fast
```

## Troubleshooting

### "API key not found"

Create a `.env` file with your OpenRouter API key:

```bash
echo "OPENROUTER_API_KEY=your-key-here" > .env
```

### "Rate limit error"

ScrollScribe automatically retries with backoff. For persistent issues:

- Try the free models first
- Use `--fast` mode to avoid API calls entirely

### "Some pages failed"

Some sites block automated access. ScrollScribe will:

- Show which URLs failed
- Continue processing other pages
- Let you retry failed URLs later

### Site-specific issues

```bash
# Increase timeout for slow sites
scribe process https://slow-site.com/ -o output/ --timeout 120000

# Use verbose mode to see what's happening
scribe process https://site.com/ -o output/ --verbose
```

## What's Different About ScrollScribe

Unlike simple web scrapers, ScrollScribe:

- **Understands documentation structure** - follows internal links intelligently
- **Cleans content** - removes navigation, ads, and irrelevant elements
- **Preserves formatting** - maintains code blocks, headers, and structure
- **Handles modern sites** - works with JavaScript-heavy documentation
- **Scales efficiently** - processes hundreds of pages reliably

## Contributing

Found a bug or want to add a feature?

1. Open an issue describing the problem
2. Fork the repository
3. Make your changes
4. Submit a pull request

### Building & Publishing

This project uses [Hatch](https://hatch.pypa.io/) for building and publishing. Contributors should have it installed.

## License

MIT License - use ScrollScribe for any purpose, commercial or personal.

---

**ScrollScribe** - Turn any documentation site into clean Markdown files or structured metadata for AI processing.
