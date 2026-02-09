# Ecosystem Alignment: MACP Research Assistant

**This document clarifies the role of the `macp-research-assistant` repository within the broader YSenseAI ecosystem.**

---

## 1. Role as a Foundational Protocol

The `macp-research-assistant` is a **public-facing, foundational protocol** designed to introduce the core concepts of the Multi-Agent Communication Protocol (MACP) to a wide audience. Its primary purpose is to serve as a simplified, easy-to-adopt entry point into the world of traceable, multi-AI research.

It is one of several foundational protocols, as illustrated in the official YSenseAI Ecosystem Map.

## 2. Relationship to the Command Central Hub

The **authoritative source of truth** and the operational core of the YSenseAI ecosystem is the **[verifimind-genesis-mcp](https://github.com/creator35lwb-web/verifimind-genesis-mcp)** repository. This private repository acts as the **Command Central Hub** and contains the most advanced, internal version of all protocols, including MACP v2.0.

This `macp-research-assistant` repository should be considered a **downstream, simplified application** of the principles developed in the central hub. It is designed for:

-   **Public Education:** Teaching the core ideas of MACP.
-   **Community Contribution:** Providing a space for open-source contributions to the simplified protocol.
-   **Broad Adoption:** Offering a low-barrier way for individual researchers to start using MACP manually.

## 3. Protocol Versioning

-   **This Repository (Simplified MACP):** The `MACP_SPECIFICATION.md` in this repository describes a simplified, JSON-based protocol suitable for manual use.
-   **Central Hub (Authoritative MACP v2.0):** The `verifimind-genesis-mcp` repository contains the full MACP v2.0 specification, which utilizes a more robust system of markdown-based handoff records, validation reports, and the FLYWHEEL TEAM protocol. This is the version used for all operational, multi-agent workflows within the YSenseAI ecosystem.

**Developers and contributors should reference the central hub for the complete and authoritative protocol specification.**

## 4. Governance via Project Namespaces

As per the *Multi-Project Conflict Assessment & Governance Architecture*, the central hub uses a **Project Namespace** pattern to manage multiple projects. While this repository is a standalone protocol definition, any tools built from it (Phase 2 and beyond) should be designed to be compatible with this governance model by including a `project_id` field in their operations to ensure they can integrate with the central hub.
