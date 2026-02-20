"""
MACP Research Assistant — WebMCP Endpoints (Phase 3C)
======================================================
8 MCP tool HTTP endpoints at /api/mcp/* for browser agent tool registration.
Response format follows MCP tool result convention.
"""

import json
import os
import sys
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from config import RATE_LIMIT_AUTH_MCP, TOOLS_DIR
from database import (
    Analysis,
    Citation,
    LearningSession,
    Note,
    Paper,
    SessionLocal,
    User,
    log_audit,
    upsert_paper,
)
from middleware import get_current_user, require_user
from github_storage import get_storage_service

# Add tools dir for imports
sys.path.insert(0, os.path.abspath(TOOLS_DIR))
from paper_fetcher import fetch_by_id, fetch_by_query, fetch_from_hysts
from llm_providers import analyze_paper as _analyze_paper, PROVIDERS

mcp_router = APIRouter(prefix="/api/mcp", tags=["WebMCP"])


# ---------------------------------------------------------------------------
# MCP Response helper
# ---------------------------------------------------------------------------

def mcp_response(data, is_error: bool = False):
    """Format response in MCP tool result convention."""
    text = json.dumps(data, default=str) if not isinstance(data, str) else data
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class McpSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(default=10, ge=1, le=50)
    source: str = Field(default="hysts", pattern="^(hf|hysts|arxiv)$")


class McpAnalyzeRequest(BaseModel):
    paper_id: str = Field(..., min_length=1)
    provider: str = Field(default="gemini")
    api_key: Optional[str] = Field(default=None)


class McpSaveRequest(BaseModel):
    paper_id: str = Field(..., min_length=1)


class McpNoteRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    paper_id: Optional[str] = Field(default=None)
    tags: list[str] = Field(default=[])


class McpSyncRequest(BaseModel):
    pass


# ---------------------------------------------------------------------------
# Discovery endpoint
# ---------------------------------------------------------------------------

@mcp_router.get("/")
async def mcp_discovery():
    """Discovery endpoint listing all available MCP tools with schemas."""
    tools = [
        {
            "name": "macp.search",
            "description": "Search for academic papers on arXiv via HuggingFace Daily Papers",
            "endpoint": "/api/mcp/search",
            "method": "POST",
            "inputSchema": McpSearchRequest.model_json_schema(),
        },
        {
            "name": "macp.analyze",
            "description": "AI-powered analysis of a paper's abstract using LLM providers",
            "endpoint": "/api/mcp/analyze",
            "method": "POST",
            "inputSchema": McpAnalyzeRequest.model_json_schema(),
        },
        {
            "name": "macp.save",
            "description": "Save a paper to user's library and sync to GitHub",
            "endpoint": "/api/mcp/save",
            "method": "POST",
            "inputSchema": McpSaveRequest.model_json_schema(),
        },
        {
            "name": "macp.analysis",
            "description": "Get analysis results for a paper",
            "endpoint": "/api/mcp/analysis/{paper_id}",
            "method": "GET",
        },
        {
            "name": "macp.library",
            "description": "List all saved papers in user's library",
            "endpoint": "/api/mcp/library",
            "method": "GET",
        },
        {
            "name": "macp.note",
            "description": "Add a research note, optionally linked to a paper",
            "endpoint": "/api/mcp/note",
            "method": "POST",
            "inputSchema": McpNoteRequest.model_json_schema(),
        },
        {
            "name": "macp.graph",
            "description": "Get knowledge graph data (papers, analyses, connections)",
            "endpoint": "/api/mcp/graph",
            "method": "GET",
        },
        {
            "name": "macp.sync",
            "description": "Force sync between database and GitHub repository",
            "endpoint": "/api/mcp/sync",
            "method": "POST",
        },
    ]
    return {"tools": tools, "count": len(tools), "version": "0.3.0"}


# ---------------------------------------------------------------------------
# 1. Search
# ---------------------------------------------------------------------------

@mcp_router.post("/search")
async def mcp_search(
    request: Request,
    req: McpSearchRequest,
    user: Optional[User] = Depends(get_current_user),
):
    """Search for papers."""
    try:
        if req.source == "hysts":
            papers = fetch_from_hysts(req.query, limit=req.limit)
        elif req.source == "hf":
            papers = fetch_by_query(req.query, limit=req.limit)
        elif req.source == "arxiv":
            paper = fetch_by_id(req.query)
            papers = [paper] if paper else []
        else:
            papers = fetch_from_hysts(req.query, limit=req.limit)

        db = SessionLocal()
        try:
            for p in papers:
                upsert_paper(db, p, user_id=user.id if user else None)
        finally:
            db.close()

        return mcp_response({"results": papers, "count": len(papers)})
    except Exception as e:
        return mcp_response(f"Search failed: {e}", is_error=True)


# ---------------------------------------------------------------------------
# 2. Analyze
# ---------------------------------------------------------------------------

@mcp_router.post("/analyze")
async def mcp_analyze(
    request: Request,
    req: McpAnalyzeRequest,
    user: Optional[User] = Depends(get_current_user),
):
    """AI analysis of a paper."""
    db = SessionLocal()
    try:
        if not req.paper_id.startswith("arxiv:"):
            req.paper_id = f"arxiv:{req.paper_id}"
        paper = db.query(Paper).filter(Paper.arxiv_id == req.paper_id).first()
        if not paper:
            return mcp_response(f"Paper {req.paper_id} not found", is_error=True)

        if req.provider not in PROVIDERS:
            return mcp_response(f"Unknown provider: {req.provider}", is_error=True)

        config = PROVIDERS[req.provider]
        authors = json.loads(paper.authors) if paper.authors else []
        abstract = paper.abstract or ""

        if not abstract:
            return mcp_response("Paper has no abstract", is_error=True)

        analysis = _analyze_paper(
            title=paper.title, authors=authors, abstract=abstract,
            provider_id=req.provider, api_key_override=req.api_key,
        )

        if not analysis:
            return mcp_response("Analysis returned empty result", is_error=True)

        provenance = json.dumps({"provider": req.provider, "model": config["model"]})
        db_analysis = Analysis(
            paper_id=paper.id, user_id=user.id if user else None,
            provider=req.provider,
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

        return mcp_response({"paper_id": paper.arxiv_id, "analysis": analysis})

    except Exception as e:
        return mcp_response(f"Analysis failed: {e}", is_error=True)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 3. Save
# ---------------------------------------------------------------------------

@mcp_router.post("/save")
async def mcp_save(
    req: McpSaveRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_user),
):
    """Save a paper to library + GitHub."""
    db = SessionLocal()
    try:
        paper_id = req.paper_id
        if not paper_id.startswith("arxiv:"):
            paper_id = f"arxiv:{paper_id}"
        paper = db.query(Paper).filter(Paper.arxiv_id == paper_id).first()
        if not paper:
            return mcp_response(f"Paper {paper_id} not found", is_error=True)

        paper.status = "saved"
        paper.user_id = user.id
        db.commit()

        # Fire-and-forget GitHub write
        storage = get_storage_service(user)
        if storage:
            background_tasks.add_task(storage.save_paper, paper)

        return mcp_response({"status": "saved", "paper_id": paper.arxiv_id})
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 4. Get Analysis
# ---------------------------------------------------------------------------

@mcp_router.get("/analysis/{paper_id}")
async def mcp_get_analysis(paper_id: str, user: Optional[User] = Depends(get_current_user)):
    """Get analysis results for a paper."""
    db = SessionLocal()
    try:
        if not paper_id.startswith("arxiv:"):
            paper_id = f"arxiv:{paper_id}"
        paper = db.query(Paper).filter(Paper.arxiv_id == paper_id).first()
        if not paper:
            return mcp_response(f"Paper {paper_id} not found", is_error=True)

        analyses = db.query(Analysis).filter(Analysis.paper_id == paper.id).all()
        return mcp_response({
            "paper_id": paper.arxiv_id,
            "title": paper.title,
            "analyses": [a.to_dict() for a in analyses],
        })
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 5. Library
# ---------------------------------------------------------------------------

@mcp_router.get("/library")
async def mcp_library(user: User = Depends(require_user)):
    """List all saved papers in user's library."""
    db = SessionLocal()
    try:
        papers = db.query(Paper).filter(Paper.user_id == user.id).order_by(Paper.added_at.desc()).all()
        return mcp_response({
            "papers": [p.to_dict() for p in papers],
            "count": len(papers),
        })
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 6. Note
# ---------------------------------------------------------------------------

@mcp_router.post("/note")
async def mcp_add_note(
    req: McpNoteRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_user),
):
    """Add a research note."""
    db = SessionLocal()
    try:
        paper_id_fk = None
        if req.paper_id:
            pid = req.paper_id if req.paper_id.startswith("arxiv:") else f"arxiv:{req.paper_id}"
            paper = db.query(Paper).filter(Paper.arxiv_id == pid).first()
            if paper:
                paper_id_fk = paper.id

        note = Note(
            user_id=user.id,
            paper_id=paper_id_fk,
            content=req.content,
            tags=json.dumps(req.tags),
        )
        db.add(note)
        db.commit()
        db.refresh(note)

        # Fire-and-forget GitHub write
        storage = get_storage_service(user)
        if storage:
            background_tasks.add_task(storage.save_note, note)

        return mcp_response({"status": "ok", "note_id": note.id})
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 7. Knowledge Graph
# ---------------------------------------------------------------------------

@mcp_router.get("/graph")
async def mcp_graph(user: Optional[User] = Depends(get_current_user)):
    """Get knowledge graph data for D3.js visualization."""
    db = SessionLocal()
    try:
        # Build nodes (papers) and edges (citations, analyses)
        papers = db.query(Paper).limit(200).all()
        analyses = db.query(Analysis).limit(500).all()

        nodes = []
        edges = []
        paper_idx = {}

        for p in papers:
            paper_idx[p.id] = len(nodes)
            nodes.append({
                "id": p.arxiv_id,
                "title": p.title,
                "type": "paper",
                "status": p.status,
            })

        for a in analyses:
            if a.paper_id in paper_idx:
                # Add analysis as node connected to paper
                analysis_id = f"analysis_{a.id}"
                nodes.append({
                    "id": analysis_id,
                    "title": f"Analysis ({a.provider})",
                    "type": "analysis",
                    "provider": a.provider,
                })
                edges.append({
                    "source": paper_idx[a.paper_id],
                    "target": len(nodes) - 1,
                    "type": "analyzed_by",
                })

        # Connect papers that share tags
        tag_papers = {}
        for a in analyses:
            tags = json.loads(a.relevance_tags) if a.relevance_tags else []
            for tag in tags:
                tag_papers.setdefault(tag, []).append(a.paper_id)

        for tag, pids in tag_papers.items():
            unique_pids = list(set(pids))
            for i in range(len(unique_pids)):
                for j in range(i + 1, len(unique_pids)):
                    if unique_pids[i] in paper_idx and unique_pids[j] in paper_idx:
                        edges.append({
                            "source": paper_idx[unique_pids[i]],
                            "target": paper_idx[unique_pids[j]],
                            "type": "shared_tag",
                            "tag": tag,
                        })

        return mcp_response({
            "nodes": nodes,
            "edges": edges,
            "stats": {"papers": len(papers), "analyses": len(analyses)},
        })
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 8. Sync
# ---------------------------------------------------------------------------

@mcp_router.post("/sync")
async def mcp_sync(user: User = Depends(require_user)):
    """Force GitHub sync (hydration)."""
    storage = get_storage_service(user)
    if not storage:
        return mcp_response("No repository connected", is_error=True)

    stats = await storage.hydrate_from_github()
    return mcp_response({"status": "synced", "stats": stats})
