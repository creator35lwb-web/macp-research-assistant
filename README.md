<p align="center">
  <img src="docs/assets/macp-logo-hd.png" alt="MACP Research Assistant Logo" width="200" height="200" />
</p>

<h1 align="center">MACP-Powered AI Research Assistant</h1>

<p align="center">
  <strong>Discover, Analyze, and Organize Academic Research with AI-Powered Multi-Agent Collaboration</strong>
</p>

<p align="center">
  <a href="https://macpresearch.ysenseai.org"><img src="https://img.shields.io/badge/Live%20Demo-macpresearch.ysenseai.org-00D4FF?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Live Demo" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License" /></a>
  <a href="https://doi.org/10.5281/zenodo.18651799"><img src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.18651799-blue?style=for-the-badge" alt="DOI" /></a>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#live-demo">Live Demo</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#webmcp-integration">WebMCP</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

## Overview

The **MACP Research Assistant** is a production-deployed web application that brings the [Multi-Agent Collaboration Protocol (MACP v2.0)](https://github.com/creator35lwb-web/LegacyEvolve) to life as an interactive research platform. It enables researchers, developers, and AI practitioners to discover papers from arXiv and HuggingFace Daily Papers, analyze them with AI (Gemini, Anthropic, OpenAI, Grok), save findings to a personal library, and sync research projects to GitHub repositories — all with complete provenance tracking.

Built by the **FLYWHEEL TEAM** (a multi-agent collaboration between Manus AI and Claude Code), this project demonstrates the MACP protocol's real-world application: AI agents collaborating with human researchers to accelerate knowledge discovery.

This project is a foundational protocol within the broader **YSenseAI Ecosystem**. For the operational command hub, see the [verifimind-genesis-mcp](https://github.com/creator35lwb-web/verifimind-genesis-mcp) repository.

---

## Features

### Core Research Workflow

| Feature | Description | Status |
|---------|-------------|--------|
| **Paper Discovery** | Search arXiv and HuggingFace Daily Papers with real-time results | ✅ Live |
| **AI Analysis** | Multi-provider LLM analysis with summary, key insights, methodology, research gaps, and strength scoring | ✅ Live |
| **PDF Preview** | View and download paper PDFs directly in the workspace | ✅ Live |
| **Personal Library** | Save papers with notes and organize by research project | ✅ Live |
| **BibTeX Export** | Export citations in BibTeX format for LaTeX integration | ✅ Live |
| **Research Notes** | Create and manage research notes linked to papers | ✅ Live |
| **GitHub Sync** | Connect repositories for version-controlled research persistence | ✅ Live |
| **Load More** | Paginated search results with progressive loading | ✅ Live |
| **BYOK Support** | Bring Your Own Key for any supported LLM provider | ✅ Live |
| **Knowledge Graph** | Visualize paper relationships and citation networks | 📋 Phase 3E |

### Multi-Provider LLM Support

The platform supports multiple AI providers for paper analysis, with both server-side keys and user-provided BYOK (Bring Your Own Key):

| Provider | Model | BYOK Support | Notes |
|----------|-------|:------------:|-------|
| **Google Gemini** | gemini-2.5-flash | ✅ | Free tier available at [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| **Anthropic** | Claude 3.5 Sonnet | ✅ | Requires paid API key |
| **OpenAI** | GPT-4o | ✅ | Requires paid API key |
| **xAI Grok** | grok-beta | ✅ | Requires paid API key |

### WebMCP Integration

The platform exposes 8 WebMCP endpoints, enabling AI agents (Claude Desktop, Cursor, etc.) to interact with the research assistant programmatically:

```
GET  /api/mcp/                    → Tool discovery
POST /api/mcp/search_papers       → Search arXiv/HuggingFace
POST /api/mcp/analyze_paper       → AI-powered analysis
POST /api/mcp/save_paper          → Save to library
POST /api/mcp/get_library         → Retrieve saved papers
POST /api/mcp/create_note         → Create research note
POST /api/mcp/get_knowledge_graph → Get paper relationships
POST /api/mcp/export_citations    → Export BibTeX citations
POST /api/mcp/get_paper_details   → Get full paper metadata
```

---

## Live Demo

**Production URL:** [https://macpresearch.ysenseai.org](https://macpresearch.ysenseai.org)

The application is deployed on **Google Cloud Run** with:

- GitHub OAuth authentication
- HTTPS with HSTS enforcement
- Security headers (CSP, X-Frame-Options, X-Content-Type-Options)
- Non-root Docker container
- CI/CD pipeline via GitHub Actions
- Input sanitization with XML structural delimiters for LLM prompts

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │  Search   │ │  Library │ │  Notes   │ │ Knowledge │  │
│  │  Papers   │ │  Manager │ │  Editor  │ │   Graph   │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘  │
│       └─────────────┴────────────┴─────────────┘        │
│                         │ API Client                     │
└─────────────────────────┼───────────────────────────────┘
                          │ HTTPS
┌─────────────────────────┼───────────────────────────────┐
│                  Backend (FastAPI + Python)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │  Search   │ │ Analyze  │ │  WebMCP  │ │  GitHub   │  │
│  │  Engine   │ │  Engine  │ │  Server  │ │  Storage  │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘  │
│       │             │            │              │        │
│  ┌────┴─────┐ ┌─────┴────┐ ┌────┴─────┐ ┌─────┴─────┐  │
│  │  arXiv   │ │  Gemini  │ │  SQLite  │ │  GitHub   │  │
│  │  HF API  │ │  Claude  │ │    DB    │ │   API     │  │
│  │          │ │  GPT-4o  │ │          │ │           │  │
│  │          │ │  Grok    │ │          │ │           │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Geist UI |
| **Backend** | FastAPI, Python 3.12, Pydantic |
| **Database** | SQLite (local), PostgreSQL (planned) |
| **Auth** | GitHub OAuth 2.0, JWT sessions |
| **LLM** | Google Gemini, Anthropic Claude, OpenAI GPT-4o, xAI Grok |
| **Deployment** | Docker, Google Cloud Run, GitHub Actions CI/CD |
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

**Result:** Wasted time re-discovering information and lost research provenance.

## The Solution

**MACP Research Assistant** solves this by tracking every research action using the **Multi-Agent Collaboration Protocol (MACP v2.0)**:

- **Complete traceability** — Know which AI analyzed which paper when
- **Easy recall** — "What have I learned about X?" queries work instantly
- **Citation provenance** — Every citation linked to AI handoffs
- **Knowledge graphs** — See relationships between papers and concepts
- **Multi-AI coordination** — Seamless handoffs between AI assistants

**Result:** Research with complete provenance, easy recall, and transparent methodology.

---

## MACP Research Workflow

```
┌─────────────────┐
│ 1. Discovery    │  Find papers (arXiv, HuggingFace)
│    (Search)     │  → Paper metadata + abstracts
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 2. Analysis     │  AI-powered analysis (Gemini/Claude/GPT-4o/Grok)
│  (Analyze)      │  → Summary, insights, methodology, gaps, score
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 3. Library      │  Save to personal library with notes
│   (Save)        │  → Organized, searchable collection
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 4. Export       │  BibTeX citations, knowledge graph
│   (Cite)        │  → Ready for papers and projects
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 5. Sync         │  Push to GitHub repository
│   (Persist)     │  → Version-controlled research
└─────────────────┘
```

**Key Innovation:** Every step maintains complete provenance — who discovered it, when it was analyzed, which AI was used, and how it connects to your research.

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

### Current: Phase 3D — Foundation Repair & GitHub Integration

- Fix save-to-library pipeline (broken in production)
- Fix BYOK UX (add validation, apply button, error feedback)
- Implement GitHub-first persistence (GitHub as source of truth, SQLite as cache)
- End-to-end pipeline: Search → Save → Library → GitHub Sync → Cold Restart → Hydrate

### Next: Phase 3E — MACP v2.0 Schema & Deep Analysis

- Define MACP v2.0 `schema.json` (self-describing repository standard)
- Deep PDF analysis (full-text extraction, section chunking)
- Multi-agent analysis files (one file per agent per paper)
- Knowledge graph visualization in web UI

### Future: Phase 3F — Multi-Agent Research Sync

- Perplexity API integration for deep research with citations
- Multi-agent consensus generation
- Agent registry (`.macp/agents/`)
- Full-text search across all analyses

---

## Roadmap

```
Phase 1 ✅ → Phase 2 ✅ → Phase 3A ✅ → Phase 3B ✅ → Phase 3C ✅ → Phase 3D 🔧 → Phase 3E 📋 → Phase 3F 📋 → Phase 4 📋
  Manual       CLI Tools     Web UI       Full Hybrid    Production    Foundation     MACP v2.0     Multi-Agent    WebMCP
  MACP         & Schemas     Prototype    WebMCP         Deployment    Repair &       Schema &      Research       Ecosystem
                                                                      GitHub Sync    Deep Analysis  Sync
```

See **[ROADMAP.md](ROADMAP.md)** for the full roadmap with sprint details, architecture diagrams, and agent assignment matrix.

---

## Security

This project follows security best practices aligned with the [Claude Code Security](https://claude.com/solutions/claude-code-security) framework and the CS Agent v3.1 Multi-Stage Verification Protocol:

- **Input Sanitization:** All user inputs validated via Pydantic models with XML structural delimiters for LLM prompts
- **Authentication:** GitHub OAuth 2.0 with JWT session tokens (configurable expiry)
- **Container Security:** Non-root user in Docker, `.dockerignore` for sensitive files
- **Headers:** CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- **CI/CD:** Automated security checks via GitHub Actions
- **Error Handling:** Sanitized error messages in production (no stack traces)
- **Prompt Injection Protection:** Structural XML delimiters prevent LLM prompt manipulation

For security concerns, please see [SECURITY.md](SECURITY.md) or contact the maintainers.

---

## WebMCP Integration

The MACP Research Assistant implements the **Web-based Model Context Protocol (WebMCP)**, enabling AI agents to interact with the platform programmatically. This is a key differentiator — your AI assistant can search, analyze, and save papers on your behalf.

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

# Search for papers
results = requests.post("https://macpresearch.ysenseai.org/api/mcp/search_papers", json={
    "query": "multi-agent reinforcement learning",
    "source": "daily_papers",
    "limit": 20
})

# Analyze a paper
analysis = requests.post("https://macpresearch.ysenseai.org/api/mcp/analyze_paper", json={
    "arxiv_id": "2503.16408",
    "provider": "gemini"
})
```

---

## Ecosystem Alignment

This project is a foundational protocol within the broader **YSenseAI Ecosystem**:

- **Command Central Hub:** [verifimind-genesis-mcp](https://github.com/creator35lwb-web/verifimind-genesis-mcp)
- **Unified Ecosystem Roadmap:** [YSenseAI Ecosystem Map & Unified Roadmap](https://github.com/creator35lwb-web/verifimind-genesis-mcp/blob/main/ecosystem/YSenseAIEcosystemMap%26UnifiedRoadmap(Feb2026).md)

The MACP specification used here is based on MACP v2.0 from the [LegacyEvolve](https://github.com/creator35lwb-web/LegacyEvolve) project.

---

## Repository Structure

```
macp-research-assistant/
├── .macp/                        # MACP protocol directory
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
│   │   └── webmcp.py             # WebMCP endpoint handlers
│   ├── frontend/                 # React + Vite frontend
│   │   └── src/
│   │       ├── components/       # UI components
│   │       ├── hooks/            # Custom React hooks
│   │       └── services/         # API client
│   ├── Dockerfile                # Multi-stage Docker build
│   └── deploy-cloudrun.sh        # GCP Cloud Run deployment
│
├── tools/                        # Phase 2 CLI tools
│   ├── paper_fetcher.py          # 3-pipeline paper discovery
│   ├── macp_cli.py               # CLI orchestrator
│   ├── knowledge_graph.py        # Knowledge graph generator
│   └── llm_providers.py          # Multi-provider LLM integration
│
├── docs/                         # Documentation
│   ├── assets/                   # Logo and images
│   ├── QUICK_START.md
│   ├── MACP_SPECIFICATION.md
│   └── ARCHITECTURE.md
│
├── templates/                    # MACP JSON templates
├── examples/                     # Usage examples
├── peas/                         # VerifiMind-PEAS validation reports
├── iteration/                    # Development iteration logs
└── README.md                     # This file
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start Guide](docs/QUICK_START.md) | Get started in 5 minutes |
| [MACP Specification](docs/MACP_SPECIFICATION.md) | MACP v2.0 protocol details |
| [Architecture](docs/ARCHITECTURE.md) | System design and data flow |
| [Best Practices](docs/BEST_PRACTICES.md) | Tips for effective research workflows |
| [FAQ](docs/FAQ.md) | Common questions and answers |

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**

- Improve documentation and examples
- Report bugs and suggest features
- Build Phase 3D/3E/3F features
- Add new LLM provider integrations
- Create research workflow templates

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
| [VerifiMind-PEAS](https://github.com/creator35lwb-web/VerifiMind-PEAS) | Ethical AI verification methodology with CS Agent v3.1 |
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
- **FLYWHEEL TEAM:** Built through multi-agent collaboration (Manus AI + Claude Code)
- **Data Sources:** arXiv API, HuggingFace Daily Papers API
- **Security:** Aligned with Claude Code Security framework and CS Agent v3.1 protocol

---

<p align="center">
  <strong>Built with the FLYWHEEL TEAM — Multi-Agent Collaboration in Action</strong>
  <br />
  <em>Made with purpose by the YSenseAI™ Team</em>
</p>
