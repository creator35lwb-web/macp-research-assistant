# Phase 3A — WebMCP Prototype

**MACP Research Assistant** | YSenseAI Ecosystem | GODELAI C-S-P Framework

A minimal, functional prototype of the WebMCP frontend for the MACP Research Assistant. Validates the core human-in-the-loop workflow where browser-based AI agents can discover and invoke research tools.

---

## Architecture

```
React Web UI (localhost:5173)  ──HTTP──>  FastAPI Backend (localhost:8000)
         │                                         │
    WebMCP Tools                              Python Engine
  (search_papers,                        (paper_fetcher.py,
   analyze_paper)                         llm_providers.py)
         │                                         │
  Browser Agent ←──── Tool Results ────→  .macp/ Data Files
```

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web UI | Vite + React + TypeScript | Single-page app hosting WebMCP tools |
| Backend API | FastAPI (Python) | Bridge between JS frontend and Python engine |
| Core Engine | Existing Python tools | paper_fetcher.py, llm_providers.py |

---

## Quick Start

### 1. Start the Backend

```bash
cd phase3_prototype/backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.
Docs at `http://localhost:8000/docs` (Swagger UI).

### 2. Start the Frontend

```bash
cd phase3_prototype/frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Open `http://localhost:5173` in your browser.

### 3. Use the App

1. Type a search query (e.g., "multi-agent systems") and click **Search**.
2. Browse results with titles, authors, and abstracts.
3. Click **Analyze** on any paper to run AI-powered analysis.
4. Configure your LLM provider and API key (BYOK) in the top section.

---

## WebMCP Integration

### For Chrome 146+ with Prompt API

If you're running Chrome 146+ with the Prompt API enabled, the tools are automatically registered via `navigator.modelContext.provideContext()`. Browser-based AI agents can discover:

- **`search_papers`** — Search arXiv/HuggingFace for papers
- **`analyze_paper`** — AI-powered paper analysis with BYOK

### For DevTools Testing

Even without the Prompt API, tools are exposed on `window.macpTools`:

```js
// In Chrome DevTools Console:
await window.macpTools.search_papers({ query: "LLM reasoning", limit: 5 })
await window.macpTools.analyze_paper({ paper_id: "2501.12345", provider: "gemini" })
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check + KB stats |
| POST | `/search` | Search papers (query, limit, source) |
| POST | `/analyze` | Analyze a paper (paper_id, provider, api_key) |

### Example: Search

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "multi-agent", "limit": 5, "source": "hysts"}'
```

### Example: Analyze

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"paper_id": "arxiv:2501.12345", "provider": "gemini"}'
```

---

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GEMINI_API_KEY` | For analysis | — | Google Gemini API key (free tier) |
| `ANTHROPIC_API_KEY` | For analysis | — | Anthropic Claude API key |
| `OPENAI_API_KEY` | For analysis | — | OpenAI API key |

API keys can also be provided per-request via the UI or the `/analyze` endpoint body (BYOK).

---

## Data Flow

1. **Search** hits the backend, which calls `paper_fetcher.fetch_from_hysts()`.
2. Discovered papers are saved to `.macp/research_papers.json` (MACP KB).
3. **Analyze** sends paper data to the selected LLM provider.
4. Analysis results include `_meta.bias_disclaimer` (C6 compliance).
5. All security events logged to `.macp/security.log` (C5 compliance).

---

*Part of the MACP Research Assistant | Phase 3A Prototype*
