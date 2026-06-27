<p align="center">
  <img src="docs/assets/macp-logo-hd.png" alt="MACP Research Assistant Logo" width="200" height="200" />
</p>

<h1 align="center">MACP-Powered AI Research Assistant</h1>

<p align="center">
  <strong>Discover, Analyze, and Organize Academic Research with AI-Powered Multi-Agent Collaboration</strong>
</p>

<p align="center">
  <a href="https://macpresearch.ysenseai.org"><img src="https://img.shields.io/badge/Live%20Demo-macpresearch.ysenseai.org-00D4FF?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Live Demo" /></a>
  <a href="https://creator35lwb-web.github.io/macp-research-assistant/"><img src="https://img.shields.io/badge/Landing%20Page-GitHub%20Pages-8B5CF6?style=for-the-badge&logo=github&logoColor=white" alt="Landing Page" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License" /></a>
  <a href="https://doi.org/10.5281/zenodo.18651799"><img src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.18651799-blue?style=for-the-badge" alt="DOI" /></a>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#live-demo">Live Demo</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#webmcp-integration">WebMCP</a> •
  <a href="#verifimind-peas-v050-integration">VerifiMind-PEAS</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

## Overview

The **MACP Research Assistant** is a production-deployed web application that brings the [Multi-Agent Collaboration Protocol (MACP v2.0)](https://github.com/creator35lwb-web/LegacyEvolve) to life as an interactive research platform. It enables researchers, developers, and AI practitioners to discover papers from arXiv and HuggingFace Daily Papers (12,800+ papers searchable), analyze them with multiple AI providers, generate multi-agent consensus analyses, conduct deep web-grounded research via Perplexity, save findings to a personal library, and sync research projects to GitHub repositories — all with complete provenance tracking.

Built by the **FLYWHEEL TEAM** (a multi-agent collaboration between Manus AI and Claude Code), this project demonstrates the MACP protocol's real-world application: AI agents collaborating with human researchers to accelerate knowledge discovery.

This project is **Tool Suite 2** within the broader **VerifiMind-PEAS v0.5.0** architecture. For the operational command hub, see the [verifimind-genesis-mcp](https://github.com/creator35lwb-web/verifimind-genesis-mcp) repository.

---

## Features

### Core Research Workflow

| Feature | Description | Status |
|---------|-------------|--------|
| **Paper Discovery** | Search 12,800+ papers from arXiv and HuggingFace Daily Papers with real-time results | ✅ Live |
| **AI Analysis (Abstract)** | Multi-provider LLM analysis with summary, key insights, methodology, research gaps, and strength scoring | ✅ Live |
| **Deep PDF Analysis** | Full-text 4-pass analysis using PyMuPDF extraction with section chunking | ✅ Built |
| **Multi-Agent Consensus** | Automated consensus generation when 2+ agents analyze the same paper (40/30/30 scoring) | ✅ Built |
| **Deep Research (Perplexity)** | Web-grounded investigation with citations, related work, code repos, and impact assessment | ✅ Built |
| **Personal Library** | Save papers with notes and organize by research project | ✅ Live |
| **BYOK Support** | Bring Your Own Key with Validate & Apply UX for any supported provider | ✅ Live |
| **PDF Preview** | View and download paper PDFs directly in the workspace | ✅ Live |
| **BibTeX Export** | Export citations in BibTeX format for LaTeX integration | ✅ Live |
| **Research Notes** | Create and manage research notes linked to papers | ✅ Live |
| **GitHub Sync** | Connect repositories for version-controlled research persistence | ✅ Live |
| **Load More** | Paginated search results with progressive loading | ✅ Live |
| **Schema Validation** | All saves validated against MACP v2.0 `schema.json` before persistence | ✅ Built |
| **Agent Registry** | Dynamic agent capability registry with 6 registered agents | ✅ Built |
| **Knowledge Graph** | Visualize paper relationships and citation networks | 📋 Phase 4 |

### Multi-Provider LLM Support

The platform supports 5 AI providers for paper analysis, with both server-side keys and user-provided BYOK (Bring Your Own Key):

| Provider | Model | BYOK Support | Capabilities |
|----------|-------|:------------:|-------------|
| **Google Gemini** | gemini-2.5-flash | ✅ | Abstract analysis, deep analysis, consensus synthesis |
| **Anthropic** | Claude 3.5 Sonnet | ✅ | Abstract analysis, deep analysis, consensus synthesis |
| **OpenAI** | GPT-4o | ✅ | Abstract analysis, deep analysis, consensus synthesis |
| **xAI Grok** | grok-beta | ✅ | Abstract analysis, deep analysis, consensus synthesis |
| **Perplexity** | Sonar Pro | ✅ | Deep web-grounded research with citations |

### BYOK Privacy Guarantee

> **Your API keys are never stored, logged, or transmitted to us.** When you provide your own API key through the BYOK (Bring Your Own Key) feature, the key is used exclusively for the duration of your request and is immediately discarded after the API call completes.

This guarantee has been verified through a comprehensive code audit (conducted 2026-02-24):

| Security Check | Result |
|---------------|--------|
| Key stored in database? | **NO** — The `Analysis` model contains only provider name, summary, insights, and score. No key field exists. |
| Key written to GitHub? | **NO** — The `save_analysis_per_agent()` data dict contains agent_id, summary, key_findings. No key field. |
| Key appears in logs? | **NO** — Error messages reference provider name and config name only. Key values are never printed. |
| Key returned in API response? | **NO** — Responses contain analysis results only. |
| Key in provenance tracking? | **NO** — Provenance records provider name and model, not credentials. |
| Key memory scope? | **Request-only** — The key lives only in the HTTP request handler scope and is garbage collected after the function returns. |
| Middleware logging of request bodies? | **NO** — No middleware captures or logs request bodies containing keys. |

The BYOK feature includes a **Validate & Apply** button that tests your key against the selected provider before use, and a **Clear** button to remove it from your browser session at any time. Keys are stored only in your browser's local memory (session state) and are never persisted server-side.

### Multi-Agent Consensus Analysis

When 2 or more AI providers analyze the same paper, the platform generates an automated **consensus analysis** using a weighted agreement score (0–1):

| Component | Weight | Semantic metric (default) | Lexical fallback |
|-----------|--------|---------------------------|------------------|
| **Key Findings Agreement** | 40% | Embedding cosine similarity between agents' findings | Jaccard word overlap |
| **Relevance Score Alignment** | 30% | 1 − normalized variance of provider scores | *(same — always numeric)* |
| **Methodology Consistency** | 30% | Embedding cosine similarity between methodology texts | Jaccard word overlap |

**Semantic scoring (Phase 4).** Findings and methodology agreement are computed from sentence embeddings (Google `text-embedding-004` free tier, with OpenAI `text-embedding-3-small` fallback), so two agents that reach the same conclusion in *different words* are correctly scored as agreeing — something pure word-overlap misses. Embeddings are batched in a single request and BYOK-aware.

**Transparent and degradation-safe.** Every consensus record reports an `agreement_method` field — `semantic:<provider>:<model>`, `lexical`, or `trivial` — plus the per-component `agreement_components` breakdown, so the score is auditable. If no embedding provider is reachable (no key, network failure), the scorer automatically falls back to lexical Jaccard overlap and records the reason; it never fails the request.

The consensus output also includes convergence points, divergence points (with each agent's position), and a `bias_cross_check` field that assesses whether agent biases cancel out or compound.

### WebMCP Integration

The platform exposes **13 MCP endpoints**, enabling AI agents (Claude Desktop, Cursor, etc.) to interact with the research assistant programmatically:

```
GET  /api/mcp/                    → Tool discovery (13 tools)
POST /api/mcp/search_papers       → Search 12,800+ papers (arXiv/HuggingFace)
POST /api/mcp/analyze_paper       → Abstract-level AI analysis
POST /api/mcp/analyze-deep        → Full-text 4-pass deep PDF analysis
POST /api/mcp/consensus           → Multi-agent consensus generation
POST /api/mcp/deep-research       → Perplexity web-grounded research
POST /api/mcp/save_paper          → Save to library + GitHub sync
POST /api/mcp/get_library         → Retrieve saved papers
POST /api/mcp/create_note         → Create research note
POST /api/mcp/get_knowledge_graph → Get paper relationships
POST /api/mcp/export_citations    → Export BibTeX citations
POST /api/mcp/get_paper_details   → Get full paper metadata
GET  /api/mcp/agents              → Agent registry (6 agents)
```

---

## Live Demo

**Production URL:** [https://macpresearch.ysenseai.org](https://macpresearch.ysenseai.org)

**Landing Page:** [https://creator35lwb-web.github.io/macp-research-assistant/](https://creator35lwb-web.github.io/macp-research-assistant/)

The application is deployed on **Google Cloud Run** with:

- GitHub OAuth authentication
- HTTPS with HSTS enforcement
- Security headers (CSP, X-Frame-Options, X-Content-Type-Options)
- Non-root Docker container
- CI/CD pipeline via GitHub Actions
- Input sanitization with XML structural delimiters for LLM prompts
- MACP v2.0 schema validation on all data writes

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Frontend (React + Vite)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌────────┐  │
│  │  Search   │ │  Library │ │  Notes   │ │ Knowledge │ │  Deep  │  │
│  │  Papers   │ │  Manager │ │  Editor  │ │   Graph   │ │Analysis│  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘ └───┬────┘  │
│       └─────────────┴────────────┴─────────────┴───────────┘       │
│                              │ API Client                           │
└──────────────────────────────┼──────────────────────────────────────┘
                               │ HTTPS
┌──────────────────────────────┼──────────────────────────────────────┐
│                    Backend (FastAPI + Python)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌────────┐  │
│  │  Search   │ │ Analyze  │ │  WebMCP  │ │  GitHub   │ │ Schema │  │
│  │  Engine   │ │  Engine  │ │  Server  │ │  Storage  │ │Validate│  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘ └───┬────┘  │
│       │             │            │              │            │       │
│  ┌────┴─────┐ ┌─────┴────┐ ┌────┴─────┐ ┌─────┴─────┐ ┌───┴────┐  │
│  │  arXiv   │ │  Gemini  │ │  SQLite  │ │  GitHub   │ │ MACP   │  │
│  │  HF API  │ │  Claude  │ │    DB    │ │   API     │ │ v2.0   │  │
│  │  (12.8K) │ │  GPT-4o  │ │          │ │           │ │ Schema │  │
│  │          │ │  Grok    │ │          │ │           │ │        │  │
│  │          │ │Perplexity│ │          │ │           │ │        │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘ └────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Geist UI, Agent Registry, Consensus Comparison UI |
| **Backend** | FastAPI, Python 3.12, Pydantic |
| **Database** | SQLite (local cache), GitHub (source of truth) |
| **Auth** | GitHub OAuth 2.0, JWT sessions |
| **LLM** | Google Gemini, Anthropic Claude, OpenAI GPT-4o, xAI Grok, Perplexity Sonar |
| **PDF Processing** | PyMuPDF (full-text extraction, section chunking) |
| **Schema** | MACP v2.0 (`schema.json` — self-describing repository standard) |
| **Deployment** | Docker, Google Cloud Run (revision 00022), GitHub Actions CI/CD (all green) |
| **Security** | CSP, HSTS, non-root container, input sanitization, prompt injection protection |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- A GitHub OAuth App (for authentication)
- At least one LLM API key (Gemini recommended — free tier available)

### Local Development

```bash
# Clone the repository
git clone https://github.com/creator35lwb-web/macp-research-assistant.git
cd macp-research-assistant/phase3_prototype

# Backend setup
cd backend
cp .env.example .env
# Edit .env with your API keys and OAuth credentials
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend setup (new terminal)
cd ../frontend
npm install
npm run dev
```

### Environment Variables

```env
# Required
JWT_SECRET=your-secure-random-secret
GITHUB_APP_CLIENT_ID=your-github-oauth-client-id
GITHUB_APP_CLIENT_SECRET=your-github-oauth-client-secret

# LLM Providers (at least one recommended)
GEMINI_API_KEY=your-gemini-api-key          # Free tier: https://aistudio.google.com/app/apikey
ANTHROPIC_API_KEY=your-anthropic-api-key     # Optional
OPENAI_API_KEY=your-openai-api-key           # Optional
XAI_API_KEY=your-xai-api-key                 # Optional
SONAR_API_KEY=your-perplexity-api-key        # Optional: deep research

# Optional
CORS_ORIGINS=http://localhost:5173
GITHUB_APP_REDIRECT_URI=http://localhost:8000/api/auth/github/callback
```

### Docker Deployment

```bash
cd phase3_prototype
docker build -t macp-research-assistant .
docker run -p 8000:8000 \
  -e JWT_SECRET=your-secret \
  -e GEMINI_API_KEY=your-key \
  -e GITHUB_APP_CLIENT_ID=your-id \
  -e GITHUB_APP_CLIENT_SECRET=your-secret \
  macp-research-assistant
```

---

## The Problem

When conducting research using multiple AI assistants (ChatGPT, Claude, Perplexity, Gemini, etc.), you face these challenges:

- **Lost context** — Each AI session starts from scratch
- **Forgotten insights** — Can't recall what you learned weeks ago
- **No traceability** — Don't know which AI contributed which insight
- **Scattered citations** — References lost across platforms
- **Disconnected knowledge** — Can't see relationships between papers
- **No consensus** — Different AIs give different conclusions with no way to reconcile

**Result:** Wasted time re-discovering information and lost research provenance.

## The Solution

**MACP Research Assistant** solves this by tracking every research action using the **Multi-Agent Collaboration Protocol (MACP v2.0)**:

- **Complete traceability** — Know which AI analyzed which paper when
- **Easy recall** — "What have I learned about X?" queries work instantly
- **Citation provenance** — Every citation linked to AI handoffs
- **Multi-agent consensus** — Automated reconciliation when agents disagree (40/30/30 scoring)
- **Deep research** — Perplexity-powered web-grounded investigation with citations
- **Knowledge graphs** — See relationships between papers and concepts
- **Schema validation** — Every data write validated against MACP v2.0 specification

**Result:** Research with complete provenance, multi-agent consensus, and transparent methodology.

---

## MACP Research Workflow

```
┌─────────────────┐
│ 1. Discovery    │  Search 12,800+ papers (arXiv, HuggingFace)
│    (Search)     │  → Paper metadata + abstracts
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 2. Analysis     │  Abstract analysis (Gemini/Claude/GPT-4o/Grok)
│  (Analyze)      │  Deep PDF analysis (4-pass full-text)
│                 │  Deep research (Perplexity web-grounded)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 3. Consensus    │  Multi-agent consensus (40/30/30 scoring)
│  (Synthesize)   │  → Convergence, divergence, agreement score
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 4. Library      │  Save to personal library with notes
│   (Save)        │  → Organized, searchable collection
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 5. Export       │  BibTeX citations, knowledge graph
│   (Cite)        │  → Ready for papers and projects
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 6. Sync         │  Push to GitHub repository (MACP v2.0 format)
│   (Persist)     │  → Version-controlled, schema-validated research
└─────────────────┘
```

**Key Innovation:** Every step maintains complete provenance — who discovered it, when it was analyzed, which AI was used, and how it connects to your research. All data is validated against the MACP v2.0 schema before persistence.

---

## VerifiMind-PEAS v0.5.0 Integration

The MACP Research Assistant serves as **Tool Suite 2** within the VerifiMind-PEAS v0.5.0 architecture:

```
VerifiMind-PEAS v0.5.0
├── Tool Suite 1: PEAS Validation Engine (X/Z/CS Trinity)
│   └── Traffic classification, content validation, report generation
│
└── Tool Suite 2: MACP Research Engine (this project)
    └── Paper search, multi-agent analysis, consensus, deep research
```

The two tool suites create a **research-validation feedback loop**: the Research Engine discovers and analyzes papers to inform validation methodology, while the Validation Engine generates evidence that becomes research material. MCP tool wrappers for VerifiMind-PEAS integration are available in the [verifimind-genesis-mcp](https://github.com/creator35lwb-web/verifimind-genesis-mcp) repository.

### Available MCP Tools for VerifiMind-PEAS

| Tool | Description |
|------|-------------|
| `macp_search` | Search 12,800+ ML/AI papers |
| `macp_analyze` | Abstract-level AI analysis |
| `macp_analyze_deep` | Full-text 4-pass deep analysis |
| `macp_consensus` | Multi-agent consensus (40/30/30 scoring) |
| `macp_deep_research` | Perplexity web-grounded research |
| `macp_agents` | List registered agents |

---

## MACP v2.0 Schema

The repository follows the **MACP v2.0 Directory Standard**, defined in `.macp/schema.json`:

```
.macp/
├── manifest.json              ← Master index of all papers, analyses, notes
├── schema.json                ← MACP v2.0 self-describing schema (v2.0.0)
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
├── research/                  ← Research data (papers, analyses from CLI tools)
│   └── ...
│
├── agents/                    ← Agent registry (6 agents)
│   ├── gemini.json
│   ├── claude.json
│   ├── openai.json
│   ├── grok.json
│   ├── perplexity.json
│   └── manus.json
│
├── handoffs/                  ← Agent-to-agent communication
│   └── ...
│
└── validation/                ← Trinity Validation reports
    └── ...
```

Any AI agent can read `schema.json` to understand the entire directory structure, data formats, and contribution rules. This makes the repository **self-describing** — a new agent joining the project can orient itself without human guidance.

---

## Development Phases

> For the complete, detailed roadmap with sprint breakdowns, architecture diagrams, and agent contribution matrix, see **[ROADMAP.md](ROADMAP.md)**.

### Completed

| Phase | Description | Highlights |
|-------|-------------|------------|
| **Phase 1** | Manual MACP Implementation | Templates, documentation, GODELAI example |
| **Phase 2** | Semi-Automated CLI Tools | Paper fetcher (3 pipelines), citation tracker, knowledge graph generator |
| **Phase 3A** | Web UI Prototype | React frontend, FastAPI backend, 2 WebMCP tools |
| **Phase 3B** | Full Hybrid Implementation | All 8 WebMCP tools, GitHub OAuth, paper library |
| **Phase 3C** | Production Deployment | GCP Cloud Run, CI/CD, security hardening, multi-provider LLM, Load More |
| **Phase 3D** | Foundation Repair & GitHub Integration | Save pipeline fix, BYOK UX (Validate & Apply), GitHub-first persistence, .gitignore fix |
| **Phase 3E** | MACP v2.0 Schema & Deep Analysis | Schema validation, deep PDF analysis (4-pass), multi-agent consensus (40/30/30), Perplexity deep research, agent registry (6 agents), 13 MCP endpoints |
| **Phase 3F** | Deployment & UI Polish | Cloud Run revision 00022, Agent Registry UI, Consensus Comparison UI, Deep Analysis View, resizable detail panel, 10/10 Dependabot PRs closed, CI #28 all green, 0 code scanning alerts |

### Current: Phase 4 — WebMCP Ecosystem & External Integrations

| Item | Status | Notes |
|------|--------|-------|
| Agent Registry UI | ✅ Done | Built in Phase 3F (card grid, cost tiers, capability chips) |
| Knowledge Graph visualization | 📋 Planned | Backend tool exists, frontend UI pending |
| n8n workflow integration | 📋 Planned | Daily paper digest, trend alerts |
| Research templates | 📋 Planned | Domain-specific research workflows |
| Collaborative notes | 📋 Planned | Multi-agent + human annotation |
| Full-text search | 📋 Planned | Search across all analyses |
| Mobile responsive | 📋 Planned | Detail panel as slide-over |
| Keyboard shortcuts | 📋 Planned | Panel navigation hotkeys |

---

## Roadmap

```
Phase 1 ✅ → Phase 2 ✅ → Phase 3A ✅ → Phase 3B ✅ → Phase 3C ✅ → Phase 3D ✅ → Phase 3E ✅ → Phase 3F ✅ → Phase 4 🔧
  Manual       CLI Tools     Web UI       Full Hybrid    Production    Foundation     MACP v2.0     Deploy &       WebMCP
  MACP         & Schemas     Prototype    WebMCP         Deployment    Repair &       Schema &      UI Polish      Ecosystem
                                                                      GitHub Sync    Deep Analysis
```

See **[ROADMAP.md](ROADMAP.md)** for the full roadmap with sprint details, architecture diagrams, and agent assignment matrix.

---

## Security

This project follows security best practices aligned with the [Claude Code Security](https://claude.com/solutions/claude-code-security) framework and the CS Agent v3.1 Multi-Stage Verification Protocol:

- **Input Sanitization:** All user inputs validated via Pydantic models with XML structural delimiters for LLM prompts
- **Schema Validation:** All data writes validated against MACP v2.0 `schema.json` before persistence
- **Authentication:** GitHub OAuth 2.0 with JWT session tokens (configurable expiry)
- **Container Security:** Non-root user in Docker, `.dockerignore` for sensitive files
- **Headers:** CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- **CI/CD:** Automated security checks via GitHub Actions
- **Error Handling:** Sanitized error messages in production (no stack traces)
- **Prompt Injection Protection:** Structural XML delimiters prevent LLM prompt manipulation

For security concerns, please see [SECURITY.md](SECURITY.md) or contact the maintainers.

---

## WebMCP Integration

The MACP Research Assistant implements the **Web-based Model Context Protocol (WebMCP)**, enabling AI agents to interact with the platform programmatically. This is a key differentiator — your AI assistant can search, analyze, generate consensus, and save papers on your behalf.

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "macp-research": {
      "url": "https://macpresearch.ysenseai.org/api/mcp/"
    }
  }
}
```

### Example: Agent-Driven Research

```python
import requests

BASE = "https://macpresearch.ysenseai.org/api/mcp"

# Search for papers
results = requests.post(f"{BASE}/search_papers", json={
    "query": "multi-agent reinforcement learning",
    "source": "hysts",
    "limit": 20
})

# Analyze a paper (abstract)
analysis = requests.post(f"{BASE}/analyze_paper", json={
    "arxiv_id": "2503.16408",
    "provider": "gemini"
})

# Deep PDF analysis (4-pass full-text)
deep = requests.post(f"{BASE}/analyze-deep", json={
    "arxiv_id": "2503.16408",
    "provider": "gemini"
})

# Generate multi-agent consensus
consensus = requests.post(f"{BASE}/consensus", json={
    "arxiv_id": "2503.16408"
})

# Deep research via Perplexity
research = requests.post(f"{BASE}/deep-research", json={
    "arxiv_id": "2503.16408"
})
```

---

## Ecosystem Alignment

This project is **Tool Suite 2** within the broader **YSenseAI Ecosystem**:

- **Command Central Hub:** [verifimind-genesis-mcp](https://github.com/creator35lwb-web/verifimind-genesis-mcp) (PRIVATE)
- **Unified Ecosystem Roadmap:** [YSenseAI Ecosystem Map & Unified Roadmap](https://github.com/creator35lwb-web/verifimind-genesis-mcp/blob/main/ecosystem/YSenseAIEcosystemMap%26UnifiedRoadmap(Feb2026).md)
- **MACP Specification:** [LegacyEvolve](https://github.com/creator35lwb-web/LegacyEvolve) (MACP v2.0 origin)
- **VerifiMind-PEAS:** [VerifiMind-PEAS](https://github.com/creator35lwb-web/VerifiMind-PEAS) (Tool Suite 1)

---

## Repository Structure

```
macp-research-assistant/
├── .macp/                        # MACP v2.0 protocol directory
│   ├── schema.json               # MACP v2.0 self-describing schema
│   ├── manifest.json             # Master index of all papers/analyses
│   ├── agents/                   # Agent registry (6 agents)
│   ├── research/                 # Research data (papers, analyses)
│   ├── analyses/                 # Per-agent analysis files
│   ├── validation/               # Trinity Validation reports
│   ├── handoffs/                 # FLYWHEEL TEAM handoff documents
│   └── security/                 # Security assessment reports
│
├── phase3_prototype/             # Production application
│   ├── backend/                  # FastAPI backend
│   │   ├── main.py               # API endpoints
│   │   ├── config.py             # Configuration management
│   │   ├── models.py             # Pydantic models
│   │   ├── auth.py               # GitHub OAuth + JWT
│   │   ├── security.py           # Security headers middleware
│   │   ├── webmcp.py             # WebMCP endpoint handlers (13 tools)
│   │   ├── schema_validator.py   # MACP v2.0 schema validation
│   │   └── github_storage.py     # GitHub-first persistence + per-agent storage
│   ├── frontend/                 # React + Vite frontend
│   │   └── src/
│   │       ├── components/       # UI components (DeepAnalysisView, etc.)
│   │       ├── hooks/            # Custom React hooks
│   │       └── services/         # API client (13 endpoints)
│   ├── Dockerfile                # Multi-stage Docker build
│   └── deploy-cloudrun.sh        # GCP Cloud Run deployment
│
├── tools/                        # Phase 2 CLI tools
│   ├── paper_fetcher.py          # 3-pipeline paper discovery + PDF extraction
│   ├── macp_cli.py               # CLI orchestrator
│   ├── knowledge_graph.py        # Knowledge graph generator
│   └── llm_providers.py          # 5-provider LLM integration + consensus scoring
│
├── docs/                         # Documentation + GitHub Pages landing page
│   ├── index.html                # Landing page (GitHub Pages)
│   ├── assets/                   # Logo and images
│   ├── QUICK_START.md
│   ├── MACP_SPECIFICATION.md
│   └── ARCHITECTURE.md
│
├── templates/                    # MACP JSON templates
├── examples/                     # Usage examples
├── peas/                         # VerifiMind-PEAS validation reports
├── iteration/                    # Development iteration logs
├── ROADMAP.md                    # Detailed development roadmap
└── README.md                     # This file
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start Guide](docs/QUICK_START.md) | Get started in 5 minutes |
| [MACP Specification](docs/MACP_SPECIFICATION.md) | MACP v2.0 protocol details |
| [Architecture](docs/ARCHITECTURE.md) | System design and data flow |
| [Roadmap](ROADMAP.md) | Detailed development roadmap with sprint breakdowns |
| [Best Practices](docs/BEST_PRACTICES.md) | Tips for effective research workflows |
| [FAQ](docs/FAQ.md) | Common questions and answers |

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**

- Improve documentation and examples
- Report bugs and suggest features
- Build Phase 4 features (knowledge graph UI, research templates)
- Add new LLM provider integrations
- Create research workflow templates
- Build knowledge graph visualizations

---

## Citation

If you use MACP Research Assistant in your research, please cite:

```bibtex
@software{macp_research_assistant_2026,
  author = {YSenseAI Team},
  title = {MACP-Powered AI Research Assistant},
  year = {2026},
  url = {https://github.com/creator35lwb-web/macp-research-assistant},
  note = {Production deployment at https://macpresearch.ysenseai.org}
}
```

---

## Related Projects

| Project | Description |
|---------|-------------|
| [VerifiMind-PEAS](https://github.com/creator35lwb-web/VerifiMind-PEAS) | Ethical AI verification methodology with CS Agent v3.1 (Tool Suite 1) |
| [verifimind-genesis-mcp](https://github.com/creator35lwb-web/verifimind-genesis-mcp) | Command Central Hub for VerifiMind-PEAS v0.5.0 |
| [GODELAI](https://github.com/creator35lwb-web/godelai) | AI alignment research project |
| [LegacyEvolve](https://github.com/creator35lwb-web/LegacyEvolve) | MACP v2.0 specification and protocol |

---

## Contact

- **Project:** YSenseAI™ | 慧觉™
- **GitHub:** [@creator35lwb-web](https://github.com/creator35lwb-web)
- **X (Twitter):** [@creator35lwb](https://x.com/creator35lwb)
- **Email:** creator35lwb@gmail.com
- **Website:** [verifimind.io](https://verifimind.io)

---

## Acknowledgments

- **MACP Protocol:** Based on MACP v2.0 from the LegacyEvolve project
- **FLYWHEEL TEAM:** Built through multi-agent collaboration (Manus AI as CSO R + Claude Code as CTO RNA)
- **Data Sources:** arXiv API, HuggingFace Daily Papers API (12,800+ papers), Perplexity Sonar API
- **Security:** Aligned with Claude Code Security framework and CS Agent v3.1 protocol

---

<p align="center">
  <strong>Built with the FLYWHEEL TEAM — Multi-Agent Collaboration in Action</strong>
  <br />
  <em>Made with purpose by the YSenseAI™ Team</em>
</p>
