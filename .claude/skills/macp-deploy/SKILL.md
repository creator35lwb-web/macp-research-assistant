---
name: macp-deploy
description: Deploy the MACP Research Assistant backend+frontend to Google Cloud Run safely. Encodes the hard-won gotchas — build via cloudbuild.yaml, deploy by exact digest, route traffic to latest, preserve env vars — plus pre-deploy verification and post-deploy smoke tests. Use when the user says "deploy", "ship to prod", "push to Cloud Run", or "release".
---

# MACP Deploy — Cloud Run Release Protocol

Production service: `macp-research-assistant` · project `ysense-platform-v4-1` ·
region `us-central1` · public URL `https://macpresearch.ysenseai.org`.
Deploy is a MANUAL, outward-facing action — confirm scope before pushing to prod.

## Hard-won gotchas (all bit us on 2026-06-27 — do NOT repeat)

1. **Build with `cloudbuild.yaml`, not `builds submit --tag ... -f Dockerfile`.**
   `-f` is not a valid flag for `builds submit --tag`. The repo's cloudbuild.yaml
   correctly references `phase3_prototype/Dockerfile`.
2. **Deploy by exact `@sha256:` digest, not `:latest`.** `:latest` can resolve to
   a stale image at deploy time. Capture the digest the build prints and deploy that.
3. **Traffic can be PINNED.** If routing is pinned to a specific revision, a new
   deploy builds + goes healthy but gets 0% traffic — the new code silently never
   goes live (symptom: live API still shows old behavior). ALWAYS finish with
   `gcloud run services update-traffic <svc> --region <r> --to-latest`.
4. **Use `--update-env-vars`, NEVER `--set-env-vars`.** `--set-env-vars` REPLACES
   the whole env set, wiping `GEMINI_API_KEY` (breaks analysis + silently disables
   semantic consensus), `SONAR_API_KEY`, `CORS_ORIGINS`. Image-only deploys
   (no env flags) preserve everything and need no shell secrets.

## Procedure

### 1. Pre-deploy verification
```bash
git fetch origin && git status -sb        # clean + not behind origin/master
python tools/test_consensus.py && python tools/test_submit.py
python phase3_prototype/backend/test_submit_endpoint.py
# frontend: cd phase3_prototype/frontend && npx tsc -b
```
Confirm CI is green on the commit (`gh run list --limit 3`). Run the unpublished-IP
scan from the `session-close` skill before anything public.

### 2. Confirm GCP target (read-only)
```bash
gcloud config get-value project          # expect ysense-platform-v4-1
gcloud run services describe macp-research-assistant --region us-central1 \
  --format="value(spec.template.spec.containers[0].env[].name)"   # GEMINI_API_KEY present?
```

### 3. Build (cloudbuild.yaml) and capture the digest
```bash
gcloud builds submit --config cloudbuild.yaml --timeout=900s .
# note the printed:  <name>: digest: sha256:XXXX ...
```

### 4. Deploy that exact digest (env preserved — no env flags)
```bash
gcloud run deploy macp-research-assistant \
  --image gcr.io/ysense-platform-v4-1/macp-research-assistant@sha256:XXXX \
  --region us-central1 --platform managed
```

### 5. Route traffic to latest (the pin safeguard)
```bash
gcloud run services update-traffic macp-research-assistant --region us-central1 --to-latest
```

### 6. Post-deploy smoke tests (non-destructive)
```bash
BASE="https://macpresearch.ysenseai.org"
curl -s "$BASE/api/mcp/" | python -c "import sys,json;d=json.load(sys.stdin);print('tools:',d['count'])"
# new route live? POST a valid body for a NON-existent paper -> expect
# isError 'Paper ... not found' (200), NOT 405 (route missing) / 404.
```
Verify the tool count increased as expected and the custom domain matches the .run.app URL.

### 7. Rollback (if a deploy goes bad)
```bash
gcloud run revisions list --service macp-research-assistant --region us-central1
gcloud run services update-traffic macp-research-assistant --region us-central1 \
  --to-revisions <good-revision>=100
```

## Or just run the script
`./phase3_prototype/deploy-cloudrun.sh` now bakes in cloudbuild.yaml + `--to-latest`
+ `--update-env-vars`. It needs `GITHUB_APP_CLIENT_ID/_SECRET/JWT_SECRET` exported
in the shell (those are the only vars it touches). For an image-only deploy that
needs no secrets, use steps 3–5 above instead.

## Security pre-flight (see also the security posture notes)
- Cloud Run `--max-instances 3` caps EDoS cost — keep it bounded.
- Rate limiting (slowapi) covers main.py search/analyze but NOT the `/api/mcp/*`
  endpoints — treat unauthenticated LLM/write endpoints as an abuse surface.
- Confirm Bandit + Safety CI are green; verify SonarCloud analysis ran.
