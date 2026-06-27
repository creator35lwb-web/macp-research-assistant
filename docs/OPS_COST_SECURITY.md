# Ops Runbook — Cost & Security (Solo / Open-Source)

**Audience:** the solo maintainer. **Philosophy:** maximum protection per dollar.
This project deliberately avoids premium GCP services (e.g. Cloud Armor ≈
$5/policy/mo + $0.75/rule + per-request) and leans on **free tiers + app-level
controls + financial guardrails**.

---

## 1. The cost-smart security stack

| Layer | What | Cost | Status |
|-------|------|------|--------|
| Financial backstop | **GCP billing budget + alerts** | Free | ✅ Done ("All projects" budget) |
| Edge DDoS/WAF/cache | **Cloudflare free tier** in front of the domain | Free | ⏳ TODO (see §3) |
| Compute cost cap | Cloud Run `--max-instances 3`, scale-to-zero | Free | ✅ Live |
| App rate limiting | slowapi on `/api/mcp/*` (20/min LLM, 60/min submit) | Free | ✅ Live |
| Write protection | `submit-analysis` requires GitHub auth | Free | ✅ Live |
| Headers/validation | CSP, HSTS, X-Frame DENY, schema validation, prompt-injection sanitization | Free | ✅ Live |
| Static analysis | Bandit + Safety (CI) + **SonarCloud CI-gated** | Free (public repo) | ✅ / see §4 |
| Repo/infra hardening | Command Central Hub CI/CD + IP blocking on sensitive-info probes | Free | ✅ (hub) |

> **EDoS reality for a solo dev:** rate limits slow an attacker, but the
> *financial* cap is the budget (§2) + `max-instances` (already 3). Set the
> budget first — it's the difference between a bad day and a bad invoice.

---

## 2. GCP billing budget + alerts (free)

**Status (2026-06-27): ✅ DONE.** An **"All projects"** budget is configured on
billing account `<BILLING_ACCOUNT_ID>`, so `<GCP_PROJECT>` is covered
(alongside `verifimind-mcp-server`). No per-project budget needed.

For reference, to create/adjust one:

1. Console → **Billing → Budgets & alerts → Create budget**
2. Scope: project `<GCP_PROJECT>` (or the whole billing account)
3. Amount: a monthly cap you're comfortable with (e.g. **$15–25**)
4. Alert thresholds: **50% / 90% / 100%** → email to `creator35lwb@gmail.com`
5. (Optional) Enable **"Connect a Pub/Sub topic"** later if you want
   programmatic auto-shutdown; email alerts are enough to start.

A budget does NOT cap spend automatically — it *alerts* you. For a hard stop,
the real cap is Cloud Run `--max-instances 3` (compute) + the LLM free tiers.

---

## 3. Cloudflare free tier (the free Cloud Armor alternative)

Gives unmetered DDoS mitigation, managed WAF rules, **edge caching** (which also
*lowers* Cloud Run cost by absorbing probes/scans), and up to 5 free rate-limit
rules — all on `macpresearch.ysenseai.org`.

1. Create a free Cloudflare account; **add the `ysenseai.org` zone**.
2. Update the domain's nameservers at your registrar to Cloudflare's.
3. DNS: point the `macpresearch` record (CNAME/A) at your Cloud Run service URL
   (from `gcloud run services describe ... --format='value(status.url)'`),
   **proxied (orange cloud ON)**.
   - Cloud Run custom-domain mapping stays; Cloudflare sits in front.
4. SSL/TLS mode: **Full (strict)** (Cloud Run serves valid TLS).
5. Enable free protections:
   - **Security → WAF → Managed rules** (free managed ruleset)
   - **Security → Bots** → enable "Bot Fight Mode" (free)
   - **Caching** → cache static assets; respect the app's `Cache-Control`
   - **Security → Rate limiting** → add a rule (e.g. 100 req/min/IP to `/api/*`)
     as an edge backstop in front of the app-level slowapi limits.
6. Keep `--allow-unauthenticated` on Cloud Run (Cloudflare is the front door).

### 3a. Lock the origin so direct `*.run.app` hits can't bypass Cloudflare (free)

Strict ingress (`internal-and-cloud-load-balancing`) needs a paid HTTPS Load
Balancer (~$18/mo) — skip it. Instead use the built-in **origin-secret guard**
(`OriginGuardMiddleware`): Cloudflare injects a secret header; the app rejects
`/api/*` requests that lack it. Free, app-layer, scoped to /api/* (static + health
stay reachable). Activate:

1. Generate a random secret: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Cloudflare → **Rules → Transform Rules → Modify Request Header → Create**:
   "Set static" header `X-Origin-Secret` = the secret, for all requests.
3. Set it on the service (preserves other env vars):
   ```bash
   gcloud run services update macp-research-assistant --region us-central1 \
     --update-env-vars CF_ORIGIN_SECRET=<the-secret>
   ```
4. Verify: `https://macpresearch.ysenseai.org/api/mcp/` works (via Cloudflare),
   but a direct `curl https://<service>.run.app/api/mcp/` now returns **403**.

Until `CF_ORIGIN_SECRET` is set, the guard is a **no-op** — safe to deploy first,
activate later. To roll back: remove the env var
(`--remove-env-vars CF_ORIGIN_SECRET`).

**Why this beats Cloud Armor here:** comparable L7 protection + origin lockdown at
**$0/mo**, and the caching actively reduces your container invocations (= lower bill).

---

## 4. SonarCloud — CI-gated analysis

Dashboard: <https://sonarcloud.io/project/overview?id=creator35lwb-web_macp-research-assistant>

CI-gated (fail the build on Quality Gate breach) is more secure than Automatic
Analysis. This repo ships `sonar-project.properties` + `.github/workflows/sonarcloud.yml`.

To activate:
1. SonarCloud → My Account → **Security → generate a token**.
2. GitHub repo → **Settings → Secrets and variables → Actions → New secret**:
   name `SONAR_TOKEN`, value = the token.
3. SonarCloud project → **Administration → Analysis Method → turn OFF
   "Automatic Analysis"** (CI and Automatic are mutually exclusive).
4. Push — the `SonarCloud` workflow runs; `sonar.qualitygate.wait=true` fails CI
   if the gate fails. Set the Quality Gate to "Sonar way" (default) to start.

---

## 5. Deploy & rollback

Use the **`macp-deploy`** skill (build via cloudbuild.yaml → deploy by digest →
`--to-latest`). Rollback:
```bash
gcloud run revisions list --service macp-research-assistant --region us-central1
gcloud run services update-traffic macp-research-assistant --region us-central1 \
  --to-revisions <good-revision>=100
```

## 6. Quick monthly check
- Billing → review spend vs budget; investigate any spike (likely EDoS or a loop)
- Cloud Run → revisions/metrics: request count, instance time, 4xx/5xx
- Cloudflare → Security events: blocked threats, top source IPs
- SonarCloud → new issues / Quality Gate status
- Dependabot + Safety: pending dependency CVEs
