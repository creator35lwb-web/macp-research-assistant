# Public-Repo Hygiene — read before committing (all agents)

`macp-research-assistant` is a **PUBLIC showcase repository.** Committing here IS
publishing. This policy keeps internal/operational/strategic material in the
**private hub** (`verifimind-genesis-mcp`), not in the public showcase.

This applies to **every contributing agent** — RNA (Claude Code), CSO-R (Manus AI),
and any other platform — equally. Run the scan in step 3 of the `session-close`
skill before every public commit.

## Private-hub ONLY — never commit to this public repo

- **Operational identifiers:** GCP project/revision/billing IDs, direct `*.run.app`
  URLs (use the public custom domain or placeholders).
- **Business / usage metrics:** WAU/DAU, engagement hours, cohort counts, eval
  scores (e.g. QWK), revenue, impressions.
- **Internal org / agent structure:** C-suite role codenames and Genesis versions.
  (Naming the *platforms* — "Claude Code, Manus AI" — as the multi-agent
  collaboration story is fine; the internal role hierarchy is not.)
- **Unpublished IP:** the existence, status, draft content, or prior-art-scan state
  of any defensive publication or unreleased spec (incl. MACP v2.5 details).
- **Competitive intelligence** and internal strategy codenames (M2, Phase NN, etc.).
- **Personal data:** real names + activity logs.

## Fine to commit publicly

- Project-scoped **technical handoffs** (code changed, decisions, next steps) — the
  original purpose of `.macp/handoffs/`.
- Architecture, capabilities, public model IDs, env-var *names*, Cloud Run revision
  *names of this project* (low-sensitivity), the custom domain, the DOI.
- A **mention** that the protocol is evolving toward MACP v2.5 — without spec details.

## If sensitive content is found already committed

Remove it from the current tree (a normal delete commit). Note: this stops it being
in the working tree / current repo view, but values remain in **git history** — a
full history rewrite (BFG / git filter-repo) is a separate, maintainer-approved step.

---

*Established 2026-06-28 after internal coordination docs were mistakenly committed
to the public repo. Routed back to the private hub. — RNA, with maintainer approval.*
