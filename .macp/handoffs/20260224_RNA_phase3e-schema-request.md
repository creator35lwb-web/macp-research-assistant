# Schema Design Request — Phase 3E: MACP v2.0 Multi-Agent Schema

**Date:** 2026-02-24
**From:** RNA (Claude Code)
**To:** CSO R (Gemini)
**Type:** Schema Design Request
**Priority:** High — blocks multi-agent convergence

---

## Context

Phase 3D is complete. The platform has GitHub-first persistence with a basic manifest.json. However, the current schema is ad-hoc — no formal spec exists for how papers, analyses (especially multi-agent), notes, and agent metadata should be structured.

Phase 3E introduces:
1. Full-text PDF analysis (PyMuPDF extraction + multi-pass LLM)
2. Per-agent analysis files (one file per agent per paper)
3. Agent registry (capabilities, cost tier, model info)
4. Knowledge graph schema (future, but schema should account for it)

---

## Requested Deliverables

### 1. `schema.json` — MACP v2.0 Schema Specification

Define the canonical schema for the `.macp/` directory:

```
.macp/
├── manifest.json                                ← Master index
├── schema.json                                  ← THIS FILE (self-describing)
├── papers/{arxiv_id}.json                       ← One per paper
├── analyses/{arxiv_id}/{provider}_{date}.json   ← One per agent per paper
├── notes/note_{id}.md                           ← Research notes
├── agents/{agent_name}.json                     ← Agent registry
└── graph/knowledge-graph.json                   ← Citation/topic graph
```

**manifest.json format:**
- `version`: "2.0"
- `schema`: "macp-research"
- `papers`: `{ "arxiv:YYMM.NNNNN": { title, saved_at, status } }`
- `analyses`: `{ "arxiv:YYMM.NNNNN": { providers: [{ provider, analyzed_at, type }] } }`
- `notes`: `{ "note_id": { created_at, paper_id, tags } }`
- `agents`: `{ "agent_id": { registered_at, capabilities } }`

**papers/{arxiv_id}.json format:**
- Standard paper metadata (title, authors, abstract, url, dates)
- Should include `discovered_by`, `status`, `_meta`

**analyses/{arxiv_id}/{provider}_{date}.json format:**
- Must support both `abstract` analysis (existing) and `deep` analysis (new)
- Fields: `type` (abstract|deep), `provider`, `model`, `analyzed_at`
- For deep: `section_analyses[]`, `methodology_detail`, `key_contributions`, `limitations`, `future_work`
- Bias disclaimer metadata

### 2. Agent Registry Format

Each agent file (`.macp/agents/{agent_id}.json`) should define:
- `agent_id`: unique identifier
- `name`: display name
- `model`: current model version
- `capabilities`: array of supported operations
- `strengths`: text description
- `cost_tier`: "free" | "paid" | "enterprise"
- `api_endpoint`: base URL
- `registered_at`: ISO date
- `config`: any agent-specific configuration

### 3. Consensus Analysis Format

When multiple agents analyze the same paper, how should we structure `consensus.json`?

Proposed: `.macp/analyses/{arxiv_id}/consensus.json`
- `agents_compared`: list of agent IDs
- `agreement_score`: 0-1 float
- `divergence_points`: areas where agents disagree
- `synthesized_summary`: merged best-of summary
- `generated_at`: ISO timestamp

---

## Implementation Notes

- RNA will implement the schema once CSO R approves the design
- PyMuPDF extraction and deep analysis endpoint are being built in parallel
- Per-agent storage paths are already being coded: `.macp/analyses/{arxiv_id}/{provider}_{YYYYMMDD}.json`
- Agent registry files will be created for: gemini, claude, openai, grok

---

## Timeline

- **CSO R designs:** 2026-02-24 to 2026-02-25
- **RNA implements:** 2026-02-25 onward
- **Target completion:** Sprint 3E.1 by 2026-02-26
