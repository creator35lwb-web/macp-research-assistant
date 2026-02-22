# FLYWHEEL TEAM — Production Hotfix Handoff

**From:** CSO R (Manus AI) — GCP Log Scanner + Code Audit
**To:** CTO RNA (Claude Code) — Implementation
**Date:** February 22, 2026
**Priority:** CRITICAL — Production service partially broken
**Scope:** `macpresearch.ysenseai.org` (GCP Cloud Run)

---

## Executive Summary

Two user-facing features are broken in production: GitHub OAuth login and paper search. Both failures share the same root cause — the frontend JavaScript bundle has `http://localhost:8000` hardcoded as the API base URL because `VITE_API_BASE` was never set during the Docker build. The CSP headers then correctly block these cross-origin requests, preventing any API communication.

GCP log analysis (320 entries) confirms zero `/search` or `/api/auth` requests ever reached the server from `macpresearch.ysenseai.org`, proving the issue is entirely client-side.

---

## Bug Analysis

### BUG-1: Frontend API calls target localhost:8000 (CRITICAL)

**Affected files:**

| File | Line | Current Code |
|------|------|-------------|
| `frontend/src/api/client.ts` | 4 | `const API_BASE = import.meta.env.VITE_API_BASE \|\| "http://localhost:8000"` |
| `frontend/src/hooks/useAuth.ts` | 29 | `` const loginUrl = `${import.meta.env.VITE_API_BASE \|\| "http://localhost:8000"}/api/auth/github` `` |

**Root cause:** Vite inlines environment variables at build time. The Dockerfile never sets `VITE_API_BASE`, so the fallback `http://localhost:8000` gets baked into the production JS bundle (`index-DYW_hE4C.js`).

**Evidence from GCP logs:** Zero requests to `/search` or `/api/auth` from `macpresearch.ysenseai.org`. The browser console shows CSP violations for `connect-src 'self'` when trying to reach `http://localhost:8000`.

**Fix:** Add `ENV VITE_API_BASE=""` to the Dockerfile's frontend build stage (Stage 1), before `RUN npm run build`. An empty string makes all API calls use relative paths (`/search`, `/api/auth/me`), which is correct since the backend serves the frontend from the same origin.

```dockerfile
# Stage 1: Frontend build
FROM node:22-slim AS frontend-build
WORKDIR /app/frontend
COPY phase3_prototype/frontend/package.json phase3_prototype/frontend/package-lock.json ./
RUN npm ci --production=false
COPY phase3_prototype/frontend/ ./
ENV VITE_API_BASE=""
RUN npm run build
```

### BUG-2: GitHub OAuth redirect_uri points to localhost (CRITICAL)

**Affected file:** `backend/config.py` lines 62-63

```python
GITHUB_APP_REDIRECT_URI: str = os.getenv(
    "GITHUB_APP_REDIRECT_URI", "http://localhost:8000/api/auth/github/callback"
)
```

**Root cause:** The `GITHUB_APP_REDIRECT_URI` environment variable was never set in the Cloud Run service. The deploy script (`deploy-cloudrun.sh`) only sets `ENFORCE_HTTPS=true`.

**Fix (two steps):**

Step A — Set the env var in Cloud Run:
```bash
gcloud run services update macp-research-assistant \
  --region us-central1 \
  --update-env-vars "GITHUB_APP_REDIRECT_URI=https://macpresearch.ysenseai.org/api/auth/github/callback"
```

Step B — Update the GitHub OAuth App settings at `https://github.com/settings/developers`:
Set "Authorization callback URL" to: `https://macpresearch.ysenseai.org/api/auth/github/callback`

### BUG-3: CORS_ORIGINS defaults to localhost (IMPORTANT)

**Affected file:** `backend/config.py` lines 44-46

```python
CORS_ORIGINS: list[str] = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
]
```

**Fix:** Set in Cloud Run env vars:
```bash
gcloud run services update macp-research-assistant \
  --region us-central1 \
  --update-env-vars "CORS_ORIGINS=https://macpresearch.ysenseai.org"
```

Note: Since frontend and backend share the same origin, CORS is less critical, but it should still be set correctly for defense-in-depth.

### BUG-4: SPA catch-all serves index.html for sensitive paths (RECOMMENDED)

**Evidence from GCP logs:** Requests to `/.env`, `/api/.env`, `/admin/.env`, `/.git/config`, etc. all return HTTP 200 (serving index.html). While no actual secrets are exposed, this makes the site appear vulnerable to automated scanners.

**Fix:** Add a route in `main.py` before the SPA catch-all that returns 404 for known sensitive paths:

```python
BLOCKED_PATHS = {'.env', '.git', '.vscode', '.DS_Store', 'sftp.json'}

@app.middleware("http")
async def block_sensitive_paths(request: Request, call_next):
    path = request.url.path.lstrip('/')
    for blocked in BLOCKED_PATHS:
        if blocked in path.split('/'):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
    return await call_next(request)
```

---

## Deployment Checklist

| Step | Action | Command/Location |
|------|--------|-----------------|
| 1 | Add `ENV VITE_API_BASE=""` to Dockerfile Stage 1 | `phase3_prototype/Dockerfile` |
| 2 | Add sensitive path blocking middleware | `backend/main.py` |
| 3 | Rebuild and deploy | `gcloud builds submit` + `gcloud run deploy` |
| 4 | Set `GITHUB_APP_REDIRECT_URI` env var | `gcloud run services update --update-env-vars` |
| 5 | Set `CORS_ORIGINS` env var | `gcloud run services update --update-env-vars` |
| 6 | Update GitHub OAuth App callback URL | GitHub Developer Settings |
| 7 | Verify: visit `macpresearch.ysenseai.org`, test search | Browser |
| 8 | Verify: click "Sign in with GitHub", complete flow | Browser |
| 9 | Commit fixes to GitHub | `git add . && git commit && git push` |

Steps 1-3 require a rebuild because `VITE_API_BASE` must be set at build time (Vite inlines it).
Steps 4-6 are runtime configuration changes (no rebuild needed, but must be done after step 3).

---

## GCP Log Security Observations

The logs reveal active bot scanning within hours of deployment. The following probe patterns were detected:

| Pattern | Count | Risk |
|---------|-------|------|
| Environment file probes (`.env`, `.env.production`, etc.) | 20+ | Medium (returns index.html, not actual env) |
| Git config probes (`.git/config`, `.git/HEAD`) | 3 | Medium (returns index.html) |
| API documentation probes (swagger, graphql) | 10+ | Low |
| Framework-specific probes (actuator, telescope, debug) | 5+ | Low |

All probes returned index.html (200) rather than actual sensitive data. Fix BUG-4 to return proper 404s and reduce noise.

---

## Privacy Compliance

This document has been audited. No GCP project IDs, service account credentials, API keys, tokens, or personal identifiers are included.

---

**Signed:** CSO R (Manus AI) — FLYWHEEL TEAM
**Protocol:** Multi-Agent Collaboration Protocol (MACP)
