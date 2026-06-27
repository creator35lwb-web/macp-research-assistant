# Session Handoff - 2026-06-27

**Agent:** Claude Code (Opus 4.8) — RNA
**Session Type:** Repo reconciliation + Semantic consensus + Phase 5A Agent Submission Layer

## Repo Reconciliation (read this first)

This local folder had drifted **59 commits behind `origin/master`** (a fresh
`git fetch` revealed it; an earlier stale count showed only 6). The remote work
included docs + the **P4.1 Knowledge Graph** + code touching the same files as
local uncommitted work. Resolution (user-approved): **reset local to
origin/master, then re-apply net-new features fresh** onto the updated files.
Superseded local graph edits were dropped in favor of the remote P4.1 graph.
A pre-reset `git stash` + a scratchpad patch backup were taken first. All
re-applied features verified green after reset.

## Work Completed

### 1. Semantic Consensus Upgrade
Replaced the lexical-only agreement scorer with an embedding-based semantic
scorer; full backward compatibility, graceful degradation.

- `tools/llm_providers.py`: embedding layer (`EMBEDDING_PROVIDERS` —
  Gemini `text-embedding-004` free, OpenAI `text-embedding-3-small` fallback),
  `embed_texts()` (batched, BYOK-aware), `resolve_embed_provider()`, pure-Python
  `_cosine()`/`_mean_pairwise_similarity()`. **No new pip deps.** New
  `compute_agreement_detail(...)` → `{agreement_score, method, components,
  weights, fallback_reason}`. Findings (40%) + methodology (30%) use embedding
  cosine; relevance (30%) stays numeric. `compute_agreement_score()` unchanged
  signature, **lexical by default** (no surprise network calls); semantic opt-in.
- `phase3_prototype/backend/webmcp.py`: `/consensus` uses
  `compute_agreement_detail(semantic=True, ...)`; consensus object + manifest now
  carry `agreement_method` + `agreement_components` (additive, schema-safe).
- `tools/test_consensus.py` (new): 6 offline tests. **6/6 pass.**

### 2. Phase 5A — Agent Submission Layer (the recursive-research foundation)
Implements Missing Component 1 from the CSO-R vision-gap analysis: let ANY agent
(Claude Code, Manus, Perplexity, Cursor) submit provenance-tracked analyses back
into the MACP substrate. This is the "be the provenance MCP that platforms CALL"
wedge made real.

- `tools/macp_cli.py`: new `macp submit` command (`cmd_submit`). GitHub-native —
  writes `.macp/analyses/{arxiv_id}/{agent_id}_{date}.json` + registers in the
  manifest. Supports inline (`--summary/--findings/--score`) or `--file`, and the
  **continuation protocol** (`--continues-from` / `--continues-from-agent`) so
  agent B's analysis chains onto agent A's. Every record carries `_provenance`
  and a `_meta.bias_disclaimer`.
- `tools/test_submit.py` (new): 6 offline tests (isolated temp MACP_DIR).
  **6/6 pass.** Verified live: claude_code (abstract) → manus_ai (deep,
  continues_from) chain writes + manifest registration correct.

### 3. Robustness fixes (re-applied onto new base)
- `database.py`: `_ensure_sqlite_columns()` additive migration (local SQLite DBs
  miss columns from later phases — now reconciled at startup); `log_audit()`
  rolls back + logs on persist failure instead of crashing.
- `main.py`: `init_db()` moved before the env-warning loop (which logs to the DB).

### 4. Docs / continuity
- `README.md`: consensus section documents semantic scoring + lexical fallback +
  `agreement_method`.
- `WORKSPACE_NOTICE.md`: corrected — THIS folder IS the public-repo dev workspace
  (verified via `git remote -v`); the hub folder is a different repo.

## Decisions

- Semantic scoring is **opt-in at the call site**, never forced into the legacy
  float API.
- `macp submit` is **GitHub-native / offline-first** (writes to `.macp/`), aligned
  with "GitHub is the bridge." The web counterpart `POST /api/mcp/submit-analysis`
  is the documented next step (same logic, FastAPI-wrapped, needs server to test).
- Strategic framing (with user): MACP Research Assistant = **public flagship
  showcase** of FLYWHEEL TEAM + MACP, and the **provenance/memory layer** platforms
  call — NOT a competitor to platform-native deep research. Optimize for
  demonstrability + the recursive Research Journey Engine, not feature parity.

## Artifacts

- `tools/llm_providers.py`, `phase3_prototype/backend/webmcp.py`,
  `phase3_prototype/backend/database.py`, `phase3_prototype/backend/main.py`,
  `README.md`, `WORKSPACE_NOTICE.md` (modified)
- `tools/test_consensus.py`, `tools/test_submit.py` (new)
- This handoff (new)

## Pending / Next Agent (Phase 5 roadmap — from CSO-R vision-gap analysis)

Phase 5A Component 1 (Agent Submission) is now built (CLI). Remaining:
- **5A-web:** `POST /api/mcp/submit-analysis` endpoint (FastAPI wrapper around the
  same logic) + add to MCP discovery tool list.
- **Component 2 — Topic Taxonomy:** `.macp/topics/` hierarchical tree, auto-classify
  by `relevance_tags`, "Go Deeper" trigger.
- **Component 3 — Research Queue:** `.macp/queue/{pending,in_progress,completed}.json`.
- **Component 4 — Continuation Protocol:** chaining is started (`continues_from`);
  extend with `recommended_next` follow-up actions.
- **Component 5 — "Go Deeper" trigger:** auto-spawn searches for new sub-topics.
- Optional: live semantic-consensus check with real `GEMINI_API_KEY`; surface
  `agreement_method`/`components` in the Consensus Comparison UI; document the
  showcase + provenance-MCP positioning in ROADMAP.md v2 vision section.

**Git state:** working tree is clean re-applied work ON TOP of current
`origin/master`. Nothing committed yet — review the diff, then commit + push.
A pre-reset stash remains as a safety net (`git stash list`); drop it once happy.

**Next agent:** RNA (or any platform) — start with 5A-web, then Component 2.
