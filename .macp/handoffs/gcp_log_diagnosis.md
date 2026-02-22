# GCP Log Scan + Production Bug Diagnosis

## Log Summary (320 entries)

| Metric | Value |
|--------|-------|
| Total entries | 320 |
| 200 OK | 231 |
| 302 Redirect | 82 (ACME cert challenges + HTTP→HTTPS) |
| 404 Not Found | 7 (early revision before static files worked) |
| Bot/scanner probes | 60+ (env files, swagger, graphql, actuator) |
| User /search or /api/auth requests | **0** (never reached server) |

## Root Cause Analysis

### BUG-1: Frontend API calls go to localhost:8000

**File:** `frontend/src/api/client.ts` line 4
```ts
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
```

**File:** `frontend/src/hooks/useAuth.ts` line 29
```ts
const loginUrl = `${import.meta.env.VITE_API_BASE || "http://localhost:8000"}/api/auth/github`;
```

**Problem:** `VITE_API_BASE` is never set during Docker build. The Dockerfile has no `ARG VITE_API_BASE` or `ENV VITE_API_BASE`. Since Vite inlines env vars at build time, the fallback `http://localhost:8000` gets baked into the production JS bundle.

**Fix:** Since the frontend and backend are served from the same origin in production (backend serves static files from `/app/static`), `VITE_API_BASE` should be set to empty string `""` so all API calls use relative paths (e.g., `/search` instead of `http://localhost:8000/search`).

### BUG-2: CSP blocks connect-src to api.github.com

**File:** `backend/security.py` line 39
```python
"connect-src 'self' https://api.github.com"
```

**Problem:** The CSP `connect-src` allows `'self'` and `https://api.github.com`. But the frontend is trying to connect to `http://localhost:8000` which is neither `'self'` nor `api.github.com`. The CSP correctly blocks it. Once BUG-1 is fixed (relative URLs), the `'self'` directive will allow the API calls.

However, the `api.github.com` in connect-src is unnecessary since GitHub API calls happen server-side, not from the browser.

### BUG-3: GitHub OAuth redirect_uri points to localhost

**File:** `backend/config.py` line 62-63
```python
GITHUB_APP_REDIRECT_URI: str = os.getenv(
    "GITHUB_APP_REDIRECT_URI", "http://localhost:8000/api/auth/github/callback"
)
```

**Problem:** The `GITHUB_APP_REDIRECT_URI` env var was never set in the Cloud Run deployment. The deploy script only sets `ENFORCE_HTTPS=true`. The default fallback is `http://localhost:8000/api/auth/github/callback`.

### BUG-4: CORS_ORIGINS defaults to localhost only

**File:** `backend/config.py` line 44-46
```python
CORS_ORIGINS: list[str] = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
]
```

**Problem:** Not set in Cloud Run env vars. However, since frontend is served from the same origin, this is less critical but should still be set correctly.

### BUG-5: SPA catch-all serves index.html for sensitive paths

All requests to `/.env`, `/api/.env`, `/admin/.env` etc. return 200 with index.html content. While no actual secrets are exposed, this is a security concern as it makes the site look vulnerable to scanners.

## Required Fixes (Priority Order)

### Fix 1: Set VITE_API_BASE="" in Dockerfile (CRITICAL)
Add to Dockerfile Stage 1 before `RUN npm run build`:
```dockerfile
ENV VITE_API_BASE=""
```

### Fix 2: Set GITHUB_APP_REDIRECT_URI in Cloud Run (CRITICAL)
```bash
gcloud run services update macp-research-assistant \
  --set-env-vars "GITHUB_APP_REDIRECT_URI=https://macpresearch.ysenseai.org/api/auth/github/callback"
```

### Fix 3: Set CORS_ORIGINS in Cloud Run (IMPORTANT)
```bash
gcloud run services update macp-research-assistant \
  --set-env-vars "CORS_ORIGINS=https://macpresearch.ysenseai.org"
```

### Fix 4: Update GitHub OAuth App callback URL (CRITICAL)
In GitHub Developer Settings, update the OAuth App's "Authorization callback URL" to:
`https://macpresearch.ysenseai.org/api/auth/github/callback`

### Fix 5: Add static file exclusions for sensitive paths (RECOMMENDED)
Add a route in main.py that returns 404 for paths like `/.env`, `/.git/`, etc. before the SPA catch-all.
