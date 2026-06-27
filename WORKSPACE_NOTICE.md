# Workspace Notice

**Last updated:** 2026-06-27 (corrected after git-verified connection audit)

---

## Purpose of This Folder

This folder **IS the development workspace** for the public **MACP Research
Assistant** project. Feature work, commits, and pushes for *this project*
happen here.

| Role | Folder | Git remote |
|------|--------|-----------|
| **This project (develop + deploy)** | `macp-research-assistant` ← YOU ARE HERE | `github.com/creator35lwb-web/macp-research-assistant` (public) |
| **Coordination hub (FLYWHEEL TEAM)** | `verifimind-genesis-mcp-private` | `github.com/creator35lwb-web/verifimind-genesis-mcp` (private) |

> **Verified 2026-06-27:** `git remote -v` confirms this folder pushes to the
> public `macp-research-assistant` repo. The hub folder points to a *different*
> repo and contains coordination docs, skills, and `macp-mcp-server` — **but no
> copy of this codebase**. This project therefore cannot be developed or pushed
> from the hub folder. Develop it here.

---

## What This Folder Is For

- Developing features for the MACP Research Assistant (backend, frontend, CLI tools)
- Running and testing the app locally
- Committing and pushing to `origin/master` (public repo)

## What the Hub Folder Is For

- Cross-project coordination, handoffs, and agent skills (Command Central Hub)
- Internal/private FLYWHEEL TEAM research and planning
- **Not** a place to develop this project's code

---

## Working Across Multiple Platforms / Sessions

This repo is developed by several agents/platforms (Claude Code, Manus AI, etc.).
Before starting work in this folder:

```bash
git fetch origin
git status -sb        # check how far behind origin/master you are
git pull --rebase     # absorb work pushed by other sessions first
```

If you have local uncommitted work, `git stash` before pulling, then `git stash pop`.

---

## Remote (This Repo)

```
https://github.com/creator35lwb-web/macp-research-assistant
```
