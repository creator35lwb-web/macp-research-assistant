#!/usr/bin/env python3
"""
MACP Research Assistant — Backend MCP Server (Phase 3B)
========================================================
A JSON-RPC 2.0 / MCP-compliant server exposing 5 research tools
over stdio transport. Designed for autonomous AI agent integration.

Tools:
  - macp.discover  — Search for papers
  - macp.analyze   — Analyze a paper with an LLM
  - macp.learn     — Record a learning insight
  - macp.cite      — Create a citation record
  - macp.recall    — Search local knowledge base

Author: RNA (Claude Code)
Date: February 19, 2026
"""

import json
import os
import sys
from typing import Any

# Setup paths so we can import sibling modules and tools
_backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _backend_dir)

from config import MACP_API_KEY, MCP_SERVER_PORT, TOOLS_DIR
from database import (
    Analysis,
    Citation,
    LearningSession,
    Paper,
    SessionLocal,
    init_db,
    log_audit,
    upsert_paper,
)
from auth import verify_api_key

# Add tools directory for paper_fetcher and llm_providers
sys.path.insert(0, os.path.abspath(TOOLS_DIR))
from paper_fetcher import fetch_by_id, fetch_by_query, fetch_from_hysts
from llm_providers import analyze_paper as _analyze_paper, PROVIDERS


# ---------------------------------------------------------------------------
# MCP Protocol Constants
# ---------------------------------------------------------------------------

MCP_VERSION = "2024-11-05"

SERVER_INFO = {
    "name": "macp-research-assistant",
    "version": "0.2.0",
}

TOOLS = [
    {
        "name": "macp.discover",
        "description": "Search for academic papers by query string.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "source": {
                    "type": "string",
                    "enum": ["hysts", "hf", "arxiv"],
                    "default": "hysts",
                    "description": "Data source: hysts (HuggingFace daily papers), hf (HuggingFace API), arxiv (arXiv by ID)",
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50,
                    "description": "Maximum number of results",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "macp.analyze",
        "description": "Analyze a paper using an LLM provider. Paper must exist in the database (search first).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paper_id": {"type": "string", "description": "arXiv paper ID (e.g., 'arxiv:2401.12345')"},
                "provider": {
                    "type": "string",
                    "default": "gemini",
                    "description": "LLM provider to use for analysis",
                },
            },
            "required": ["paper_id"],
        },
    },
    {
        "name": "macp.learn",
        "description": "Record a learning insight about a paper.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paper_id": {"type": "string", "description": "arXiv paper ID"},
                "insight": {"type": "string", "description": "The insight or takeaway to record"},
                "agent": {
                    "type": "string",
                    "default": "mcp-agent",
                    "description": "Name of the agent recording the insight",
                },
            },
            "required": ["paper_id", "insight"],
        },
    },
    {
        "name": "macp.cite",
        "description": "Create a citation record linking a paper to a project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paper_id": {"type": "string", "description": "arXiv paper ID"},
                "project": {"type": "string", "description": "Project name to cite in"},
                "context": {
                    "type": "string",
                    "default": "",
                    "description": "Context for the citation",
                },
            },
            "required": ["paper_id", "project"],
        },
    },
    {
        "name": "macp.recall",
        "description": "Search the local knowledge base for papers and learning sessions matching a query.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query to match against titles, abstracts, and insights"},
            },
            "required": ["query"],
        },
    },
]


# ---------------------------------------------------------------------------
# Tool Implementations
# ---------------------------------------------------------------------------

def _resolve_paper(db, paper_id: str) -> Paper:
    """Resolve an arxiv_id to a Paper ORM object, or raise ValueError."""
    if not paper_id.startswith("arxiv:"):
        paper_id = f"arxiv:{paper_id}"
    paper = db.query(Paper).filter(Paper.arxiv_id == paper_id).first()
    if not paper:
        raise ValueError(f"Paper {paper_id} not found. Use macp.discover first.")
    return paper


def tool_discover(args: dict) -> dict:
    query = args.get("query", "")
    source = args.get("source", "hysts")
    limit = args.get("limit", 10)

    if not query:
        raise ValueError("query is required")

    if source == "hysts":
        papers = fetch_from_hysts(query, limit=limit)
    elif source == "hf":
        papers = fetch_by_query(query, limit=limit)
    elif source == "arxiv":
        paper = fetch_by_id(query)
        papers = [paper] if paper else []
    else:
        papers = fetch_from_hysts(query, limit=limit)

    db = SessionLocal()
    try:
        for p in papers:
            upsert_paper(db, p)
        log_audit(event="mcp_discover", message=f"query='{query}' results={len(papers)}", db=db)
    finally:
        db.close()

    return {"results": papers, "count": len(papers), "source": source}


def tool_analyze(args: dict) -> dict:
    paper_id = args.get("paper_id", "")
    provider = args.get("provider", "gemini")

    if not paper_id:
        raise ValueError("paper_id is required")
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDERS.keys())}")

    db = SessionLocal()
    try:
        paper = _resolve_paper(db, paper_id)
        title = paper.title
        authors = json.loads(paper.authors) if paper.authors else []
        abstract = paper.abstract or ""

        if not abstract:
            raise ValueError("Paper has no abstract — cannot analyze.")

        analysis = _analyze_paper(title=title, authors=authors, abstract=abstract, provider_id=provider)
        if not analysis:
            raise ValueError("LLM analysis returned empty result.")

        config = PROVIDERS[provider]
        provenance = json.dumps({
            "provider": provider,
            "model": config["model"],
            "bias_disclaimer": "AI-generated analysis may contain inaccuracies or reflect biases from the underlying model.",
        })

        db_analysis = Analysis(
            paper_id=paper.id,
            provider=provider,
            summary=analysis.get("summary", ""),
            key_insights=json.dumps(analysis.get("key_insights", [])),
            methodology=analysis.get("methodology", ""),
            research_gaps=json.dumps(analysis.get("research_gaps", [])),
            relevance_tags=json.dumps(analysis.get("relevance_tags", [])),
            score=analysis.get("strength_score", 0),
            provenance=provenance,
        )
        db.add(db_analysis)
        paper.status = "analyzed"
        db.commit()

        log_audit(event="mcp_analyze", message=f"paper={paper.arxiv_id} provider={provider}", db=db)
        return {"paper_id": paper.arxiv_id, "title": title, "analysis": analysis}
    finally:
        db.close()


def tool_learn(args: dict) -> dict:
    paper_id = args.get("paper_id", "")
    insight = args.get("insight", "")
    agent = args.get("agent", "mcp-agent")

    if not paper_id:
        raise ValueError("paper_id is required")
    if not insight:
        raise ValueError("insight is required")

    db = SessionLocal()
    try:
        paper = _resolve_paper(db, paper_id)
        session = LearningSession(paper_id=paper.id, insight=insight, agent=agent)
        db.add(session)
        db.commit()
        log_audit(event="mcp_learn", message=f"paper={paper.arxiv_id} agent={agent}", db=db)
        return {"status": "ok", "paper_id": paper.arxiv_id, "session_id": session.id}
    finally:
        db.close()


def tool_cite(args: dict) -> dict:
    paper_id = args.get("paper_id", "")
    project = args.get("project", "")
    context = args.get("context", "")

    if not paper_id:
        raise ValueError("paper_id is required")
    if not project:
        raise ValueError("project is required")

    db = SessionLocal()
    try:
        paper = _resolve_paper(db, paper_id)
        citation = Citation(paper_id=paper.id, project=project, context=context)
        db.add(citation)
        paper.status = "cited"
        db.commit()
        log_audit(event="mcp_cite", message=f"paper={paper.arxiv_id} project={project}", db=db)
        return {"status": "ok", "paper_id": paper.arxiv_id, "citation_id": citation.id}
    finally:
        db.close()


def tool_recall(args: dict) -> dict:
    query = args.get("query", "")
    if not query:
        raise ValueError("query is required")

    db = SessionLocal()
    try:
        like_query = f"%{query}%"
        papers = db.query(Paper).filter(
            (Paper.title.ilike(like_query)) | (Paper.abstract.ilike(like_query))
        ).limit(20).all()

        sessions = db.query(LearningSession).filter(
            LearningSession.insight.ilike(like_query)
        ).limit(20).all()

        log_audit(event="mcp_recall", message=f"query='{query}' hits={len(papers)+len(sessions)}", db=db)
        return {
            "papers": [p.to_dict() for p in papers],
            "sessions": [s.to_dict() for s in sessions],
            "total": len(papers) + len(sessions),
        }
    finally:
        db.close()


TOOL_HANDLERS = {
    "macp.discover": tool_discover,
    "macp.analyze": tool_analyze,
    "macp.learn": tool_learn,
    "macp.cite": tool_cite,
    "macp.recall": tool_recall,
}


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

_authenticated = False


def _check_auth(params: dict) -> bool:
    """Check if the request includes a valid API key in _meta.auth."""
    global _authenticated
    if not MACP_API_KEY:
        # No key configured — open mode
        return True
    if _authenticated:
        return True
    meta = params.get("_meta", {})
    token = meta.get("auth", "")
    if token.startswith("Bearer "):
        token = token[7:]
    if verify_api_key(token):
        _authenticated = True
        return True
    return False


# ---------------------------------------------------------------------------
# JSON-RPC / MCP Message Handling
# ---------------------------------------------------------------------------

def _make_response(id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": id, "result": result}


def _make_error(id: Any, code: int, message: str, data: Any = None) -> dict:
    error = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": id, "error": error}


def handle_message(msg: dict) -> dict | None:
    """Process a single JSON-RPC message and return a response."""
    msg_id = msg.get("id")
    method = msg.get("method", "")
    params = msg.get("params", {})

    # --- MCP Lifecycle ---

    if method == "initialize":
        return _make_response(msg_id, {
            "protocolVersion": MCP_VERSION,
            "capabilities": {
                "tools": {},
            },
            "serverInfo": SERVER_INFO,
        })

    if method == "notifications/initialized":
        # Client acknowledgment — no response needed
        return None

    if method == "ping":
        return _make_response(msg_id, {})

    # --- Tool Operations ---

    if method == "tools/list":
        return _make_response(msg_id, {"tools": TOOLS})

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            return _make_error(msg_id, -32601, f"Unknown tool: {tool_name}")

        # Auth check (pass arguments for _meta extraction)
        if not _check_auth(arguments):
            return _make_error(msg_id, -32000, "Authentication required. Provide API key in _meta.auth.")

        try:
            result = handler(arguments)
            return _make_response(msg_id, {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
            })
        except ValueError as e:
            return _make_response(msg_id, {
                "content": [{"type": "text", "text": str(e)}],
                "isError": True,
            })
        except Exception as e:
            log_audit(event="mcp_error", message=f"tool={tool_name} error={e}", level="ERROR")
            return _make_response(msg_id, {
                "content": [{"type": "text", "text": f"Internal error: {e}"}],
                "isError": True,
            })

    # Unknown method
    return _make_error(msg_id, -32601, f"Method not found: {method}")


# ---------------------------------------------------------------------------
# Stdio Transport
# ---------------------------------------------------------------------------

def run_stdio():
    """Run the MCP server over stdio (newline-delimited JSON)."""
    init_db()
    log_audit(event="mcp_server_start", message="Backend MCP server started (stdio)")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            err = _make_error(None, -32700, "Parse error")
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()
            continue

        response = handle_message(msg)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio()
