# MACP Research Assistant — Multi-Platform Development Journey

**Report date:** 2026-06-27
**Author:** Claude Code (Opus 4.8) — RNA
**Purpose:** Describe, record, and document the multi-platform development
progression so the maintainer can review, commit, and re-align after a period
of drift. All claims below are backed by repository evidence (git history,
handoff artifacts, test runs) gathered on the report date.

---

## 1. Executive Summary

The MACP Research Assistant is a **production-deployed, multi-agent research
platform** built by the **FLYWHEEL TEAM** — a human maintainer coordinating
several AI platforms (Claude Code, Manus AI, and the founding agent "L/Godel")
that hand work to each other through a shared GitHub repository.

After ~4.5 months and **231 commits across 8 development phases**, the project
reached **v1.0.0** (public launch) and is now entering **Phase 5: the recursive
Research Journey Engine**. This report documents that journey, the coordination
model that made it possible, a **drift-and-reconciliation incident** resolved in
this session, and the **two flagship features** added today (semantic consensus
+ the Agent Submission Layer).

**Bottom line:** the repository is healthy, the divergence has been reconciled,
the new work is tested green, and there is a clear, documented path forward.

---

## 2. The Contributors — Evidence of Multi-Platform Development

`git shortlog -sn --all` (report date):

| Contributor | Commits | Role |
|-------------|--------:|------|
| `creator35lwb-web` | 122 | Maintainer / merges / agent-authored pushes |
| `Alton Lee Wei Bin` | 78 | Maintainer (local platform commits) |
| `dependabot[bot]` | 30 | Automated dependency upgrades |
| `L (Godel) via Manus AI` | 1 | Founding agent attribution |

**Agent signatures in commit messages** (the platforms identify themselves):
- **RNA (Claude Code):** 15 commits
- **CSO-R (Manus AI):** 1 commit (Manus more often authored *handoff docs* than code)
- **handoff-related commits:** 34

- **Total commits:** 231 · **First:** 2026-02-09 · **Latest:** 2026-06-27
- **Parallel work streams (branches):** `feature/phase3.5-preflight`,
  `feature/phase3a-prototype`, `feature/phase3b-full-hybrid`,
  `feature/phase3c-implementation`, plus `master`.

This is concrete evidence that the project was built by **multiple AI platforms
working in parallel**, coordinated by a human, against one public repo.

---

## 3. The Coordination Model — How Multi-Platform Work Stayed Coherent

Three mechanisms (all present in the repo today):

1. **GitHub as the bridge.** Every platform reads and writes the same repo.
   State lives in `.macp/` (papers, analyses, manifest, schema). No platform
   needs another to be online — they synchronize through git.

2. **`.macp/schema.json` — the self-describing protocol.** Any agent reads one
   schema file to understand the entire data layout and contribution rules. This
   is what lets a *new* platform join and orient itself without human onboarding.

3. **Handoff records (`.macp/handoffs/`).** Structured session-to-session
   continuity. **35 handoff documents** exist, e.g.:
   - `20260210_L_foundational_alignment.md` (project genesis, agent "L")
   - `20260219_L_phase3{a,b,c}_spec_handoff.md` (Manus/L specs → Claude Code build)
   - `20260224_RNA_phase3e-*.md` (Claude Code implementation reports)
   - `20260225_CSO-R_vision-gap-analysis-recursive-research.md` (the Phase 5 vision)
   - `20260627_RNA_semantic-consensus-workspace-audit.md` (this session)

   The naming convention `YYYYMMDD_<AGENT>_<topic>.md` is itself the audit trail
   of who did what, when, across platforms.

**Division of labor that emerged:** "L" (Godel/Manus) founded and wrote early
specs; **CSO-R (Manus AI)** produced strategy, audits, and vision documents;
**RNA (Claude Code)** did the bulk of implementation and deployment.

---

## 4. Phase Progression — Evidence Timeline

From commit-message milestones (`git log --all`):

| Phase | Milestone (commit evidence) | Outcome |
|-------|------------------------------|---------|
| **1** | `20260210_L_foundational_alignment` | Manual MACP, templates, GODELAI example |
| **2** | `Phase2_csp_tools` | CLI tools (paper fetcher, citations, knowledge graph) |
| **3A** | `feature/phase3a-prototype` | React + FastAPI web prototype, 2 WebMCP tools |
| **3B** | `688d7f8 Phase 3B Full Hybrid` | DB, GitHub OAuth, MCP server, all WebMCP tools |
| **3C** | `486353f Phase 3C multi-user SaaS` | GCP Cloud Run, CI/CD, security hardening |
| **3D** | `20260222_CSO-R_phase3d` | Save-pipeline repair, BYOK Validate & Apply UX |
| **3E** | `b22c361 / e837667 / e91e1a7` | Schema validation, deep PDF analysis, **consensus (40/30/30)**, Perplexity, agent registry |
| **3F** | `f0f819d Phase 3F COMPLETE` | Deploy revision, Agent Registry UI, CI green |
| **4** | `283e87e Phase 4 sprint`, `8a7b53f P4.1 Knowledge Graph` | PWA, mobile, **Knowledge Graph (P4.1)** |
| **v1.0.0** | `24a914e LinkedIn announcement v1.0.0` | **Public launch** |
| **Phase 5 (vision)** | `70f2432 Vision gap analysis` | Recursive Research Journey Engine (~30% implemented) |

---

## 5. The Drift Incident — and Its Resolution (This Session)

**What happened.** The maintainer's local working folder had fallen behind the
remote because multiple platforms were pushing in parallel. A fresh `git fetch`
showed the local `master` was **59 commits behind `origin/master`** (an earlier
cached status had under-reported it as 6). Local uncommitted work overlapped the
*same files* the remote had since evolved (notably the P4.1 Knowledge Graph).

**Why it mattered.** A naive `stash → pull → pop` would have produced merge
conflicts and risked either losing work or shipping a broken, half-merged graph.

**How it was resolved (maintainer-approved).**
1. **Backed up** all local work (a `git stash` + a standalone patch in scratchpad).
2. **Verified collision risk** file-by-file (`git diff master..origin/master`):
   confirmed the maintainer's semantic-consensus work was *net-new* (the remote's
   `llm_providers.py` changes were Knowledge-Graph concept extraction, **not**
   embeddings — verified by grep).
3. **Reset local to `origin/master`** (adopting all 59 commits, incl. P4.1 graph).
4. **Re-applied the net-new features fresh** onto the updated files — surgical,
   since they are additive and well-understood.
5. **Dropped** the superseded local graph edits in favor of the remote's P4.1.

**Result:** clean working tree on top of current `origin/master`, all tests green.
The pre-reset stash remains as a recoverable safety net.

> **Lesson for future multi-platform work:** before starting in any local folder,
> run `git fetch && git status -sb`; if behind, `git pull --rebase` *first*. The
> corrected `WORKSPACE_NOTICE.md` now documents this.

---

## 6. This Session's Deliverables — With Evidence

**Diff stat** (`git diff --stat`, uncommitted vs `origin/master`):

```
 README.md                            |  18 +-
 phase3_prototype/backend/database.py |  43 +++-
 phase3_prototype/backend/main.py     |   5 +-
 phase3_prototype/backend/webmcp.py   |  20 +-
 tools/llm_providers.py               | 419 ++++++++++++++++++++++++-----
 tools/macp_cli.py                    | 190 ++++++++++++++++
 6 files changed, 596 insertions(+), 99 deletions(-)
```
Plus 4 new untracked files (2 tests, 1 handoff, corrected workspace notice).

### 6.1 Semantic Consensus Upgrade
Replaced the lexical-only (Jaccard word-overlap) agreement scorer with an
embedding-based semantic scorer.
- Embedding layer in `llm_providers.py` (Gemini `text-embedding-004` free tier,
  OpenAI `text-embedding-3-small` fallback), batched, BYOK-aware, **no new pip
  dependencies** (pure-Python cosine).
- New `compute_agreement_detail()` returns `{agreement_score, method, components,
  weights, fallback_reason}` — auditable, transparent.
- Backward compatible: `compute_agreement_score()` unchanged, lexical by default.
- **Why it matters:** two agents agreeing in *different words* are now scored as
  agreeing (semantic ≈1.0 vs lexical <0.2 on paraphrases) — the headline
  technical fix.
- **Evidence:** `tools/test_consensus.py` → **6/6 pass**.

### 6.2 Phase 5A — Agent Submission Layer (recursive-research foundation)
Implements "Missing Component 1" from the CSO-R vision-gap analysis.
- New `macp submit` CLI: any agent (Claude Code, Manus, Perplexity, Cursor) can
  submit a provenance-tracked analysis into `.macp/analyses/{paper}/{agent}_{date}.json`
  and register it in the manifest. Supports the **continuation protocol**
  (`--continues-from`) for agent-to-agent chains. Every record carries
  `_provenance` and a `_meta.bias_disclaimer`.
- **Why it matters:** this is the "be the provenance/memory MCP that platforms
  *call*" strategy made real — the wedge that complements (not duplicates)
  platform-native deep research.
- **Evidence:** `tools/test_submit.py` → **6/6 pass**; verified live with a
  `claude_code` (abstract) → `manus_ai` (deep, continues-from) chain.

### 6.3 Robustness + Continuity
- `database.py`: additive SQLite migration (`_ensure_sqlite_columns`) so local
  DBs gain columns from later phases; `log_audit` rolls back instead of crashing.
- `main.py`: `init_db()` ordered before DB-logging.
- `README.md`: consensus section documents semantic scoring honestly.
- `WORKSPACE_NOTICE.md`: corrected (this folder IS the public-repo dev workspace,
  verified via `git remote -v`).

**Verification (report date):** all touched files compile; `test_consensus.py`
6/6, `test_submit.py` 6/6.

---

## 7. Strategic Alignment

Confirmed with the maintainer this session:
- **Do not duplicate** platform-native deep research (Claude Code / Manus /
  Perplexity already do it well).
- **Position MACP Research Assistant as** (a) a public **flagship showcase** of
  FLYWHEEL TEAM + the MACP protocol, and (b) the **provenance/memory layer**
  that platform agents call to capture, attribute, version, and reconcile
  research across sessions.
- The genuinely non-commodity assets are: the self-describing repo-as-protocol,
  auditable multi-agent consensus, and git-native provenance.

---

## 8. Current State & What's Safe to Commit

Working tree (on top of current `origin/master`, nothing committed yet):

```
 M README.md
 M phase3_prototype/backend/database.py
 M phase3_prototype/backend/main.py
 M phase3_prototype/backend/webmcp.py
 M tools/llm_providers.py
 M tools/macp_cli.py
?? .macp/handoffs/20260627_RNA_semantic-consensus-workspace-audit.md
?? WORKSPACE_NOTICE.md
?? tools/test_consensus.py
?? tools/test_submit.py
?? docs/DEVELOPMENT_JOURNEY_2026-06-27.md   (this report)
```

All changes are additive and tested. Safe to commit. Suggested message:

```
feat: semantic consensus + Phase 5A Agent Submission Layer

- Semantic embedding-based agreement scoring (Gemini/OpenAI, lexical
  fallback, auditable agreement_method); backward compatible
- macp submit CLI: agents ingest provenance-tracked analyses with
  continuation chains (Phase 5A, vision Component 1)
- DB additive SQLite migration + audit rollback; init_db ordering
- Corrected WORKSPACE_NOTICE; dev-journey report; tests (12/12 green)

Reconciled local from 59 commits behind origin/master.
```

After committing, drop the safety stash: `git stash list` then `git stash drop`.

---

## 9. The Path Forward — Phase 5 (from the vision-gap analysis)

| Component | Status |
|-----------|--------|
| 1. Agent Submission | ✅ CLI built this session · ⏳ `POST /api/mcp/submit-analysis` (web) next |
| 2. Topic Taxonomy (`.macp/topics/`) | 📋 Planned |
| 3. Research Queue (`.macp/queue/`) | 📋 Planned |
| 4. Continuation Protocol | 🟡 Started (`continues_from`); extend with `recommended_next` |
| 5. "Go Deeper" Trigger | 📋 Planned |

**Recommended next increment:** the web endpoint `POST /api/mcp/submit-analysis`
(FastAPI wrapper around the tested CLI logic) + add it to MCP discovery — so
platform agents can submit via the live MCP surface, completing Agent Submission
on both CLI and web.

---

*FLYWHEEL TEAM — "The foundation is solid. The vision is clear. The gap is buildable."*
