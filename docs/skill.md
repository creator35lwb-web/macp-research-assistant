# MACP Research Assistant — Skill Definition

## Identity

- **Name:** MACP Research Assistant
- **Version:** 0.1.0-alpha
- **Author:** YSenseAI / FLYWHEEL TEAM
- **License:** MIT
- **Repository:** https://github.com/creator35lwb-web/macp-research-assistant

## Description

A CLI tool for tracking AI-powered research with complete citation provenance. It enables multi-agent research workflows where each AI assistant's contributions are tracked, traced, and recallable.

## Prerequisites

- Python 3.10+
- `pip install -r requirements.txt` (installs `requests`, `jsonschema`)

## Commands

### `discover` — Find and store research papers

Discovers papers from HuggingFace or arXiv and stores them in `.macp/research_papers.json`.

```bash
# By date (HuggingFace Daily Papers)
python tools/macp_cli.py discover --date 2026-02-15

# By date range
python tools/macp_cli.py discover --date-range 2026-02-10:2026-02-15

# By search query (HuggingFace Paper Search API)
python tools/macp_cli.py discover --query "multi-agent systems" --limit 5

# By arXiv ID
python tools/macp_cli.py discover --arxiv-id 2602.06570
```

**Output:** Papers are added to `.macp/research_papers.json` with deduplication.

### `learn` — Record a learning insight

Records an insight linked to specific papers, creating a learning session in `.macp/learning_log.json`.

```bash
python tools/macp_cli.py learn "T-Score 0.3-0.5 is optimal for conflict data" \
  --papers 2602.06570,2602.07890 \
  --agent claude \
  --tags ai-alignment,conflict-data
```

**Parameters:**
- `summary` (required): The key insight text
- `--papers` / `-p` (required): Comma-separated arXiv IDs
- `--agent` / `-a`: Which AI produced this insight (default: "human")
- `--tags` / `-t`: Comma-separated tags
- `--insight` / `-i`: Concise key insight (defaults to summary)
- `--force` / `-f`: Add even if papers aren't in the knowledge base

### `cite` — Record a citation

Links a paper to a project or document with context.

```bash
python tools/macp_cli.py cite 2602.06570 \
  --project "GODELAI C-S-P Design" \
  --context "T-Score range used for conflict data collection" \
  --agent manus-ai
```

**Parameters:**
- `arxiv_id` (required): The arXiv ID of the cited paper
- `--project` / `-p` (required): Name of the project citing this paper
- `--context` / `-c` (required): How the paper is being used
- `--agent` / `-a`: Which agent made the citation (default: "human")

### `recall` — Search the knowledge base

Natural language search across papers, learning sessions, and citations.

```bash
python tools/macp_cli.py recall "conflict data for AI alignment" --limit 10
```

**Parameters:**
- `question` (required): Natural language search query
- `--limit` / `-l`: Max results per category (default: 5)

### `status` — View knowledge base status

Shows paper counts, learning sessions, citations, and recent activity.

```bash
python tools/macp_cli.py status
```

## Data Files

All data is stored in `.macp/` and validated against JSON schemas in `schemas/`.

| File | Schema | Purpose |
|------|--------|---------|
| `.macp/research_papers.json` | `schemas/research_papers_schema.json` | Discovered and analyzed papers |
| `.macp/learning_log.json` | `schemas/learning_log_schema.json` | Learning sessions and insights |
| `.macp/citations.json` | `schemas/citations_schema.json` | Citation records |
| `.macp/knowledge_graph.json` | `schemas/knowledge_graph_schema.json` | Relationship graph |
| `.macp/handoffs.json` | `schemas/handoffs_schema.json` | Agent handoff records |

## Typical Workflow

```
1. discover  → Find papers (Conflict phase)
2. learn     → Extract insights (Synthesis phase)
3. cite      → Apply to projects (Propagation phase)
4. recall    → Query knowledge base anytime
5. status    → Monitor progress
```

## Security

- All inputs are validated and sanitized
- JSON writes use atomic operations (temp file + rename)
- All data validated against JSON schemas before write
- No subprocess calls — all API access via HTTP
- No API keys required (uses free-tier HuggingFace + arXiv APIs)

## Integration Points

- **MACP Protocol:** `.macp/` directory follows MACP v2.0 specification
- **Knowledge Graph:** Run `python tools/knowledge_graph.py` to generate relationship graph + Mermaid diagram
- **VerifiMind-PEAS:** Validated by X-Z-CS RefleXion Trinity (see `peas/` directory)
