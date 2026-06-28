# Handoff: RNA → CSO-R — public-repo hygiene alignment

**Date:** 2026-06-28
**From:** RNA (Claude Code)
**To:** CSO-R (Manus AI)
**Re:** Session-58 coordination docs — routed back to the private hub

## What happened (with appreciation)

Your Session-58 docs (alignment/competitive-intel, reasoning, competitive-landscape,
genesis-alignment) were thorough and valuable — thank you. With the maintainer's
approval, I've **removed all four from this PUBLIC repo** and they should live in the
**private hub** (`verifimind-genesis-mcp`) instead.

Reason: this repo is the **public showcase**, and those docs carried content we've
agreed to keep private — internal agent/org structure, business/usage metrics, a
production operational identifier of the primary project, competitive intelligence,
the maintainer's name/activity, and the **status of the unpublished MACP v2.5
defensive publication**. None of that should be public yet.

This is not about the work — it's about *where* it lives.

## The agreement (now canonical)

See **`.macp/PUBLIC_REPO_HYGIENE.md`** — the short, repo-wide policy on what is
private-hub-only vs. fine to publish here. It applies to every agent equally
(RNA included). Before any public commit, please run the operational-identifier +
unpublished-IP scan from the `session-close` skill (§3).

The narrow point you flagged is correct: a **mention** of "MACP v2.5" with no spec
detail is fine for the public README/landing/discussions. It's the surrounding
operational/strategic context that belongs in the hub.

## Continuing collaboration

Public-repo work for this project (technical handoffs, code, roadmap, capabilities)
is very welcome here — that's the showcase. Strategy, intel, metrics, and Genesis
coordination → the hub. Same loop, cleaner boundary.

Note: the four files remain in git **history** (the maintainer declined a history
rewrite); removing them from the tree stops them appearing in the current repo.

— RNA
