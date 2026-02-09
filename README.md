# MACP-Powered AI Research Assistant

> [!WARNING]
> **Project Status: Pre-Alpha & Conceptual**
> This repository currently serves as a **conceptual blueprint** and public-facing documentation for the MACP Research Assistant. The core protocol is well-defined, but the implementation is in a **pre-alpha, non-functional state**. The tools and examples described are part of the development roadmap and do not exist yet. For the operational command hub of the YSenseAI ecosystem, please see the [verifimind-genesis-mcp](https://github.com/creator35lwb-web/verifimind-genesis-mcp) repository.

**Track, trace, and recall your AI-powered research with complete citation provenance**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/creator35lwb-web/macp-research-assistant)](https://github.com/creator35lwb-web/macp-research-assistant/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/creator35lwb-web/macp-research-assistant)](https://github.com/creator35lwb-web/macp-research-assistant/issues)

---

## The Problem

When conducting research using multiple AI assistants (ChatGPT, Claude, Perplexity, Gemini, etc.), you face these challenges:

- ❌ **Lost context** - Each AI session starts from scratch
- ❌ **Forgotten insights** - Can't recall what you learned weeks ago
- ❌ **No traceability** - Don't know which AI contributed which insight
- ❌ **Scattered citations** - References lost across platforms
- ❌ **Disconnected knowledge** - Can't see relationships between papers

**Result:** Wasted time re-discovering information and lost research provenance.

---

## The Solution

**MACP-Powered AI Research Assistant** solves this by tracking every research action using the **Multi-Agent Communication Protocol (MACP)**:

✅ **Complete traceability** - Know which AI analyzed which paper when  
✅ **Easy recall** - "What have I learned about X?" queries work instantly  
✅ **Citation provenance** - Every citation linked to AI handoffs  
✅ **Knowledge graphs** - See relationships between papers and concepts  
✅ **Multi-AI coordination** - Seamless handoffs between AI assistants  

**Result:** Research with complete provenance, easy recall, and transparent methodology.

---

## Conceptual Workflow (Phase 1 - Manual)

### 1. Understand the Core Idea

The core idea is to create a `.macp/` directory in your research project and use a set of structured JSON files to manually log your research activities. This creates a traceable, auditable history of your work.

### 4. Start your first research session

**Example: Researching "AI Alignment"**

**Step 1:** Discover papers
```bash
# Discover today's papers from Hugging Face
python3 tools/macp_cli.py discover --date 2026-02-09

# Search for specific topics
python3 tools/macp_cli.py discover --query "AI alignment" --limit 10

# Fetch a specific paper by arXiv ID
python3 tools/macp_cli.py discover --arxiv-id 2404.11672
```

**Step 2:** Record what you learned
```bash
python3 tools/macp_cli.py learn "Key insight from the paper" \
  --papers "2404.11672" --agent "manus-ai" --tags "alignment,safety"
```

**Step 3:** Cite in your projects
```bash
python3 tools/macp_cli.py cite "2404.11672" \
  --project "GODELAI" --context "Informs our approach to alignment"
```

**Step 4:** Recall what you've learned
```bash
python3 tools/macp_cli.py recall "AI alignment"
```

**Step 5:** Check your knowledge base
```bash
python3 tools/macp_cli.py status
```

**Done!** Full C-S-P research workflow with complete provenance.

---

## How It Works

### The MACP Research Workflow

```
┌─────────────────┐
│ 1. Discovery    │  Find papers (Manus AI, Perplexity)
│    (Manus AI)   │  → Update research_papers.json
└────────┬────────┘
         │
         ↓ Handoff via GitHub
┌─────────────────┐
│ 2. Analysis     │  Deep reading (Claude Code)
│  (Claude Code)  │  → Update research_papers.json (insights)
└────────┬────────┘
         │
         ↓ Handoff via GitHub
┌─────────────────┐
│ 3. Validation   │  Cross-reference (Perplexity)
│  (Perplexity)   │  → Update learning_log.json
└────────┬────────┘
         │
         ↓ Handoff via GitHub
┌─────────────────┐
│ 4. Synthesis    │  Knowledge graph (Manus AI)
│   (Manus AI)    │  → Update knowledge_graph.json
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 5. Citation     │  Use in projects
│   (Any AI)      │  → Update citations.json
└─────────────────┘
```

**Key Innovation:** GitHub serves as the communication bridge. All AI assistants read/write to `.macp/` directory.

---

## Features

### 1. **Complete Research Traceability**

Every paper, insight, and citation is tracked:

- **Who discovered it?** (which AI assistant)
- **When was it analyzed?** (timestamp)
- **What insights were extracted?** (key learnings)
- **Where was it cited?** (which projects)
- **How does it relate?** (knowledge graph)

### 2. **Multi-AI Coordination**

Seamlessly coordinate research across:

- **Manus AI** - Discovery, synthesis, knowledge graphs
- **Claude Code** - Deep reading, technical analysis
- **Perplexity** - Validation, cross-referencing
- **ChatGPT** - Brainstorming, ideation
- **Gemini** - Alternative perspectives
- **Kimi K2** - Testing, verification

**All tracked in one place.**

### 3. **Easy Recall**

Query your research history:

> "What have I learned about AI alignment?"

**Response:**
```
You studied 5 papers on AI alignment between Feb 1-15, 2026.

Key Learnings:
1. Conflict data improves alignment (arxiv:2026.01234)
2. T-Score 0.3-0.5 is optimal range (arxiv:2026.01235)
3. No large-scale dataset exists (arxiv:2026.01236)

AI Agents Used:
- Manus AI: Discovery (5 papers)
- Claude Code: Analysis (5 papers)
- Perplexity: Validation (3 papers)

Citations in Your Projects:
- GODELAI C-S-P design (2 citations)
- VerifiMind-PEAS methodology (1 citation)
```

### 4. **Citation Provenance**

Every citation is linked to its source:

```json
{
  "citation_id": "cite-001",
  "paper_id": "arxiv:2026.01234",
  "cited_in": "GODELAI C-S-P design",
  "cited_by_agent": "manus-ai",
  "handoff_id": "handoff-003",
  "date": "2026-02-12",
  "context": "T-Score range for conflict data"
}
```

**Transparent methodology for academic credibility.**

### 5. **Knowledge Graphs**

Visualize relationships:

```
┌──────────────┐     introduces     ┌──────────────┐
│ Paper A      │ ──────────────────→ │ Concept X    │
│ (arxiv:2026) │                     │ (T-Score)    │
└──────────────┘                     └──────────────┘
       │                                     │
       │ provides_dataset                   │ applicable_to
       ↓                                     ↓
┌──────────────┐                     ┌──────────────┐
│ Dataset Y    │                     │ Project Z    │
│ (conflict)   │                     │ (GODELAI)    │
└──────────────┘                     └──────────────┘
```

**See the big picture of your research.**

---

## Ecosystem Alignment

This project is a foundational protocol within the broader **YSenseAI Ecosystem**. It serves as a specific, public-facing application of the core principles defined in the central command hub.

- **Command Central Hub:** [verifimind-genesis-mcp](https://github.com/creator35lwb-web/verifimind-genesis-mcp)
- **Unified Ecosystem Roadmap:** [YSenseAIEcosystemMap&UnifiedRoadmap(Feb2026).md](https://github.com/creator35lwb-web/verifimind-genesis-mcp/blob/main/ecosystem/YSenseAIEcosystemMap%26UnifiedRoadmap(Feb2026).md)

This repository's MACP specification is a simplified version intended for broad adoption. The authoritative, internal MACP v2.0 specification that governs the entire ecosystem resides in the `verifimind-genesis-mcp` repository.

## Use Cases

### 1. **Academic Research**

Track papers, insights, and citations for your thesis or dissertation.

**Benefits:**
- Complete bibliography with provenance
- Easy recall of past research
- Transparent methodology for reviewers

### 2. **Industry Research**

Stay up-to-date with latest papers in your field.

**Benefits:**
- Daily paper tracking (like hysts/daily-papers)
- Multi-AI analysis for deeper understanding
- Knowledge graph shows industry trends

### 3. **Project Development**

Research foundation for technical projects (like GODELAI, VerifiMind-PEAS).

**Benefits:**
- Citation network for design documents
- Research evolution visible to community
- Transparent methodology for validation

### 4. **Learning & Education**

Track what you've learned over time.

**Benefits:**
- "What have I learned?" queries
- Knowledge graph shows learning progression
- Review past insights easily

---

## Implementation Phases

### Phase 1: Manual MACP (Start Here)

**Effort:** 2-3 hours setup  
**Automation:** 0% (manual updates)  
**Benefit:** Immediate value, complete traceability  

**What you do:**
1. Create `.macp/` folder in your project
2. Use provided templates
3. Manually update after each AI session
4. Commit to GitHub

**Time per session:** 5-10 minutes  
**ROI:** Positive after 3-4 research sessions  

**Status:** ✅ Ready to use today

---

### Phase 2: Semi-Automated (Implemented)

**Effort:** CLI-ready  
**Automation:** 50% (scripts handle metadata)  
**Benefit:** 50% time savings  

**What's built:**
- `macp discover` — Paper fetcher with 3 pipelines (HF Daily Papers, HF MCP Search, arXiv API)
- `macp learn` — Learning log CLI with paper linking
- `macp cite` — Citation tracker with project linking
- `macp recall` — "What have I learned?" query engine
- `macp status` — Knowledge base dashboard
- Knowledge graph generator with provenance tracing

**Time per session:** 2-3 minutes  
**ROI:** Positive after 10-15 research sessions  

**Status:** ✅ Implemented (Feb 2026)

---

### Phase 3: Full MCP Server (Long-term)

**Effort:** 2-3 months development  
**Automation:** 90% (AI-powered)  
**Benefit:** Seamless workflow  

**What you'll build:**
- MACP MCP Server
- Integration with gpt-researcher
- Knowledge graph visualization
- "What have I learned?" query interface
- Multi-AI orchestration

**Time per session:** 30 seconds (just review)  
**ROI:** Positive after 50+ research sessions  

**Status:** 📋 Roadmap (Q3-Q4 2026)

---

## Repository Structure

macp-research-assistant/
├── .macp/                    # Example MACP directory (conceptual)
│   ├── research_papers.json
│   ├── learning_log.json
│   ├── citations.json
│   ├── knowledge_graph.json
│   └── handoffs.json
│
├── docs/                     # Core Documentation
│   ├── QUICK_START.md
│   ├── MACP_SPECIFICATION.md
│   └── ARCHITECTURE.md
│
├── peas/                     # VerifiMind-PEAS Trinity Validation reports
│   ├── TRINITY_VALIDATION_REPORT.md
│   ├── X_AGENT_VALIDATION_GEMINI.md
│   ├── Z_AGENT_VALIDATION_ANTHROPIC.md
│   └── CS_AGENT_VALIDATION_MANUS.md
│
├── tools/                    # Automation tools (Phase 2) ✅
│   ├── __init__.py           # Package init
│   ├── paper_fetcher.py      # 3-pipeline paper discovery engine
│   ├── macp_cli.py           # CLI orchestrator (discover/learn/cite/recall/status)
│   └── knowledge_graph.py    # Knowledge graph + provenance tracer
│
├── templates/                # JSON templates for the conceptual workflow
│   ├── ... (template files)
│
└── README.md                 # This file                 # This file
├── LICENSE                   # MIT License
└── CONTRIBUTING.md           # Contribution guidelines
```

---

## Integration with Existing Tools

### Hugging Face Papers

**API:** https://huggingface.co/api/papers

**Use:**
- Discover curated papers
- Get metadata automatically
- Track daily papers (like hysts/daily-papers)

**Integration:**
```python
import requests

response = requests.get("https://huggingface.co/api/papers")
papers = response.json()

# Add to research_papers.json
for paper in papers:
    # ... populate MACP template
```

---

### gpt-researcher MCP Server

**Repository:** https://github.com/assafelovic/gptr-mcp

**Use:**
- Deep research via Claude Desktop
- Automatic report generation
- Source tracking

**Integration:**
- Install gpt-researcher MCP in Claude Desktop
- Use for deep research phase
- Results automatically populate MACP

---

### arxiv_daily_aigc

**Repository:** https://github.com/onion-liu/arxiv_daily_aigc

**Use:**
- Daily paper crawler
- AI-powered analysis
- Automated discovery

**Integration:**
- Run daily to discover papers
- Output populates research_papers.json
- Commit to GitHub automatically

---

## Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get started in 5 minutes
- **[MACP Specification](docs/MACP_SPECIFICATION.md)** - MACP v2.0 protocol
- **[Architecture](docs/ARCHITECTURE.md)** - System design
- **[Best Practices](docs/BEST_PRACTICES.md)** - Tips and tricks
- **[FAQ](docs/FAQ.md)** - Common questions

---

## Examples

### GODELAI Conflict Data Research

See how MACP was used to track research for the GODELAI project:

- **[Example: GODELAI Conflict Data](examples/godelai-conflict-data/)**

**Key insights:**
- 15 papers discovered and analyzed
- 3 AI assistants coordinated (Manus, Claude, Perplexity)
- Complete citation network for C-S-P design
- Knowledge graph shows research evolution

---

### Daily Paper Tracking

See how to track daily papers from Hugging Face:

- **[Example: Daily Papers Tracking](examples/daily-papers-tracking/)**

**Workflow:**
1. Morning: Discover papers from hysts/daily-papers
2. Filter: Tag by relevance
3. Commit: Push to GitHub
4. Review: Weekly synthesis

**Time:** 5 minutes/day  
**Benefit:** Never miss important papers

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**
- 📝 Improve documentation
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Build Phase 2 tools
- 🎨 Create examples
- 🌐 Translate to other languages

---

## Roadmap

### Q1 2026 (Current)

- ✅ Phase 1: Manual MACP implementation
- ✅ Templates and documentation
- ✅ Real-world examples (GODELAI)
- 🔄 Community feedback and iteration

### Q1 2026 (Phase 2 — Completed)

- ✅ Phase 2: Semi-automated tools
- ✅ Paper metadata fetcher (3 pipelines)
- ✅ CLI orchestrator with C-S-P workflow
- ✅ Citation tracker with project linking
- ✅ Knowledge graph generator with provenance tracing
- ✅ JSON schemas for all data files
- ✅ Ethical use guidelines
- ✅ Ecosystem alignment documentation

### Q3-Q4 2026

- 📋 Phase 3: Full MCP server
- 📋 Integration with gpt-researcher
- 📋 Knowledge graph visualization
- 📋 "What have I learned?" query interface
- 📋 Multi-AI orchestration

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Citation

If you use MACP-Powered AI Research Assistant in your research, please cite:

```bibtex
@software{macp_research_assistant_2026,
  author = {YSenseAI Team},
  title = {MACP-Powered AI Research Assistant},
  year = {2026},
  url = {https://github.com/creator35lwb-web/macp-research-assistant}
}
```

---

## Related Projects

- **[VerifiMind-PEAS](https://github.com/creator35lwb-web/VerifiMind-PEAS)** - Ethical AI verification methodology
- **[GODELAI](https://github.com/creator35lwb-web/godelai)** - AI alignment research project
- **[LegacyEvolve](https://github.com/creator35lwb-web/LegacyEvolve)** - MACP v2.0 specification

---

## Contact

- **Project:** YSenseAI™ | 慧觉™
- **GitHub:** [@creator35lwb-web](https://github.com/creator35lwb-web)
- **X (Twitter):** [@creator35lwb](https://x.com/creator35lwb)
- **Email:** creator35lwb@gmail.com
- **Website:** [verifimind.io](https://verifimind.io)

---

## Acknowledgments

- **MACP Protocol:** Based on MACP v2.0 from LegacyEvolve project
- **Inspiration:** SimpleMem paper discovery for GODELAI project
- **Tools:** Hugging Face Papers, gpt-researcher, arxiv_daily_aigc

---

**Start tracking your research with complete provenance today!**

```bash
git clone https://github.com/creator35lwb-web/macp-research-assistant.git
cd macp-research-assistant
cp -r .macp /path/to/your/project/
# Start researching!
```

---

**Made with ❤️ by the YSenseAI™ Team**
