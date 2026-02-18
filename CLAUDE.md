# Claude Code Instructions - MACP Research Assistant

**Project:** MACP-Powered AI Research Assistant
**Repository:** creator35lwb-web/macp-research-assistant (PUBLIC)
**Command Central Hub:** creator35lwb-web/verifimind-genesis-mcp
**Status:** Phase 2 Complete / P-1.5 Pre-Flight Done

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

## Completed: P-1.5 Pre-Flight Implementation

All 7 mandatory conditions from Phase 2 Trinity Validation are implemented:

| Condition | Status | Implementation |
|-----------|--------|----------------|
| C1: Database Design | DONE | `docs/architecture/phase3/DATABASE_DESIGN.md` |
| C2: Auth Design | DONE | `docs/architecture/phase3/AUTH_DESIGN.md` |
| C3: Strict Schema Validation | DONE | `validate_json_data(strict=True)` + `--force` flags |
| C4: Dual-Use Risk Mitigation | DONE | `tools/risk_mitigation.py` + `cmd_analyze` integration |
| C5: Structured Security Logging | DONE | `tools/security_logger.py` → `.macp/security.log` |
| C6: Bias Awareness Disclosure | DONE | `_meta` field in `analyze_paper()` output |
| C7: Data Retention / Purge | DONE | `macp purge` command with `--dry-run` |

## CURRENT TASK

**Task:** Implement Phase 3C — Public Launch
**Status:** **🟡 IN PROGRESS**
**Handoff from L (Godel):** `20260219_L_phase3c_spec_handoff.md`
**Specification:** `docs/architecture/phase3/PHASE_3C_STRATEGIC_PLAN.md`

### Implementation Checklist

- [ ] **P3C-H1: Unit & Integration Tests**
- [ ] **P3C-H2: Container Security**
- [ ] **P3C-H3: Configuration Validation**
- [ ] **P3C-D1: Public API Documentation**
- [ ] **P3C-D2: User & Developer Guides**
- [ ] **P3C-D3: GitHub Community Setup**
- [ ] **P3C-L1: Terms of Service & Privacy Policy**
- [ ] **P3C-L2: License Review**
- [ ] **P3C-O1: CI/CD Pipeline**
- [ ] **P3C-O2: Deployment Scripts**

### Definition of Done

- All checklist items are complete.
- All existing tests pass, and new tests for DB/MCP server are added.
- A new handoff record is created in `.macp/handoffs/`.
- A PR is opened from `feature/phase3b` to `master`.

---

## COMPLETED TASKS

- **Task:** Implement Phase 3B — Full Hybrid Architecture
  - **Status:** ✅ **COMPLETE**
  - **Merge commit:** `e7b90d9`
- **Task:** Implement P-2.5 Pre-Flight Conditions
  - **Status:** ✅ **COMPLETE**
  - **Merge commit:** `aaf7b27`
- **Task:** Implement Phase 3A WebMCP Prototype
  - **Status:** ✅ **COMPLETE**
  - **Commit:** `250a5c7`
- **Task:** Implement P-1.5 Pre-Flight Conditions
  - **Status:** ✅ **COMPLETE**
  - **Commit:** `b5a9424`

---

## Backlog Task: Phase 3C — Public Launch

**Guide:** TBD
**Objective:** Prepare for public launch, including documentation, website, and community engagement.

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
| `tools/` | CLI tools (macp_cli.py, paper_fetcher.py, llm_providers.py, risk_mitigation.py, security_logger.py) |
| `schemas/` | JSON schemas for MACP research records |
| `templates/` | Research templates |
| `peas/` | VerifiMind-PEAS validation |
| `docs/` | Documentation + Phase 3 architecture |
| `.macp/` | MACP data (papers, sessions, citations, handoffs, security log) |
| `.macp/research/` | Knowledge tree — auto-created directories per paper |

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
- Phase 2 complete with all 7 pre-flight conditions met
- Never commit API keys, tokens, or credentials
- This project doubles as a new ideas discovery tool

---

**Protocol:** MACP v2.0 | FLYWHEEL Level 2
