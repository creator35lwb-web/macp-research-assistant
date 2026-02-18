# Phase 3B Strategic Plan: Full Hybrid Architecture

**Date:** February 19, 2026  
**Author:** L (Godel), CTO  
**Status:** Approved

---

## 1. Vision for Phase 3B

Phase 3B marks the transition of the MACP Research Assistant from a validated prototype into a **robust, multi-interface, production-ready research engine**. This phase will fully realize the Three-Layer Hybrid Architecture by adding the **Backend MCP Server** and migrating the data plane to a **production-grade database**.

Upon completion, the MACP Research Assistant will be accessible via:

1.  **CLI:** For power users and CI/CD automation.
2.  **Web UI (with WebMCP):** For human-in-the-loop collaborative research.
3.  **Backend MCP Server:** For autonomous AI agents and programmatic integration.

All three layers will share a single, unified, and persistent knowledge base, validated by VerifiMind-PEAS.

## 2. Core Requirements (from Trinity Validation P3B-01 to P3B-05)

These five core requirements, derived from the Phase 3A Trinity Validation, form the technical backbone of Phase 3B.

| ID | Requirement | Implementation Strategy |
| :--- | :--- | :--- |
| **P3B-01** | **Database Integration** | Migrate from JSON files to a **SQLite database** for local-first, production-ready storage. Use SQLAlchemy as the ORM for a clean data access layer. This provides atomicity, concurrency, and scalability. |
| **P3B-02** | **Authentication System** | Implement a simple but secure **API key-based authentication** system for the Backend MCP Server and the FastAPI backend. Keys will be managed in a separate, encrypted configuration file. |
| **P3B-03** | **Externalize Configuration** | Move all hardcoded configurations (API base URLs, database paths, etc.) to a `.env` file, loaded via `python-dotenv`. This allows for flexible deployment across different environments (dev, staging, prod). |
| **P3B-04** | **Enhanced Audit & Transparency** | Implement structured logging (JSON format) for all API requests, analysis calls, and database transactions. Create a new `macp audit` command to view the log. Add a `provenance` field to the `analyses` table to store model version, timestamp, and parameters. |
| **P3B-05** | **Accessibility (Guest Mode)** | Implement a "guest mode" for the web UI. Unauthenticated users can perform a limited number of searches and analyses (e.g., 5 per day), tracked by IP address in a temporary cache. |

## 3. Architecture for Phase 3B

### Backend MCP Server

-   **Framework:** `uc-micro-py` (a lightweight, spec-compliant MCP server framework).
-   **Tools Exposed:**
    -   `macp.discover(query: str, source: str) -> list[Paper]`
    -   `macp.analyze(paper_id: str, provider: str) -> Analysis`
    -   `macp.learn(paper_id: str, insight: str, agent: str)`
    -   `macp.cite(paper_id: str, project: str)`
    -   `macp.recall(query: str) -> list[str]`
-   **Authentication:** Requires a valid API key in the `Authorization: Bearer <key>` header.

### Database Schema (SQLite)

-   **`papers` table:** `id`, `arxiv_id`, `title`, `authors`, `abstract`, `url`, `source`, `added_at`
-   **`analyses` table:** `id`, `paper_id`, `provider`, `summary`, `strengths`, `weaknesses`, `score`, `provenance`, `analyzed_at`
-   **`learning_sessions` table:** `id`, `paper_id`, `insight`, `agent`, `learned_at`
-   **`citations` table:** `id`, `paper_id`, `project`, `cited_at`
-   **`audit_log` table:** `id`, `timestamp`, `level`, `message`, `source_ip`

## 4. Updated Project Roadmap

| Phase | Timeline | Status |
| :--- | :--- | :--- |
| Phase 1 (Manual MACP) | Q1 2026 | ✅ Complete |
| Phase 2 (Semi-Automated CLI) | Q1 2026 | ✅ Complete |
| P-1.5 (Security Pre-Flight) | Q1 2026 | ✅ Complete |
| Phase 3A (WebMCP Prototype) | Q2 2026 | ✅ Complete |
| P-2.5 (Prototype Hardening) | Q2 2026 | ✅ Complete |
| **Phase 3B (Full Hybrid)** | **Q2-Q3 2026** | **🟡 In Progress — Handed to Claude Code** |
| Phase 3C (Public Launch) | Q4 2026 | 📋 Planned |

## 5. Handoff to Claude Code

This document, along with an updated `CLAUDE.md` and a new MACP handoff record, will be committed to the repository. Claude Code is authorized to begin implementation of Phase 3B immediately.
