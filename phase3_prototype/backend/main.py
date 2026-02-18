"""
MACP Research Assistant — Phase 3A Backend API
================================================
FastAPI server that bridges the React frontend to our existing
Python CLI engine (paper_fetcher.py, llm_providers.py).

Author: RNA (Claude Code)
Date: February 19, 2026
"""

import os
import sys
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Add the tools directory to the Python path so we can import the engine
TOOLS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "tools")
sys.path.insert(0, os.path.abspath(TOOLS_DIR))

from paper_fetcher import (
    fetch_by_query,
    fetch_from_hysts,
    fetch_by_id,
    load_papers,
    add_papers,
)
from llm_providers import analyze_paper as _analyze_paper, PROVIDERS
from security_logger import log_api_error


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


class PaperResponse(BaseModel):
    id: str
    title: str
    authors: list[str] = []
    abstract: str = ""
    url: str = ""
    status: str = "discovered"


class AnalysisResponse(BaseModel):
    summary: str = ""
    key_insights: list[str] = []
    methodology: str = ""
    relevance_tags: list[str] = []
    research_gaps: list[str] = []
    strength_score: int = 0
    _meta: dict = {}


# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure .macp directory exists on startup."""
    os.makedirs(os.path.join(TOOLS_DIR, "..", ".macp"), exist_ok=True)
    yield


# ---------------------------------------------------------------------------
# Rate Limiting (P2.5-02)
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="MACP Research Assistant API",
    description="Phase 3A WebMCP Prototype — bridges the React UI to the MACP Python engine.",
    version="0.1.0",
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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    """Health check."""
    papers = load_papers()
    return {
        "status": "ok",
        "engine": "macp-research-assistant",
        "version": "phase3a-prototype",
        "papers_in_kb": len(papers.get("papers", [])),
    }


@app.post("/search")
@limiter.limit("30/minute")
async def search_papers(request: Request, req: SearchRequest):
    """
    Search for research papers.

    Wraps paper_fetcher.fetch_by_query / fetch_from_hysts.
    Results are also persisted to the MACP knowledge base.
    """
    try:
        if req.source == "hysts":
            papers = fetch_from_hysts(req.query, limit=req.limit)
        elif req.source == "hf":
            papers = fetch_by_query(req.query, limit=req.limit)
        elif req.source == "arxiv":
            # Single paper by ID
            paper = fetch_by_id(req.query)
            papers = [paper] if paper else []
        else:
            papers = fetch_from_hysts(req.query, limit=req.limit)
    except Exception as e:
        log_api_error("search", str(e))
        raise HTTPException(status_code=502, detail=f"Search engine error: {e}")

    # Persist discovered papers to the knowledge base
    if papers:
        try:
            add_papers(papers, force=True)
        except Exception:
            pass  # Non-critical — search results still returned

    return {"results": papers, "count": len(papers), "source": req.source}


@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze_paper_endpoint(request: Request, req: AnalyzeRequest):
    """
    Analyze a paper using an LLM provider.

    Wraps llm_providers.analyze_paper().
    The caller must provide an API key (BYOK) or have it set in env.
    """
    # Resolve provider config
    if req.provider not in PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {req.provider}")

    config = PROVIDERS[req.provider]

    # BYOK: temporarily set the API key in the environment if provided
    env_key = config["env_key"]
    original_key = os.environ.get(env_key)
    if req.api_key:
        os.environ[env_key] = req.api_key

    try:
        # Resolve paper from KB or fetch it
        paper_id = req.paper_id
        if not paper_id.startswith("arxiv:"):
            paper_id = f"arxiv:{paper_id}"

        papers_data = load_papers()
        paper = None
        for p in papers_data.get("papers", []):
            if p["id"] == paper_id:
                paper = p
                break

        if not paper:
            raise HTTPException(
                status_code=404,
                detail=f"Paper {paper_id} not found in knowledge base. Search first.",
            )

        title = paper.get("title", "")
        authors = paper.get("authors", [])
        abstract = paper.get("abstract", "")

        if not abstract:
            raise HTTPException(
                status_code=422,
                detail="Paper has no abstract — analysis requires an abstract.",
            )

        analysis = _analyze_paper(
            title=title,
            authors=authors,
            abstract=abstract,
            provider_id=req.provider,
        )

        if not analysis:
            raise HTTPException(status_code=502, detail="LLM analysis returned empty result.")

        return {"paper_id": paper_id, "title": title, "analysis": analysis}

    except HTTPException:
        raise
    except Exception as e:
        log_api_error(req.provider, str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
    finally:
        # Restore original env state
        if req.api_key:
            if original_key is not None:
                os.environ[env_key] = original_key
            else:
                os.environ.pop(env_key, None)
