# PWA Strategic Recommendation — MACP Research Assistant

**Author:** CSO R (Manus AI)
**Date:** 2026-02-25
**Type:** Strategic Architecture Decision + Implementation Spec
**Protocol:** MACP v2.0 / Multi-Agent Handoff Bridge
**Decision:** STRONGLY RECOMMENDED — PWA aligns with every strategic pillar

---

## Executive Summary

The question is not whether MACP Research Assistant *should* become a Progressive Web App — it is whether we can afford *not* to. PWA capabilities directly serve the project's three core goals: Human-AI collaboration, deep research workflows, and Agent-to-Agent communication credibility. The implementation cost is low (zero infrastructure spend, ~2 hours of CTO RNA's time), while the strategic value is high across the entire YSenseAI ecosystem.

**Recommendation: YES — implement PWA as Sprint 4A.0 (before Knowledge Graph UI).**

---

## Strategic Alignment Analysis

The following table maps each PWA capability to the MACP Research Assistant's strategic goals. Every capability aligns with at least one pillar, and several capabilities serve all three simultaneously.

| PWA Capability | Human-AI Collaboration | Deep Research | Agent-to-Agent Communication | Alignment Score |
|---------------|:---------------------:|:------------:|:---------------------------:|:--------------:|
| **Installable (Home Screen)** | Researchers install it like a native tool — daily use habit | Quick access to library without browser navigation | Agents see a "real application" not just a webpage | 3/3 |
| **Offline Paper Reading** | Read cached papers on flights, commutes, offline environments | Continue research without internet dependency | Offline cache = local data layer agents can reference | 3/3 |
| **Background Sync** | Save papers offline → auto-sync to GitHub when reconnected | Research continuity across connectivity gaps | GitHub sync queue ensures no data loss between agent handoffs | 3/3 |
| **Push Notifications** | Alert when consensus analysis completes | Notify when new papers match research interests | Agent completion signals delivered to human collaborator | 3/3 |
| **Service Worker Caching** | Instant load times, app feels native | Cached API responses reduce latency for repeated queries | WebMCP calls can be intercepted, queued, and retried | 3/3 |
| **Web Share API** | Share research findings natively (mobile share sheet) | Share papers with collaborators via native OS sharing | N/A | 2/3 |
| **Periodic Background Sync** | Auto-fetch new daily papers without opening the app | Always-fresh research library | Agents can trigger periodic sync for new data | 3/3 |

**Average Alignment Score: 2.86/3.0** — This is exceptionally high. PWA is not a "nice to have" — it is architecturally aligned with the project's DNA.

---

## Why PWA Aligns with WebMCP

The WebMCP protocol defines 13 endpoints that AI agents call to interact with the research platform. Currently, these endpoints require an active internet connection. PWA's service worker creates a **resilience layer** between the agent and the server:

```
CURRENT (fragile):
Agent → HTTP → Cloud Run → Response
         ↑ fails if offline or server cold-starts

WITH PWA (resilient):
Agent → Service Worker → Cache (instant) → Background Sync → Cloud Run
         ↑ always responds, syncs when possible
```

This is particularly important for the MACP v2.0 vision where multiple agents (Manus AI, Claude Code, Perplexity, Cursor, Antigravity) communicate through the platform. A service worker ensures that even if one agent's request arrives during a connectivity gap or a Cloud Run cold start, the request is queued and retried automatically. The research journey is never interrupted.

Furthermore, the service worker can implement **intelligent caching strategies** per endpoint:

| WebMCP Endpoint | Caching Strategy | Rationale |
|----------------|-----------------|-----------|
| `/api/mcp/search` | StaleWhileRevalidate (5 min) | Search results change slowly; serve cache, refresh in background |
| `/api/mcp/analyze` | NetworkFirst | Analysis is unique per request; always try network first |
| `/api/mcp/analyze-deep` | NetworkFirst | Deep analysis is compute-heavy; must reach server |
| `/api/mcp/consensus` | CacheFirst (1 hour) | Consensus for same paper set is stable; cache aggressively |
| `/api/mcp/deep-research` | NetworkFirst | Perplexity results are real-time; must reach server |
| `/api/mcp/agents` | CacheFirst (24 hours) | Agent registry changes rarely; cache for a full day |
| `/recall` (Library) | StaleWhileRevalidate (1 min) | Library is personal; serve cache, sync in background |

---

## Why PWA Aligns with No Burn-Rate Strategy

This is critical. PWA adds zero infrastructure cost:

| Cost Component | Impact |
|---------------|--------|
| Server cost | ZERO — service worker runs in the user's browser |
| CDN cost | REDUCED — cached assets reduce bandwidth |
| Cloud Run cost | REDUCED — fewer cold starts, fewer API calls |
| Development cost | LOW — `vite-plugin-pwa` handles 80% of the work |
| Maintenance cost | MINIMAL — service worker auto-updates with each deploy |

PWA actually *saves* money by reducing Cloud Run invocations through client-side caching. This directly supports the no burn-rate strategy.

---

## Implementation Specification for CTO RNA

### Dependencies

```bash
cd phase3_prototype/frontend
npm install vite-plugin-pwa -D
```

### Vite Configuration

```typescript
// vite.config.ts
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['vite.svg'],
      manifest: {
        name: 'MACP Research Assistant',
        short_name: 'MACP Research',
        description: 'Multi-Agent Collaboration Protocol for AI Research',
        theme_color: '#0a0a1a',
        background_color: '#0a0a1a',
        display: 'standalone',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: '/icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/macpresearch\.ysenseai\.org\/api\/mcp\/agents/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'macp-agents',
              expiration: { maxAgeSeconds: 86400 }
            }
          },
          {
            urlPattern: /^https:\/\/macpresearch\.ysenseai\.org\/api\/mcp\/search/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'macp-search',
              expiration: { maxAgeSeconds: 300, maxEntries: 50 }
            }
          },
          {
            urlPattern: /^https:\/\/macpresearch\.ysenseai\.org\/recall/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'macp-library',
              expiration: { maxAgeSeconds: 60 }
            }
          },
          {
            urlPattern: /^https:\/\/cdn\.jsdelivr\.net\/.*/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'cdn-fonts',
              expiration: { maxAgeSeconds: 604800 }
            }
          }
        ]
      }
    })
  ]
})
```

### Icon Generation

Generate PWA icons from the existing HD logo:

```bash
# Using sharp or any image tool
# Input: docs/assets/macp-logo-hd.png (1024x1024)
# Output: frontend/public/icons/icon-192x192.png
#         frontend/public/icons/icon-512x512.png
```

### Meta Tags

Add to `frontend/index.html`:

```html
<meta name="theme-color" content="#0a0a1a" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
```

### Offline Fallback Page

Create `frontend/public/offline.html` — a minimal page shown when the user is offline and the requested page is not cached. Should display the MACP logo and a message: "You're offline. Your cached papers are still available in My Library."

---

## PWA × VerifiMind-PEAS v0.5.0

When the MACP tool wrappers are registered in VerifiMind-PEAS, the PWA service worker creates an additional resilience layer for MCP tool calls. If a Claude Desktop user invokes `macp_search` through VerifiMind-PEAS and the Cloud Run instance is cold-starting, the service worker can serve cached results immediately while the fresh request completes in the background. This makes the MCP tools feel instantaneous.

Additionally, the PWA's push notification capability can be wired to the existing `notifyOwner` system. When a multi-agent consensus analysis completes (triggered by VerifiMind-PEAS), the platform can push a notification to the researcher's device — even if the browser tab is closed. This closes the loop on the Human-AI collaboration cycle: the human initiates research, agents analyze asynchronously, and the human is notified when results are ready.

---

## PWA × GODELAI Research

For GODELAI research specifically, PWA enables a powerful workflow:

1. **Morning commute:** Open MACP PWA (installed on phone), browse cached daily papers on AI alignment
2. **Offline annotation:** Save interesting papers to library (queued in IndexedDB)
3. **Back online:** Background Sync pushes saves to GitHub automatically
4. **Agent pickup:** Claude Code detects new papers in `.macp/research/`, triggers deep analysis
5. **Push notification:** "Consensus analysis complete for 3 new AI alignment papers"
6. **Evening review:** Open PWA, review multi-agent consensus, export findings

This is the full Human-AI research loop — and PWA makes it seamless across connectivity states.

---

## Sprint Priority Recommendation

Given the low implementation effort and high strategic alignment, PWA should be inserted as **Sprint 4A.0** — before the Knowledge Graph UI:

| Sprint | Priority | Focus | Effort |
|--------|----------|-------|--------|
| **4A.0** | P0 | **PWA Setup** (manifest, service worker, icons, caching) | ~2 hours |
| 4A.1 | P0 | Knowledge Graph UI (D3 visualization) | ~8 hours |
| 4B | P1 | Research Templates + Citations | ~6 hours |
| 4C | P2 | VerifiMind-PEAS v0.5.0 registration | ~4 hours |

**Release:** PWA should ship with v1.1.0 (Knowledge Intelligence Release).

---

## Acceptance Criteria

| Criterion | Test |
|-----------|------|
| Installable | Chrome shows "Install" prompt on desktop and mobile |
| Lighthouse PWA score | ≥ 90 |
| Offline fallback | Disconnect network → app shows offline page with cached library |
| Background sync | Save paper offline → reconnect → paper appears in GitHub |
| Icon quality | 192x192 and 512x512 icons render correctly on all platforms |
| Theme color | Status bar matches `#0a0a1a` dark theme |
| Cache strategy | Repeated searches return cached results instantly |

---

## Sandbox Boundary Check

Created at `/home/ubuntu/macp-research-assistant/.macp/handoffs/20260225_CSO-R_pwa-strategic-recommendation.md`. Will be pushed to GitHub at `macp-research-assistant/.macp/handoffs/20260225_CSO-R_pwa-strategic-recommendation.md`. Accessible to Claude Code and local environment.

---

*CSO R (Manus AI) — FLYWHEEL TEAM*
*"PWA is not a feature. It is the delivery mechanism for Human-AI collaboration."*
