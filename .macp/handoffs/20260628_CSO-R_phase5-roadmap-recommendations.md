# Session Handoff — 2026-06-28 (Session 59)

**Agent:** T (Manus AI) — CSO-R Strategic Mode  
**Session Type:** Phase 5C/5D roadmap recommendations + architecture contribution  
**Continues from:** RNA Session 4 (`20260628_RNA_corpus-deploy-hygiene-skills.md`)

---

## Context

Phase 5 is ~55% complete. Sprints 5A (Agent Submission) and 5B (Topic Taxonomy) are
live and deployed. RNA identified "auto-classify on analysis" as the next step. This
handoff provides strategic architecture recommendations for the remaining 5C/5D work,
grounded in the current codebase state and the competitive landscape.

---

## Recommendation 1: Auto-Classify as the Bridge (5B → 5C)

Auto-classify on analysis is the correct next step because it bridges the existing
Topic Taxonomy (5B) into the Research Queue (5C) without requiring the queue to exist
first. The implementation path:

**Trigger point:** After any successful analysis (abstract, deep, or submitted), extract
`relevance_tags` from the response and call the existing `cmd_topic(classify)` logic.

**Where to wire it:**
- `webmcp.py` → after `db.commit()` in both `mcp_analyze` (~line 332) and
  `mcp_analyze_deep` (~line 569), and in `mcp_submit_analysis` (~line 1212)
- Use the analysis response's `relevance_tags` field (already present in all 3 paths)
- Call the topic classify function with `paper=arxiv_id, tags=relevance_tags`

**Why this matters strategically:** Once papers auto-classify into topics, the topic
tree becomes a live, growing map of what the user has researched. This map is the
input to the Research Queue — "topics with few papers" or "topics with no deep
analysis" become natural queue candidates.

---

## Recommendation 2: Research Queue Architecture (5C)

The ROADMAP specifies `.macp/queue/pending.json` as a file-based queue. Given the
current architecture (PostgreSQL + GitHub dual-write), I recommend a hybrid approach:

**Database-first, file-second:**

```
Table: research_queue
- id (serial)
- topic_slug (varchar) — links to topic taxonomy
- task_type (enum: 'discover', 'analyze_deep', 'consensus', 'go_deeper')
- paper_id (nullable) — specific paper, or NULL for topic-level tasks
- priority (int, 1-5)
- status (enum: 'pending', 'claimed', 'completed', 'expired')
- claimed_by (varchar, nullable) — agent_id that claimed it
- created_at, claimed_at, completed_at (timestamps)
- trigger_reason (text) — why this task was queued
- recommended_next (jsonb) — continuation chain metadata
```

**Why database-first:**
- Concurrent agent access (multiple agents claiming tasks without conflicts)
- Status tracking with timestamps (provenance)
- Query efficiency (find all pending tasks for a topic, find all tasks by priority)
- The GitHub dual-write already exists for analyses — extend it for queue state

**File sync (`.macp/queue/`):** A periodic snapshot of pending tasks for CLI access
and offline agents. Not the source of truth — the DB is.

**API endpoints to add:**
- `POST /api/mcp/queue/add` — queue a research task (with trigger_reason)
- `GET /api/mcp/queue/pending` — list available tasks (filterable by topic, type)
- `POST /api/mcp/queue/claim` — agent claims a task (returns task details)
- `POST /api/mcp/queue/complete` — agent marks task done (with result reference)

---

## Recommendation 3: Queue Population Triggers (5C → 5D Bridge)

The queue should populate from three sources:

**Source A — Analysis gaps (automatic):**
When auto-classify adds a paper to a topic, check:
- Does this topic have < N papers? → queue `discover` task
- Does this paper have only abstract analysis? → queue `analyze_deep` task
- Does this paper have < 3 provider analyses? → queue `consensus` task

**Source B — Research gaps from analyses (semi-automatic):**
The `research_gaps` field already exists in every analysis response. Parse it and
queue `go_deeper` tasks for identified gaps. This is the "continuation protocol"
(Component 4) made concrete — the `continues_from` field already exists in
submit-analysis.

**Source C — User-triggered (manual):**
"Go Deeper" button in the UI → queues a task for the next agent session.

---

## Recommendation 4: Gemini File Search as Queue Backend (Evaluation)

Before building a custom vector search for "find related papers in my corpus,"
evaluate Gemini File Search API:

**Test case:** Upload 50 papers (PDF or extracted text) with metadata labels
(`topic: transformer`, `analysis_status: deep`, `provider_count: 3`). Then query:
- "Papers about attention mechanisms that have not been deeply analyzed"
- "Papers related to [new paper X] in my corpus"

**If it works:** Replace the planned custom embedding pipeline with Gemini File
Search. Metadata filtering maps directly to queue queries. Page citations map to
provenance. Cost: free tier.

**If it doesn't:** Fall back to the database + topic taxonomy approach (which
already works for structured queries).

**Decision point:** RNA should evaluate this BEFORE building the queue's
"find related papers" feature. The queue's "find by status/topic" queries work
fine with PostgreSQL alone.

---

## Recommendation 5: Orchestration Architecture (5D)

Phase 5D ("wire everything together") should be event-driven, not polling-based:

**Event flow:**
```
Paper analyzed → auto-classify → check gaps → queue tasks → [agent claims] → analyze → loop
```

**Implementation:** Use the existing `background_tasks` pattern (already in webmcp.py)
to chain post-analysis actions. No external event bus needed — FastAPI background
tasks + database state is sufficient at current scale.

**The "Go Deeper" trigger:**
- User clicks "Go Deeper" on a paper or topic
- System queues: `discover` (find more papers) + `analyze_deep` (existing papers) + `consensus` (if enough analyses exist)
- Next agent session pulls pending tasks and executes them
- Results auto-classify back into the topic tree → loop continues

**Key constraint:** Orchestration must be agent-agnostic. Any agent (RNA via CLI,
CSO-R via API, Perplexity via deep-research, a new agent via submit-analysis) should
be able to claim and complete queue tasks. The queue is the coordination layer — not
any single agent.

---

## Recommended Sprint Sequence

| Order | Task | Effort | Dependency |
|-------|------|--------|------------|
| 1 | Auto-classify on analysis | ~2h | None (5A + 5B already live) |
| 2 | Research Queue DB schema + API | ~1 day | Auto-classify (provides queue population) |
| 3 | Gap detection triggers (Source A) | ~4h | Queue API |
| 4 | "Go Deeper" UI button | ~2h | Queue API |
| 5 | Gemini File Search evaluation | ~4h | Independent (can parallel) |
| 6 | Agent task claiming flow | ~4h | Queue API |
| 7 | Orchestration wiring (event chain) | ~1 day | All above |

**Total estimated: ~4-5 days of implementation for a single agent.**

---

## Artifacts

- This handoff (public-safe, technical, actionable)
- No code changes (recommendation only — RNA implements)

---

## For RNA (Next Session)

1. Start with auto-classify on analysis — it is the smallest change with the
   highest leverage (bridges 5B → 5C naturally).
2. Consider the DB-first queue architecture vs file-only — concurrent agent
   access is the key differentiator.
3. Gemini File Search evaluation can run in parallel with queue implementation.
4. The `continues_from` field in submit-analysis already implements the
   continuation protocol (Component 4) — just needs queue integration.

---

**Next agent:** RNA (auto-classify implementation)

— T (CSO-R) · Session 59 · FLYWHEEL TEAM · 2026-06-28
