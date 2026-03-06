"""
MACP Research Assistant — WebMCP Endpoints (Phase 3C)
======================================================
8 MCP tool HTTP endpoints at /api/mcp/* for browser agent tool registration.
Response format follows MCP tool result convention.
"""

import json
import logging
import os
import sys
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from pydantic import BaseModel, Field

from config import TOOLS_DIR, MACP_DIR
from database import (
    Analysis,
    GraphEdge,
    GraphNode,
    Note,
    Paper,
    SessionLocal,
    User,
    upsert_paper,
)
from middleware import get_current_user, require_user
from github_storage import get_storage_service

# Add tools dir for imports
sys.path.insert(0, os.path.abspath(TOOLS_DIR))
from paper_fetcher import fetch_by_id, fetch_by_query, fetch_from_hysts, download_pdf, extract_text, check_extraction_quality, fetch_arxiv_html
from llm_providers import (
    analyze_paper as _analyze_paper,
    analyze_paper_deep as _analyze_deep,
    compute_agreement_score,
    generate_consensus_synthesis,
    deep_research as _deep_research,
    PROVIDERS,
)
from schema_validator import get_consensus_weights, get_consensus_min_agents

logger = logging.getLogger(__name__)
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


class McpAnalyzeDeepRequest(BaseModel):
    paper_id: str = Field(..., min_length=1)
    provider: str = Field(default="gemini")
    api_key: Optional[str] = Field(default=None)


class McpConsensusRequest(BaseModel):
    paper_id: str = Field(..., min_length=1)
    provider: str = Field(default="gemini", description="LLM provider for synthesis generation")
    api_key: Optional[str] = Field(default=None)
    analysis_type: str = Field(default="abstract", pattern="^(abstract|deep)$", description="Compare only analyses of this type")


class McpDeepResearchRequest(BaseModel):
    paper_id: str = Field(..., min_length=1)
    api_key: Optional[str] = Field(default=None, description="Perplexity SONAR_API_KEY")


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
            "name": "macp.analyze-deep",
            "description": "Deep full-text analysis of a paper using PDF extraction and multi-pass LLM",
            "endpoint": "/api/mcp/analyze-deep",
            "method": "POST",
            "inputSchema": McpAnalyzeDeepRequest.model_json_schema(),
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
            "name": "macp.consensus",
            "description": "Generate multi-agent consensus analysis for a paper (requires 2+ existing analyses)",
            "endpoint": "/api/mcp/consensus",
            "method": "POST",
            "inputSchema": McpConsensusRequest.model_json_schema(),
        },
        {
            "name": "macp.deep-research",
            "description": "Perplexity-powered deep research: citations, related work, code repos, impact assessment",
            "endpoint": "/api/mcp/deep-research",
            "method": "POST",
            "inputSchema": McpDeepResearchRequest.model_json_schema(),
        },
        {
            "name": "macp.agents",
            "description": "List all registered agents with capabilities",
            "endpoint": "/api/mcp/agents",
            "method": "GET",
        },
        {
            "name": "macp.sync",
            "description": "Force sync between database and GitHub repository",
            "endpoint": "/api/mcp/sync",
            "method": "POST",
        },
    ]
    return {"tools": tools, "count": len(tools), "version": "0.4.0"}


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
                upsert_paper(db, p, user_id=None)
        finally:
            db.close()

        return mcp_response({"results": papers, "count": len(papers)})
    except Exception:
        logger.exception("Search failed")
        return mcp_response("Search failed. Please try again.", is_error=True)


# ---------------------------------------------------------------------------
# 2. Analyze
# ---------------------------------------------------------------------------

@mcp_router.post("/analyze")
async def mcp_analyze(
    request: Request,
    req: McpAnalyzeRequest,
    background_tasks: BackgroundTasks,
    user: Optional[User] = Depends(get_current_user),
):
    """AI analysis of a paper. Syncs to GitHub + updates manifest."""
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
        db.refresh(paper)        # reload attrs before session closes (prevents DetachedInstanceError)
        db.refresh(db_analysis)  # same — background task accesses these after db.close()

        # GitHub dual-write: save analysis with per-agent path (MACP v2.0)
        if user:
            storage = get_storage_service(user)
            if storage:
                async def _sync_analysis():
                    await storage.save_analysis_per_agent(paper, db_analysis, analysis)
                    await storage.update_manifest_entry("analyses", paper.arxiv_id, {
                        "providers": [{
                            "provider": req.provider,
                            "type": "abstract",
                            "analyzed_at": __import__("datetime").datetime.now(
                                __import__("datetime").timezone.utc).isoformat(),
                        }],
                    })
                background_tasks.add_task(_sync_analysis)

        return mcp_response({"paper_id": paper.arxiv_id, "analysis": analysis})

    except Exception:
        logger.exception("Analysis failed")
        return mcp_response("Analysis failed. Please try again.", is_error=True)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Graph population helper (P4.1 — Knowledge Graph)
# ---------------------------------------------------------------------------

def _populate_graph(db, paper: Paper, analysis: dict, user_id: Optional[int]) -> None:
    """
    Persist concept/method/author nodes and edges extracted from a deep analysis.

    Called after each successful deep analysis. Uses upsert pattern:
    - If a concept/method node already exists, increment paper_count.
    - Create paper→concept (uses_concept), paper→method (uses_method),
      paper→author (authored_by) edges.
    - Cross-paper relates_to edges are built lazily in the /graph endpoint.
    """
    from re import sub as re_sub

    def _node_id(node_type: str, label: str) -> str:
        """Normalised stable ID: concept_constitutional_ai"""
        slug = re_sub(r"[^a-z0-9]+", "_", label.lower().strip()).strip("_")
        return f"{node_type}_{slug[:80]}"

    def _upsert_node(node_id: str, node_type: str, label: str) -> GraphNode:
        node = db.query(GraphNode).filter(
            GraphNode.node_id == node_id,
            GraphNode.user_id == user_id,
        ).first()
        if node:
            node.paper_count += 1
            node.updated_at = __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc)
        else:
            node = GraphNode(
                user_id=user_id,
                node_id=node_id,
                node_type=node_type,
                label=label,
                paper_count=1,
            )
            db.add(node)
        db.flush()
        return node

    def _add_edge(source: GraphNode, target: GraphNode, edge_type: str) -> None:
        exists = db.query(GraphEdge).filter(
            GraphEdge.source_node_id == source.id,
            GraphEdge.target_node_id == target.id,
            GraphEdge.edge_type == edge_type,
            GraphEdge.user_id == user_id,
        ).first()
        if not exists:
            db.add(GraphEdge(
                user_id=user_id,
                source_node_id=source.id,
                target_node_id=target.id,
                edge_type=edge_type,
            ))

    try:
        # Upsert paper node
        paper_node = _upsert_node(paper.arxiv_id, "paper", paper.title)

        # Author nodes (from paper metadata — free, no extraction needed)
        authors = json.loads(paper.authors) if paper.authors else []
        for author in authors[:5]:  # cap at 5 authors per paper
            if not author or not author.strip():
                continue
            author_id = _node_id("author", author)
            author_node = _upsert_node(author_id, "author", author)
            _add_edge(paper_node, author_node, "authored_by")

        # Concept nodes from PASS3
        concepts = []
        for section in analysis.get("section_analyses", []):
            if section.get("pass") == "results":
                concepts = section.get("data", {}).get("concepts", [])
                break
        for concept in concepts[:5]:  # max 5 per paper
            if not concept or not str(concept).strip():
                continue
            c_id = _node_id("concept", str(concept))
            c_node = _upsert_node(c_id, "concept", str(concept))
            _add_edge(paper_node, c_node, "uses_concept")

        # Method nodes from PASS3
        methods = []
        for section in analysis.get("section_analyses", []):
            if section.get("pass") == "results":
                methods = section.get("data", {}).get("methods", [])
                break
        for method in methods[:5]:  # max 5 per paper
            if not method or not str(method).strip():
                continue
            m_id = _node_id("method", str(method))
            m_node = _upsert_node(m_id, "method", str(method))
            _add_edge(paper_node, m_node, "uses_method")

        db.commit()
        logger.info(
            "Graph populated for %s: %d concepts, %d methods, %d authors",
            paper.arxiv_id, len(concepts), len(methods), len(authors[:5])
        )
    except Exception:
        logger.exception("Graph population failed for %s — skipping", paper.arxiv_id)
        db.rollback()


# ---------------------------------------------------------------------------
# 2b. Deep Analysis (Phase 3E — full-text multi-pass)
# ---------------------------------------------------------------------------

@mcp_router.post("/analyze-deep")
async def mcp_analyze_deep(
    request: Request,
    req: McpAnalyzeDeepRequest,
    background_tasks: BackgroundTasks,
    user: Optional[User] = Depends(get_current_user),
):
    """Deep full-text analysis: download PDF, extract text, multi-pass LLM analysis."""
    db = SessionLocal()
    try:
        if not req.paper_id.startswith("arxiv:"):
            req.paper_id = f"arxiv:{req.paper_id}"
        paper = db.query(Paper).filter(Paper.arxiv_id == req.paper_id).first()
        if not paper:
            return mcp_response(f"Paper {req.paper_id} not found", is_error=True)

        if req.provider not in PROVIDERS:
            return mcp_response(f"Unknown provider: {req.provider}", is_error=True)

        # Extract arXiv ID for PDF download
        arxiv_id = paper.arxiv_id.replace("arxiv:", "")

        # Step 1: Download PDF
        try:
            pdf_path = download_pdf(arxiv_id)
        except (RuntimeError, ImportError) as e:
            logger.warning("PDF download failed for %s: %s", arxiv_id, e)
            return mcp_response("PDF download failed. The paper may not have a PDF available.", is_error=True)

        # Step 2: Extract text
        try:
            extracted = extract_text(pdf_path)
        except (RuntimeError, ImportError) as e:
            logger.warning("PDF extraction failed for %s: %s", arxiv_id, e)
            return mcp_response("PDF text extraction failed.", is_error=True)

        # Quality gate: check if extraction got meaningful text
        quality = check_extraction_quality(extracted)
        if not quality["is_sufficient"]:
            logger.warning(
                "PDF extraction quality poor for %s: %s — trying HTML fallback",
                arxiv_id, quality["reason"]
            )
            html_extracted = fetch_arxiv_html(arxiv_id)
            if html_extracted:
                extracted = html_extracted
                logger.info(
                    "HTML fallback succeeded for %s: %d chars",
                    arxiv_id, len(html_extracted["full_text"])
                )
            else:
                logger.warning(
                    "HTML fallback also failed for %s — proceeding with limited text", arxiv_id
                )

        sections = extracted.get("sections", [])
        if not sections:
            return mcp_response("No text could be extracted from PDF", is_error=True)

        extraction_source = extracted.get("source", "pdf")

        # Step 3: Multi-pass deep analysis
        config = PROVIDERS[req.provider]
        authors = json.loads(paper.authors) if paper.authors else []

        analysis = _analyze_deep(
            title=paper.title,
            authors=authors,
            sections=sections,
            provider_id=req.provider,
            api_key_override=req.api_key,
            extraction_source=extraction_source,
        )

        if not analysis:
            return mcp_response("Deep analysis returned empty result", is_error=True)

        # Step 4: Save to DB
        provenance = json.dumps({
            "provider": req.provider, "model": config["model"],
            "type": "deep", "page_count": extracted.get("page_count", 0),
        })
        db_analysis = Analysis(
            paper_id=paper.id, user_id=user.id if user else None,
            provider=req.provider,
            summary=analysis.get("summary", ""),
            key_insights=json.dumps(analysis.get("key_contributions", [])),
            methodology=analysis.get("methodology_detail", ""),
            research_gaps=json.dumps(analysis.get("research_gaps", [])),
            relevance_tags=json.dumps(analysis.get("relevance_tags", [])),
            score=analysis.get("strength_score", 0),
            provenance=provenance,
        )
        db.add(db_analysis)
        paper.status = "analyzed"
        db.commit()
        db.refresh(paper)        # reload attrs before session closes (prevents DetachedInstanceError)
        db.refresh(db_analysis)  # same — background task accesses these after db.close()

        # Step 4b: Populate knowledge graph nodes/edges (P4.1)
        _populate_graph(db, paper, analysis, user.id if user else None)

        # Step 5: GitHub dual-write with per-agent path (MACP v2.0) + graph sync (P4.4)
        if user:
            storage = get_storage_service(user)
            if storage:
                async def _sync_deep_analysis():
                    await storage.save_analysis_per_agent(paper, db_analysis, analysis)
                    await storage.update_manifest_entry("analyses", paper.arxiv_id, {
                        "providers": [{
                            "provider": req.provider,
                            "type": "deep",
                            "analyzed_at": __import__("datetime").datetime.now(
                                __import__("datetime").timezone.utc).isoformat(),
                        }],
                    })
                background_tasks.add_task(_sync_deep_analysis)

                async def _sync_graph_to_github():
                    """P4.4 — sync graph nodes/edges JSON to user's connected repo."""
                    try:
                        _db = SessionLocal()
                        _user_id = user.id
                        gn_rows = _db.query(GraphNode).filter(
                            GraphNode.user_id == _user_id
                        ).limit(500).all()
                        ge_rows = _db.query(GraphEdge).filter(
                            GraphEdge.user_id == _user_id
                        ).limit(2000).all()

                        node_idx = {gn.id: i for i, gn in enumerate(gn_rows)}
                        graph_json = {
                            "generated": __import__("datetime").datetime.now(
                                __import__("datetime").timezone.utc).isoformat(),
                            "version": "1.0",
                            "nodes": [gn.to_dict() for gn in gn_rows],
                            "edges": [
                                {
                                    "source": node_idx[ge.source_node_id],
                                    "target": node_idx[ge.target_node_id],
                                    "type": ge.edge_type,
                                }
                                for ge in ge_rows
                                if ge.source_node_id in node_idx and ge.target_node_id in node_idx
                            ],
                        }
                        _db.close()
                        await storage.save_graph(graph_json)
                        logger.info("Graph synced to GitHub for user %s: %d nodes", _user_id, len(gn_rows))
                    except Exception:
                        logger.exception("GitHub graph sync failed — skipping")
                background_tasks.add_task(_sync_graph_to_github)

        return mcp_response({
            "paper_id": paper.arxiv_id,
            "analysis_type": "deep",
            "page_count": extracted.get("page_count", 0),
            "sections_extracted": len(sections),
            "extraction_source": extraction_source,
            "analysis": analysis,
        })

    except Exception:
        logger.exception("Deep analysis failed")
        return mcp_response("Deep analysis failed. Please try again.", is_error=True)
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

        # GitHub dual-write with retry (fire-and-forget but logged)
        github_synced = False
        storage = get_storage_service(user)
        if storage:
            async def _sync_to_github():
                ok = await storage.save_paper(paper)
                if ok:
                    await storage.update_manifest_entry("papers", paper.arxiv_id, {
                        "title": paper.title[:80],
                        "saved_at": __import__("datetime").datetime.now(
                            __import__("datetime").timezone.utc).isoformat(),
                        "status": "saved",
                    })
            background_tasks.add_task(_sync_to_github)
            github_synced = True  # queued for sync

        return mcp_response({"status": "saved", "paper_id": paper.arxiv_id, "github_queued": github_synced})
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
    """List all saved papers in user's library. Auto-hydrates from GitHub on cold start."""
    db = SessionLocal()
    try:
        papers = db.query(Paper).filter(
            Paper.user_id == user.id,
            Paper.status == "saved",
        ).all()

        # Auto-hydrate from GitHub if DB is empty but user has a connected repo
        if not papers and user.connected_repo:
            storage = get_storage_service(user)
            if storage:
                try:
                    stats = await storage.hydrate_from_github()
                    if stats.get("papers", 0) > 0:
                        papers = db.query(Paper).filter(Paper.user_id == user.id).all()
                except Exception:
                    pass  # Hydration failure is non-fatal

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

        # Fire-and-forget GitHub write + manifest update
        storage = get_storage_service(user)
        if storage:
            async def _sync_note():
                await storage.save_note(note)
                await storage.update_manifest_entry("notes", str(note.id), {
                    "created_at": note.created_at.isoformat() if note.created_at else "",
                    "paper_id": req.paper_id or "",
                    "tags": req.tags,
                })
            background_tasks.add_task(_sync_note)

        return mcp_response({"status": "ok", "note_id": note.id})
    finally:
        db.close()


@mcp_router.get("/notes")
async def mcp_list_notes(user: User = Depends(require_user)):
    """List all research notes for the current user."""
    db = SessionLocal()
    try:
        notes = db.query(Note).filter(Note.user_id == user.id).order_by(Note.created_at.desc()).all()
        return mcp_response({
            "notes": [n.to_dict() for n in notes],
            "count": len(notes),
        })
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
        user_id = user.id if user else None

        # --- Rich graph from graph_nodes/graph_edges tables (P4.1) ---
        db_nodes = db.query(GraphNode).filter(GraphNode.user_id == user_id).limit(500).all()

        if db_nodes:
            # Build index: db node id → position in nodes list
            node_idx = {}
            nodes = []
            for gn in db_nodes:
                node_idx[gn.id] = len(nodes)
                nodes.append(gn.to_dict())

            db_edges = db.query(GraphEdge).filter(GraphEdge.user_id == user_id).limit(2000).all()
            edges = []
            for ge in db_edges:
                if ge.source_node_id in node_idx and ge.target_node_id in node_idx:
                    edges.append({
                        "source": node_idx[ge.source_node_id],
                        "target": node_idx[ge.target_node_id],
                        "type": ge.edge_type,
                    })

            # Cross-paper relates_to: papers sharing a concept node
            concept_papers: dict[int, list[int]] = {}
            for ge in db_edges:
                if ge.edge_type == "uses_concept" and ge.source_node_id in node_idx:
                    concept_papers.setdefault(ge.target_node_id, []).append(ge.source_node_id)
            for concept_id, paper_db_ids in concept_papers.items():
                unique_ids = list(set(paper_db_ids))
                for i in range(len(unique_ids)):
                    for j in range(i + 1, len(unique_ids)):
                        if unique_ids[i] in node_idx and unique_ids[j] in node_idx:
                            edges.append({
                                "source": node_idx[unique_ids[i]],
                                "target": node_idx[unique_ids[j]],
                                "type": "relates_to",
                            })

            concept_count = sum(1 for n in nodes if n["type"] == "concept")
            method_count = sum(1 for n in nodes if n["type"] == "method")
            paper_count = sum(1 for n in nodes if n["type"] == "paper")
            return mcp_response({
                "nodes": nodes,
                "edges": edges,
                "stats": {
                    "papers": paper_count,
                    "concepts": concept_count,
                    "methods": method_count,
                    "connections": len(edges),
                },
            })

        # --- Fallback: legacy on-the-fly graph (no graph_nodes data yet) ---
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

        tag_papers: dict[str, list[int]] = {}
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
            "stats": {
                "papers": len(papers),
                "concepts": 0,
                "methods": 0,
                "connections": len(edges),
            },
        })
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 8. Deep Research (Phase 3E — Perplexity Web-Grounded)
# ---------------------------------------------------------------------------

@mcp_router.post("/deep-research")
async def mcp_deep_research(
    request: Request,
    req: McpDeepResearchRequest,
    user: Optional[User] = Depends(get_current_user),
):
    """Perplexity-powered deep research: citations, related work, code, impact."""
    db = SessionLocal()
    try:
        if not req.paper_id.startswith("arxiv:"):
            req.paper_id = f"arxiv:{req.paper_id}"
        paper = db.query(Paper).filter(Paper.arxiv_id == req.paper_id).first()
        if not paper:
            return mcp_response(f"Paper {req.paper_id} not found", is_error=True)

        authors = json.loads(paper.authors) if paper.authors else []
        result = _deep_research(
            title=paper.title,
            authors=authors,
            abstract=paper.abstract or "",
            api_key_override=req.api_key,
        )

        if not result:
            return mcp_response("Deep research failed — check SONAR_API_KEY", is_error=True)

        return mcp_response({
            "paper_id": paper.arxiv_id,
            "title": paper.title,
            "research": result,
        })

    except Exception:
        logger.exception("Deep research failed")
        return mcp_response("Deep research failed. Please try again.", is_error=True)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 9. Consensus Analysis (Phase 3E — Multi-Agent Convergence)
# ---------------------------------------------------------------------------

@mcp_router.post("/consensus")
async def mcp_consensus(
    request: Request,
    req: McpConsensusRequest,
    background_tasks: BackgroundTasks,
    user: Optional[User] = Depends(get_current_user),
):
    """Generate multi-agent consensus analysis for a paper.

    Requires at least 2 existing analyses for the paper.
    Agreement score uses 40/30/30 weighting from MACP v2.0 schema.
    """
    db = SessionLocal()
    try:
        if not req.paper_id.startswith("arxiv:"):
            req.paper_id = f"arxiv:{req.paper_id}"
        paper = db.query(Paper).filter(Paper.arxiv_id == req.paper_id).first()
        if not paper:
            return mcp_response(f"Paper {req.paper_id} not found", is_error=True)

        # Load all existing analyses for this paper
        db_analyses = db.query(Analysis).filter(Analysis.paper_id == paper.id).all()

        # CSO R rule: "Same paper, same type" — filter by analysis type
        filtered_analyses = []
        for a in db_analyses:
            provenance = json.loads(a.provenance) if a.provenance else {}
            a_type = provenance.get("type", "abstract")
            if a_type == req.analysis_type:
                filtered_analyses.append(a)

        # If no type-matched analyses found, fall back to all analyses
        if len(filtered_analyses) < 2 and len(db_analyses) >= 2:
            filtered_analyses = db_analyses

        min_agents = get_consensus_min_agents()
        if len(filtered_analyses) < min_agents:
            return mcp_response(
                f"Need at least {min_agents} {req.analysis_type} analyses for consensus, "
                f"found {len(filtered_analyses)} (total: {len(db_analyses)})",
                is_error=True,
            )

        # Convert DB analyses to dicts for scoring
        analysis_dicts = []
        agents_compared = []
        for a in filtered_analyses:
            agent_id = a.provider or "unknown"
            if agent_id not in agents_compared:
                agents_compared.append(agent_id)
            analysis_dicts.append({
                "agent_id": agent_id,
                "summary": a.summary or "",
                "key_findings": json.loads(a.key_insights) if a.key_insights else [],
                "methodology": a.methodology or "",
                "relevance_score": (a.score or 5) / 10.0 if a.score and a.score > 1 else (a.score or 0.5),
                "strength_score": a.score or 5,
            })

        # Compute agreement score with schema-defined weights
        weights = get_consensus_weights()
        agreement_score = compute_agreement_score(analysis_dicts, weights)

        # Generate LLM synthesis
        synthesis = generate_consensus_synthesis(
            title=paper.title,
            analyses=analysis_dicts,
            provider_id=req.provider,
            api_key_override=req.api_key,
        )

        # Build consensus object per MACP v2.0 schema
        now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        consensus = {
            "arxiv_id": paper.arxiv_id,
            "agents_compared": agents_compared,
            "generated_at": now.isoformat(),
            "generated_by": req.provider,
            "agreement_score": agreement_score,
            "synthesized_summary": (synthesis or {}).get("synthesized_summary", ""),
            "convergence_points": (synthesis or {}).get("convergence_points", []),
            "divergence_points": (synthesis or {}).get("divergence_points", []),
            "recommended_action": (synthesis or {}).get("recommended_action", "read_full_paper"),
            "bias_cross_check": (synthesis or {}).get("bias_cross_check", ""),
            "confidence_distribution": {
                a["agent_id"]: a["relevance_score"] for a in analysis_dicts
            },
        }

        # If LLM synthesis failed, build a basic consensus from analysis data
        if not synthesis:
            all_findings = []
            for a in analysis_dicts:
                all_findings.extend(a.get("key_findings", []))
            # Deduplicate findings
            seen = set()
            unique_findings = []
            for f in all_findings:
                f_lower = f.lower().strip()
                if f_lower not in seen:
                    seen.add(f_lower)
                    unique_findings.append(f)
            consensus["synthesized_summary"] = f"Consensus from {len(agents_compared)} agents. Agreement score: {agreement_score:.2f}."
            consensus["convergence_points"] = unique_findings[:5]

        # GitHub dual-write
        if user:
            storage = get_storage_service(user)
            if storage:
                async def _sync_consensus():
                    await storage.save_consensus(paper.arxiv_id, consensus)
                    await storage.update_manifest_entry("analyses", paper.arxiv_id, {
                        "consensus": {
                            "agreement_score": agreement_score,
                            "agents": agents_compared,
                            "generated_at": now.isoformat(),
                        },
                    })
                background_tasks.add_task(_sync_consensus)

        return mcp_response({
            "paper_id": paper.arxiv_id,
            "consensus": consensus,
        })

    except Exception:
        logger.exception("Consensus generation failed")
        return mcp_response("Consensus generation failed. Please try again.", is_error=True)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 9. Agents Registry
# ---------------------------------------------------------------------------

@mcp_router.get("/agents")
async def mcp_agents():
    """List all registered agents from .macp/agents/ directory."""
    agents_dir = os.path.join(MACP_DIR, "agents")
    agents = []
    if os.path.isdir(agents_dir):
        for fname in sorted(os.listdir(agents_dir)):
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(agents_dir, fname), "r", encoding="utf-8") as f:
                        agent_data = json.load(f)
                    agents.append(agent_data)
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning("Failed to load agent %s: %s", fname, e)

    return mcp_response({"agents": agents, "count": len(agents)})


# ---------------------------------------------------------------------------
# 10. Sync
# ---------------------------------------------------------------------------

@mcp_router.post("/sync")
async def mcp_sync(user: User = Depends(require_user)):
    """Force GitHub sync (hydration)."""
    storage = get_storage_service(user)
    if not storage:
        return mcp_response("No repository connected", is_error=True)

    stats = await storage.hydrate_from_github()
    return mcp_response({"status": "synced", "stats": stats})
