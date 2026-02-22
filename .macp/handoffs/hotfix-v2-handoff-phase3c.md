# FLYWHEEL TEAM — Hotfix V2 + Feature Enhancement Handoff

**From:** CSO R (Manus AI) | **To:** CTO RNA (Claude Code)
**Date:** February 22, 2026
**Priority:** HIGH — Production bugs + user-requested features
**Repo:** `macp-research-assistant` (public) | Branch: `main`

---

## Context

The Phase 3C deployment is live at `https://macpresearch.ysenseai.org`. GitHub OAuth login is working. Paper search is functional and returning results. Three issues remain:

1. **BUG:** Analyze returns 502 (Bad Gateway) — "LLM analysis returned empty result"
2. **FEATURE:** Only 10 papers shown, no "Load More" / pagination
3. **CLARIFICATION:** GitHub repo connection flow needs documentation

---

## BUG-1: Analyze Returns 502 — Root Cause & Fix

### Diagnosis

The console shows `POST https://macpresearch.ysenseai.org/analyze → 502 (Bad Gateway)`. The error message displayed is "LLM analysis returned empty result." This traces to `main.py:447`:

```python
if not analysis:
    raise HTTPException(status_code=502, detail="LLM analysis returned empty result.")
```

The `_analyze_paper()` function in `tools/llm_providers.py` returns `None` when:
1. No API key is configured (`GEMINI_API_KEY` env var missing in Cloud Run)
2. The API call fails (network error, rate limit, invalid key)
3. The response cannot be parsed as JSON

### Root Cause

**`GEMINI_API_KEY` is not set as a Cloud Run environment variable.** The deploy script (`deploy-cloudrun.sh`) only sets `ENFORCE_HTTPS=true`. The Gemini free tier requires a valid API key from Google AI Studio.

The code path is:
```
main.py:analyze_paper_endpoint() 
  → llm_providers.py:analyze_paper() 
    → api_key = os.environ.get("GEMINI_API_KEY", "")  ← empty string
    → if not api_key: return None  ← returns None
  → if not analysis: raise HTTPException(502, "LLM analysis returned empty result.")
```

### Fix (2 steps)

**Step 1:** Set `GEMINI_API_KEY` in Cloud Run:
```bash
gcloud run services update macp-research-assistant \
  --region us-central1 \
  --set-env-vars "GEMINI_API_KEY=<your-gemini-api-key>"
```

Get a free Gemini API key from https://aistudio.google.com/apikey if not already available.

**Step 2 (recommended):** Add better error messaging when no API key is configured. In `main.py`, before calling `_analyze_paper()`, add a pre-check:

```python
# Add after line 425 (config = PROVIDERS[req.provider])
api_key = req.api_key or os.environ.get(config["env_key"], "")
if not api_key:
    raise HTTPException(
        status_code=503,
        detail=f"{config['name']} API key not configured. "
               f"Set {config['env_key']} environment variable or provide your own key in the BYOK field."
    )
```

This gives users a clear error message instead of a generic 502.

**Step 3 (frontend):** The BYOK (Bring Your Own Key) field is already in the UI. Verify that the `api_key` field from `AnalyzeRequest` is being passed through correctly. The user can enter their own Gemini API key in the "API Key" input field as a workaround.

---

## FEATURE-1: Load More / Pagination

### Current State

The search endpoint accepts `limit` (1-50, default 10) but has no `offset` parameter. The frontend hardcodes `limit = 10` with no "Load More" button.

### Implementation Plan

**Backend changes** (`main.py` + `tools/paper_fetcher.py`):

1. Add `offset` field to `SearchRequest`:
```python
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(default=10, ge=1, le=50)
    offset: int = Field(default=0, ge=0)
    source: str = Field(default="hysts", pattern="^(hf|hysts|arxiv)$")
```

2. The hysts dataset API (`fetch_from_hysts`) already supports offset via the `offset` parameter in the HuggingFace Datasets Server API. Add `offset` parameter to the function:
```python
def fetch_from_hysts(query: str, limit: int = 10, offset: int = 0) -> list[dict]:
    resp = requests.get(
        f"{HYSTS_DATASET_API}/search",
        params={
            "dataset": HYSTS_DATASET_NAME,
            "config": "default",
            "split": "train",
            "query": query,
            "offset": offset,
            "length": limit,
        },
        timeout=30,
    )
```

3. Pass offset through in the search endpoint:
```python
papers = fetch_from_hysts(req.query, limit=req.limit, offset=req.offset)
```

4. Return `offset` and `has_more` in the response:
```python
return {
    "results": papers,
    "count": len(papers),
    "source": req.source,
    "offset": req.offset,
    "has_more": len(papers) == req.limit,  # If we got exactly `limit` results, there may be more
}
```

**Frontend changes** (`frontend/src/api/client.ts` + `frontend/src/hooks/usePapers.ts` + UI component):

1. Update `searchPapers` to accept offset:
```typescript
export const searchPapers = (query: string, limit = 10, source = "hysts", offset = 0) =>
  apiFetch("/search", {
    method: "POST",
    body: JSON.stringify({ query, limit, source, offset }),
  });
```

2. Update `usePapers` hook to track offset and accumulate results:
```typescript
const [offset, setOffset] = useState(0);
const [hasMore, setHasMore] = useState(false);
const [allPapers, setAllPapers] = useState<Paper[]>([]);

const search = async (query: string, limit = 10, source = "hysts") => {
  setOffset(0);
  const data = await searchPapers(query, limit, source, 0);
  setAllPapers(data.results);
  setHasMore(data.has_more);
};

const loadMore = async () => {
  const newOffset = offset + 10;
  const data = await searchPapers(currentQuery, 10, currentSource, newOffset);
  setAllPapers(prev => [...prev, ...data.results]);
  setOffset(newOffset);
  setHasMore(data.has_more);
};
```

3. Add a "Load More" button at the bottom of the results list:
```tsx
{hasMore && (
  <button onClick={loadMore} className="load-more-btn">
    Load More Papers
  </button>
)}
```

### Effort Estimate: 2-3 hours

---

## CLARIFICATION: GitHub Repository Connection

### What It Does

When a user clicks "Connect Repository" in the sidebar, they can link a GitHub repository (e.g., `username/my-research`). The system then:

1. **Creates a `.macp-research/` directory structure** in the connected repo with subdirectories for papers, analyses, notes, and a knowledge graph
2. **Dual-writes** all research data — every save goes to both the local database (fast cache) AND the GitHub repo (persistent source of truth)
3. **Enables sync** — the user can hydrate their local DB from GitHub, or push local changes to GitHub

### The Flow

```
User clicks "Connect Repository"
  → POST /api/github/connect { repo: "owner/repo" }
    → Saves repo to user.connected_repo in DB
    → Calls GitHubStorageService.init_repo_structure()
      → Creates .macp-research/manifest.json
      → Creates .macp-research/papers/.gitkeep
      → Creates .macp-research/analyses/.gitkeep
      → Creates .macp-research/graph/.gitkeep
      → Creates .macp-research/notes/.gitkeep
```

After connection, every paper save, analysis, and note automatically writes to the GitHub repo via the Contents API. This means the user's research is version-controlled and portable — they can clone the repo and have all their research data locally.

### Current Status

The backend implementation is complete (`github_storage.py`). The frontend has a "Connect Repository" button in the sidebar. The GitHub OAuth token is stored encrypted in the database and used for API calls. **This feature should work as-is** once the user connects a repo — no code changes needed.

### Recommended Enhancement (Phase 3D)

Add a visual indicator showing sync status (last synced timestamp, number of papers synced) and a manual "Sync Now" button for users who want to force a full sync.

---

## Deployment Checklist

After implementing the fixes:

1. Set `GEMINI_API_KEY` in Cloud Run env vars
2. Rebuild and deploy the Docker image with the code changes
3. Test analyze with a paper (should return structured analysis)
4. Test "Load More" by searching for a common term (e.g., "LLM") and clicking Load More
5. Test BYOK by entering a personal Gemini API key in the UI field
6. Verify "Connect Repository" flow with a test repo

---

## Files to Modify

| File | Change | Priority |
|------|--------|----------|
| Cloud Run env vars | Add `GEMINI_API_KEY` | CRITICAL |
| `backend/main.py` line ~425 | Add API key pre-check with clear error message | HIGH |
| `backend/main.py` `SearchRequest` | Add `offset` field | MEDIUM |
| `tools/paper_fetcher.py` `fetch_from_hysts()` | Add `offset` parameter | MEDIUM |
| `backend/main.py` search endpoint | Pass offset, return `has_more` | MEDIUM |
| `frontend/src/api/client.ts` | Add offset to `searchPapers()` | MEDIUM |
| `frontend/src/hooks/usePapers.ts` | Add `loadMore()` and state tracking | MEDIUM |
| Frontend search results component | Add "Load More" button | MEDIUM |

---

**Sandbox Boundary Check:** Created at `/home/ubuntu/hotfix-v2-handoff-phase3c.md`. Will be pushed to GitHub at `verifimind-genesis-mcp/.macp/handoffs/hotfix-v2-handoff-phase3c.md` and `macp-research-assistant/.macp/handoffs/hotfix-v2-handoff-phase3c.md`. Accessible to Claude Code and local environment.
