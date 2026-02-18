"""
MACP Research Assistant — Phase 3B Backend API
================================================
FastAPI server with SQLite database, API key auth, guest mode,
audit logging, and rate limiting.

Author: RNA (Claude Code)
Date: February 19, 2026
"""

import json
import os
import sys
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from config import CORS_ORIGINS, RATE_LIMIT_ANALYZE, RATE_LIMIT_SEARCH, TOOLS_DIR
from database import (
    Analysis,
    AuditLog,
    Citation,
    LearningSession,
    Paper,
    SessionLocal,
    get_db,
    init_db,
    log_audit,
    upsert_paper,
)
from auth import get_api_key
from guest import check_guest_limit

# Add the tools directory to the Python path
sys.path.insert(0, os.path.abspath(TOOLS_DIR))

from paper_fetcher import fetch_by_id, fetch_by_query, fetch_from_hysts
from llm_providers import analyze_paper as _analyze_paper, PROVIDERS


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(default=10, ge=1, le=50)
    source: str = Field(default="hysts", pattern="^(hf|hysts|arxiv)$")


class AnalyzeRequest(BaseModel):
    paper_id: str = Field(..., min_length=1)
    provider: str = Field(default="gemini")
    api_key: Optional[str] = Field(default=None)


class LearnRequest(BaseModel):
    paper_id: str = Field(..., min_length=1)
    insight: str = Field(..., min_length=1, max_length=2000)
    agent: str = Field(default="human", max_length=100)


class CiteRequest(BaseModel):
    paper_id: str = Field(..., min_length=1)
    project: str = Field(..., min_length=1, max_length=200)
    context: str = Field(default="", max_length=2000)


class RecallRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)


# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    log_audit(event="server_start", message="Phase 3B backend started")
    yield
    log_audit(event="server_stop", message="Phase 3B backend stopped")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="MACP Research Assistant API",
    description="Phase 3B Full Hybrid — SQLite DB, auth, audit, guest mode.",
    version="0.2.0",
    lifespan=lifespan,
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please wait before making more requests."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _resolve_paper(db, paper_id: str) -> Paper:
    """Resolve an arxiv_id to a Paper ORM object, or raise 404."""
    if not paper_id.startswith("arxiv:"):
        paper_id = f"arxiv:{paper_id}"
    paper = db.query(Paper).filter(Paper.arxiv_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found. Search first.")
    return paper


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    db = SessionLocal()
    try:
        count = db.query(Paper).count()
    finally:
        db.close()
    return {
        "status": "ok",
        "engine": "macp-research-assistant",
        "version": "phase3b",
        "papers_in_db": count,
    }


@app.post("/search")
@limiter.limit(RATE_LIMIT_SEARCH)
async def search_papers(
    request: Request,
    req: SearchRequest,
    auth_key: Optional[str] = Depends(get_api_key),
):
    if auth_key is None:
        check_guest_limit(request, "search")

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
    except Exception as e:
        log_audit(event="search_error", message=str(e), level="ERROR",
                  source_ip=get_remote_address(request))
        raise HTTPException(status_code=502, detail=f"Search engine error: {e}")

    db = SessionLocal()
    try:
        for p in papers:
            upsert_paper(db, p)
        log_audit(event="search", message=f"query='{req.query}' results={len(papers)}",
                  source_ip=get_remote_address(request), db=db)
    finally:
        db.close()

    return {"results": papers, "count": len(papers), "source": req.source}


@app.post("/analyze")
@limiter.limit(RATE_LIMIT_ANALYZE)
async def analyze_paper_endpoint(
    request: Request,
    req: AnalyzeRequest,
    auth_key: Optional[str] = Depends(get_api_key),
):
    if auth_key is None:
        check_guest_limit(request, "analyze")

    if req.provider not in PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {req.provider}")

    config = PROVIDERS[req.provider]
    env_key = config["env_key"]
    original_key = os.environ.get(env_key)
    if req.api_key:
        os.environ[env_key] = req.api_key

    try:
        db = SessionLocal()
        paper = _resolve_paper(db, req.paper_id)

        title = paper.title
        authors = json.loads(paper.authors) if paper.authors else []
        abstract = paper.abstract or ""

        if not abstract:
            raise HTTPException(status_code=422, detail="Paper has no abstract.")

        analysis = _analyze_paper(
            title=title, authors=authors, abstract=abstract, provider_id=req.provider,
        )

        if not analysis:
            raise HTTPException(status_code=502, detail="LLM analysis returned empty result.")

        provenance = json.dumps({
            "provider": req.provider,
            "model": config["model"],
            "bias_disclaimer": "AI-generated analysis may contain inaccuracies or reflect biases from the underlying model.",
        })

        db_analysis = Analysis(
            paper_id=paper.id,
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

        log_audit(event="analyze", message=f"paper={paper.arxiv_id} provider={req.provider}",
                  source_ip=get_remote_address(request), db=db)
        db.close()

        return {"paper_id": paper.arxiv_id, "title": title, "analysis": analysis}

    except HTTPException:
        raise
    except Exception as e:
        log_audit(event="analyze_error", message=str(e), level="ERROR",
                  source_ip=get_remote_address(request))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
    finally:
        if req.api_key:
            if original_key is not None:
                os.environ[env_key] = original_key
            else:
                os.environ.pop(env_key, None)


@app.post("/learn")
@limiter.limit(RATE_LIMIT_SEARCH)
async def learn_endpoint(
    request: Request,
    req: LearnRequest,
    auth_key: Optional[str] = Depends(get_api_key),
):
    if auth_key is None:
        check_guest_limit(request, "search")

    db = SessionLocal()
    try:
        paper = _resolve_paper(db, req.paper_id)
        session = LearningSession(
            paper_id=paper.id, insight=req.insight, agent=req.agent,
        )
        db.add(session)
        db.commit()
        log_audit(event="learn", message=f"paper={paper.arxiv_id} agent={req.agent}",
                  source_ip=get_remote_address(request), db=db)
        return {"status": "ok", "paper_id": paper.arxiv_id, "session_id": session.id}
    finally:
        db.close()


@app.post("/cite")
@limiter.limit(RATE_LIMIT_SEARCH)
async def cite_endpoint(
    request: Request,
    req: CiteRequest,
    auth_key: Optional[str] = Depends(get_api_key),
):
    if auth_key is None:
        check_guest_limit(request, "search")

    db = SessionLocal()
    try:
        paper = _resolve_paper(db, req.paper_id)
        citation = Citation(
            paper_id=paper.id, project=req.project, context=req.context,
        )
        db.add(citation)
        paper.status = "cited"
        db.commit()
        log_audit(event="cite", message=f"paper={paper.arxiv_id} project={req.project}",
                  source_ip=get_remote_address(request), db=db)
        return {"status": "ok", "paper_id": paper.arxiv_id, "citation_id": citation.id}
    finally:
        db.close()


@app.post("/recall")
@limiter.limit(RATE_LIMIT_SEARCH)
async def recall_endpoint(
    request: Request,
    req: RecallRequest,
    auth_key: Optional[str] = Depends(get_api_key),
):
    if auth_key is None:
        check_guest_limit(request, "search")

    db = SessionLocal()
    try:
        query = f"%{req.query}%"
        papers = db.query(Paper).filter(
            (Paper.title.ilike(query)) | (Paper.abstract.ilike(query))
        ).limit(20).all()

        sessions = db.query(LearningSession).filter(
            LearningSession.insight.ilike(query)
        ).limit(20).all()

        return {
            "papers": [p.to_dict() for p in papers],
            "sessions": [s.to_dict() for s in sessions],
            "total": len(papers) + len(sessions),
        }
    finally:
        db.close()


@app.get("/audit")
@limiter.limit("10/minute")
async def audit_endpoint(
    request: Request,
    limit: int = 50,
    level: Optional[str] = None,
    auth_key: Optional[str] = Depends(get_api_key),
):
    """P3B-04: View audit log entries."""
    db = SessionLocal()
    try:
        q = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
        if level:
            q = q.filter(AuditLog.level == level.upper())
        entries = q.limit(min(limit, 500)).all()
        return {"entries": [e.to_dict() for e in entries], "count": len(entries)}
    finally:
        db.close()
