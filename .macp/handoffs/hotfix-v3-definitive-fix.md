# FLYWHEEL-HOTFIX-V3: Definitive Analyze Fix + Grok Integration

> **CSO R (Manus AI) → CTO RNA (Claude Code)**
> **Date:** 2026-02-22
> **Priority:** CRITICAL — This is the ONLY remaining blocker for Phase 3C completion
> **Handoff Protocol:** multi-agent-handoff-bridge v1.0

---

## Executive Summary

The 502 analyze error has been **definitively diagnosed** through direct API testing. The root cause is NOT a missing API key — it is a **token output limit that truncates the JSON response**, causing a parse failure. This handoff provides the exact 1-line fix, plus a Grok/xAI integration spec to add open-source LLM options.

---

## Part 1: Definitive Analyze Bug Fix

### Root Cause (Verified by Direct API Testing)

The `maxOutputTokens` parameter in `_call_gemini()` is set to **1024**, but the analysis prompt requires approximately **1,800 characters** of structured JSON output. The Gemini API returns `finishReason: "MAX_TOKENS"` — the response is truncated mid-JSON — and `json.loads()` fails on the incomplete JSON, returning `None`, which triggers the 502.

### Proof

| Test | maxOutputTokens | finishReason | Result |
|------|----------------|--------------|--------|
| Sandbox with 1024 | 1024 | `MAX_TOKENS` | Truncated JSON (39 tokens of ~400 needed) |
| Sandbox with 4096 | 4096 | `STOP` | Complete JSON, 1876 chars, valid parse |

The 502 (not 503) HTTP status confirms the `GEMINI_API_KEY` IS set in Cloud Run. The pre-check at line 461-467 would return 503 if the key were missing. The issue is purely the output truncation.

### Fix — 3 Files, 3 Lines

**File 1: `tools/llm_providers.py` — Line 134**

```python
# BEFORE (line 134):
"generationConfig": {"temperature": 0.3, "maxOutputTokens": 1024},

# AFTER:
"generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096},
```

**File 2: `tools/llm_providers.py` — Line 156 (_call_anthropic)**

```python
# BEFORE:
"max_tokens": 1024,

# AFTER:
"max_tokens": 4096,
```

**File 3: `tools/llm_providers.py` — Line 176 (_call_openai)**

```python
# BEFORE:
"max_tokens": 1024,

# AFTER:
"max_tokens": 4096,
```

### Deployment

After the code fix, redeploy:

```bash
cd phase3_prototype
gcloud builds submit --config cloudbuild.yaml --project <PROJECT_ID>
gcloud run deploy macp-research-assistant \
  --image gcr.io/<PROJECT_ID>/macp-research-assistant:latest \
  --region us-central1
```

Or simply run the deploy script if it handles the build:

```bash
./phase3_prototype/deploy-cloudrun.sh
```

### Verification

```bash
# Should return valid JSON analysis, NOT 502
curl -X POST https://macpresearch.ysenseai.org/analyze \
  -H "Content-Type: application/json" \
  -H "Cookie: <session_cookie>" \
  -d '{"paper_id":"2405.19888","provider":"gemini"}'
```

---

## Part 2: Grok/xAI Integration (New LLM Provider)

### Why Grok?

Per the Orchestrator's strategic direction:
- **Open-source alignment** — Grok models align with the project's open-source philosophy
- **Cost management** — Paid LLMs (Gemini, Anthropic) should be BYOK; open-source models should be the default
- **Multi-model diversity** — More providers = better resilience and user choice

### xAI API Key Facts

| Property | Value |
|----------|-------|
| **Base URL** | `https://api.x.ai` |
| **Chat endpoint** | `POST https://api.x.ai/v1/chat/completions` |
| **Auth** | `Authorization: Bearer <xAI API key>` |
| **Compatibility** | Fully OpenAI REST API compatible |
| **Free tier** | Discontinued May 2025 — requires paid key |
| **Recommended model** | `grok-3` ($3.50/$10.50 per 1M tokens) |

### Implementation — 2 Changes

**Change 1: Add Grok to PROVIDERS dict in `tools/llm_providers.py`**

```python
# Add after the "openai" entry in PROVIDERS:
"grok": {
    "name": "xAI Grok",
    "env_key": "GROK_API_KEY",
    "model": "grok-3",
    "endpoint": "https://api.x.ai/v1/chat/completions",
    "free_tier": False,
},
```

**Change 2: Add `_call_grok()` function in `tools/llm_providers.py`**

```python
def _call_grok(api_key: str, prompt: str, model: str) -> Optional[str]:
    """Call xAI Grok API (OpenAI-compatible)."""
    resp = requests.post(
        PROVIDERS["grok"]["endpoint"],
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 4096,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    choices = data.get("choices", [])
    if choices:
        return choices[0].get("message", {}).get("content", "")
    return None
```

**Change 3: Register in `_CALLERS` dict**

```python
_CALLERS = {
    "gemini": _call_gemini,
    "anthropic": _call_anthropic,
    "openai": _call_openai,
    "grok": _call_grok,  # ADD THIS
}
```

**Change 4: Add Grok to frontend provider dropdown**

In the frontend component that renders the provider `<select>`, add:

```html
<option value="grok">xAI Grok</option>
```

### Optional: Add Ollama for Local Open-Source Models

For true open-source/free models (Qwen3, Llama, etc.), consider adding Ollama support:

```python
"ollama": {
    "name": "Ollama (Local)",
    "env_key": "OLLAMA_BASE_URL",  # e.g., http://localhost:11434
    "model": "qwen3:8b",
    "endpoint": "{base_url}/api/chat",
    "free_tier": True,
},
```

This would require the user to run Ollama locally, but aligns perfectly with the open-source-first strategy.

---

## Part 3: Default Provider Strategy

Per Orchestrator directive on cost management and open-source alignment:

| User Type | Default Provider | Rationale |
|-----------|-----------------|-----------|
| **Guest (no login)** | Gemini (free tier) | Zero cost, rate-limited |
| **Authenticated user** | Gemini (server key) | Low cost, good quality |
| **BYOK user** | User's choice | Full control |
| **Future: Self-hosted** | Ollama/Qwen3 | Zero cost, open-source |

The current `select_provider()` logic already supports this hierarchy. The Grok addition gives users another BYOK option alongside Anthropic and OpenAI.

---

## Execution Checklist

- [ ] Fix `maxOutputTokens` from 1024 → 4096 in all 3 caller functions
- [ ] Add Grok provider config, caller function, and _CALLERS registration
- [ ] Add Grok to frontend provider dropdown
- [ ] Set `GROK_API_KEY` in Cloud Run (optional, for server-side default)
- [ ] Redeploy to Cloud Run
- [ ] Verify analyze works with Gemini (no BYOK)
- [ ] Verify analyze works with Grok (BYOK)
- [ ] Commit and push to `macp-research-assistant`

---

## Sandbox Boundary Check

- Created at: `/home/ubuntu/HOTFIX_V3_Definitive_Fix_Handoff.md`
- Will be pushed to: `macp-research-assistant/.macp/handoffs/hotfix-v3-definitive-fix.md`
- Will be pushed to: `verifimind-genesis-mcp/.macp/handoffs/hotfix-v3-definitive-fix.md`
- Accessible to: Claude Code (local) and Manus AI (sandbox)
