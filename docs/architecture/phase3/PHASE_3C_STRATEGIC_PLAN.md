# MACP Research Assistant — Phase 3C Public Launch Strategic Plan

**Project:** MACP Research Assistant
**Phase:** 3C — Public Launch
**Date:** 2026-02-19

---

## 1. Executive Summary

The successful completion of the P-3.5 Pre-Flight has resolved all critical blockers identified during the Phase 3B Trinity Validation. The MACP Research Assistant is now technically sound, secure, and ethically robust, clearing the path for its public launch. 

Phase 3C is not about adding new features; it is about **hardening, documenting, and deploying** the existing full hybrid architecture for public use. This phase will focus on four key pillars: Production Hardening, Community & Documentation, Legal & Compliance, and Deployment & Operations.

## 2. Updated Roadmap

| Phase | Status |
| :--- | :--- |
| Phase 1 (Manual MACP) | ✅ Complete |
| Phase 2 (Semi-Automated CLI) | ✅ Complete |
| P-1.5 (Security Pre-Flight) | ✅ Complete |
| Phase 3A (WebMCP Prototype) | ✅ Complete |
| P-2.5 (Prototype Hardening) | ✅ Complete |
| Phase 3B (Full Hybrid) | ✅ Complete |
| P-3.5 (Pre-Flight Hardening) | ✅ Complete |
| **Phase 3C (Public Launch)** | **🟡 In Progress — This Plan** |

## 3. Phase 3C Implementation Plan

This plan outlines the tasks for Claude Code to execute for the public launch.

### Pillar 1: Production Hardening

| Task ID | Task | Description |
| :--- | :--- | :--- |
| **P3C-H1** | **Unit & Integration Tests** | Implement a comprehensive test suite using `pytest` for the backend and `vitest` for the frontend. Aim for >80% code coverage. |
| **P3C-H2** | **Container Security** | Create a production `Dockerfile` that uses a minimal base image (e.g., `python:3.11-slim`), runs as a non-root user, and includes a health check. |
| **P3C-H3** | **Configuration Validation** | Enhance `config.py` to perform validation on startup and fail fast if critical environment variables (e.g., `DATABASE_URL`) are missing. |

### Pillar 2: Community & Documentation

| Task ID | Task | Description |
| :--- | :--- | :--- |
| **P3C-D1** | **Public API Documentation** | Use FastAPI's automatic OpenAPI/Swagger generation to create comprehensive, interactive API documentation. Add detailed descriptions for every endpoint and model. |
| **P3C-D2** | **User & Developer Guides** | Create a `docs/guides` directory with Markdown files explaining how to use the web UI, the CLI, and the MCP server, and how to contribute to development. |
| **P3C-D3** | **GitHub Community Setup** | Create `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and issue/pull request templates to foster a welcoming open-source community. |

### Pillar 3: Legal & Compliance

| Task ID | Task | Description |
| :--- | :--- | :--- |
| **P3C-L1** | **Terms of Service & Privacy Policy** | Create `docs/legal/TERMS_OF_SERVICE.md` and `docs/legal/PRIVACY_POLICY.md`. These should be professionally reviewed but can be based on standard open-source templates. |
| **P3C-L2** | **License** | Ensure the `LICENSE` file (currently MIT) is appropriate for the project's goals. |

### Pillar 4: Deployment & Operations

| Task ID | Task | Description |
| :--- | :--- | :--- |
| **P3C-O1** | **CI/CD Pipeline** | Create a GitHub Actions workflow (`.github/workflows/main.yml`) that runs tests on every push and automates the build and deployment process. |
| **P3C-O2** | **Deployment Scripts** | Create a `scripts` directory with shell scripts to automate deployment, database migrations, and backups. |

## 4. Handoff to Claude Code

This strategic plan provides the blueprint for the final push to public launch. The next step is to hand this off to Claude Code for execution.
