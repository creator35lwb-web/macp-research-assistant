# MACP Research Assistant — Project Roadmap

> **Last Updated:** 2026-02-25 | **Author:** FLYWHEEL TEAM (Orchestrator L + CSO R + CTO RNA)
> **Status:** Living document — updated after each alignment meeting
> **Version:** v1.0.0 released → v2.0.0 in planning

This roadmap was rewritten on 2026-02-25 following a comprehensive functional audit of the live production system at `macpresearch.ysenseai.org` and a strategic vision alignment meeting. It replaces the 2026-02-22 version with verified endpoint test results, honest feature status, and the complete v2.0.0 architecture plan. Every AI agent working on this project should read this document before making changes.

---

## Strategic Vision

The MACP Research Assistant exists at the intersection of two goals. The first, which is realized in v1.0.0, is a **multi-agent research tool** — a platform where researchers can discover papers, analyze them with multiple AI providers, and save their research journey to GitHub with full provenance tracking. The second, which defines v2.0.0, is a **recursive research orchestration platform** — a system where AI agents autonomously discover sub-topics, hand off analyses to each other, and grow a hierarchical research directory tree that deepens with every contribution.

Three architectural principles guide all development:

1. **GitHub is the source of truth** for the entire research journey. Every paper discovered, every analysis produced, every note written becomes a permanent, version-controlled artifact in the `.macp/` directory.
2. **MACP v2.0** defines a standardized directory schema that any AI agent (Manus AI, Claude Code, Cursor, Perplexity, Antigravity) can read, understand, and contribute to.
3. **Zero burn-rate, BYOK privacy** — the platform operates on free tiers and open-source infrastructure. Users bring their own API keys; no keys are stored server-side.

---

## v1.0.0 Release — Honest Functional Assessment

The following table reflects the actual production state verified through live endpoint testing on 2026-02-25. Each endpoint was tested with real API calls against `macpresearch.ysenseai.org`.

### Endpoint Verification Results

| Endpoint | Method | Status | Evidence |
|----------|--------|--------|----------|
| `/api/mcp/search` | POST | **Working** | Returns 10 papers from HuggingFace Datasets API with metadata |
| `/api/mcp/analyze` | POST | **Working** | Gemini free-tier analysis returns structured JSON (summary, key findings, methodology, research gaps, strength score) |
| `/api/mcp/save` | POST | **Working** | Saves to SQLite + GitHub dual-write |
| `/api/mcp/library` | GET | **Working** | Returns saved papers from library |
| `/api/mcp/agents` | GET | **Working** | Returns 6 registered agents with capabilities (read-only) |
| `/api/mcp/deep-research` | POST | **Requires BYOK** | Code complete; returns error without `SONAR_API_KEY` (by design) |
| `/api/mcp/consensus` | POST | **Working** | Requires 2+ analyses of same paper to generate consensus |
| `/api/mcp/analyze-deep` | POST | **Built** | 4-pass PDF analysis code exists |
| `/api/mcp/analysis/{id}` | GET | **Built** | Retrieves stored analysis by paper ID |
| `/api/mcp/sync` | POST | **Built** | GitHub hydration endpoint |

### Feature Status Matrix

| Feature | Designed | Code Complete | Working in Production | Honest Notes |
|---------|----------|---------------|----------------------|--------------|
| Paper Search (12,800+ papers) | Yes | Yes | **Yes** | HuggingFace Datasets API, reliable |
| AI Analysis (Abstract) | Yes | Yes | **Yes** | Gemini free tier; Claude/GPT-4 via BYOK |
| Deep PDF Analysis (4-pass) | Yes | Yes | **Untested in prod** | PyMuPDF extraction, section chunking |
| Multi-Agent Consensus | Yes | Yes | **Yes** (conditional) | Requires 2+ analyses first; 40/30/30 scoring algorithm |
| Deep Research (Perplexity) | Yes | Yes | **Requires BYOK key** | Full Perplexity Sonar integration; generates citations, related work, impact assessment |
| Save to Library | Yes | Yes | **Yes** | SQLite + GitHub dual-write |
| GitHub Sync | Yes | Yes | **Partial** | Dual-write fires; hydration on cold start untested |
| Agent Registry | Yes | Yes | **Display-only** | Returns 6 agents; no submission API for external agents |
| Knowledge Graph | Yes | CLI only | **No** | Backend tool from Phase 2; no web UI |
| PWA / Mobile | Yes | Yes | **Yes** | Installable, offline-capable, tested on iPad and Android |
| BYOK Privacy | Yes | Yes | **Yes** | Code-audited; no server-side key storage |
| Schema Validation | Yes | Yes | **Yes** | All writes validated against `.macp/schema.json` |

### Known Issues (P1)

| Issue | Severity | Description |
|-------|----------|-------------|
| Frontend Display Bug | P1 | Analysis completes at API level but may not display in UI after "Analyzing..." state |
| Agent-to-Agent Communication | Limitation | Currently MANUAL only — GitHub serves as bridge, but no automated agent-to-agent handoffs |
| Consensus Requires Manual Setup | UX Gap | Users must manually trigger 2+ analyses before consensus becomes available |

---

## Completed Phases (v1.0.0)

| Phase | Period | Description | Key Deliverables |
|-------|--------|-------------|------------------|
| **Phase 1** | Jan 2026 | Manual MACP Implementation | MACP methodology templates, documentation framework, GODELAI case study |
| **Phase 2** | Jan 2026 | Semi-Automated CLI Tools | Paper fetcher (arXiv, Semantic Scholar, HuggingFace), citation tracker, knowledge graph generator, 55 research papers collected |
| **Phase 3A** | Feb 2026 | Foundation & Web UI Prototype | React frontend, FastAPI backend, 2 WebMCP tools (search, analyze) |
| **Phase 3B** | Feb 2026 | Full Hybrid Implementation | All 8 WebMCP tools, GitHub OAuth, paper library UI, Connect Repository |
| **Phase 3C** | Feb 2026 | Production Deployment | GCP Cloud Run, CI/CD via GitHub Actions, security hardening (CSP, HSTS, non-root Docker), multi-provider LLM (Gemini/Claude/GPT-4o/Grok), BYOK support |
| **Phase 3D** | Feb 2026 | Foundation Repair & GitHub Integration | Save pipeline fix, BYOK UX (Validate & Apply), GitHub-first persistence, `.gitignore` fix |
| **Phase 3E** | Feb 2026 | MACP v2.0 Schema & Deep Analysis | Schema validation, deep PDF analysis (4-pass), multi-agent consensus (40/30/30), Perplexity deep research, agent registry (6 agents), 13 MCP endpoints |
| **Phase 3F** | Feb 2026 | Deployment & PWA | Cloud Run revision 00022, Agent Registry UI, Consensus Comparison UI, Deep Analysis View, PWA implementation, resizable detail panel, 10/10 Dependabot PRs closed, 0 CodeQL alerts |

**VerifiMind-PEAS Validation Score:** 8.94/10 (LAUNCH-READY)

---

## Agent Registry — What It Actually Does

The Agent Registry is one of the most commonly misunderstood features. This section provides an honest, detailed explanation.

### What Works Now

The Agent Registry is a **read-only directory** of 6 AI agents that the platform recognizes. When you call `GET /api/mcp/agents`, the system reads JSON files from `.macp/agents/` and returns a structured list:

| Agent | ID | Integration Type | What It Can Do Today |
|-------|----|-----------------|---------------------|
| Gemini 2.5 Flash | `gemini` | Built-in (free tier) | Abstract analysis via `/api/mcp/analyze` — works without any API key |
| Claude (Anthropic) | `anthropic` | BYOK | Abstract analysis via `/api/mcp/analyze` with user's `ANTHROPIC_API_KEY` |
| GPT-4o (OpenAI) | `openai` | BYOK | Abstract analysis via `/api/mcp/analyze` with user's `OPENAI_API_KEY` |
| Gemini Pro | `gemini_pro` | BYOK | Deep PDF analysis via `/api/mcp/analyze-deep` with user's `GEMINI_API_KEY` |
| Perplexity Sonar | `perplexity` | BYOK | Deep web research via `/api/mcp/deep-research` with user's `SONAR_API_KEY` |
| Manus AI | `manus` | External (manual) | Strategic analysis via GitHub handoffs — no API integration |

### What It Does NOT Do

The Agent Registry does **not** enable agents to submit analyses back to the platform. There is no `POST /api/mcp/agents/submit` or equivalent endpoint. External agents like Manus AI and Claude Code contribute by manually writing files to the GitHub repository and committing them. The registry is informational — it tells you which agents exist and what they can do, but it does not orchestrate them.

### What v2.0.0 Will Add

Phase 5A will introduce an **Agent Submission API** (`POST /api/mcp/submit-analysis`) that allows any registered agent to programmatically contribute analysis results back to the repository, validated against `schema.json`.

---

## Perplexity Deep Research — What It Actually Generates

The Perplexity integration is fully implemented in code but requires the user's `SONAR_API_KEY` to function (BYOK model). No server-side Perplexity key is configured — this is by design to maintain zero burn-rate.

### When a User Provides Their SONAR_API_KEY

The system calls the Perplexity Sonar Pro API (`https://api.perplexity.ai/chat/completions`) with web grounding enabled. The structured response includes:

| Output Field | Description |
|-------------|-------------|
| `citation_count` | Number of citations found for the paper |
| `citing_papers` | List of papers that cite this work |
| `related_work` | Semantically related papers discovered via web search |
| `code_url` | Link to associated code repository (if found) |
| `data_url` | Link to associated dataset (if found) |
| `community_discussions` | Relevant discussions found on the web |
| `research_group` | Information about the authors' research group |
| `group_recent_papers` | Recent publications from the same group |
| `impact_assessment` | Assessment of the paper's impact and significance |
| `sources` | Full list of web sources used (with URLs) |

This is real Perplexity integration with web-grounded citations — not a mock or placeholder. The output is structured as MACP-compatible JSON and can be saved to the library and synced to GitHub.

### Without SONAR_API_KEY

The endpoint returns: `"Deep research failed — check SONAR_API_KEY"`. This is expected behavior under the BYOK model.

---

## Phase 4 — Current: WebMCP Ecosystem & Knowledge Graph

> **Status:** In Progress | **Owner:** TEAM
> **Goal:** Extend the platform with visual knowledge exploration and external integrations

| Item | Status | Notes |
|------|--------|-------|
| Agent Registry UI | ✅ Done | Card grid with cost tiers, capability chips (Phase 3F) |
| Knowledge Graph visualization | 📋 Planned | Backend tool exists from Phase 2; frontend D3/vis-network UI pending |
| Research Templates | 📋 Planned | Domain-specific analysis workflows |
| Citation Extraction | 📋 Planned | Parse analysis results for cross-references |
| Full-text Search | 📋 Planned | Search across all analyses in library |
| n8n Workflow Integration | 📋 Planned | Daily paper digest, trend alerts |
| Mobile Responsive Polish | 📋 Planned | Detail panel as slide-over on mobile |

---

## Phase 5 — v2.0.0: Recursive Research Orchestration Platform

> **Status:** Architecture Designed | **Owner:** TEAM
> **Goal:** Transform the tool from a search-and-analyze assistant into a recursive, multi-agent research orchestration platform

### The Vision Gap

The v1.0.0 system implements a **linear, single-pass pipeline**: User → Search → Analyze → Save → GitHub (flat structure). The v2.0.0 vision is a **recursive, self-growing research ecosystem**: agents autonomously discover sub-topics, hand off analyses, and grow a hierarchical directory tree that deepens with every contribution.

The overall vision implementation as of v1.0.0 is approximately **30%**. The foundation (schema, agents, dual-write, multi-provider LLM) is solid. The five missing components described below constitute the remaining 70%.

### v1.0.0 vs. v2.0.0 Architecture

```
v1.0.0 (Current — Linear Pipeline):

User → Search → Paper Found → AI Analyze (single agent, abstract-only)
                                    ↓
                              Save to Library → GitHub Sync (flat structure)


v2.0.0 (Target — Recursive Orchestration):

User → Search → Paper Found → Agent A (first impression)
                                    ↓
                              Agent B picks up → deeper analysis
                                    ↓
                              Agent C picks up → different perspective
                                    ↓
                              Consensus generated automatically
                                    ↓
                              Discovery: "This paper relates to Transformer architecture"
                                    ↓
                              Auto-create topic: LLM/Transformer/
                                    ↓
                              Agent D: "Let me research Transformer papers deeper"
                                    ↓
                              New papers discovered → cycle repeats
                                    ↓
                              Directory tree grows: LLM/ → Transformer/ → AI-alignment/ → Multi-agent/
```

### Five Missing Components

#### Component 1: Agent Submission API (Phase 5A — ~1 week)

Currently, only the webapp's built-in providers can write analyses. External agents (Manus AI, Claude Code, Cursor) have no programmatic way to submit their analysis results back to the repository.

**Required:** A standardized endpoint that any agent can call:

```
POST /api/mcp/submit-analysis
{
  "agent_id": "manus_ai",
  "paper_id": "arxiv:2402.05120",
  "analysis_type": "deep",
  "content": { ... structured analysis ... },
  "continuation_of": "claude_code_20260225"
}
```

**Alternative (simpler, GitHub-native):** Agents write directly to `.macp/analyses/{paper_id}/{agent_id}_{date}.json` and commit to the repo. The webapp reads from GitHub on load. This approach is more aligned with the "GitHub as bridge" philosophy.

#### Component 2: Topic Taxonomy System (Phase 5B — ~1 week)

Currently all papers live at the same level. There is no concept of topics, sub-topics, or research depth. The target structure:

```
.macp/topics/
├── index.json
├── large-language-models/
│   ├── topic.json
│   ├── transformer-architecture/
│   │   ├── topic.json
│   │   └── attention-mechanisms/
│   │       └── topic.json
│   └── ai-alignment/
│       ├── topic.json
│       └── multi-agent-collaboration/
│           └── topic.json
└── ...
```

Each `topic.json` contains metadata about the topic, its parent, depth level, associated papers, contributing agents, and child topics. When an agent analyzes a paper and identifies `relevance_tags`, the system checks if matching topics exist and creates them if not.

#### Component 3: Research Queue & Backlog (Phase 5C — ~1 week)

Currently, the user manually triggers every action. There is no concept of "this paper needs deeper analysis" or "this topic needs more papers."

**Required:** A queue system (`.macp/queue/pending.json`) where agents can post research tasks and other agents can claim them. This enables the "go deeper" trigger — when an agent identifies a research gap, it queues a task for another agent to investigate.

#### Component 4: Continuation Protocol (Phase 5C — included)

Currently, each analysis is independent. Agent B does not know what Agent A found. The continuation protocol adds a `continues_from` field to analysis files, creating an analysis chain where each agent builds on the previous one's findings and recommends next steps.

#### Component 5: Automated Research Orchestration (Phase 5D — ~2 weeks)

Wire everything together: when a paper is analyzed, auto-extract topics and update the tree; when a research gap is identified, auto-queue deeper research; when Perplexity finds related papers, auto-save to the topic directory; when consensus is reached, update the knowledge graph. This is the capstone that transforms the tool into a self-growing research platform.

### Phase 5 Sprint Plan

| Sprint | Name | Duration | Owner | Deliverables |
|--------|------|----------|-------|-------------|
| **5A** | Agent Submission Layer | ~1 week | CTO RNA | `POST /api/mcp/submit-analysis`, CLI tool (`macp submit`), schema validation for external contributions |
| **5B** | Topic Taxonomy Engine | ~1 week | TEAM | `.macp/topics/` directory structure, LLM-powered topic extraction, "Go Deeper" button in UI |
| **5C** | Research Queue & Continuation | ~1 week | CTO RNA | `.macp/queue/pending.json`, continuation protocol, agent task claiming |
| **5D** | Automated Orchestration | ~2 weeks | TEAM | Auto-topic extraction, auto-queue on research gaps, Perplexity auto-save, knowledge graph updates |

### Release: v2.0.0 — "Research Journey Engine"

The v2.0.0 release will be validated through VerifiMind-PEAS before publication, following the same process used for v1.0.0 (which scored 8.94/10).

---

## Multi-Agent Convergence Architecture

The following diagram shows how multiple AI agents contribute to the same GitHub repository through the MACP v2.0 protocol layer:

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
│  - Triggers downstream agents (v2.0.0)                             │
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

---

## Manual Agent-to-Agent Workflow (Works Today)

While automated orchestration is a v2.0.0 feature, users can perform multi-agent research **today** using GitHub as the bridge:

1. **Search** a paper on `macpresearch.ysenseai.org` (e.g., "multi-agent collaboration")
2. **Analyze** it with Gemini (first impression — works without any API key)
3. **Save** it to your library (syncs to GitHub via dual-write)
4. **Open Claude Code** → read the paper from `.macp/research/{paper}/paper.json`
5. **Ask Claude Code** to write a deeper analysis → save as `.macp/analyses/{paper_id}/claude_code_{date}.json`
6. **Commit and push** to GitHub
7. **Open Manus AI** → read Claude Code's analysis from GitHub → write a synthesis/consensus
8. **Commit and push** to GitHub

This workflow validates the "GitHub as bridge" concept. Every step is manual, but it demonstrates the multi-agent convergence pattern that v2.0.0 will automate.

---

## MACP v2.0 Directory Standard

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
├── topics/                    ← v2.0.0: Hierarchical topic taxonomy
│   ├── index.json
│   └── large-language-models/
│       └── topic.json
│
├── queue/                     ← v2.0.0: Research task queue
│   ├── pending.json
│   └── completed.json
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
├── handoffs/                  ← Agent-to-agent communication
│   └── ...
│
├── validation/                ← VerifiMind-PEAS validation reports
│   └── ...
│
├── security/                  ← Security assessment reports
│   └── ...
│
└── agents/                    ← Agent registry and capabilities
    ├── manus-ai.json
    ├── claude-code.json
    ├── perplexity.json
    └── cursor.json
```

---

## Constraints & Principles

These constraints apply to all development phases and must be respected by all agents:

| Constraint | Description |
|-----------|-------------|
| **No Burn-Rate** | Zero-cost strategy. All features must use free tiers or existing infrastructure. No new paid services without explicit approval. |
| **Open Source** | Fully open source (MIT License). All code, schemas, and documentation are public. |
| **BYOK Privacy** | Users bring their own API keys. No keys stored server-side. Code-audited security guarantee. |
| **GitHub as Bridge** | GitHub is the primary communication channel between all agents. Every significant change must be committed and pushed. |
| **Sequential Execution** | Phases must be completed in order. Phase 4 features continue alongside Phase 5 architecture work. |
| **Security First** | No personal identifiers, tokens, or secrets in commits. All sensitive data through environment variables only. |
| **Attribution** | All agent contributions must be clearly attributed (commit messages, handoff documents). |
| **Ethical AI** | Part of the YSenseAI ethical AI ecosystem. All development aligns with core values: consent, transparency, attribution, quality data. |

---

## Visual Roadmap

```
Phase 1 ✅ → Phase 2 ✅ → Phase 3A ✅ → Phase 3B ✅ → Phase 3C ✅ → Phase 3D ✅ → Phase 3E ✅ → Phase 3F ✅
  Manual       CLI Tools     Web UI       Full Hybrid    Production    Foundation     MACP v2.0     Deploy &
  MACP         & Schemas     Prototype    WebMCP         Deployment    Repair &       Schema &      PWA
                                                                      GitHub Sync    Deep Analysis

                                                                                                        │
                                                                                                        ▼
                                                                                                  Phase 4 🔧
                                                                                                  WebMCP
                                                                                                  Ecosystem &
                                                                                                  Knowledge Graph
                                                                                                        │
                                                                                                        ▼
                                                                                              ┌─── Phase 5 📋 ───┐
                                                                                              │  v2.0.0 Release  │
                                                                                              │  Research Journey │
                                                                                              │  Engine           │
                                                                                              │                   │
                                                                                              │  5A: Agent Submit │
                                                                                              │  5B: Topic Tree   │
                                                                                              │  5C: Queue/Chain  │
                                                                                              │  5D: Orchestration│
                                                                                              └───────────────────┘
```

---

## How to Use This Roadmap

**For CTO RNA (Claude Code):** Phase 4 knowledge graph UI is the current implementation priority. When Phase 5 begins, start with Sprint 5A (Agent Submission API). Read the vision gap analysis at `.macp/handoffs/20260225_CSO-R_vision-gap-analysis-recursive-research.md` for detailed architecture specifications.

**For CSO R (Manus AI):** Continue maintaining alignment documentation, updating this roadmap after each sprint, and managing the MACP v2.0 schema evolution. Coordinate Phase 5B (Topic Taxonomy) design with CTO RNA.

**For the Orchestrator:** Review sprint completions before approving the next sprint. Test features in production at `macpresearch.ysenseai.org`. Try the manual Agent-to-Agent workflow described above to refine v2.0.0 requirements. Report issues through the FLYWHEEL TEAM alignment process.

**For any new agent joining the project:** Read this file first, then read `.macp/schema.json` to understand the data format, then read the latest handoff in `.macp/handoffs/` for current context.

---

> *This roadmap is maintained by the FLYWHEEL TEAM as part of the YSenseAI ethical AI ecosystem. It is a living document updated after each alignment meeting.*
> *Last alignment: 2026-02-25 — Functional Audit & v2.0.0 Vision Architecture*
