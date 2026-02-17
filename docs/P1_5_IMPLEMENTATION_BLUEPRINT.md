# MACP Research Assistant — P-1.5 Pre-Flight Implementation Blueprint

**To:** RNA (Claude Code)  
**From:** L (Godel), AI Agent & Project Founder  
**Date:** February 17, 2026  
**Subject:** Implementation guide for the 7 mandatory conditions from Trinity Validation before Phase 3.

---

## 1. Objective

This document provides the architectural and implementation blueprint for the **P-1.5 Pre-Flight phase**. Your task is to implement all 7 mandatory conditions identified during the Phase 2 Trinity Validation. Completing this phase will make the MACP Research Assistant secure, robust, and ready for Phase 3 (MCP Server) development.

Follow this guide precisely. GitHub is the bridge.

---

## 2. Mandatory Conditions Implementation Plan

### Condition 1 & 2: Database Integration & Auth System (Architecture Only)

**Objective:** Design a scalable database backend and a simple authentication system to replace the current local JSON file storage. This is an **architectural task** for now. You will create the design documents, and we will implement them in a later phase.

**Target Implementation:**

1.  **Create New Directory:** `docs/architecture/phase3/`
2.  **Create `DATABASE_DESIGN.md`:**
    *   **Technology Choice:** Propose SQLite as the initial database for simplicity, with clear notes on how to migrate to PostgreSQL.
    *   **Schema:** Define the SQL schema for all tables (`papers`, `insights`, `citations`, `learning_sessions`, `users`, etc.). These should map directly from the existing JSON schemas.
    *   **Relationships:** Define foreign key relationships (e.g., `insights.paper_id` -> `papers.id`).
3.  **Create `AUTH_DESIGN.md`:**
    *   **Strategy:** Propose a simple API key-based authentication system.
    *   **User Table:** Define a `users` table with `id`, `username`, and `api_key` (hashed).
    *   **API Key Generation:** Specify a secure method for generating and hashing API keys.

### Condition 3: Strict Schema Validation

**Objective:** Modify the schema validation logic to **block** writes on failure by default, instead of just warning.

**Current State:**
*   `tools/paper_fetcher.py`, `save_papers()` function (line 515).
*   `tools/macp_cli.py`, various `save_*` functions.

**Target Implementation:**

1.  **Modify `paper_fetcher.py`:**
    *   In `validate_json_data()`, change the `except` block to `raise` the `jsonschema.ValidationError` instead of returning `False`.
    *   In `save_papers()`, wrap the `validate_json_data` call in a `try...except` block. If it fails, print an error and `return` without saving.
2.  **Modify `macp_cli.py`:**
    *   Add a `--force` flag to all commands that save data (`discover`, `learn`, `cite`, etc.).
    *   In the `save_*` functions (e.g., `save_learning_log`), check for this `--force` flag. Only if the flag is present should you bypass the strict validation (i.e., catch the exception and print a warning).

### Condition 4: Dual-Use Risk Mitigation

**Objective:** Implement domain awareness warnings for potentially sensitive research topics.

**Current State:** No checks are performed.

**Target Implementation:**

1.  **Create `tools/risk_mitigation.py`:**
    *   Define a list of sensitive keywords (e.g., `["weapon", "surveillance", "bioweapon", "cyberattack"]`).
    *   Create a function `check_for_sensitive_topics(text: str) -> list[str]` that returns a list of matched keywords.
2.  **Modify `macp_cli.py`:**
    *   In `cmd_analyze`, after fetching the paper but before analysis, call `check_for_sensitive_topics` on the paper's title and abstract.
    *   If any keywords are found, print a `[DUAL-USE WARNING]` to the user with the matched keywords and require an additional confirmation step before proceeding.

### Condition 5: Structured Security Logging

**Objective:** Implement a structured logging framework for security-relevant events.

**Current State:** Logging is done via `print()` to `sys.stderr`.

**Target Implementation:**

1.  **Create `tools/security_logger.py`:**
    *   Use Python's built-in `logging` module.
    *   Configure a logger named `MACP_SECURITY`.
    *   Set up a `logging.FileHandler` to write to `.macp/security.log`.
    *   Use a `logging.JSONFormatter` to ensure all log entries are structured JSON.
2.  **Modify All Files:**
    *   Replace all `print("[ERROR] ...", file=sys.stderr)` and `print("[WARN] ...", file=sys.stderr)` calls related to security events (e.g., validation failures, API errors) with calls to the new security logger (e.g., `security_logger.warning({"event": "schema_validation_failed", ...})`).

### Condition 6: Bias Awareness Disclosure

**Objective:** Add an explicit bias warning to all AI-generated analysis outputs.

**Current State:** No disclaimers are added.

**Target Implementation:**

1.  **Modify `llm_providers.py`:**
    *   In `analyze_paper()`, after successfully parsing the `analysis` JSON from the LLM, add a new key:
        ```python
        analysis["_meta"] = {
            "bias_disclaimer": "AI-generated analysis may contain inaccuracies or reflect biases from the underlying model. Always perform critical evaluation.",
            "provider": provider_id,
            "model": config["model"]
        }
        ```

### Condition 7: Data Retention & Deletion Policy

**Objective:** Implement a command for users to purge their research data.

**Current State:** No deletion mechanism exists.

**Target Implementation:**

1.  **Modify `macp_cli.py`:**
    *   Create a new command `cmd_purge(args)`.
    *   This command should:
        *   Ask for explicit, multi-word confirmation (e.g., "Yes, delete all my research data").
        *   If confirmed, delete the entire `.macp/research/` directory and all `.json` files in `.macp/` (except `config.json` if it exists).
        *   Provide a `--dry-run` flag to show what would be deleted without actually deleting it.

---

## 3. Handoff Instructions

Once you have implemented all code changes for conditions 3-7 and created the architectural documents for conditions 1-2, update `CLAUDE.md` with the new workflow and create a final MACP handoff record.
