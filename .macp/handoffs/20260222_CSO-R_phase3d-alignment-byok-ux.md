# FLYWHEEL Phase 3D Alignment + BYOK UX Improvement Spec

> **CSO R (Manus AI) → CTO RNA (Claude Code)**
> **Date:** 2026-02-22
> **Priority:** HIGH — UX polish + Phase 3D planning
> **Handoff Protocol:** multi-agent-handoff-bridge v1.0

---

## Executive Summary

Phase 3C is fully deployed and operational at `macpresearch.ysenseai.org`. This handoff covers two items: (1) a detailed BYOK UX improvement specification to fix known usability issues, and (2) Phase 3D alignment and priorities based on the Orchestrator's strategic direction. The README has been updated from "Pre-Alpha" to production-ready documentation, and an HD logo has been generated.

---

## Part 1: BYOK UX Improvement Specification

### Current Problems

| Issue | Severity | Description |
|-------|----------|-------------|
| **No "Apply" button** | HIGH | API keys are entered but there is no explicit confirmation action. Users don't know if the key was saved. |
| **No key-provider validation** | MEDIUM | User can paste a Gemini key but select "Anthropic" as the provider. The system silently fails on analysis. |
| **No key format validation** | LOW | No client-side check that the key matches expected format patterns. |
| **No success/error feedback** | HIGH | After entering a key, no toast/notification confirms it was accepted or rejected. |

### Proposed UX Flow

```
┌─────────────────────────────────────────────────┐
│  LLM Provider Settings                          │
│                                                 │
│  Provider: [Gemini ▼]                           │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │ API Key: ••••••••••••••••••••           │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  [Validate & Apply]  [Clear Key]                │
│                                                 │
│  ✅ Key validated — Gemini API responding        │
│     Model: gemini-2.5-flash                     │
│     Rate limit: 15 RPM (free tier)              │
│                                                 │
│  ─────────────────────────────────────────────  │
│  Or use server default: Gemini (free tier)      │
└─────────────────────────────────────────────────┘
```

### Implementation Requirements

**1. "Validate & Apply" Button**

When clicked:
- Send a lightweight test request to the selected provider's API (e.g., a 1-token completion)
- Display loading spinner during validation (typically 1-3 seconds)
- On success: Show green toast "API key validated for [Provider]", persist key in session/localStorage
- On failure: Show red toast with specific error (invalid key, wrong provider, rate limited, network error)

**2. Key-Provider Cross-Validation**

Before sending the test request, perform client-side heuristic checks:

| Provider | Key Prefix Pattern | Expected Length |
|----------|-------------------|-----------------|
| Gemini | `AIza` | 39 chars |
| Anthropic | `sk-ant-` | 108+ chars |
| OpenAI | `sk-` (not `sk-ant-`) | 51+ chars |
| xAI Grok | `xai-` | Variable |

If the key pattern doesn't match the selected provider, show a warning: "This key looks like a [detected_provider] key. Did you mean to select [detected_provider]?"

**3. Backend Validation Endpoint**

Add a new endpoint:

```python
@app.post("/api/validate-key")
async def validate_api_key(provider: str, api_key: str):
    """
    Send a minimal test request to validate the API key.
    Returns: { valid: bool, provider: str, model: str, error?: str }
    """
```

This endpoint should:
- Use a minimal prompt ("Say 'ok'") with `max_tokens: 5`
- Timeout after 10 seconds
- Return structured response with validation result
- NOT log or persist the API key server-side

**4. Frontend State Management**

```typescript
interface BYOKState {
  provider: string;
  apiKey: string;
  validated: boolean;
  validatedAt: number | null;
  error: string | null;
}
```

- Store BYOK state in localStorage (encrypted if possible, or at minimum base64 encoded)
- Re-validate on session start if key is older than 24 hours
- Clear key on logout

**5. UI Components Needed**

- `BYOKSettingsPanel.tsx` — Full settings panel with provider selector, key input, validate button
- `BYOKStatusBadge.tsx` — Small badge showing current provider status in the analysis panel header
- Toast notifications for validation success/failure

### Acceptance Criteria

- [ ] User can enter API key and click "Validate & Apply"
- [ ] System validates key against selected provider's API
- [ ] Success toast shows provider name and model
- [ ] Error toast shows specific failure reason
- [ ] Client-side heuristic warns on key-provider mismatch
- [ ] Key persists across page refreshes (localStorage)
- [ ] "Clear Key" button removes key and reverts to server default
- [ ] Status badge shows current provider in analysis panel

---

## Part 2: Phase 3D Alignment

### Strategic Priorities (from Orchestrator)

The Orchestrator has expressed strong interest in using the tool for **LLM/Multi-Agent research papers**. Phase 3D should focus on making the analysis deeper and more useful for this specific use case.

### Phase 3D Feature Priorities

| Priority | Feature | Description | Effort |
|----------|---------|-------------|--------|
| **P0** | BYOK UX Fix | Apply button, validation, key-provider matching (Part 1 above) | 2-3 hours |
| **P1** | Deep PDF Analysis | Download arXiv PDF, extract full text, multi-section analysis | 4-6 hours |
| **P2** | GitHub Repo Sync | Dual-write on paper save — sync to connected GitHub repo | 3-4 hours |
| **P3** | Citation Extraction | Parse references from PDF, cross-link with library | 4-6 hours |
| **P4** | Multi-Pass Analysis | Configurable depth (quick/standard/deep), multi-LLM comparison | 3-4 hours |
| **P5** | Full-Text Search | Search across saved papers and analyses | 2-3 hours |

### Deep PDF Analysis Spec (P1)

Current limitation: Analysis uses only title + authors + abstract from HuggingFace/arXiv metadata. This misses methodology details, experimental results, and discussion sections.

**Proposed Pipeline:**

```
arXiv ID → Download PDF → Extract Text (PyMuPDF) → Chunk by Section →
  → Send sections to LLM with structured prompts →
  → Aggregate into comprehensive analysis
```

**Key Decisions:**
- Use PyMuPDF (fitz) for PDF text extraction — lightweight, no external service needed
- Chunk by section headers (Introduction, Related Work, Methodology, Experiments, Conclusion)
- For papers > 30 pages, use first 15 pages + conclusion
- Cache extracted text in SQLite to avoid re-downloading

### GitHub Repo Sync Spec (P2)

Current state: "Connect Repository" button exists but doesn't actually sync. The dual-write pattern was designed but not implemented.

**Proposed Implementation:**

On paper save or analysis completion:
1. Check if user has connected a GitHub repo
2. Create/update a file in the repo: `.macp/papers/{arxiv_id}.json`
3. Include: paper metadata, analysis results, user notes, BibTeX
4. Use GitHub API with user's OAuth token (already available from auth)

**File format in GitHub repo:**

```json
{
  "macp_version": "2.0",
  "paper_id": "2405.19888",
  "title": "...",
  "authors": ["..."],
  "abstract": "...",
  "analysis": {
    "provider": "gemini",
    "summary": "...",
    "key_insights": ["..."],
    "methodology": "...",
    "research_gaps": ["..."],
    "strength_score": 8.5
  },
  "notes": "...",
  "saved_at": "2026-02-22T10:30:00Z",
  "analyzed_at": "2026-02-22T10:31:00Z"
}
```

---

## Part 3: Artifacts Completed This Session (CSO R)

| Artifact | Location | Description |
|----------|----------|-------------|
| HD Logo | `docs/assets/macp-logo-hd.png` | 1024x1024 HD logo for GitHub README |
| README.md | `README.md` (repo root) | Complete rewrite — production-ready documentation |
| This Handoff | `.macp/handoffs/20260222_CSO-R_phase3d-alignment-byok-ux.md` | BYOK UX spec + Phase 3D alignment |

---

## Part 4: Open Items for CTO RNA

### Immediate (This Sprint)

1. **Implement BYOK UX improvements** (Part 1 above) — P0
2. **Close alignment issues #13 and #14** after reviewing this handoff
3. **Test all features end-to-end** from UI (User Acceptance Testing)

### Next Sprint (Phase 3D)

4. **Deep PDF Analysis** — P1
5. **GitHub Repo Sync** — P2
6. **Citation Extraction** — P3

### Deferred

7. Multi-Pass Analysis — P4
8. Full-Text Search — P5
9. Ollama/Local LLM Support — Phase 3E
10. Knowledge Graph Visualization — Phase 3E

---

## Sandbox Boundary Check

- Created at: `/home/ubuntu/macp-research-assistant/.macp/handoffs/20260222_CSO-R_phase3d-alignment-byok-ux.md`
- Will be pushed to: `macp-research-assistant/.macp/handoffs/`
- Will be pushed to: `verifimind-genesis-mcp/.macp/handoffs/` (Command Central Hub)
- Accessible to: Claude Code (local) and Manus AI (sandbox)
