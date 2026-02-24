# FLYWHEEL TEAM — Phase 4 Sprint Plan: Knowledge Intelligence

**Author:** CSO R (Manus AI)
**Date:** 2026-02-25
**Type:** Sprint Plan + Execution Guidance
**Protocol:** MACP v2.0 / Multi-Agent Handoff Bridge
**Milestone:** v1.0.0 Released (confirmed via `gh release view v1.0.0`)

---

## 1. Where We Stand

### v1.0.0 Production State

| Metric | Value |
|--------|-------|
| GitHub Release | `v1.0.0 — MACP Research Assistant` (122 commits since v0.1.0-alpha) |
| Cloud Run Revision | `macp-research-assistant-00022-n5d` |
| CI Status | ALL GREEN (CI #28 + Security #28) |
| Open Issues / PRs / Alerts | 0 / 0 / 0 |
| MCP Endpoints | 13 live-tested |
| Agent Registry | 6 agents (Gemini, Claude, GPT-4o, Grok, Perplexity, Manus) |
| Papers Searchable | 12,800+ (live from HuggingFace + arXiv) |
| Papers in Library | 61 directories in `.macp/research/`, 1 in manifest |
| Analyses | 1 consensus analysis (arxiv_2509.11648) |
| VerifiMind-PEAS v0.5.0 | 6 MCP tool wrappers built (`v050-macp-tools/`) |

### What Phase 3 Delivered (Complete Arc)

The entire Phase 3 arc (3A through 3F) was completed in approximately 3 weeks. The platform went from a CLI-only tool to a production-deployed web application with multi-agent consensus, deep PDF analysis, Perplexity integration, BYOK privacy guarantees, and a clean CI/CD pipeline.

### What Phase 4 Must Deliver

Phase 4 transforms the MACP Research Assistant from a **paper analysis tool** into a **knowledge intelligence platform**. The key difference: Phase 3 answered "What does this paper say?" — Phase 4 answers "How do all these papers connect, and what does the research landscape look like?"

---

## 2. Phase 4 Sprint Structure

Phase 4 is organized into 3 sprints, each building on the previous:

### Sprint 4A — Knowledge Graph UI (P0)

> **Goal:** Visualize paper relationships, citation networks, and research themes in the web UI
> **Owner:** CTO RNA (Claude Code)
> **Duration:** 1-2 sessions

The knowledge graph backend already exists from Phase 2 (`.macp/knowledge_graph.json`). The frontend has a placeholder. This sprint connects them.

| Task | Description | Acceptance Criteria |
|------|-------------|-------------------|
| **Knowledge Graph Data Endpoint** | Create `/api/mcp/knowledge-graph` endpoint that reads `.macp/knowledge_graph.json` and returns nodes + edges | Returns JSON with nodes (papers) and edges (citations, shared themes) |
| **Graph Visualization Component** | Build interactive graph using D3.js or vis-network in `KnowledgeGraph.tsx` | Nodes are clickable (open paper detail), edges show relationship type |
| **Graph Filters** | Filter by: research theme, date range, analysis status, agent | User can narrow the graph to specific research areas |
| **Graph Layout** | Force-directed layout with zoom/pan, node size by citation count | Graph is readable with 50+ papers |
| **Integration with Library** | Papers in My Library appear as highlighted nodes | User can see which papers they've saved vs. discovered |

**Technical Notes:**
- The existing `knowledge_graph.py` in the backend generates graph data from `.macp/research/` directories
- Consider using `react-force-graph-2d` (lightweight, React-native) or `vis-network` (feature-rich)
- Node colors should match the analysis type color scheme (green=AI, blue=deep, purple=consensus)
- The graph should update when new papers are saved or analyzed

### Sprint 4B — Research Templates & Citation Networks (P1)

> **Goal:** Pre-built analysis workflows for specific research domains + citation chain tracking
> **Owner:** CTO RNA (Claude Code)
> **Duration:** 1-2 sessions

| Task | Description | Acceptance Criteria |
|------|-------------|-------------------|
| **Research Templates** | Pre-built analysis configurations for domains: AI Safety, Multi-Agent Systems, LLM Evaluation, Ethical AI, Formal Verification | User selects a template, it pre-fills search queries + analysis prompts |
| **Template UI** | Template selector in Search panel with description and suggested queries | Templates are discoverable and easy to use |
| **Citation Extraction** | Extract references from analyzed papers (from deep PDF analysis text) | Each paper shows its cited references as links |
| **Citation Network** | Build citation chains: Paper A cites Paper B, Paper B cites Paper C | Citation graph is navigable; user can follow citation chains |
| **Cross-Paper Comparison** | Compare methodology, findings, and limitations across 2-3 papers side-by-side | Comparison view shows aligned sections for easy reading |

**Technical Notes:**
- Research templates should be stored as JSON in `.macp/templates/` and be schema-validated
- Citation extraction can use regex patterns on the deep analysis text (references section)
- The citation network extends the knowledge graph with directional edges

### Sprint 4C — Platform Integration & Ecosystem (P2)

> **Goal:** Make the research assistant accessible to other tools and workflows
> **Owner:** FLYWHEEL TEAM
> **Duration:** 2-3 sessions

| Task | Description | Acceptance Criteria |
|------|-------------|-------------------|
| **VerifiMind-PEAS v0.5.0 Integration** | Register the 6 MACP tools in the main VerifiMind-PEAS MCP server | `macp_search`, `macp_analyze`, `macp_consensus` available in Claude Desktop |
| **n8n Workflow Integration** | Create n8n workflow templates for: daily paper digest, trend alerts, weekly research summary | Workflows trigger via webhook and produce structured output |
| **Notification System** | Alert the Orchestrator when: new high-relevance papers found, consensus reached, citation chain discovered | Notifications via existing `notifyOwner()` pattern |
| **Export & Sharing** | Export research collection as: Markdown report, BibTeX, PDF literature review | User can download their research in portable formats |
| **GODELAI Research Collection** | Use the platform to build a GODELAI-specific research library on AI alignment, formal verification, ethical AI | 20+ papers analyzed with multi-agent consensus on key topics |

**Technical Notes:**
- The 6 MCP tool wrappers already exist in `verifimind-genesis-mcp/v050-macp-tools/`
- n8n integration uses the `N8N_INSTANCE_URL` and `N8N_API_KEY` already available
- The GODELAI research collection serves as both a real use case and a validation of the platform

---

## 3. Priority Matrix

| Sprint | Priority | Effort | Impact | Dependencies |
|--------|----------|--------|--------|-------------|
| **4A: Knowledge Graph UI** | P0 | Medium | High | Backend exists, frontend placeholder exists |
| **4B: Research Templates** | P1 | Medium | Medium | Requires 4A for visualization |
| **4C: Platform Integration** | P2 | High | High | Requires 4A + 4B for full value |

### Recommended Execution Order

```
Sprint 4A (Knowledge Graph UI)
    │
    ├── Graph endpoint + D3 visualization
    ├── Filters + layout
    └── Library integration
    │
    ▼
Sprint 4B (Research Templates + Citations)
    │
    ├── Template system + UI
    ├── Citation extraction from deep analysis
    └── Cross-paper comparison view
    │
    ▼
Sprint 4C (Platform Integration)
    │
    ├── VerifiMind-PEAS v0.5.0 registration
    ├── n8n workflows
    ├── Export system
    └── GODELAI research collection
```

---

## 4. Phase 4 Completion Criteria

Phase 4 is considered **COMPLETE** when:

1. Knowledge graph is interactive in the web UI with 50+ papers visualized
2. At least 3 research templates are available and functional
3. Citation extraction works on deep-analyzed papers
4. MACP tools are registered in VerifiMind-PEAS v0.5.0
5. At least one n8n workflow is functional
6. GODELAI research collection has 20+ papers with multi-agent consensus

### Release Target

Upon Phase 4 completion: **v1.1.0** (Knowledge Intelligence Release)

---

## 5. CTO RNA Recommendations from Phase 3F Handoff

CTO RNA suggested these items for the next session (from `20260225_RNA_phase3f-complete.md`):

1. Citation network visualization
2. Knowledge graph improvements
3. Keyboard shortcuts for panel navigation
4. Mobile responsive improvements (detail panel as slide-over)

Items 1-2 are captured in Sprint 4A. Items 3-4 are UX polish that can be addressed alongside Sprint 4A.

---

## 6. Claude Code Prompt for Sprint 4A

> Read `.macp/handoffs/20260225_CSO-R_phase4-sprint-plan.md` in `macp-research-assistant`. Phase 4 Sprint 4A: Build the Knowledge Graph UI. Create `/api/mcp/knowledge-graph` endpoint that reads the existing knowledge graph data and returns nodes + edges. Build `KnowledgeGraph.tsx` component using `react-force-graph-2d` or `vis-network` with force-directed layout, clickable nodes (open paper detail), edge labels (citation/theme), zoom/pan, and filters by research theme and analysis status. Node colors should match the analysis type color scheme. Also add keyboard shortcuts for panel navigation (Ctrl+1/2/3 for sidebar items).

---

*CSO R (Manus AI) — FLYWHEEL TEAM*
*"Phase 3 answered 'What does this paper say?' — Phase 4 answers 'How do all these papers connect?'"*
