# MACP Research Assistant — Project Roadmap

> **Last Updated:** 2026-02-22 | **Author:** FLYWHEEL TEAM (Orchestrator + CSO R + CTO RNA)
> **Status:** Living document — updated after each alignment meeting

This roadmap is the product of the first full FLYWHEEL TEAM alignment meeting held on 2026-02-22. It replaces all previous informal phase descriptions with a structured, honest assessment of what has been built, what works, what is broken, and what comes next. Every AI agent working on this project should read this document before making changes.

---

## Strategic Vision

The MACP Research Assistant is not just a paper search tool. It is designed to be a **multi-agent research knowledge system** where:

1. **GitHub is the source of truth** for the entire research journey — every paper discovered, every analysis produced, every note written becomes a permanent, version-controlled artifact.
2. **MACP v2.0** defines a standardized directory schema that any AI agent (Manus AI, Claude Code, Cursor, Antigravity, Perplexity) can read, understand, and contribute to.
3. **Multiple AI agents** with different strengths converge their research outputs into the same repository — creating a multi-alignment knowledge base that grows deeper with each contribution.

This vision is partially designed but not yet fully realized. The roadmap below traces the path from the current state to the complete vision.

---

## Completed Phases

| Phase | Period | Description | Key Deliverables |
|-------|--------|-------------|------------------|
| **Phase 1** | Jan 2026 | Manual MACP Implementation | MACP methodology templates, documentation framework, GODELAI case study |
| **Phase 2** | Jan 2026 | Semi-Automated CLI Tools | Paper fetcher (arXiv, Semantic Scholar, HuggingFace), citation tracker, knowledge graph generator, 55 research papers collected |
| **Phase 3A** | Feb 2026 | Web UI Prototype | React frontend, FastAPI backend, 2 WebMCP tools (search, analyze) |
| **Phase 3B** | Feb 2026 | Full Hybrid Implementation | All 8 WebMCP tools, GitHub OAuth, paper library UI, Connect Repository |
| **Phase 3C** | Feb 2026 | Production Deployment | GCP Cloud Run, CI/CD via GitHub Actions, security hardening (CSP, HSTS, non-root Docker), multi-provider LLM (Gemini/Claude/GPT-4o/Grok), BYOK support, Load More pagination |

---

## Current State: Honest Assessment (as of 2026-02-22)

The following table reflects the actual production state verified through live examination of `macpresearch.ysenseai.org`:

| Feature | Designed | Implemented | Working in Production | Notes |
|---------|----------|-------------|----------------------|-------|
| Paper Search (HF/arXiv) | Yes | Yes | **Yes** | Returns relevant results reliably |
| Paper Analysis (LLM) | Yes | Yes | **Yes** (abstract only) | Full-text PDF analysis not yet built |
| Save to Library | Yes | Yes (buggy) | **No** | `handleSave` silently catches all errors; no user feedback |
| My Library Display | Yes | Yes | **No** | Always shows empty because save is broken |
| BYOK API Key | Yes | Yes (UX issues) | **Partial** | No Apply button, no key-provider validation, no success/error toast |
| Connect Repository | Yes | Yes | **Partial** | Dropdown lists repos, shows green "Connected" badge, but sync unproven |
| GitHub Dual-Write | Yes | Partial | **No** | Fire-and-forget BackgroundTask with no error reporting |
| GitHub Hydration | Yes | Yes | **Untested** | `hydrate_from_github()` exists but never triggered in production |
| Knowledge Graph | Yes | CLI only | **No** | Exists as CLI tool output (`.macp/knowledge_graph.json`), not in web UI |

**Root Cause Chain:** Save fails silently → Library stays empty → GitHub Sync has nothing to push → The entire research journey persistence pipeline is non-functional in production.

**Additional Issue:** The local `.macp/research/` directory contains 55 paper JSON files and 5 analysis files from Phase 2 CLI tools, but this directory is listed in `.gitignore` — none of this research data has ever reached GitHub.

---

## Phase 3D — Foundation Repair & GitHub Integration

> **Status:** Next Sprint | **Owner:** CTO RNA (Claude Code)
> **Goal:** Make the core save → library → GitHub pipeline work end-to-end

This is the most critical phase. Without a working persistence pipeline, no subsequent feature (deep analysis, multi-agent sync, knowledge graph) can function. Phase 3D is divided into two sprints.

### Sprint 3D.1 — Critical Fixes (P0)

These must be completed before any other work proceeds.

| Task | Description | Acceptance Criteria |
|------|-------------|-------------------|
| **Fix Save Pipeline** | Rewrite `handleSave` in `Workspace.tsx` with proper error handling | Save button shows success/error toast; saved paper appears in My Library |
| **Fix Library Persistence** | Investigate SQLite ephemeral storage on Cloud Run; implement GitHub-first persistence or external database | Papers survive cold starts; Library shows previously saved papers |
| **Fix BYOK UX** | Add "Validate & Apply" button, key-provider cross-validation, success/error feedback | User can paste API key, see validation result, and confirm activation |
| **Remove `.macp/research/` from gitignore** | Allow research data to be tracked in Git, OR implement GitHub API as primary store | Research journey data reaches GitHub |
| **Fix GitHub Dual-Write** | Add error handling and retry logic to `save_paper()` BackgroundTask | User is notified if GitHub sync fails; retry on transient errors |

### Sprint 3D.2 — GitHub as Source of Truth (P1)

| Task | Description | Acceptance Criteria |
|------|-------------|-------------------|
| **GitHub-First Persistence** | Make GitHub the write-ahead log; SQLite becomes a cache that hydrates from GitHub on cold start | App works correctly after Cloud Run cold start; all data survives |
| **End-to-End Pipeline Test** | Test: Search → Save → Library → GitHub Sync → Cold Restart → Hydrate → Library shows papers | Full cycle works without manual intervention |
| **Manifest Updates** | Ensure `manifest.json` is updated on every save/analyze operation | Manifest accurately reflects all papers and analyses in the repo |

### Architecture: GitHub-First Persistence Model

```
User Action (Save Paper)
        │
        ▼
┌─────────────────┐
│  Backend API     │──── Write to GitHub API (Primary) ────▶ .macp/papers/arxiv_XXXX.json
│  (FastAPI)       │                                         manifest.json updated
│                  │──── Update SQLite (Cache) ────▶ Local DB for fast reads
└─────────────────┘
        │
        ▼ (On Cold Start)
┌─────────────────┐
│  Hydration       │──── Read manifest.json from GitHub ────▶ Populate SQLite cache
│  (Startup)       │
└─────────────────┘
```

---

## Phase 3E — MACP v2.0 Schema & Multi-Agent Analysis

> **Status:** Planned | **Owner:** TEAM (CSO R designs schema, CTO RNA implements)
> **Goal:** Standardize the repository structure so any AI agent can contribute

### MACP v2.0 Directory Standard

```
.macp/
├── manifest.json              ← Master index of all papers, analyses, notes
├── schema.json                ← MACP v2.0 self-describing schema definition
│
├── papers/                    ← One JSON file per paper
│   ├── arxiv_2405.19888.json
│   └── ...
│
├── analyses/                  ← One folder per paper, one file per agent
│   ├── arxiv_2405.19888/
│   │   ├── gemini_20260222.json
│   │   ├── claude_20260223.json
│   │   ├── perplexity_20260224.json
│   │   └── consensus.json     ← Multi-agent consensus summary
│   └── ...
│
├── citations/                 ← Cross-reference graph
│   └── citation_graph.json
│
├── notes/                     ← Research notes (human + agent)
│   └── note_001.md
│
├── graph/                     ← Knowledge graph data
│   └── knowledge-graph.json
│
├── handoffs/                  ← Agent-to-agent communication (existing)
│   └── ...
│
└── agents/                    ← Agent registry and capabilities
    ├── manus-ai.json
    ├── claude-code.json
    ├── perplexity.json
    └── cursor.json
```

### Sprint 3E.1 — Schema Definition & Deep Analysis

| Task | Description | Owner |
|------|-------------|-------|
| **Define `schema.json`** | Create the MACP v2.0 schema specification that describes all file formats and directory conventions | CSO R |
| **Deep PDF Analysis** | Extract full text from PDFs (PyMuPDF), chunk into sections, analyze beyond abstract | CTO RNA |
| **Multi-Agent Analysis Files** | When a paper is analyzed by different LLMs, store each as a separate file under `analyses/{paper_id}/` | CTO RNA |
| **Agent Registry** | Create `.macp/agents/` directory with JSON files describing each agent's capabilities and access patterns | CSO R |

### Sprint 3E.2 — Knowledge Graph Visualization

| Task | Description | Owner |
|------|-------------|-------|
| **Citation Extraction** | Parse analysis results for cited papers; build citation graph | CTO RNA |
| **Knowledge Graph UI** | Visualize paper relationships, citation networks, and research themes in the web UI | CTO RNA |
| **Graph Sync to GitHub** | Write `knowledge-graph.json` to GitHub on every update | CTO RNA |

---

## Phase 3F — Multi-Agent Research Sync & Perplexity Integration

> **Status:** Planned | **Owner:** TEAM
> **Goal:** Enable multiple AI agents to contribute research to the same GitHub repository

### The Multi-Agent Convergence Architecture

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Manus AI │  │ Claude   │  │Perplexity│  │ Cursor   │  │Antigrav- │
│ (CSO R)  │  │ Code     │  │ API      │  │          │  │ ity      │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
┌────────────────────────────────────────────────────────────────────┐
│                 MACP v2.0 GitHub API Layer                         │
│  - Validates against schema.json                                   │
│  - Updates manifest.json                                           │
│  - Writes to correct directory                                     │
│  - Triggers downstream agents                                      │
└──────────────────────────┬─────────────────────────────────────────┘
                           ▼
                ┌──────────────────────┐
                │   GitHub Repository   │
                │  .macp/ (Source of    │
                │         Truth)        │
                └──────────────────────┘
```

### Agent Contribution Matrix

| Agent | Strength | Contribution Type | Integration Method |
|-------|----------|-------------------|-------------------|
| **Manus AI (CSO R)** | Strategic planning, web research, documentation | Paper discovery, README updates, handoffs, alignment docs | Direct GitHub push via `gh` CLI |
| **Claude Code (CTO RNA)** | Code implementation, deep reasoning | Code fixes, deep methodology analysis, architecture decisions | Direct GitHub push via local git |
| **Perplexity API** | Real-time web research with citations | Deep research reports, citation networks, trend analysis | API call → structured JSON → GitHub push via agent |
| **Cursor** | Code-aware analysis | Code repository analysis, implementation feasibility | Local git push |
| **Antigravity** | Operational monitoring | Weekly reports, metric validation | GitHub push via MACP protocol |
| **HuggingFace MCP** | Model/dataset discovery | Paper metadata, model links, dataset references | MCP server → agent → GitHub push |

### Sprint 3F.1 — Perplexity Integration

| Task | Description | Owner |
|------|-------------|-------|
| **Perplexity API Client** | Build server-side client using `SONAR_API_KEY` for deep research queries | CTO RNA |
| **Research Query Builder** | Construct research queries from paper title, abstract, and key concepts | CTO RNA |
| **Structured Output Parser** | Parse Perplexity response (with citations) into MACP v2.0 analysis format | CTO RNA |
| **Citation Cross-Reference** | Extract new papers from Perplexity citations; add to discovery queue | CTO RNA |
| **GitHub Sync** | Write Perplexity analysis to `.macp/analyses/{paper_id}/perplexity_{date}.json` | CTO RNA |

### Sprint 3F.2 — Multi-Agent Consensus

| Task | Description | Owner |
|------|-------------|-------|
| **Consensus Generator** | When multiple agents have analyzed the same paper, generate a `consensus.json` that synthesizes findings | CTO RNA |
| **Conflict Detection** | Identify disagreements between agent analyses and flag for human review | TEAM |
| **Full-Text Search** | Index all analysis files for keyword search across the entire research library | CTO RNA |

---

## Phase 4 — WebMCP Ecosystem & External Integrations

> **Status:** Future | **Owner:** TEAM
> **Goal:** Make the MACP Research Assistant a platform that other tools can integrate with

| Feature | Description | Priority |
|---------|-------------|----------|
| **WebMCP Server Mode** | Expose the research library as an MCP server that Claude Desktop and other MCP clients can query | High |
| **n8n Workflow Integration** | Trigger research workflows from n8n (e.g., daily paper digest, trend alerts) | Medium |
| **Notification System** | Alert the Orchestrator when new high-relevance papers are discovered or when multi-agent consensus is reached | Medium |
| **Research Templates** | Pre-built analysis templates for different research domains (AI safety, multi-agent systems, LLM evaluation) | Low |
| **Collaborative Notes** | Shared research notes that multiple agents and humans can edit | Low |

---

## Constraints & Principles

These constraints apply to all development phases and must be respected by all agents:

| Constraint | Description |
|-----------|-------------|
| **No Burn-Rate** | The Orchestrator operates as a solo developer with a zero-cost strategy. All features must use free tiers or existing infrastructure. No new paid services without explicit approval. |
| **Open Source** | The project is fully open source (MIT License). All code, schemas, and documentation are public. |
| **GitHub as Bridge** | GitHub is the primary communication channel between all agents. Every significant change must be committed and pushed. |
| **Sequential Execution** | Phases must be completed in order. Phase 3D must be fully working before Phase 3E begins. |
| **Security First** | No personal identifiers, tokens, or secrets in commits. All sensitive data through environment variables only. |
| **Attribution** | All agent contributions must be clearly attributed (commit messages, handoff documents). |
| **Ethical AI** | The project is part of the YSenseAI ethical AI ecosystem. All development must align with the core values: consent, transparency, attribution, quality data. |

---

## Visual Roadmap

```
Phase 1 ✅ ─── Phase 2 ✅ ─── Phase 3A ✅ ─── Phase 3B ✅ ─── Phase 3C ✅
  Manual         CLI Tools      Web UI         Full Hybrid     Production
  MACP           & Schemas      Prototype      WebMCP          Deployment

                                                                    │
                                                                    ▼
                                                              Phase 3D 🔧
                                                              Foundation
                                                              Repair &
                                                              GitHub Sync
                                                                    │
                                                                    ▼
                                                              Phase 3E 📋
                                                              MACP v2.0
                                                              Schema &
                                                              Deep Analysis
                                                                    │
                                                                    ▼
                                                              Phase 3F 📋
                                                              Multi-Agent
                                                              Research Sync
                                                              & Perplexity
                                                                    │
                                                                    ▼
                                                              Phase 4 📋
                                                              WebMCP
                                                              Ecosystem
```

---

## How to Use This Roadmap

**For CTO RNA (Claude Code):** Start with Sprint 3D.1. Read the handoff at `.macp/handoffs/20260222_TEAM-ALIGNMENT_strategic-questions-roadmap.md` and `.macp/handoffs/20260222_CSO-R_phase3d-alignment-byok-ux.md` for detailed implementation specs. Do not proceed to Sprint 3D.2 until Sprint 3D.1 is fully verified in production.

**For CSO R (Manus AI):** Begin drafting the MACP v2.0 `schema.json` specification while CTO RNA works on Sprint 3D.1. Update this roadmap after each sprint completion. Maintain alignment documentation in both `macp-research-assistant` and `verifimind-genesis-mcp`.

**For the Orchestrator:** Review sprint completions before approving the next sprint. Test features in production at `macpresearch.ysenseai.org`. Report issues through the FLYWHEEL TEAM alignment process.

**For any new agent joining the project:** Read this file first, then read `schema.json` (once it exists) to understand the data format, then read the latest handoff in `.macp/handoffs/` for current context.

---

> *This roadmap is maintained by the FLYWHEEL TEAM as part of the YSenseAI ethical AI ecosystem. It is a living document updated after each alignment meeting.*
> *Last alignment: 2026-02-22 — Full Team Strategic Q&A*
