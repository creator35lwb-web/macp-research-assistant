# FLYWHEEL TEAM — v1.0.0 Functional Audit Report
## Live Production Endpoint Verification

**Date:** 2026-02-25
**Author:** CSO R (Manus AI)
**Classification:** Technical Audit — Production Verification
**Protocol:** Multi-Agent Handoff Bridge

---

## 1. Audit Methodology

This audit was conducted by testing every public API endpoint on the live production deployment at `macpresearch.ysenseai.org` using direct HTTP requests. Each endpoint was called with real parameters and the response was recorded. The audit also included source code review of the FastAPI backend to verify integration implementations.

---

## 2. Endpoint-by-Endpoint Results

### Working Endpoints

| Endpoint | Method | Test Result | Response Details |
|----------|--------|-------------|------------------|
| `/api/mcp/search` | POST | **PASS** | Returns 10 papers from HuggingFace Datasets API with title, authors, abstract, arXiv ID |
| `/api/mcp/analyze` | POST | **PASS** | Gemini 2.5 Flash returns structured analysis: summary, key_findings, methodology, research_gaps, strength_score |
| `/api/mcp/save` | POST | **PASS** | Saves paper to SQLite + fires GitHub dual-write BackgroundTask |
| `/api/mcp/library` | GET | **PASS** | Returns list of saved papers from library |
| `/api/mcp/agents` | GET | **PASS** | Returns 6 agents: gemini, anthropic, openai, gemini_pro, perplexity, manus |

### Conditional Endpoints

| Endpoint | Method | Test Result | Condition |
|----------|--------|-------------|-----------|
| `/api/mcp/deep-research` | POST | **REQUIRES BYOK** | Returns "Deep research failed — check SONAR_API_KEY" without user's Perplexity key |
| `/api/mcp/consensus` | POST | **REQUIRES 2+ ANALYSES** | Returns "Need at least 2 abstract analyses for consensus, found 0" — correct behavior |

### Built but Untested in Production

| Endpoint | Method | Code Status | Notes |
|----------|--------|-------------|-------|
| `/api/mcp/analyze-deep` | POST | Complete | 4-pass PDF analysis with PyMuPDF |
| `/api/mcp/analysis/{id}` | GET | Complete | Retrieves stored analysis |
| `/api/mcp/sync` | POST | Complete | GitHub hydration on cold start |

---

## 3. Agent Registry Deep Dive

The Agent Registry (`GET /api/mcp/agents`) is **functional as a read-only directory**. It reads JSON files from `.macp/agents/` and returns structured metadata for 6 agents. However, it does NOT provide any mechanism for external agents to submit analyses back to the platform. There is no `POST /api/mcp/agents/submit` or equivalent endpoint.

**Classification:** Display-only for external agents; functional routing for built-in providers (Gemini, Claude, GPT-4, Perplexity).

---

## 4. Perplexity Integration Deep Dive

The Perplexity deep research integration is **fully implemented in code**. The `_call_perplexity()` function in `webmcp.py` calls the Perplexity Sonar Pro API with web grounding enabled and returns structured output including citation_count, citing_papers, related_work, code_url, data_url, community_discussions, research_group, impact_assessment, and sources.

This is real API integration — not a mock. It requires the user's `SONAR_API_KEY` via the BYOK model. No server-side key is configured (zero burn-rate design).

---

## 5. Artifacts Bridged

| Artifact | Repository | Path |
|----------|-----------|------|
| This document | `macp-research-assistant` | `.macp/handoffs/20260225_CSO-R_functional-audit-v100.md` |
| Updated ROADMAP.md | `macp-research-assistant` | `ROADMAP.md` |

---

*CSO R — FLYWHEEL TEAM*
*"Honest assessment enables honest progress."*
