# FLYWHEEL TEAM Alignment Meeting — Strategic Questions & Roadmap Clarification

> **Meeting Type:** Full Team Alignment
> **Date:** 2026-02-22
> **Participants:** Orchestrator (Alton Lee Wei Bin), CSO R (Manus AI), CTO RNA (Claude Code)
> **Protocol:** multi-agent-handoff-bridge v1.0
> **Classification:** STRATEGIC — shapes all future development

---

## Preamble: Live Webapp Examination Results

Before addressing the three strategic questions, CSO R conducted a thorough examination of the live production deployment at `macpresearch.ysenseai.org`. The findings below provide essential context for understanding the gap between the current implementation and the Orchestrator's strategic vision.

| Component | Status | Evidence |
|-----------|--------|----------|
| Search (HuggingFace/arXiv) | Working | Returned 5+ relevant multi-agent papers |
| Analyze (Gemini free tier) | Working | Confirmed in previous sessions |
| Save to Library | **BROKEN** | Clicked Save — no toast, no error, no feedback. My Library shows empty. |
| My Library | **EMPTY** | Zero papers displayed despite multiple save attempts |
| Connect Repository | **Partially Working** | Dropdown lists all user repos, shows green "Connected" badge for `macp-research-assistant` |
| Sync to GitHub | **UNPROVEN** | Sync button exists but nothing to sync since Save is broken |
| BYOK API Key | **UX Issues** | No Apply button, no key-provider validation, no success/error feedback |

The root cause chain is: **Save fails silently** (the `handleSave` function catches all errors and discards them) → **Library stays empty** → **GitHub Sync has nothing to push** → **The entire research journey persistence pipeline is non-functional in production.**

Additionally, the local `.macp/research/` directory contains 55 paper JSON files and 5 analysis JSON files from development/testing, but this directory is explicitly listed in `.gitignore` — meaning none of this research data has ever reached GitHub.

---

## Q1: Is GitHub the Source of Truth for the Research Journey?

### The Orchestrator's Vision (as understood)

> "My Library actually meant to be like our Command Central Hub receiving handoff and alignment for further AI Agents to communicate."

The Orchestrator envisions the GitHub repository (`macp-research-assistant`) not merely as a code repository, but as a **living research knowledge base** — a structured, version-controlled library where every paper discovered, every analysis produced, and every research note written becomes a permanent, traceable artifact that any AI agent in the FLYWHEEL TEAM can read, reason about, and extend.

### Current Reality: Honest Assessment

**The answer is: Not yet. The architecture was designed for this, but the implementation is incomplete.**

The codebase contains all the building blocks. The `github_storage.py` module implements `save_paper()`, `save_analysis()`, `save_note()`, and `save_graph()` methods that write structured JSON files to a `.macp/` directory tree in the connected GitHub repository. The `hydrate_from_github()` method can pull data back from GitHub into the local database. The manifest system (`manifest.json`) was designed to track what exists in the repo.

However, three critical gaps prevent this from functioning as the source of truth:

**Gap 1 — The Save Pipeline Is Broken.** The frontend `handleSave` function wraps the API call in a try/catch that silently discards all errors. Even when the backend successfully updates the SQLite database, the user receives no confirmation. On Cloud Run's ephemeral filesystem, the SQLite database resets on every cold start, so saved papers vanish.

**Gap 2 — Research Data Is Gitignored.** The `.gitignore` file explicitly excludes `.macp/research/` and `.macp/exports/`. This means that even when the local development environment accumulates research data (55 papers currently exist locally), none of it is committed to or tracked by GitHub. The research journey exists only in a transient, local state.

**Gap 3 — GitHub Dual-Write Is Fire-and-Forget.** The `save_paper` call to GitHub storage runs as a `BackgroundTask` with no error reporting back to the user. If the GitHub API call fails (rate limit, auth expiry, network issue), the failure is logged server-side but the user never knows.

### What Must Be Built to Realize the Vision

To make GitHub the true source of truth for the research journey, the following architectural changes are required:

| Change | Description | Owner |
|--------|-------------|-------|
| **Fix Save Pipeline** | Add proper error handling, user feedback (toast notifications), and retry logic to the save flow | CTO RNA |
| **Remove `.macp/research/` from .gitignore** | Allow the research directory tree to be tracked in Git, or implement the GitHub API dual-write as the primary persistence layer (not SQLite) | CTO RNA |
| **Make GitHub the Primary Store** | Instead of SQLite → GitHub (fire-and-forget), make GitHub the authoritative store and SQLite the cache. On app startup, hydrate from GitHub. On save, write to GitHub first, then update local cache. | CTO RNA |
| **Structured Directory Convention** | Adopt a standardized directory tree that all agents understand (see Q2 below) | TEAM |

### Recommended Architecture: GitHub-First Persistence

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Web UI      │────▶│  Backend API │────▶│  GitHub API  │
│  (React)     │     │  (FastAPI)   │     │  (Primary)   │
└──────────────┘     └──────┬───────┘     └──────┬───────┘
                            │                     │
                            ▼                     ▼
                     ┌──────────────┐     ┌──────────────┐
                     │  SQLite      │     │  GitHub Repo │
                     │  (Cache)     │     │  (Source of  │
                     │              │     │   Truth)     │
                     └──────────────┘     └──────────────┘
```

In this model, GitHub is the **write-ahead log**. Every save operation writes to GitHub first. If the GitHub write succeeds, the local SQLite cache is updated. If the GitHub write fails, the user is notified and can retry. On application startup (or cold start on Cloud Run), the app hydrates its local cache from GitHub. This eliminates the ephemeral storage problem entirely.

---

## Q2: Does GitHub Apply MACP v2.0 for AI Agents to Auto-Generate a Directory Tree?

### The Orchestrator's Vision (as understood)

> "Are we developed, GitHub applied MACP v2.0 for AI agents (such as Manus AI, Cursor, Antigravity, Claude Code, etc.) to keep deep and deeper analysis on the research topics then auto-generate directory tree on it to trace on journey?"

The Orchestrator envisions a system where any AI agent — whether it is Manus AI, Claude Code, Cursor, Antigravity, or a future agent — can connect to the GitHub repository, understand its structure through a standardized MACP v2.0 schema, and autonomously contribute deeper analysis. The directory tree itself becomes a **living knowledge graph** that grows organically as agents add layers of analysis.

### Current Reality: Honest Assessment

**The answer is: Partially designed, not yet implemented.**

The `github_storage.py` module defines a directory structure under `.macp/` with subdirectories for `papers/`, `analyses/`, `notes/`, and `graph/`. Each file uses a structured JSON format. However, this structure is not yet standardized as "MACP v2.0," it is not documented in a way that other agents can discover and follow, and the auto-generation of the directory tree does not happen because the save pipeline is broken.

The 55 papers that exist locally in `.macp/research/` use a different directory convention (one folder per paper with `paper.json` and optionally `analysis.json` inside) than what `github_storage.py` writes (flat `papers/arxiv_XXXX.json` files). This inconsistency means even the two systems within the same codebase disagree on the directory structure.

### What MACP v2.0 Directory Standard Should Look Like

Below is a proposed standardized directory tree that all agents can understand, discover, and contribute to. This is the **MACP v2.0 Research Repository Standard**:

```
macp-research-assistant/
├── .macp/
│   ├── manifest.json              ← Master index: lists all papers, analyses, notes
│   ├── schema.json                ← MACP v2.0 schema definition (self-describing)
│   │
│   ├── papers/                    ← One JSON file per paper
│   │   ├── arxiv_2405.19888.json
│   │   ├── arxiv_2503.01935.json
│   │   └── ...
│   │
│   ├── analyses/                  ← One JSON file per analysis (linked to paper)
│   │   ├── arxiv_2405.19888/
│   │   │   ├── gemini_20260222.json      ← Gemini analysis
│   │   │   ├── claude_20260223.json      ← Claude deeper analysis
│   │   │   ├── perplexity_20260224.json  ← Perplexity deep research
│   │   │   └── consensus.json            ← Multi-agent consensus summary
│   │   └── ...
│   │
│   ├── citations/                 ← Cross-reference graph
│   │   └── citation_graph.json
│   │
│   ├── notes/                     ← Research notes (human + agent)
│   │   ├── note_001.md
│   │   └── ...
│   │
│   ├── graph/                     ← Knowledge graph data
│   │   └── knowledge-graph.json
│   │
│   ├── handoffs/                  ← Agent-to-agent communication
│   │   ├── 20260222_CSO-R_phase3d-alignment.md
│   │   └── ...
│   │
│   └── agents/                    ← Agent registry and capabilities
│       ├── manus-ai.json          ← CSO R capabilities and access
│       ├── claude-code.json       ← CTO RNA capabilities and access
│       ├── perplexity.json        ← Deep research agent
│       └── cursor.json            ← Code analysis agent
│
├── README.md
├── docs/
└── phase3_prototype/              ← Application source code
```

The key innovation is the `analyses/` subdirectory structure. Each paper gets its own folder under `analyses/`, and each agent that analyzes the paper creates a separate JSON file. This enables the **"deeper and deeper"** analysis pattern the Orchestrator described: Gemini does the first pass, Claude does a deeper methodology review, Perplexity adds real-time citation context, and a `consensus.json` file aggregates the multi-agent findings.

The `schema.json` file at the root of `.macp/` is the self-describing schema that any new agent can read to understand the repository structure, file formats, and contribution conventions. This is the "MACP v2.0 protocol" that makes the repo agent-readable.

### How Auto-Generation Works

When a user saves a paper through the web UI or when an agent discovers a paper through the MCP server:

1. The paper metadata is written to `.macp/papers/arxiv_XXXX.json`
2. The `manifest.json` is updated to include the new paper
3. When analysis is triggered, the result is written to `.macp/analyses/arxiv_XXXX/{agent}_{date}.json`
4. The directory tree grows automatically — no manual intervention needed
5. Any agent reading `manifest.json` can discover all papers and their analysis history

This is not yet implemented. The architecture exists in concept and partially in code, but the broken save pipeline and the gitignore exclusion prevent it from functioning.

---

## Q3: Is GitHub a Multi-Alignment Source with Perplexity.ai Deep Research Integration?

### The Orchestrator's Vision (as understood)

> "Are we developed, GitHub as multi-alignment sources into it such as using Perplexity.ai for deep research and later on submit or sync or updates into GitHub for further continue study and deep analysis with others relevant citation too."

The Orchestrator envisions a research workflow where multiple AI tools — not just the MACP web app, but also Perplexity.ai, and potentially other research tools — can all contribute their findings to the same GitHub repository. The repository becomes a **convergence point** where different AI agents with different strengths (Perplexity for real-time web research, Gemini for fast analysis, Claude for deep reasoning) all deposit their outputs in a standardized format.

### Current Reality: Honest Assessment

**The answer is: Not yet developed. This requires a new integration layer.**

Currently, the MACP Research Assistant is a standalone web application. It searches HuggingFace and arXiv, analyzes papers using a single LLM provider (Gemini/Claude/OpenAI/Grok), and was designed to save results to GitHub. There is no integration with Perplexity.ai, no mechanism for external tools to push research into the repository, and no API endpoint that accepts research contributions from outside the web app.

The Orchestrator is correct that Perplexity.ai would need to be accessed via API through an AI agent to sync with GitHub. Perplexity cannot directly write to GitHub — an intermediary agent must orchestrate the flow.

### Proposed Multi-Agent Research Sync Architecture

The following architecture enables the Orchestrator's vision of GitHub as a multi-alignment convergence point:

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESEARCH ORCHESTRATION LAYER                  │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Manus AI │  │ Claude   │  │Perplexity│  │ Cursor   │       │
│  │ (CSO R)  │  │ Code     │  │ API      │  │          │       │
│  │          │  │ (CTO RNA)│  │          │  │          │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │              │              │              │             │
│       ▼              ▼              ▼              ▼             │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              MACP v2.0 GitHub API Layer              │       │
│  │  - Validates against schema.json                     │       │
│  │  - Updates manifest.json                             │       │
│  │  - Writes to correct directory                       │       │
│  │  - Triggers downstream agents                        │       │
│  └──────────────────────────┬───────────────────────────┘       │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │   GitHub Repository   │
                    │  macp-research-       │
                    │  assistant            │
                    │                       │
                    │  .macp/               │
                    │  ├── papers/          │
                    │  ├── analyses/        │
                    │  ├── citations/       │
                    │  └── manifest.json    │
                    └──────────────────────┘
```

### Perplexity.ai Integration Pathway

The Orchestrator is correct: Perplexity.ai must be accessed via its API through an AI agent. The integration would work as follows:

**Step 1 — Trigger.** When a paper is saved to the library, or when a user explicitly requests "deep research," the system triggers a Perplexity API call. The `SONAR_API_KEY` is already available in the Manus AI environment.

**Step 2 — Research Query.** The agent constructs a research query from the paper's title, abstract, and key concepts. For example: "What are the latest developments in multi-agent collaboration for LLMs? What papers cite or extend [paper title]? What are the practical applications?"

**Step 3 — Structured Output.** The Perplexity response (which includes source citations) is parsed into the MACP v2.0 analysis format and written to `.macp/analyses/arxiv_XXXX/perplexity_{date}.json`.

**Step 4 — Citation Extraction.** The citations from Perplexity's response are cross-referenced with existing papers in the library. New papers discovered through citations are added to a "discovery queue" for future analysis.

**Step 5 — GitHub Sync.** The new analysis file and updated manifest are committed to GitHub with a descriptive commit message.

### Which Agents Can Contribute and How

| Agent | Strength | Contribution Type | Integration Method |
|-------|----------|-------------------|-------------------|
| **Manus AI (CSO R)** | Strategic planning, web research, documentation | Paper discovery, README updates, handoffs, alignment docs | Direct GitHub push via `gh` CLI |
| **Claude Code (CTO RNA)** | Code implementation, deep reasoning | Code fixes, deep methodology analysis, architecture decisions | Direct GitHub push via local git |
| **Perplexity API** | Real-time web research with citations | Deep research reports, citation networks, trend analysis | API call → structured JSON → GitHub push via agent |
| **Cursor** | Code-aware analysis | Code repository analysis, implementation feasibility | Local git push |
| **Antigravity** | Operational monitoring | Weekly reports, metric validation | GitHub push via MACP protocol |
| **HuggingFace MCP** | Model/dataset discovery | Paper metadata, model links, dataset references | MCP server → agent → GitHub push |

### The Key Insight

The Orchestrator's vision is fundamentally about making the GitHub repository a **protocol-level communication channel** — not just for code, but for research knowledge. This is an extension of the existing FLYWHEEL TEAM handoff protocol (which already uses `.macp/handoffs/` in the `verifimind-genesis-mcp` Command Central Hub) to include structured research data.

The MACP Research Assistant repository would serve a dual purpose: it hosts the application code AND it serves as the research knowledge base. This is analogous to how `verifimind-genesis-mcp` serves as both a code repository and the Command Central Hub for agent communication.

---

## Summary: Gap Analysis and Priority Roadmap

### What Exists vs. What's Needed

| Capability | Designed | Implemented | Working in Production | Priority to Fix |
|-----------|----------|-------------|----------------------|-----------------|
| Paper Search (HF/arXiv) | Yes | Yes | Yes | — |
| Paper Analysis (LLM) | Yes | Yes | Yes (abstract only) | P1 |
| Save to Library | Yes | Yes (buggy) | **No** | **P0** |
| My Library Display | Yes | Yes | **No** (empty) | **P0** |
| GitHub Dual-Write | Yes | Partial | **No** | **P0** |
| GitHub Hydration | Yes | Yes | Untested | P1 |
| MACP v2.0 Schema | No | No | No | P1 |
| Auto Directory Tree | Partial | Partial | No | P1 |
| Perplexity Integration | No | No | No | P2 |
| Multi-Agent Contribution | No | No | No | P2 |
| Agent Registry | No | No | No | P3 |
| Citation Network | Partial | Partial | No | P3 |
| BYOK UX Fix | Designed | No | No | P0 |

### Recommended Sprint Sequence

**Sprint 1 (Immediate — CTO RNA):** Fix the Save pipeline. Add error handling, toast notifications, and ensure papers persist. Remove `.macp/research/` from `.gitignore` or implement GitHub-first persistence. Fix BYOK UX.

**Sprint 2 (Next — CTO RNA + CSO R):** Define and implement MACP v2.0 schema (`schema.json`). Standardize the directory tree. Ensure GitHub dual-write works reliably. Test the full Save → Library → Sync → GitHub pipeline end-to-end.

**Sprint 3 (Following — TEAM):** Integrate Perplexity API for deep research. Implement multi-agent analysis (multiple analysis files per paper). Build the agent registry so new agents can self-describe their capabilities.

**Sprint 4 (Future — TEAM):** Full-text PDF analysis. Citation network extraction. Knowledge graph visualization from GitHub data. Multi-agent consensus generation.

---

## Handoff Instructions

### For CTO RNA (Claude Code)

Read this document at `macp-research-assistant/.macp/handoffs/20260222_TEAM-ALIGNMENT_strategic-questions-roadmap.md`. The immediate action items are:

1. Fix the `handleSave` function in `Workspace.tsx` — remove the silent catch, add proper error handling and toast notifications
2. Investigate why the backend `/api/mcp/save` endpoint may be failing (check if the paper exists in the ephemeral SQLite before save is called)
3. Remove `.macp/research/` from `.gitignore` OR implement GitHub-first persistence
4. Test the full Save → Library → GitHub Sync pipeline end-to-end
5. Implement BYOK UX improvements per the spec in `20260222_CSO-R_phase3d-alignment-byok-ux.md`

### For CSO R (Manus AI)

Continue with:
1. Draft the MACP v2.0 `schema.json` specification
2. Prototype the Perplexity API integration using `SONAR_API_KEY`
3. Update the README when Sprint 1 fixes are merged
4. Maintain alignment documentation in the Command Central Hub

---

## Sandbox Boundary Check

> **Created at:** `/home/ubuntu/macp-research-assistant/.macp/handoffs/20260222_TEAM-ALIGNMENT_strategic-questions-roadmap.md`
> **Will be pushed to:** `macp-research-assistant/.macp/handoffs/` (Public repo)
> **Will be pushed to:** `verifimind-genesis-mcp/.macp/handoffs/` (Command Central Hub)
> **Accessible to:** Claude Code (local), Manus AI (sandbox), and any future agent with repo access
