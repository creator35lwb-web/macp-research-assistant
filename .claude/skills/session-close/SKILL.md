---
name: session-close
description: Close a development session on the MACP Research Assistant — detect git drift, summarize the work, record decisions/pending, and write a standardized handoff to .macp/handoffs/ so the next agent (Claude Code / Manus / Perplexity) can continue without context loss. Use at the end of a working session, or when the user says "close the session", "create a handoff", "wrap up", or "hand off to the next agent".
---

# Session Close — FLYWHEEL TEAM Handoff Protocol

This project is built by **multiple AI platforms in parallel** (Claude Code/RNA,
Manus AI/CSO-R, Perplexity, founding agent L/GodelAI), coordinated through one
public GitHub repo. Cross-platform continuity depends on **handoff records**, not
memory. This skill standardizes the close so every session ends in a state the
next agent can pick up cleanly.

## When to use

End of a working session, or on: "close the session", "create a handoff",
"wrap up", "hand off to the next agent".

## Procedure

### 1. Detect git drift FIRST (the #1 multi-platform hazard)

Other platforms push to `origin/master` between sessions. Always check before
concluding anything about repo state:

```bash
git fetch origin
git status -sb                       # how far behind/ahead origin/master?
git rev-list --left-right --count master...origin/master   # left=ahead right=behind
```

- If **behind**: warn the user. Do NOT blindly `stash pop` over divergence — check
  collision risk per file (`git diff master..origin/master --stat -- <files>`)
  before reconciling. Prefer `git pull --rebase`; if local uncommitted work
  overlaps remote-changed files, back it up (stash + patch to a temp dir) first.
- If **clean/ahead**: proceed.

**Scan INCOMING commits for hygiene leaks (not just your own).** Other platforms
(e.g. CSO-R / Manus AI) may push internal coordination docs that violate
`.macp/PUBLIC_REPO_HYGIENE.md` (operational identifiers, business metrics, internal
org structure, unpublished-IP status, competitive intel, personal data). Run the
step-3 scans over the incoming range and review new docs:

```bash
git log master..origin/master --name-only            # what landed
git diff master..origin/master | grep -inE "[0-9A-F]{6}-[0-9A-F]{6}-[0-9A-F]{6}|[a-z0-9-]+\.run\.app|WAU|engagement hours|defensive publication|competitive"
```

If a teammate's commit leaked sensitive content into this public repo, surface it
to the maintainer; the fix is a normal delete commit (route it to the private hub)
+ an alignment handoff — NOT silently proceeding. Their work is valuable; it's about
*where* it lives.

### 2. Verify the work is sound

- Run the project's tests for anything touched, e.g.:
  `python tools/test_consensus.py` · `python tools/test_submit.py`
- Compile-check changed Python: `python -m py_compile <files>`
- Confirm `git status` matches what you intend to leave behind.

### 3. Unpublished-IP + operational-identifier scan (BEFORE any public commit)

Committing to the public repo IS publishing. Two classes to keep out of public
commits (especially docs/handoffs/skills):

1. **Unpublished IP** prepared in the private hub (release is the maintainer's call).
2. **Operational identifiers** — these are recon fodder, not credentials, but
   should NOT be broadcast: GCP **billing account IDs**, **project IDs/numbers**,
   and direct **`*.run.app` URLs** (they bypass the custom domain + any edge WAF).
   Use placeholders (`<GCP_PROJECT>`) or dynamic refs (`gcloud config get-value
   project`); reference the public custom domain, not the `.run.app` host.

```bash
git diff | grep -inE "defensive publication|prior art|patent|unpublished|confidential|proprietary|do not publish"
git diff | grep -inE "[0-9A-F]{6}-[0-9A-F]{6}-[0-9A-F]{6}|[a-z0-9-]+\.run\.app|projects/[a-z0-9-]+-[0-9]+|[0-9]{11,}"
```

Architecture details, revision names, region, the custom domain, and env-var
*names* are public-by-design for this open-source project — not secrets.
If anything matches, or you are unsure content is cleared for public release —
STOP and confirm with the maintainer before committing.

### 4. Write the handoff record

Create `.macp/handoffs/YYYYMMDD_<AGENT>_<short-topic>.md` (e.g.
`20260627_RNA_semantic-consensus.md`). Agent codes: **RNA**=Claude Code,
**CSO-R**=Manus AI, **L**=GodelAI/founding, **PPLX**=Perplexity. Include:

- **Header:** date, agent + model, session type
- **Git reconciliation note** (if any drift was handled)
- **Work Completed** — concrete, file-level
- **Decisions** — with the *why*
- **Artifacts** — files modified/created
- **Pending / Next Agent** — the prioritized next steps + who should pick up

### 5. Print a suggested commit message

Conventional-commit style, summarizing the session. Note whether the maintainer
wants commit-only or commit+push (push makes it public; other platforms pull it).

### 6. Confirm outward-facing actions

Commit + push to a public repo is outward-facing and effectively irreversible.
Confirm scope (message, push y/n) with the user unless already explicitly told to
proceed.

## Output

A written handoff file, a one-paragraph session summary, and a ready-to-use
commit message — leaving the repo in a clean, documented, pick-up-ready state.

## Related

- Continuity model + journey context: `docs/DEVELOPMENT_JOURNEY_2026-06-27.md`
- Vision / Phase 5 roadmap: `.macp/handoffs/20260225_CSO-R_vision-gap-analysis-recursive-research.md`
- Inbound coordination: the `macp-inbox` skill (check hub for pending tasks)
