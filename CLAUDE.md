# Claude Code Instructions - MACP Research Assistant

**Project:** MACP-Powered AI Research Assistant
**Repository:** creator35lwb-web/macp-research-assistant (PUBLIC)
**Command Central Hub:** creator35lwb-web/verifimind-genesis-mcp
**Status:** Pre-Alpha / Conceptual Blueprint

---

## MACP Integration

This project is coordinated via Command Central Hub (verifimind-genesis-mcp).

### Session Start: Check MACP Inbox

At the start of every session, check for pending tasks:

Use the `macp_read_messages` MCP tool with:
- repository: `creator35lwb-web/verifimind-genesis-mcp`
- filters.to: `RNA`
- limit: 5

Or run `/macp-inbox`.

### Session End: Create Handoff

Use the `macp_create_handoff` MCP tool with:
- repository: `creator35lwb-web/verifimind-genesis-mcp`
- agent: `RNA`
- session_type: `development`
- All required fields (completed, decisions, artifacts, pending, blockers, next_agent)

---

## Current Task: P-1.5 Pre-Flight Implementation

**Objective:** Implement the 7 mandatory conditions from the Phase 2 Trinity Validation.

**Guide:** `docs/P1_5_IMPLEMENTATION_BLUEPRINT.md`

**Workflow:**
1. Read the blueprint.
2. Implement all code changes for conditions 3-7.
3. Create the architectural design documents for conditions 1-2.
4. Commit all changes with a clear commit message.
5. Create a handoff record for L (Godel) to review.

---

## Session Start Checklist

When starting a new session, ALWAYS:

1. [ ] Read this CLAUDE.md file
2. [ ] **Check MACP inbox** for pending tasks
3. [ ] Check README.md for project overview and status
4. [ ] Review recent git log for latest changes

---

## Project Overview

MACP Research Assistant tracks, traces, and recalls AI-powered research with complete citation provenance across multiple AI assistants. It solves the problem of lost context, forgotten insights, and scattered citations when using multiple AI tools for research.

### Key Features (Planned)

- Complete traceability — which AI analyzed which paper when
- Easy recall — "What have I learned about X?" queries
- Citation provenance — every citation linked to AI handoffs
- Knowledge graphs — relationships between papers and concepts
- Multi-AI coordination — seamless handoffs between AI assistants

### Key Technologies

- Python (CLI tools)
- MACP v2.0 protocol (.macp/ directory structure)
- arXiv / HuggingFace paper discovery
- Knowledge graph generation

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `tools/` | CLI tools (macp_cli.py, paper_fetcher.py, knowledge_graph.py) |
| `schemas/` | JSON schemas for MACP research records |
| `templates/` | Research templates |
| `peas/` | VerifiMind-PEAS validation |
| `docs/` | Documentation |
| `.macp/` | MACP data (citations, handoffs, papers, knowledge graph) |

### Relationship to Other Projects

- **Sourced from:** `macp-mcp-server` (uses MACP protocol concepts)
- **Hub:** `verifimind-genesis-mcp` (coordination)
- **Validates with:** VerifiMind-PEAS Trinity

---

## Development Workflow

```
1. Check MACP inbox for tasks
2. Implement changes locally
3. Test: python tools/macp_cli.py --help
4. Commit with descriptive message
5. Push to origin/master
6. Create handoff record via macp_create_handoff
```

---

## Important Notes

- This is a PUBLIC repository
- Default branch is `master` (not `main`)
- Currently pre-alpha — conceptual blueprint stage
- Never commit API keys, tokens, or credentials
- This project doubles as a new ideas discovery tool

---

**Protocol:** MACP v2.0 | FLYWHEEL Level 2
