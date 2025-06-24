<p align="center">
  <img src="https://40gwsazwi1.ufs.sh/f/GNQKLEu6hrNnLVZuuzM7lFAhGirR1v0IKaEQxCWZNeDoBMOj" width="120" height="120" alt="ScrollScribe Logo">
</p>

<h1 align="center">ScrollScribe</h1>

<p align="center">
  <strong>Convert any documentation website into clean, searchable Markdown files.</strong>
</p>

<p align="center">
  Turn weeks of documentation research into hours of productive development with a powerful Python CLI.
</p>

<p align="center">
  <a href="https://github.com/unclecode/crawl4ai">
    <img src="https://img.shields.io/badge/Powered%20by-Crawl4AI-blue?style=for-the-badge&logo=python&logoColor=white" alt="Powered by Crawl4AI">
  </a>
  <a href="https://github.com/tiangolo/typer">
    <img src="https://img.shields.io/badge/CLI-Typer-orange?style=for-the-badge&logo=python&logoColor=white" alt="Built with Typer">
  </a>
  <a href="https://github.com/JamesN-dev/Scroll-Scribe/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
  </a>
</p>

<p align="center">
  <a href="#what-scrollscribe-does">Features</a> |
  <a href="#installation">Installation</a> |
  <a href="#quick-start">Quick Start</a> |
  <a href="#processing-modes">Processing Modes</a> |
  <a href="#commands">Commands</a> |
  <a href="#common-examples">Examples</a> |
  <a href="#troubleshooting">FAQ</a>
</p>

---

With ScrollScribe, you can build your own docs library in minutes. Automatically discover all pages on a documentation site and convert them to clean Markdown files—perfect for AI agents, custom search systems, or offline documentation.

---

_Supports both fast and AI-powered (LLM) conversion modes for the best results._

---

## ⚡ Two Processing Modes

### Fast Mode (`--fast`)

- Quickly converts large documentation sites—great for bulk extraction, drafts, or when you don’t need perfect formatting. No API key required.

### AI Mode (default, or `--no-fast`)

- Uses LLMs for the highest quality Markdown output—ideal for publishing, feeding into websites, or when you want perfectly structured docs. Requires an API key and takes longer per page.

---

## What ScrollScribe Does

1. **Discovers** all documentation pages from a starting URL
2. **Downloads** the content from each page
3. **Converts** HTML to clean Markdown using AI or fast processing
4. **Saves** each page as a separate `.md` file

**Example:** Point it at `https://docs.fastapi.com/` and get 200+ clean Markdown files covering the entire FastAPI documentation.

## Installation

```bash
git clone https://github.com/your-username/scrollscribe
cd scrollscribe
uv sync  # or pip install -r requirements.txt
```

---

## 🛠️ Building & Publishing

This project uses [Hatch](https://hatch.pypa.io/) for building and publishing. Contributors should have it installed.

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

Extract just the URLs from a site (useful for manual curation):

```bash
# Get list of all documentation URLs
scribe discover https://docs.fastapi.com/ -o urls.txt
```

**Why use discover separately?**

- **Manual curation**: Edit `urls.txt` to remove pages you don't want
- **Planning**: See how many pages before processing
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
│   ├── api-reference-users.md  # API reference pages
│   ├── ...                     # Other pages
├── javascript-docs/
│   ├── index.md
│   └── ...
└── go-docs/
    ├── index.md
    └── ...
```

Each file contains:

- Clean Markdown formatting
- Preserved code blocks and syntax highlighting
- Working internal links (converted to relative paths)
- Original page title as the filename

This flexible structure makes it easy to build your own docs library, organize by project or language, and prepare for **future features like serving docs with an MCP server**.

## Common Examples

### Popular Documentation Sites

```bash
# Python libraries
scribe process https://docs.pydantic.dev/ -o pydantic-docs/
scribe process https://docs.sqlalchemy.org/ -o sqlalchemy-docs/

# Web frameworks
scribe process https://docs.djangoproject.com/ -o django-docs/
scribe process https://nextjs.org/docs -o nextjs-docs/

# Cloud services
scribe process https://docs.aws.amazon.com/s3/ -o aws-s3-docs/
scribe process https://cloud.google.com/docs/apis -o gcp-docs/

# Dev tools
scribe process https://docs.docker.com/ -o docker-docs/
scribe process https://kubernetes.io/docs/ -o k8s-docs/
```

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

## Performance Tips

- **Use `--fast` for large sites** (1000+ pages) to avoid API costs
- **Use AI mode for quality** when you need clean, well-formatted output
- **Process in chunks** using `--start-at` for very large sites
- **Set longer timeouts** for slow or heavy documentation sites

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

## License

MIT License - use ScrollScribe for any purpose, commercial or personal.

---

**ScrollScribe** - Turn any documentation site into clean, searchable Markdown files.
