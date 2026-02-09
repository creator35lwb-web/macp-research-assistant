# MACP Research Assistant: Phase 2 Architecture

**Date:** February 10, 2026
**Author:** L (Godel), AI Agent & Project Founder
**Status:** Proposed Architecture

---

## 1. Goal

To build the semi-automated features of the MACP Research Assistant, transitioning it from a conceptual blueprint into a functional, intelligent research tool. This phase focuses on creating a suite of Python tools to automate paper discovery, logging, and recall, all while showcasing the GODELAI C-S-P framework.

## 2. Core Components

Phase 2 will be built as a collection of modular Python scripts and a central Command-Line Interface (CLI) to orchestrate the research workflow. All tools will read from and write to the `.macp/` directory, using the JSON schemas for data validation.

### 2.1. Data Pipelines (The "Discovery" Engine)

We will leverage three distinct, powerful data pipelines for paper discovery:

| Pipeline | Source | Method | Use Case |
| :--- | :--- | :--- | :--- |
| **1. Daily Papers** | `hysts-bot-data/daily-papers` HF Dataset | Direct dataset loading via `datasets` library | Fetching all papers for a specific date range. |
| **2. Semantic Search** | `paper_search` MCP Tool | `manus-mcp-cli` | Finding relevant papers based on a natural language query (e.g., "memory augmented language models"). |
| **3. Direct Fetch** | `arXiv API` | Standard HTTP requests | Retrieving detailed, up-to-the-minute metadata for a specific arXiv ID. |

### 2.2. The `paper_fetcher.py` Module

This will be the core data access library for the project.

-   **`fetch_by_date(start_date, end_date)`:** Loads the `hysts-bot-data/daily-papers` dataset, filters by the date range, and returns a list of paper objects.
-   **`fetch_by_query(query, limit)`:** Calls the `paper_search` MCP tool and returns a list of paper objects.
-   **`fetch_by_id(arxiv_id)`:** Queries the arXiv API to get the full, canonical metadata for a single paper.
-   **`normalize_paper(paper_data)`:** A utility function to convert paper data from any of the three pipelines into the standardized format defined by our `research_papers_schema.json`.

### 2.3. The `macp_cli.py` Orchestrator

This will be the user-facing tool for interacting with the research assistant. It will use a library like `click` or `argparse` to create a clean CLI.

**Commands:**

-   `macp discover --query "..."` or `macp discover --date YYYY-MM-DD`
    -   Calls the appropriate function in `paper_fetcher.py`.
    -   For each discovered paper, it checks if the `arxiv_id` already exists in `research_papers.json`.
    -   If not, it adds the new paper with `status: "discovered"` and `discovered_by: "macp_cli"`.
    -   Validates the updated `research_papers.json` against the schema.

-   `macp learn "<summary of key insight>" --papers <arxiv_id_1>,<arxiv_id_2>`
    -   Creates a new session in `learning_log.json`.
    -   Links the insight to the specified papers.
    -   Updates the `status` of the linked papers to `analyzed`.

-   `macp cite <arxiv_id> --in "<project_name>" --context "..."`
    -   Adds a new entry to `citations.json`.

-   `macp recall "<question>"`
    -   Performs a semantic search across the `summary` fields in `learning_log.json` and the `title`/`abstract` fields in `research_papers.json`.
    -   Presents a synthesized answer, listing the key insights and the papers they came from.

## 3. Showcasing the GODELAI C-S-P Framework

This architecture is a direct implementation of the **Conflict-Synthesis-Propagation (C-S-P)** framework.

-   **Conflict (C):** The `discover` command intentionally uses multiple, overlapping data pipelines. A semantic search might return a paper that the daily feed missed, or vice-versa. The tool will highlight these discrepancies, forcing the researcher to resolve the **conflict** and decide what is relevant.

-   **Synthesis (S):** The `learn` and `recall` commands are the core of **synthesis**. The `learn` command forces the user to synthesize their findings into a concise summary. The `recall` command synthesizes information from across the entire knowledge base to answer a high-level question.

-   **Propagation (P):** The `cite` command is the act of **propagation**. It takes a synthesized insight from the research phase and propagates it into a concrete application or project, creating a traceable link from foundational research to final output.

## 4. Development Plan

This architecture will be implemented in the following order, corresponding to the project plan phases:

1.  **Phase 4:** Build `paper_fetcher.py` and the `macp discover` command.
2.  **Phase 5:** Build the `macp learn` and `macp recall` commands.
3.  **Phase 6:** Build the `macp cite` command and the `knowledge_graph.py` generator.

This phased approach ensures we deliver value incrementally, starting with the most critical feature: intelligent paper discovery.
