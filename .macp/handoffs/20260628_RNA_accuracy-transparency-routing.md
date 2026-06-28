# Session Handoff - 2026-06-28 (session 3)

**Agent:** Claude Code (Opus 4.8) — RNA
**Session Type:** Analysis accuracy & transparency + HTML-first extraction + smart model routing
**Continues from:** `20260628_RNA_public-refresh-security-topic-taxonomy.md`

## Git Reconciliation
No drift — local `master` 0/0 vs `origin/master` throughout. All commits CI-green.
Working tree clean. (These features are on master but NOT yet deployed — prod still
runs the prior revision with the dormant origin guard.)

## Context: the accuracy question (drove this session)
Traced the 3 analysis paths in code to answer "does the AI read the full paper?":
- **Abstract analysis** (`analyze_paper`): title + authors + **abstract only**. Does NOT read the paper.
- **Deep analysis** (`analyze_paper_deep`): downloads PDF → extracts → quality gate
  (`check_extraction_quality`, MIN_BODY_CHARS=500) → multi-pass over full sections.
  Genuinely reads the full text; errors instead of faking if extraction fails.
- **Deep research** (Perplexity): title + abstract → **web search** (citations/related
  work/impact). Does NOT read the PDF.
- Accuracy honesty: "did it read real text" is guaranteed; "is the interpretation
  correct" is NOT (mitigated by multi-agent consensus + provenance + disclaimers).

## Work Completed

### 1. Transparency indicators (UI) — limitations now disclosed to users
- `AnalysisView.tsx`: abstract analyses show an "Abstract-only — not the full paper"
  banner; deep analyses show a "✓ Read full text (HTML/PDF)" badge from
  `extraction_source` + an extraction-warnings note. `components.css`: `.source-note*`.

### 2. HTML-first extraction for arXiv (better full-text quality)
- `webmcp.py` deep handler: try arXiv HTML (ar5iv) FIRST (clean structured text),
  fall back to PDF only when HTML is unavailable/below the quality gate; prefer HTML
  if the PDF parse is also poor. `extraction_source` now "html" | "pdf".
- Research basis: rule-based PyMuPDF lags learning-based parsers; arXiv HTML is
  free + high-quality. (Future options: PyMuPDF4LLM for non-arXiv; Docling/GROBID
  for scanned/hard PDFs — deferred for cost.)

### 3. Smart model routing (`llm_providers.py`)
- `MODEL_TIERS` (per-provider lite/pro, env-overridable) + `select_model(provider,
  task, signals)`. Abstract → "lite" tier; deep → "standard", or "pro" for
  long/complex papers (>=40k chars or >=12 sections, env-tunable). Undefined tiers
  fall back to standard (safe no-op for anthropic/grok/groq/perplexity).
- Wired into `analyze_paper` + `analyze_paper_deep` (4 passes); chosen model + route
  reason recorded in `_meta.model_route` (transparent). `test_routing.py` 7/7.
- **Default ON** ("balanced"); `MODEL_ROUTING=off` pins the standard model.

## Decisions
- HTML-first (not just fallback) because arXiv HTML is the highest-quality + free path.
- Routing default-ON balanced: cheaper model for trivial abstracts, stronger for
  hard deep papers — net cost+quality win, made transparent via provenance. Opt-out
  via `MODEL_ROUTING=off` for BYOK users who want their exact model pinned.
- Tiers env-configurable (consistent with the model-deprecation-proof design).

## Artifacts
- New: `tools/test_routing.py`, this handoff.
- Modified: `tools/llm_providers.py`, `phase3_prototype/backend/webmcp.py`,
  `phase3_prototype/frontend/src/components/analysis/AnalysisView.tsx`,
  `phase3_prototype/frontend/src/styles/components.css`.

## Pending / Next Agent

### Deploy (maintainer)
- HTML-first + smart routing + transparency indicators are on master, NOT deployed.
  Run `/macp-deploy` to ship. **Routing is default-on** — flag to BYOK users; set
  `MODEL_ROUTING=off` to pin standard models.

### Optional follow-ups (proposed, not built)
- Surface the routed model in the UI (`_meta.model_route` is captured, not shown).
- Document routing env vars (`*_LITE_MODEL`, `*_PRO_MODEL`, `DEEP_COMPLEX_*`) in README.
- Extraction upgrades for non-arXiv/scanned PDFs (PyMuPDF4LLM, Docling/GROBID) — cost-gated.

### Phase 5 (continuing the recursive engine)
- Auto-classify on analysis (grow the topic tree automatically); Research Queue
  (Component 3); "Go Deeper" trigger (Component 5).

### Cloudflare (maintainer, in progress)
- NS switched + propagating; keep `verifimind` DNS-only; verify email; proxy
  `macpresearch`; then activate origin guard via `CF_ORIGIN_SECRET`. (Local checklist.)

**Next agent:** RNA (or any platform). Deploy the accuracy/routing batch, then
auto-classify-on-analysis is the next recursive-engine step.
