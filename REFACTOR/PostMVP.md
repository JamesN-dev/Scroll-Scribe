🎯 Let's Stick With My Simple Plan
My "performance fix with light modularization" approach was exactly right—and it's DONE.
Core Focus (Do This Now):

- Complete CLI & UI rehaul for a modern, delightful user experience
- Add interactive config wizard for easy onboarding
- Migrate to Typer for type-safe, rich CLI help and subcommands
- Persistent, adaptive Rich progress bar and status UI
- Refactor logging and error output for clarity and polish
- Remove emojis for a professional, scriptable CLI
- Ensure config file + CLI flag override logic is robust

Estimated Time: 4-6 hours (not 8-12!)
🚀 Post-MVP: MCP Integration

After we get Phase2 working and fast, THEN we can add MCP as a separate phase:

---

## Phase 2.5: MCP Integration (Future)

### 🏗️ Directory Structure

├── app/mcp/
│ ├── server.py # MCP server for Claude/AI integration
│ ├── document_store.py # Parse markdown into searchable chunks
│ └── tools.py # MCP tools: list_sections, get_section, search_sections

---

### 🛠️ MCP Tools for Claude & AI Clients

- **list_sections()** — Show available docs/sections
- **get_section()** — Get specific content
- **search_sections()** — Semantic search
- **get_table_of_contents()** — Navigation

---

### 🧩 High-Level Plan for MCP Integration

- **Per-Folder Serving:**
  Users can serve any processed docs folder as its own MCP endpoint.
  Example:

    ```
    scribe process https://docs.site.com/ my_docs/
    scribe mcp-serve my_docs/
    ```

    Each server instance exposes only the docs in its folder, allowing multiple independent endpoints.

- **Dual Config Wizards:**

    - `scribe config` — Interactive wizard for scraping options (model, timeout, etc.)
    - `scribe mcp-init` — Wizard for MCP server setup (port, host, folder, etc.)

- **Advanced CLI Subcommands:**

    - `scribe mcp-serve <markdown_dir> [--config ...] [--make-tools]`
    - `scribe mcp-init`
    - `scribe mcp-stop` (optional)
    - `scribe mcp-status` (optional)
    - `scribe toc <markdown_dir>` — Generate TOC only (optional)

- **MCP Tools & Processing:**

    - `--make-tools` flag to preprocess markdown for MCP (TOC, search, etc.)
    - Standard server flags: `--port`, `--host`, etc.

- **Exporting MCP Server Config Snippets:**

    - After starting a server or via `scribe mcp-export-config <docs_folder>`, output a ready-to-use JSON snippet for Claude, VSCode, Cursor, etc.
    - Example snippet:
        ```json
        {
            "mcpServers": {
                "my_docs": {
                    "command": "uv",
                    "args": [
                        "--directory",
                        "/ABSOLUTE/PATH/TO/DOCS_FOLDER",
                        "run",
                        "server.py"
                    ]
                }
            }
        }
        ```
    - Optionally, provide a flag to **merge** this entry into an existing config file (never overwrite).

- **Safe Config File Merging:**
    - Always load, merge, and write back—never wipe the file.
    - Optionally, back up the config file before writing.
    - Print the snippet for manual copy-paste by default; offer `--write` or `--merge` for power users.

---

### 🧠 Example Workflow

```bash
# 1. Scrape docs (interactive or scripted)
scribe config
scribe process https://docs.example.com/ output/

# 2. Set up MCP server (interactive)
scribe mcp-init

# 3. Start MCP server for a specific docs folder
scribe mcp-serve output/ --make-tools

# 4. Export config snippet for Claude/VSCode/Cursor
scribe mcp-export-config output/ --name my_docs

# 5. (Optional) Merge snippet into existing config file
scribe mcp-export-config output/ --name my_docs --write ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

---

### 🏆 Success Criteria

- Users can scrape docs and serve them as an MCP endpoint with minimal friction.
- Both interactive and scripted workflows are supported.
- CLI is modern, discoverable, and professional.
- Per-folder serving is supported—users can run multiple servers for different doc sets.
- Exporting and merging config snippets is safe, easy, and never overwrites user data.
- New features (MCP tools, plugins, etc.) can be added without major refactoring.

---

✅ Decision: Move Forward with Simple Plan

My original simple plan is good to go. It:

- Fixes the real performance issues
- Adds unified CLI
- Doesn't over-engineer
- Sets up for future MCP integration

You can move forward with it and we'll tackle MCP integration after V2 is stable and fast.
The lesson learned: Ship the performance fixes first, add fancy features later.

---

## 🎯 MVP Goals (Restated)

- Fix duplicate fetching bug → 2x speed improvement immediately
- Add session reuse → Additional 2-3x speed boost
- Unified CLI → python -m app process https://docs.site.com/ -o output/
- Keep everything else working → Same quality, same Rich progress, same LLM filtering

### 💨 Expected Performance Gains

- Current: ~4.9 pages/min (already impressive for LLM-filtered content!)
- After V2: ~15-20 pages/min (3-4x faster)
- Why: Eliminate duplicate HTTP requests + browser session reuse

### 🎁 The Beauty of This Plan

- Small scope → Actually achievable in 4-6 hours
- Huge impact → Massive performance improvement
- Foundation ready → Sets up perfectly for future MCP integration
- No risk → Keeps all existing functionality working

---

✅ You're Ready to Go!

The plan I wrote is solid and focused. It fixes the real bottlenecks without over-engineering.
Key insight: ScrollScribe's 4.9 pages/min is already competitive when you consider each page gets AI content curation. Making it 15-20 pages/min puts it in a totally different league.
Ready to ship this performance beast! 🔥
