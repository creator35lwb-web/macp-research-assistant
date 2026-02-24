# FLYWHEEL TEAM — Strategic Alignment: MACP v2.0 × VerifiMind-PEAS v0.5.0

**Author:** CSO R (Manus AI)
**Date:** 2026-02-24
**Type:** Strategic Architecture Alignment
**Classification:** TEAM-INTERNAL → PUBLIC-READY

---

## Executive Summary

This document formalizes the strategic relationship between the MACP Research Assistant and the VerifiMind-PEAS MCP Server. The user's vision is correct and architecturally sound: MACP v2.0 is not merely a research tool — it is a **protocol that becomes a tool** inside VerifiMind-PEAS. This document defines exactly how these two systems converge in VerifiMind-PEAS v0.5.0.

---

## 1. Answering the Strategic Vision

### 1.1 "Is this actually a product of MACP v2.0?"

**Yes.** The MACP Research Assistant is the first production implementation of the MACP v2.0 protocol. The distinction matters:

| Layer | What It Is | Where It Lives |
|-------|-----------|----------------|
| **MACP v2.0 Protocol** | A specification for how AI agents store, share, and converge research analyses in a Git-compatible directory structure | `.macp/schema.json` in any GitHub repo |
| **MACP Research Assistant** | A web application that implements the MACP v2.0 protocol for human users | `macpresearch.ysenseai.org` |
| **MACP v2.0 MCP Tool** | A programmatic interface that exposes MACP v2.0 operations as MCP tools for AI agents | Future: inside VerifiMind-PEAS |

The protocol is the standard. The web app is the human interface. The MCP tool is the agent interface. All three share the same `.macp/` directory structure and `schema.json` specification.

### 1.2 "Not documentation by thesis but practically applying?"

**Exactly right.** This is the key differentiator. Most research protocols exist only as papers. MACP v2.0 exists as:

1. **Running code** — 12,839+ papers searchable, 61 papers saved, analysis pipeline working
2. **Structured data** — Every paper, analysis, and note stored as JSON in `.macp/research/`
3. **Agent registry** — 6 AI agents formally registered with capabilities and cost tiers
4. **Schema specification** — `schema.json` that any new agent can read to understand the entire system
5. **Production deployment** — Live at `macpresearch.ysenseai.org` on GCP Cloud Run

This is **protocol-by-implementation**, not protocol-by-thesis.

### 1.3 "Will this improve VerifiMind-PEAS validation?"

**Yes, through a feedback loop.** The relationship is bidirectional:

```
Research Discovery (MACP)
    → Deeper understanding of LLM behavior
    → Better validation prompts for PEAS
    → More accurate traffic classification
    → Better validation data
    → Published as research evidence
    → Feeds back into MACP library
```

When you research papers about "multi-agent collaboration" or "LLM reasoning," the insights directly improve how VerifiMind-PEAS validates AI-generated content. The research tool makes the validation tool smarter.

---

## 2. VerifiMind-PEAS v0.5.0 Architecture

### 2.1 Two Major Tools

The user's vision for v0.5.0 is architecturally correct. VerifiMind-PEAS v0.5.0 consists of two complementary tool suites:

```
VerifiMind-PEAS v0.5.0
├── Tool Suite 1: PEAS Validation Engine (existing)
│   ├── traffic_classification    → Classify AI vs human content
│   ├── validate_content          → Run PEAS methodology
│   ├── generate_report           → Produce validation evidence
│   └── z_protocol_check          → Z Protocol guardian
│
└── Tool Suite 2: MACP Research Engine (new)
    ├── macp.search               → Search 12,839+ papers
    ├── macp.analyze              → Multi-agent paper analysis
    ├── macp.save                 → Save to GitHub-first library
    ├── macp.consensus            → Generate multi-agent consensus
    ├── macp.deep_research        → Perplexity-powered deep dive
    └── macp.knowledge_graph      → Citation network analysis
```

### 2.2 How They Work Together

**Scenario: User asks Claude Desktop to validate a new AI technique**

1. Claude Desktop calls `macp.search` → finds 5 relevant papers
2. Claude Desktop calls `macp.analyze` → gets Gemini + Claude analysis
3. Claude Desktop calls `macp.consensus` → generates agreement report
4. Claude Desktop calls `validate_content` → runs PEAS validation using research context
5. Claude Desktop calls `generate_report` → produces evidence report enriched with citations

The research engine provides **context** that makes the validation engine **smarter**. Without MACP, PEAS validates in isolation. With MACP, PEAS validates with the full weight of relevant research behind it.

### 2.3 Value Proposition for Users

| User Type | Without MACP | With MACP in PEAS v0.5.0 |
|-----------|-------------|--------------------------|
| **Researcher** | Manual paper search, isolated analysis | AI-powered multi-agent analysis with consensus |
| **Developer** | Validate code without research context | Validate with relevant methodology papers cited |
| **Enterprise** | Binary AI/human classification | Classification backed by published research evidence |
| **Open Source** | Trust the tool's output | Verify the tool's reasoning through its research library |

---

## 3. The Paper Count Question: Why 55+ and Not 12,839+?

### 3.1 The Honest Answer

The "55+" (actually 61) number represents **papers that users have actively saved to their library**, not the total papers available. Here is the full picture:

| Metric | Count | Source |
|--------|-------|--------|
| **Papers available via hysts dataset** | 12,839 | `hysts-bot-data/daily-papers` HuggingFace dataset |
| **Papers available via HF search** | 120+ per query | `huggingface.co/api/papers/search` |
| **Papers available via arXiv** | 2.4M+ | `export.arxiv.org/api/query` |
| **Papers available via HF Daily** | ~18/day | `huggingface.co/api/daily_papers` |
| **Papers saved to local library** | 61 | `.macp/research/` directory |
| **Papers in production database** | ~61 | SQLite on Cloud Run (ephemeral) |

### 3.2 Why Not All HuggingFace Papers?

The search pipeline **already accesses all 12,839+ papers** in real-time. When you search "multi-agent" on the webapp, it queries the hysts dataset and returns matching results from the full 12,839 papers. The "55+" number on the landing page refers to papers that have been explicitly saved and analyzed — the curated research library.

### 3.3 Live Updates

New papers published on HuggingFace Daily Papers are **already available in real-time**. The search endpoint queries the live API:

- `https://huggingface.co/api/daily_papers?date=2026-02-24` → returns 18 papers published today
- The hysts dataset is continuously updated by the hysts-bot, adding new papers as they are published
- No manual update is needed — the search always hits the live API

### 3.4 What We Should Update

The landing page stat should be more accurate. Instead of "55+ Research Papers," it should say something like:

- **12,800+ Papers Searchable** (from hysts dataset)
- **61 Papers in Library** (user-curated collection)

This is a simple landing page text update. The underlying capability is already there.

---

## 4. Recommended Landing Page Update

```
Current:  "55+ Research Papers"
Proposed: "12,800+ Papers Searchable"
```

And add a second stat:
```
Current:  (none)
Proposed: "61 Curated & Analyzed"
```

---

## 5. Implementation Roadmap for VerifiMind-PEAS v0.5.0

### Sprint 1: MACP MCP Tool Wrapper (CTO RNA)

Wrap the existing MACP backend endpoints as MCP-compatible tools that can be called from Claude Desktop, Cursor, or any MCP client.

```python
# New file: verifimind-genesis-mcp/tools/macp_research.py
@tool("macp.search")
def search_papers(query: str, source: str = "hysts", limit: int = 10):
    """Search 12,800+ ML papers across arXiv, HuggingFace, and Semantic Scholar."""
    # Calls the existing MACP backend API
    ...

@tool("macp.analyze")
def analyze_paper(arxiv_id: str, provider: str = "gemini"):
    """Analyze a paper using the specified AI agent."""
    ...
```

### Sprint 2: Cross-Tool Integration

Enable PEAS validation tools to optionally call MACP tools for research context enrichment.

### Sprint 3: Unified GitHub Persistence

Both PEAS validation reports and MACP research analyses write to the same `.macp/` directory in the user's project repo.

---

## 6. Updated Landing Page Stats Recommendation

| Current | Proposed | Rationale |
|---------|----------|-----------|
| 6 AI Agents | 6 AI Agents | Accurate |
| 55+ Research Papers | 12,800+ Papers Searchable | Reflects actual dataset size |
| 8 WebMCP Tools | 8 WebMCP Tools | Accurate |
| v2.0 MACP Schema | v2.0 MACP Schema | Accurate |

---

## 7. Conclusion

The user's strategic vision is not only workable — it is the natural evolution of both projects. MACP v2.0 provides the **research intelligence layer** that VerifiMind-PEAS has always needed. Together, they form a complete system: research informs validation, validation generates evidence, evidence becomes research. This is the flywheel.

VerifiMind-PEAS v0.5.0 = PEAS Validation Engine + MACP Research Engine.

**Next action:** CTO RNA to create the MCP tool wrapper for MACP endpoints in `verifimind-genesis-mcp`.

---

*CSO R (Manus AI) — FLYWHEEL TEAM*
*YSenseAI™ | 慧觉™*
