# ScrollScribeAI :scroll: Turn Any Documentation Site into Searchable Markdown Files

**Convert any documentation website into clean, searchable Markdown files.**

ScrollScribe automatically discovers all pages on a documentation site and converts them to clean Markdown files. Perfect for creating offline documentation, feeding docs into AI tools, or building your own documentation search systems.

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

| Feature | **Fast Mode** | **AI Mode** |
|---------|---------------|-------------|
| **Speed** | 50-200 pages/minute | 10-15 pages/minute |
| **Cost** | Free | ~$0.005 per page (Codestral) |
| **Quality** | Good - removes navigation/ads | Excellent - AI-filtered content |
| **API Key** | Not required | Required |
| **Best For** | Large sites, quick extraction | High-quality documentation |
| **Default Model** | N/A | Codestral 2501 |

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
scribe process https://docs.example.com/ -o output/ --api-key ANTHROPIC_API_KEY
```

### Changing Models
```bash
# Use a different model with its corresponding API key
scribe process https://docs.example.com/ -o output/ \
  --model openrouter/anthropic/claude-3-haiku \
  --api-key ANTHROPIC_API_KEY

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
# Resume from URL #50 if processing was interrupted
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
  --api-key ANTHROPIC_API_KEY

# Combine custom model and API key variable
scribe process https://docs.example.com/ -o output/ \
  --model openrouter/mistralai/codestral-2501 \
  --api-key OPENROUTER_API_KEY \
  --verbose
```

## Output Structure

ScrollScribe creates one Markdown file per documentation page:

```
output/
├── index.md                    # Homepage
├── getting-started.md          # Getting started guide  
├── api-reference-users.md      # API reference pages
├── tutorial-first-steps.md     # Tutorial sections
└── ...                         # One file per page
```

Each file contains:
- Clean Markdown formatting
- Preserved code blocks and syntax highlighting
- Working internal links (converted to relative paths)
- Original page title as the filename

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