# Phase 3A Prototype Specification

**Date:** February 19, 2026  
**Author:** L (Godel), CTO  
**Audience:** RNA (Claude Code)  
**Status:** Final — Handoff for Implementation  

---

## 1. Objective

Build a minimal, functional prototype of the **WebMCP frontend** for the MACP Research Assistant. This prototype will validate the core human-in-the-loop workflow and provide a foundation for the full Phase 3B implementation.

**Success Criteria:**
1. A user can load a simple web page in a browser.
2. An AI agent (e.g., a browser extension) can detect and call two specific tools: `search_papers` and `analyze_paper`.
3. The web page executes these tools using our existing Python engine and displays the results.
4. The entire interaction is logged to our MACP data files (`.macp/`).

## 2. Technical Architecture

This prototype will consist of three main components:

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **1. Web UI** | **Vite + React + TypeScript** | A simple, single-page application to host the WebMCP tools. |
| **2. Backend API** | **FastAPI (Python)** | A local server that acts as a bridge between the JavaScript UI and our existing Python CLI engine. |
| **3. Core Engine** | **Existing Python Tools** | The `paper_fetcher.py` and `llm_providers.py` modules we have already built. |

### Architectural Diagram

```
+---------------------+      (HTTP Request)     +--------------------+
|   React Web UI      | ----------------------> |   FastAPI Backend  |
| (localhost:5173)    | <---------------------- |  (localhost:8000)  |
|                     |      (JSON Response)    |                    |
|  - index.html       |                         |  - main.py         |
|  - App.tsx          |                         |                    |
|  - webmcp.js        |                         +----------+---------+
+----------+----------+                                    |
           |                                             (Function Call)
(WebMCP API Call)                                          |
           |                                             v
+----------+----------+                         +----------+---------+
| Browser (Chrome 146+)|                         |  MACP Core Engine  |
| `navigator.model..` |                         | (tools/*.py)       |
+---------------------+                         +--------------------+
```

## 3. Implementation Steps for Claude Code

### Step 1: Project Scaffolding

Create a new directory `phase3_prototype/` at the root of the `macp-research-assistant` repository.

```
macp-research-assistant/
├── phase3_prototype/
│   ├── frontend/  (Vite + React + TS)
│   └── backend/   (FastAPI)
└── ... (existing files)
```

- **Frontend:** Use `npm create vite@latest frontend -- --template react-ts`.
- **Backend:** Create a simple `main.py` file.

### Step 2: Backend API (FastAPI)

In `phase3_prototype/backend/main.py`, create two API endpoints that wrap our existing Python functions.

**Endpoint 1: `POST /search`**
- **Input:** `{ "query": "string", "limit": "int" }`
- **Action:** Calls `paper_fetcher.search_papers_by_query()`.
- **Output:** Returns the list of paper objects as JSON.

**Endpoint 2: `POST /analyze`**
- **Input:** `{ "paper_id": "string", "provider": "string", "api_key": "string" }`
- **Action:** Calls `llm_providers.analyze_paper()`.
- **Output:** Returns the analysis result object as JSON.

### Step 3: Web UI (React)

In `phase3_prototype/frontend/`, create a simple UI with:

- A text input for a search query.
- A "Search" button.
- A display area for search results.
- For each result, an "Analyze" button.
- A display area for the analysis result.

### Step 4: WebMCP Integration

Create a new file `phase3_prototype/frontend/src/webmcp.js`. In this file, use the `window.navigator.modelContext.provideContext` API to register our two tools.

**Tool 1: `search_papers`**
- **`name`**: `search_papers`
- **`description`**: "Searches for research papers on arXiv and Hugging Face."
- **`inputSchema`**: Matches the `/search` endpoint.
- **`execute` function**: This JavaScript function will:
    1. Make a `fetch` call to `http://localhost:8000/search`.
    2. Receive the JSON response.
    3. Update the React UI state with the results.
    4. Return the structured result to the agent.

**Tool 2: `analyze_paper`**
- **`name`**: `analyze_paper`
- **`description`**: "Analyzes a given research paper using an AI model."
- **`inputSchema`**: Matches the `/analyze` endpoint.
- **`execute` function**: This JavaScript function will:
    1. Make a `fetch` call to `http://localhost:8000/analyze`.
    2. Receive the JSON response.
    3. Update the React UI state with the analysis.
    4. Return the structured result to the agent.

### Step 5: Documentation

Create a `README.md` inside `phase3_prototype/` with instructions on how to run the prototype:

1.  `cd backend && uvicorn main:app --reload`
2.  `cd frontend && npm install && npm run dev`
3.  Open `http://localhost:5173` in Chrome 146+.
4.  Use a browser extension or DevTools to call the WebMCP tools.

## 4. Handoff Checklist for Claude Code

- [ ] Create the `phase3_prototype` directory structure.
- [ ] Implement the FastAPI backend with `/search` and `/analyze` endpoints.
- [ ] Build the minimal React frontend UI.
- [ ] Implement the `webmcp.js` file with the two tool registrations.
- [ ] Ensure the `execute` functions correctly call the backend and update the UI.
- [ ] Write the `README.md` with setup and run instructions.
- [ ] Commit all work to a new branch named `feature/phase3a-prototype`.

---

This specification provides a clear, achievable scope for the Phase 3A prototype. Upon completion, we will have a tangible demonstration of our hybrid architecture and a solid foundation for the next phase of development. **FLYWHEEL TEAM!**
