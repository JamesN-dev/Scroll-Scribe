# 🚀 ScrollScribe MVP: MCP Integration

The real MVP is making ScrollScribe immediately valuable to users by turning any documentation into Claude-accessible knowledge.

---

## MVP: MCP Integration

### 🏗️ Directory Structure

```
ScrollScribe/
├── app/
│   ├── mcp/
│   │   ├── server.py           # MCP server for Claude/AI integration  
│   │   ├── document_store.py   # Parse markdown into searchable chunks
│   │   └── tools.py            # MCP tools: list_sections, get_section, search_sections
│   └── ...
```

---

### 🎯 The MVP Value Prop

**"Turn any documentation into Claude tools in 5 minutes"**

```bash
# The magic workflow
scribe process https://docs.fastapi.com
scribe serve --mcp ./output/ --port 8000
# → Claude now has FastAPI docs as native tools
```

### 📁 Per-Folder MCP Servers

Each documentation set gets its own independent MCP server:

```bash
# Multiple servers for different doc sets
Terminal 1: scribe serve --mcp ./fastapi-docs/ --port 8000
Terminal 2: scribe serve --mcp ./react-docs/ --port 8001  
Terminal 3: scribe serve --mcp ./company-docs/ --port 8002
```

**Benefits:**
- **Isolated knowledge bases** - each doc set is separate
- **Multiple Claude integrations** - different tools for different domains
- **Easy management** - start/stop servers independently

### 🔧 Claude Configuration

Each server generates its own Claude config entry:

```json
{
  "mcpServers": {
    "fastapi-docs": {
      "command": "scribe", 
      "args": ["serve", "--mcp", "./fastapi-docs/", "--port", "8000"]
    },
    "react-docs": {
      "command": "scribe",
      "args": ["serve", "--mcp", "./react-docs/", "--port", "8001"] 
    }
  }
}
```

### 🛠️ Core MCP Tools for Claude & AI Clients

- **list_sections()** — Show available docs/sections
- **get_section()** — Get specific content
- **search_sections()** — Semantic search
- **get_table_of_contents()** — Navigation

## 🚀 Implementation Strategy

### **Step 1: Fork fast-markdown-mcp**
- Copy existing working MCP server into ScrollScribe codebase
- Modify to work with ScrollScribe's output format  
- Ensure compatibility with processed markdown files

### **Step 2: Integration** 
- Add `scribe serve --mcp <folder_path>` command to CLI
- Support `--port` flag for multiple concurrent servers
- Auto-detect markdown files in specified folder
- Start MCP server serving that specific documentation set

### **Step 3: Claude Configuration**
- Generate Claude desktop config snippets
- Provide easy setup instructions
- Test end-to-end workflow

---

### 🧩 Advanced Features (Phase 2+)

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
# 1. Process different documentation sets
scribe process https://docs.fastapi.com ./fastapi-docs/
scribe process https://docs.react.dev ./react-docs/

# 2. Start separate MCP servers
scribe serve --mcp ./fastapi-docs/ --port 8000
scribe serve --mcp ./react-docs/ --port 8001

# 3. Each server provides its own Claude config snippet
# FastAPI server outputs:
# "Add this to your Claude config: ..."

# 4. Claude now has separate tool sets:
# - FastAPI tools (authentication, routing, etc.)
# - React tools (hooks, components, etc.)
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

### 🏆 MVP Success Criteria

- Users can process docs and serve them as an MCP endpoint with minimal friction
- `scribe process` → `scribe serve --mcp` → Claude integration works end-to-end  
- File-based architecture proves the concept before building postgres version
- Clear path to expand to code repositories and other content types

---

## 🔄 Migration Path: Post-MVP Expansion  

Once the file-based MCP proves valuable:

### **Phase 3: Postgres + Vector Search** 
- Migrate to postgres + pgvector for advanced queries
- Add semantic search capabilities  
- Maintain same MCP interface, upgraded backend

### **Phase 4: Multi-Content Support**
- Code repositories (GitHub/GitLab integration)
- PDFs and research papers
- Forum posts and community content

**Foundation:** Prove MCP value with docs → Expand content types → Scale with enterprise storage

---
