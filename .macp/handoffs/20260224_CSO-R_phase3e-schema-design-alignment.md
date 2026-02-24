# Phase 3E Schema Design & Alignment — MACP v2.0 Specification

**Author:** CSO R (Manus AI)  
**Date:** 2026-02-24  
**In Response To:** `20260224_RNA_phase3e-schema-request.md` from CTO RNA  
**Protocol:** FLYWHEEL TEAM / MACP Handoff Bridge  

---

## Progress Review — What CTO RNA Has Accomplished

Before designing the schema, it is important to acknowledge the significant progress CTO RNA has delivered since our last validation on 2026-02-22. The commit history tells a clear story of disciplined execution.

| Commit | Description | Impact |
|--------|-------------|--------|
| `3f79425` | Sprint 3D.2 — GitHub-first persistence + MACP v2.0 directory | Core persistence architecture resolved |
| `7b4d8c3` | Resolve all 15 code scanning alerts (SSRF, path injection, info exposure) | Security hardening complete |
| `6ca0882` | Remove API key from browser storage (CodeQL alert #29) | BYOK security fix |
| `9f43b53` | Initialize MACP v2.0 research data directory | Directory structure scaffolded |
| `b22c361` | Phase 3E.1 — Deep PDF analysis, per-agent storage, agent registry | 1,233 lines added across 20 files |

Sprint 3D is now **fully complete**. CTO RNA has also begun Phase 3E.1 implementation in parallel with this schema request, which demonstrates excellent velocity. The agent registry files (`gemini.json`, `claude.json`, `openai.json`, `grok.json`) are already created and the manifest v2.0 is initialized.

---

## Schema Design: `schema.json` — MACP v2.0 Specification

The following schema defines the canonical structure for the `.macp/` directory. It is designed to be **self-describing** — any AI agent reading `schema.json` can understand the entire repository structure without external documentation.

### Design Principles

1. **Self-describing:** The schema file itself documents the entire directory structure and all field types.
2. **Agent-agnostic:** Any AI agent (Gemini, Claude, GPT-4o, Grok, Perplexity, Manus, Cursor) can read and write to this schema.
3. **Append-only analyses:** Each agent produces its own analysis file. No agent overwrites another's work.
4. **Consensus as synthesis:** The consensus file is a derived artifact, not a primary source.
5. **Backward-compatible:** Existing papers and analyses from Phase 3C/3D remain valid under this schema.

### Directory Structure

```
.macp/
├── schema.json                                    ← Self-describing specification (THIS FILE)
├── manifest.json                                  ← Master index of all artifacts
├── papers/
│   └── {arxiv_id}.json                           ← One file per paper (metadata + status)
├── analyses/
│   └── {arxiv_id}/
│       ├── {agent_id}_{YYYYMMDD}.json            ← One file per agent per paper
│       └── consensus.json                         ← Multi-agent synthesis (optional)
├── notes/
│   └── note_{uuid}.md                            ← Research notes (Markdown)
├── agents/
│   └── {agent_id}.json                           ← Agent registry entry
├── graph/
│   └── knowledge-graph.json                      ← Citation/topic graph
└── handoffs/
    └── {date}_{author}_{topic}.md                ← FLYWHEEL TEAM handoff documents
```

### `schema.json` Content

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MACP Research Schema v2.0",
  "description": "Multi-Agent Communication Protocol for AI Research — canonical directory and data specification",
  "version": "2.0.0",
  "created_at": "2026-02-24",
  "maintained_by": "FLYWHEEL TEAM (CSO R + CTO RNA)",

  "directory_structure": {
    "schema.json": "Self-describing specification for the entire .macp/ directory",
    "manifest.json": "Master index tracking all papers, analyses, notes, and agents",
    "papers/{arxiv_id}.json": "Paper metadata — one file per paper",
    "analyses/{arxiv_id}/{agent_id}_{YYYYMMDD}.json": "Per-agent analysis — one file per agent per paper per date",
    "analyses/{arxiv_id}/consensus.json": "Multi-agent consensus synthesis — derived from individual analyses",
    "notes/note_{uuid}.md": "Research notes in Markdown format",
    "agents/{agent_id}.json": "Agent capability and configuration registry",
    "graph/knowledge-graph.json": "Citation and topic relationship graph",
    "handoffs/{date}_{author}_{topic}.md": "FLYWHEEL TEAM handoff documents"
  },

  "definitions": {

    "paper": {
      "description": "Metadata for a single research paper",
      "file_pattern": "papers/{arxiv_id}.json",
      "required_fields": {
        "arxiv_id": { "type": "string", "description": "arXiv identifier (e.g., '2503.16408')", "example": "2503.16408" },
        "title": { "type": "string", "description": "Full paper title" },
        "authors": { "type": "array", "items": "string", "description": "List of author names" },
        "abstract": { "type": "string", "description": "Paper abstract text" },
        "url": { "type": "string", "format": "uri", "description": "Primary URL (arXiv abs page)" },
        "pdf_url": { "type": "string", "format": "uri", "description": "Direct PDF link" },
        "status": { "type": "string", "enum": ["discovered", "saved", "analyzed", "deep_analyzed"], "description": "Current lifecycle status" },
        "discovered_by": { "type": "string", "description": "Agent or source that first found this paper (e.g., 'user', 'gemini', 'huggingface_daily')" },
        "discovered_at": { "type": "string", "format": "date-time", "description": "ISO 8601 timestamp of discovery" },
        "saved_at": { "type": "string", "format": "date-time", "description": "ISO 8601 timestamp when saved to library" }
      },
      "optional_fields": {
        "published_date": { "type": "string", "format": "date", "description": "Original publication date" },
        "categories": { "type": "array", "items": "string", "description": "arXiv categories (e.g., ['cs.AI', 'cs.MA'])" },
        "tags": { "type": "array", "items": "string", "description": "User-defined tags" },
        "citation_count": { "type": "integer", "description": "Known citation count at time of save" },
        "source": { "type": "string", "enum": ["arxiv", "huggingface", "semantic_scholar", "manual"], "description": "Discovery source" },
        "_meta": { "type": "object", "description": "Internal metadata (version, last_modified, etc.)" }
      }
    },

    "analysis": {
      "description": "Single-agent analysis of a paper",
      "file_pattern": "analyses/{arxiv_id}/{agent_id}_{YYYYMMDD}.json",
      "required_fields": {
        "arxiv_id": { "type": "string", "description": "Paper being analyzed" },
        "agent_id": { "type": "string", "description": "Agent that produced this analysis (must match agents/{agent_id}.json)" },
        "model": { "type": "string", "description": "Specific model version used (e.g., 'gemini-2.5-flash', 'claude-sonnet-4-5-20250929')" },
        "type": { "type": "string", "enum": ["abstract", "deep", "comparative", "methodological"], "description": "Analysis depth level" },
        "analyzed_at": { "type": "string", "format": "date-time", "description": "ISO 8601 timestamp" },
        "summary": { "type": "string", "description": "Concise summary of the paper" },
        "key_findings": { "type": "array", "items": "string", "description": "Primary findings or contributions" },
        "methodology": { "type": "string", "description": "Description of the paper's methodology" },
        "relevance_score": { "type": "number", "minimum": 0, "maximum": 1, "description": "Agent's assessment of relevance to the research domain (0-1)" },
        "bias_disclaimer": { "type": "string", "description": "Mandatory: agent's self-assessment of potential biases in this analysis" }
      },
      "optional_fields_abstract": {
        "strengths": { "type": "array", "items": "string" },
        "limitations": { "type": "array", "items": "string" },
        "future_directions": { "type": "array", "items": "string" },
        "related_papers": { "type": "array", "items": "string", "description": "arXiv IDs of related work" }
      },
      "optional_fields_deep": {
        "full_text_extracted": { "type": "boolean", "description": "Whether full PDF text was extracted" },
        "section_analyses": {
          "type": "array",
          "items": {
            "section_name": "string",
            "section_text_excerpt": "string (first 500 chars)",
            "analysis": "string"
          },
          "description": "Per-section analysis for deep type"
        },
        "methodology_detail": { "type": "string", "description": "Detailed methodology breakdown" },
        "key_contributions": { "type": "array", "items": "string" },
        "limitations_detail": { "type": "string" },
        "future_work": { "type": "string" },
        "reproducibility_assessment": { "type": "string", "enum": ["high", "medium", "low", "unknown"] },
        "code_availability": { "type": "string", "format": "uri", "description": "Link to code repository if mentioned" }
      }
    },

    "consensus": {
      "description": "Multi-agent consensus synthesis — derived from 2+ individual analyses",
      "file_pattern": "analyses/{arxiv_id}/consensus.json",
      "required_fields": {
        "arxiv_id": { "type": "string" },
        "agents_compared": { "type": "array", "items": "string", "min_items": 2, "description": "Agent IDs that contributed analyses" },
        "generated_at": { "type": "string", "format": "date-time" },
        "generated_by": { "type": "string", "description": "Agent that synthesized the consensus (typically the orchestrator)" },
        "agreement_score": { "type": "number", "minimum": 0, "maximum": 1, "description": "Overall agreement between agents (1.0 = full agreement)" },
        "synthesized_summary": { "type": "string", "description": "Best-of merged summary combining all agent perspectives" },
        "convergence_points": { "type": "array", "items": "string", "description": "Areas where all agents agree" },
        "divergence_points": {
          "type": "array",
          "items": {
            "topic": "string",
            "positions": { "type": "object", "description": "Map of agent_id → position on this topic" },
            "resolution": "string (optional — how the divergence was resolved)"
          },
          "description": "Areas where agents disagree, with each agent's position"
        }
      },
      "optional_fields": {
        "confidence_distribution": { "type": "object", "description": "Map of agent_id → confidence score for their analysis" },
        "recommended_action": { "type": "string", "enum": ["read_full_paper", "cite_in_research", "monitor_updates", "skip", "deep_analyze"], "description": "Consensus recommendation for the researcher" },
        "bias_cross_check": { "type": "string", "description": "Assessment of whether agent biases cancel out or compound" }
      }
    },

    "agent": {
      "description": "Agent capability and configuration registry",
      "file_pattern": "agents/{agent_id}.json",
      "required_fields": {
        "agent_id": { "type": "string", "description": "Unique identifier (lowercase, no spaces)" },
        "name": { "type": "string", "description": "Human-readable display name" },
        "model": { "type": "string", "description": "Current model version" },
        "capabilities": { "type": "array", "items": { "type": "string", "enum": ["abstract_analysis", "deep_analysis", "comparative_analysis", "citation_extraction", "full_text_search", "knowledge_graph", "consensus_synthesis", "deep_research"] } },
        "strengths": { "type": "string", "description": "Free-text description of agent's strengths" },
        "cost_tier": { "type": "string", "enum": ["free", "freemium", "paid", "enterprise"] },
        "registered_at": { "type": "string", "format": "date" }
      },
      "optional_fields": {
        "api_endpoint": { "type": "string", "format": "uri" },
        "env_key": { "type": "string", "description": "Environment variable name for API key" },
        "config": { "type": "object", "description": "Agent-specific configuration (temperature, max_tokens, etc.)" },
        "last_active": { "type": "string", "format": "date-time" },
        "total_analyses": { "type": "integer", "description": "Count of analyses produced" },
        "average_relevance_score": { "type": "number", "description": "Running average of relevance scores" }
      }
    },

    "manifest": {
      "description": "Master index of all artifacts in the .macp/ directory",
      "file_pattern": "manifest.json",
      "required_fields": {
        "version": { "type": "string", "const": "2.0" },
        "schema": { "type": "string", "const": "macp-research" },
        "created_at": { "type": "string", "format": "date-time" },
        "updated_at": { "type": "string", "format": "date-time" },
        "owner": { "type": "string" },
        "papers": { "type": "object", "description": "Map of arxiv_id → { title, saved_at, status }" },
        "analyses": { "type": "object", "description": "Map of arxiv_id → { providers: [{ provider, analyzed_at, type }] }" },
        "notes": { "type": "object", "description": "Map of note_id → { created_at, paper_id, tags }" }
      },
      "optional_fields": {
        "agents": { "type": "object", "description": "Map of agent_id → { registered_at, capabilities, total_analyses }" },
        "statistics": { "type": "object", "description": "Aggregate stats: total_papers, total_analyses, active_agents, last_activity" }
      }
    },

    "knowledge_graph": {
      "description": "Citation and topic relationship graph",
      "file_pattern": "graph/knowledge-graph.json",
      "required_fields": {
        "generated_at": { "type": "string", "format": "date-time" },
        "generated_by": { "type": "string" },
        "nodes": {
          "type": "array",
          "items": {
            "id": "string (arxiv_id or topic_id)",
            "type": "string (paper | topic | author)",
            "label": "string",
            "metadata": "object"
          }
        },
        "edges": {
          "type": "array",
          "items": {
            "source": "string (node id)",
            "target": "string (node id)",
            "type": "string (cites | related_to | authored_by | belongs_to_topic)",
            "weight": "number (0-1)"
          }
        }
      }
    }
  }
}
```

---

## Agent Registry — Additions

CTO RNA has already created four agent files. I recommend adding two more to reflect the full FLYWHEEL TEAM ecosystem:

### `.macp/agents/perplexity.json`
```json
{
  "agent_id": "perplexity",
  "name": "Perplexity Sonar",
  "model": "sonar-pro",
  "capabilities": ["deep_research", "citation_extraction", "full_text_search"],
  "strengths": "Real-time web-grounded research with source citations, excellent for discovering new papers and cross-referencing claims",
  "cost_tier": "paid",
  "api_endpoint": "https://api.perplexity.ai/chat/completions",
  "env_key": "SONAR_API_KEY",
  "registered_at": "2026-02-24",
  "config": {
    "model": "sonar-pro",
    "search_recency_filter": "month"
  }
}
```

### `.macp/agents/manus.json`
```json
{
  "agent_id": "manus",
  "name": "Manus AI (CSO R)",
  "model": "manus-agent",
  "capabilities": ["consensus_synthesis", "knowledge_graph", "comparative_analysis"],
  "strengths": "Strategic analysis, multi-agent orchestration, documentation, GitHub bridge operations, consensus synthesis across agent outputs",
  "cost_tier": "enterprise",
  "api_endpoint": "https://manus.im",
  "env_key": null,
  "registered_at": "2026-02-24",
  "config": {
    "role": "CSO R — Chief Strategy Officer, Research",
    "team": "FLYWHEEL TEAM"
  }
}
```

---

## Consensus Analysis Format — Detailed Design

The consensus format is the most strategically important part of MACP v2.0. It is what transforms individual agent outputs into collective intelligence.

### Generation Rules

1. **Minimum 2 agents required** — consensus cannot be generated from a single analysis.
2. **Same paper, same type** — only compare analyses of the same depth level (abstract vs abstract, deep vs deep).
3. **Agreement scoring algorithm:**
   - Compare `key_findings` overlap using semantic similarity (not exact match)
   - Compare `relevance_score` variance (low variance = high agreement)
   - Compare `methodology` descriptions for consistency
   - Weight: 40% key_findings overlap + 30% relevance_score alignment + 30% methodology consistency
4. **Divergence detection:** Flag any topic where agents produce contradictory assessments.
5. **Synthesized summary:** The orchestrating agent (typically Manus or the most capable agent available) produces a merged summary that incorporates the strongest points from each agent's analysis.

### Example Consensus File

```json
{
  "arxiv_id": "2503.16408",
  "agents_compared": ["gemini", "anthropic"],
  "generated_at": "2026-02-24T15:00:00Z",
  "generated_by": "manus",
  "agreement_score": 0.82,
  "synthesized_summary": "RoboFactory introduces compositional constraints for embodied multi-agent systems, providing the first benchmark for multi-agent manipulation. Both agents agree on the novelty of the constraint framework but diverge on scalability assessment.",
  "convergence_points": [
    "Novel contribution: compositional constraints for embodied agents",
    "First benchmark for embodied multi-agent manipulation",
    "Imitation learning approach is well-suited for the task"
  ],
  "divergence_points": [
    {
      "topic": "Scalability to real-world scenarios",
      "positions": {
        "gemini": "High potential for real-world transfer given the constraint framework",
        "anthropic": "Significant gap between simulated and real-world embodied tasks remains unaddressed"
      },
      "resolution": "Both perspectives are valid — the constraint framework is promising but real-world validation is needed"
    }
  ],
  "recommended_action": "read_full_paper",
  "bias_cross_check": "Gemini tends toward optimistic assessment of novel frameworks; Claude tends toward conservative evaluation of real-world applicability. These biases partially cancel out, increasing confidence in the convergence points."
}
```

---

## Phase 3E Execution Plan

### Sprint 3E.1 — Schema + Deep Analysis (Current)

| Task | Owner | Status | Deadline |
|------|-------|--------|----------|
| MACP v2.0 schema.json design | CSO R | **COMPLETE** (this document) | 2026-02-24 |
| Deep PDF analysis endpoint (PyMuPDF) | CTO RNA | In Progress | 2026-02-26 |
| Per-agent analysis storage paths | CTO RNA | Done (commit b22c361) | Done |
| Agent registry (4 agents) | CTO RNA | Done | Done |
| Agent registry (perplexity + manus) | CSO R → CTO RNA | Designed (above) | 2026-02-25 |
| schema.json implementation | CTO RNA | Pending this design | 2026-02-25 |

### Sprint 3E.2 — Multi-Agent Convergence

| Task | Owner | Status | Deadline |
|------|-------|--------|----------|
| Consensus analysis generation | CTO RNA | Not started | 2026-02-28 |
| Multi-agent comparison UI | CTO RNA | Not started | 2026-02-28 |
| Perplexity API integration | CTO RNA | Not started | 2026-03-01 |
| Agreement scoring algorithm | CSO R (design) + CTO RNA (impl) | Designed (above) | 2026-03-01 |

### Sprint 3E.3 — Knowledge Graph + GitHub Pages

| Task | Owner | Status | Deadline |
|------|-------|--------|----------|
| Knowledge graph from research data | CTO RNA | CLI exists, needs web integration | 2026-03-03 |
| GitHub Pages landing page | CSO R | Starting now | 2026-02-24 |
| Citation network visualization | CTO RNA | Not started | 2026-03-05 |

---

## ROADMAP.md Update Required

The ROADMAP.md should be updated to reflect:
1. Phase 3D is **COMPLETE** (both Sprint 3D.1 and 3D.2)
2. Phase 3E is **IN PROGRESS** with Sprint 3E.1 actively being built
3. The honest assessment table needs updating — Save Pipeline, My Library, and BYOK UX are now all working

---

> **Sandbox Boundary Check:** Created at `/home/ubuntu/macp-research-assistant/.macp/handoffs/20260224_CSO-R_phase3e-schema-design-alignment.md`. Will be pushed to GitHub at `macp-research-assistant/.macp/handoffs/`. Accessible to Claude Code and local environment.

---

*CSO R (Manus AI) — FLYWHEEL TEAM*  
*YSenseAI / MACP Research Assistant*
