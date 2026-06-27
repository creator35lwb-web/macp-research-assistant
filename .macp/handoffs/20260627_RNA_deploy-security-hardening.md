# Session Handoff - 2026-06-27 (session 3 of the day)

**Agent:** Claude Code (Opus 4.8) — RNA
**Session Type:** Phase 5A web endpoint + production deploy + security hardening (P1) + ops runbook
**Continues from:** `20260627_RNA_consensus-ui-autoresearch.md`

## Git Reconciliation
No drift — local `master` 0 ahead / 0 behind `origin/master` throughout.
Commits pushed this session (all green, on origin/master):
- `4093ffc` — POST /api/mcp/submit-analysis (Phase 5A web endpoint)
- `59933fc` — deploy-cloudrun.sh hardening + macp-deploy skill
- `4a8ffef` — P1 security: MCP rate limits + auth on submit-analysis
- `3b2906f` — CI-gated SonarCloud config + OPS_COST_SECURITY runbook

## Work Completed

### 1. Phase 5A — Agent Submission Layer COMPLETE (CLI + web)
- `webmcp.py`: `POST /api/mcp/submit-analysis` (FastAPI). Resolves paper, persists
  provenance-tracked Analysis, dual-writes GitHub + manifest, supports
  `continues_from` chains. Registered in MCP discovery (`macp.submit-analysis`,
  13 tools total). Integration tests `test_submit_endpoint.py` (6/6).

### 2. DEPLOYED to production (Cloud Run)
- Live: rev `macp-research-assistant-00039-z42`, 100% traffic, project
  `<GCP_PROJECT>`, region us-central1. Semantic consensus + submit-analysis
  now live; env (GEMINI_API_KEY etc.) preserved.
- **Deploy saga / root cause (important for next agent):** the deploy initially
  appeared to "not take" — discovery kept showing old code. Root cause was NOT the
  build (verified the uploaded source had the code) and NOT layer caching — it was
  **traffic PINNED to revision 00035-vhx**, so new revisions built + went healthy
  but got 0% traffic. Fix: `gcloud run services update-traffic --to-latest`. This
  is now baked into deploy-cloudrun.sh and the macp-deploy skill.

### 3. P1 security hardening (live in prod)
- New `phase3_prototype/backend/rate_limit.py`: limiter + 3-tier key extracted
  from main.py so webmcp can apply limits WITHOUT a circular import.
- Rate limits on expensive `/api/mcp/*`: analyze, analyze-deep, consensus,
  deep-research = 20/min/key (RATE_LIMIT_AUTH_ANALYZE); submit-analysis = 60/min.
- `submit-analysis` now requires GitHub auth (`require_user`) — closes the
  unauthenticated DB-write vector. Verified in prod: 401 without login.

### 4. Deploy + ops tooling
- `deploy-cloudrun.sh`: build via cloudbuild.yaml (the `-f` form is invalid for
  `builds submit --tag`), `--update-env-vars` (never `--set-env-vars` — would wipe
  GEMINI_API_KEY), `--to-latest` safeguard.
- `macp-deploy` skill: full release protocol + gotchas + rollback.
- `sonar-project.properties` + `.github/workflows/sonarcloud.yml`: CI-gated
  SonarCloud (quality-gate wait).
- `docs/OPS_COST_SECURITY.md`: solo/OSS cost-first runbook.
- `/security-review` run on pending changes: clean (no exploitable findings).

## Decisions
- **No Cloud Armor** (too costly for a solo OSS dev). Use **Cloudflare free tier**
  as the L7 DDoS/WAF/cache front + a **GCP billing budget** as the EDoS financial
  backstop. App-level rate limits + max-instances 3 cap compute.
- **CI-gated SonarCloud** over Automatic Analysis (more secure / gate enforcement).
- `submit-analysis` **requires auth** — it's a write; real agents carry the user token.

## Artifacts
- New: `rate_limit.py`, `test_submit_endpoint.py`, `sonar-project.properties`,
  `.github/workflows/sonarcloud.yml`, `docs/OPS_COST_SECURITY.md`,
  `.claude/skills/macp-deploy/SKILL.md`, this handoff.
- Modified: `webmcp.py`, `main.py`, `deploy-cloudrun.sh`.

## Pending / Next Agent

### Maintainer manual actions (cannot be done by an agent — account/console/DNS)
1. **GCP billing budget** — verify/create for project `<GCP_PROJECT>`.
   Could NOT verify via gcloud (Billing Budget API disabled + billing perms). The
   existing VeriFimind budget may be scoped to that project only — check the
   budget's SCOPE in console: if it covers "all projects" on billing account
   <BILLING_ACCOUNT_ID>, this project is already covered; if it lists only
   verifimind-mcp-server, add coverage for <GCP_PROJECT>. (Runbook §2.)
2. **SonarCloud CI**: add GitHub secret `SONAR_TOKEN` + turn OFF Automatic Analysis
   in SonarCloud (mutually exclusive). Until then the new SonarCloud CI check FAILS
   (harmless — not a required check; doesn't affect the app). (Runbook §4.)
3. **Cloudflare free tier**: proxy macpresearch.ysenseai.org (Runbook §3).

### Next code (Phase 5 — from CSO-R vision-gap analysis)
- Component 2: Topic Taxonomy (`.macp/topics/` hierarchical tree, auto-classify by
  relevance_tags, "Go Deeper" trigger).
- Component 3: Research Queue (`.macp/queue/`).
- Component 5: "Go Deeper" trigger; extend continuation with `recommended_next`.

**Next agent:** RNA (or any platform). Start with Component 2 (Topic Taxonomy);
the Agent Submission Layer it builds on is done and live.
