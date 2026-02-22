"""
MACP Research Assistant — Phase 3C Backend API
================================================
FastAPI server with GitHub OAuth, JWT sessions, multi-user support,
3-tier rate limiting, security headers, and audit logging.

Author: RNA (Claude Code)
Date: February 21, 2026
"""

import json
import os
import secrets
import sys
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import httpx

from config import (
    CORS_ORIGINS,
    ENFORCE_HTTPS,
    GITHUB_APP_CLIENT_ID,
    RATE_LIMIT_ANALYZE,
    RATE_LIMIT_AUTH_ANALYZE,
    RATE_LIMIT_AUTH_SEARCH,
    RATE_LIMIT_SEARCH,
    TOOLS_DIR,
)
from database import (
    Analysis,
    AuditLog,
    Citation,
    LearningSession,
    Paper,
    SessionLocal,
    User,
    get_db,
    init_db,
    log_audit,
    upsert_paper,
)
from github_auth import (
    create_jwt,
    exchange_code_for_token,
    get_authorize_url,
    get_github_user,
    upsert_user,
)
from middleware import get_current_user, is_authenticated, require_user
from guest import check_guest_limit
from security import SecurityHeadersMiddleware
from github_storage import GitHubStorageService, get_storage_service
from webmcp import mcp_router

# Add the tools directory to the Python path
sys.path.insert(0, os.path.abspath(TOOLS_DIR))

from paper_fetcher import fetch_by_id, fetch_by_query, fetch_from_hysts
from llm_providers import analyze_paper as _analyze_paper, PROVIDERS


# ---------------------------------------------------------------------------
# Rate limiting: 3-tier key function
# ---------------------------------------------------------------------------

def _rate_limit_key(request: Request) -> str:
    """
    3-tier rate limit key:
    - Authenticated (JWT): user:{user_id}
    - Authenticated (API key): apikey:{ip}
    - Guest: guest:{ip}
    """
    auth = request.headers.get("authorization")
    api_key = request.headers.get("x-api-key")
    cookie = request.cookies.get("macp_session")

    if is_authenticated(authorization=auth, x_api_key=api_key, macp_session=cookie):
        # Try to extract user ID from JWT
        from github_auth import decode_jwt
        from jwt import InvalidTokenError
        for token in [cookie, auth[7:] if auth and auth.startswith("Bearer ") else None]:
            if token:
                try:
                    payload = decode_jwt(token)
                    return f"user:{payload.get('sub', 'unknown')}"
                except InvalidTokenError:
                    pass
        return f"apikey:{get_remote_address(request)}"

    return f"guest:{get_remote_address(request)}"


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(default=10, ge=1, le=50)
    offset: int = Field(default=0, ge=0)
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

REQUIRED_ENV_VARS = {
    "JWT_SECRET": "JWT session signing (CRITICAL — sessions will be insecure without this)",
}

RECOMMENDED_ENV_VARS = {
    "GEMINI_API_KEY": "Gemini API for paper analysis (analyze endpoint will return 503 without this)",
    "GITHUB_APP_CLIENT_ID": "GitHub OAuth (login will be unavailable without this)",
    "GITHUB_APP_CLIENT_SECRET": "GitHub OAuth secret",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and validate environment on startup."""
    # Validate required env vars — fail fast
    missing_required = []
    for var, desc in REQUIRED_ENV_VARS.items():
        if not os.environ.get(var):
            missing_required.append(f"  - {var}: {desc}")

    if missing_required:
        print(f"\n{'='*60}", file=sys.stderr)
        print("FATAL: Missing required environment variables:", file=sys.stderr)
        for m in missing_required:
            print(m, file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        sys.exit(1)

    # Warn about recommended env vars
    for var, desc in RECOMMENDED_ENV_VARS.items():
        if not os.environ.get(var):
            log_audit(event="env_warning", message=f"Missing recommended env var: {var} — {desc}", level="WARNING")

    init_db()
    log_audit(event="server_start", message="Phase 3C backend started — all env vars validated")
    yield
    log_audit(event="server_stop", message="Phase 3C backend stopped")


limiter = Limiter(key_func=_rate_limit_key)

app = FastAPI(
    title="MACP Research Assistant API",
    description="Phase 3C — GitHub OAuth, multi-user, WebMCP, security headers.",
    version="0.3.0",
    lifespan=lifespan,
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please wait before making more requests."},
    )


# Middleware (order matters — last added runs first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "Cookie"],
)

# Note: Do NOT use HTTPSRedirectMiddleware on Cloud Run.
# Cloud Run terminates TLS externally and forwards HTTP internally,
# causing infinite redirect loops. HSTS header in security.py handles
# browser enforcement. The X-Forwarded-Proto header is set by Cloud Run.

# Register WebMCP router
app.include_router(mcp_router)


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


def _get_user_id(user: Optional[User]) -> Optional[int]:
    """Extract user ID from User object, or None."""
    return user.id if user else None


# ---------------------------------------------------------------------------
# Auth Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/auth/github")
async def auth_github_redirect():
    """Redirect to GitHub OAuth authorization page."""
    if not GITHUB_APP_CLIENT_ID:
        raise HTTPException(status_code=503, detail="GitHub OAuth not configured")
    state = secrets.token_urlsafe(16)
    url = get_authorize_url(state=state)
    return RedirectResponse(url=url)


@app.get("/api/auth/github/callback")
async def auth_github_callback(code: str, state: Optional[str] = None):
    """Exchange OAuth code for token, create JWT, redirect to frontend."""
    try:
        access_token = await exchange_code_for_token(code)
        github_user = await get_github_user(access_token)
        user = upsert_user(github_user, access_token)
        token = create_jwt(user)

        log_audit(
            event="login",
            message=f"GitHub login: {user.github_login}",
            user_id=user.id,
        )

        # Set JWT in HttpOnly cookie and redirect to frontend
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(
            key="macp_session",
            value=token,
            httponly=True,
            secure=ENFORCE_HTTPS,
            samesite="lax",
            max_age=168 * 3600,  # 7 days
        )
        return response

    except Exception as e:
        log_audit(event="login_error", message=str(e), level="ERROR")
        raise HTTPException(status_code=401, detail="GitHub authentication failed. Please try again.")


@app.get("/api/auth/me")
async def auth_me(user: Optional[User] = Depends(get_current_user)):
    """Return current user profile, or null for guests."""
    if user is None:
        return {"user": None, "authenticated": False}
    return {"user": user.to_dict(), "authenticated": True}


@app.post("/api/auth/logout")
async def auth_logout():
    """Clear the session cookie."""
    response = JSONResponse(content={"status": "ok"})
    response.delete_cookie("macp_session")
    return response


# ---------------------------------------------------------------------------
# GitHub Storage Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/github/repos")
async def github_repos(user: User = Depends(require_user)):
    """List user's GitHub repositories (for Connect Repository flow)."""
    from github_auth import decrypt_token
    token = decrypt_token(user.github_access_token) if user.github_access_token else ""
    if not token:
        raise HTTPException(status_code=400, detail="No GitHub token")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.github.com/user/repos",
            params={"per_page": 100, "sort": "updated", "type": "owner"},
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"},
        )
        resp.raise_for_status()

    repos = [{"full_name": r["full_name"], "name": r["name"], "private": r["private"],
              "description": r.get("description", "")} for r in resp.json()]
    return {"repos": repos}


@app.post("/api/github/connect")
async def github_connect(
    request: Request,
    user: User = Depends(require_user),
):
    """Connect a repository for GitHub-first storage."""
    body = await request.json()
    repo = body.get("repo", "").strip()
    if not repo or "/" not in repo:
        raise HTTPException(status_code=400, detail="Invalid repo format. Use owner/repo.")

    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        db_user.connected_repo = repo
        db.commit()

        # Initialize repo structure
        db.refresh(db_user)
        storage = GitHubStorageService(db_user)
        ok = await storage.init_repo_structure()

        log_audit(event="github_connect", message=f"Connected repo: {repo}",
                  user_id=user.id, db=db)

        return {"status": "ok" if ok else "partial", "repo": repo,
                "message": "Repository connected" + (" and initialized" if ok else "")}
    finally:
        db.close()


@app.post("/api/github/sync")
async def github_sync(user: User = Depends(require_user)):
    """Trigger full sync from GitHub to DB (hydration)."""
    storage = get_storage_service(user)
    if not storage:
        raise HTTPException(status_code=400, detail="No repository connected")

    stats = await storage.hydrate_from_github()
    log_audit(event="github_sync", message=f"Hydrated: {stats}", user_id=user.id)
    return {"status": "ok", "stats": stats}


@app.get("/api/github/status")
async def github_status(user: User = Depends(require_user)):
    """Check GitHub storage connection status."""
    if not user.connected_repo:
        return {"connected": False, "repo": None}

    storage = get_storage_service(user)
    manifest = await storage.get_manifest() if storage else None
    return {
        "connected": True,
        "repo": user.connected_repo,
        "manifest": manifest,
    }


# ---------------------------------------------------------------------------
# Core Endpoints
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
        "version": "phase3c",
        "papers_in_db": count,
    }


@app.post("/search")
@limiter.limit(RATE_LIMIT_AUTH_SEARCH)
async def search_papers(
    request: Request,
    req: SearchRequest,
    user: Optional[User] = Depends(get_current_user),
):
    if user is None and not is_authenticated(
        authorization=request.headers.get("authorization"),
        x_api_key=request.headers.get("x-api-key"),
    ):
        check_guest_limit(request, "search")

    try:
        if req.source == "hysts":
            papers = fetch_from_hysts(req.query, limit=req.limit, offset=req.offset)
        elif req.source == "hf":
            papers = fetch_by_query(req.query, limit=req.limit)
        elif req.source == "arxiv":
            paper = fetch_by_id(req.query)
            papers = [paper] if paper else []
        else:
            papers = fetch_from_hysts(req.query, limit=req.limit, offset=req.offset)
    except Exception as e:
        log_audit(event="search_error", message=str(e), level="ERROR",
                  source_ip=get_remote_address(request))
        raise HTTPException(status_code=502, detail="Search service temporarily unavailable. Please try again.")

    db = SessionLocal()
    try:
        for p in papers:
            upsert_paper(db, p, user_id=_get_user_id(user))
        log_audit(event="search", message=f"query='{req.query}' results={len(papers)}",
                  source_ip=get_remote_address(request), user_id=_get_user_id(user), db=db)
    finally:
        db.close()

    return {
        "results": papers,
        "count": len(papers),
        "source": req.source,
        "offset": req.offset,
        "has_more": len(papers) == req.limit,
    }


@app.post("/analyze")
@limiter.limit(RATE_LIMIT_AUTH_ANALYZE)
async def analyze_paper_endpoint(
    request: Request,
    req: AnalyzeRequest,
    user: Optional[User] = Depends(get_current_user),
):
    if user is None and not is_authenticated(
        authorization=request.headers.get("authorization"),
        x_api_key=request.headers.get("x-api-key"),
    ):
        check_guest_limit(request, "analyze")

    if req.provider not in PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {req.provider}")

    config = PROVIDERS[req.provider]

    # Pre-check: ensure API key is available before calling LLM
    api_key = req.api_key or os.environ.get(config["env_key"], "")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=f"{config['name']} API key not configured. "
                   f"Set {config['env_key']} environment variable or provide your own key in the BYOK field."
        )

    db = SessionLocal()
    try:
        paper = _resolve_paper(db, req.paper_id)

        title = paper.title
        authors = json.loads(paper.authors) if paper.authors else []
        abstract = paper.abstract or ""

        if not abstract:
            raise HTTPException(status_code=422, detail="Paper has no abstract.")

        analysis = _analyze_paper(
            title=title, authors=authors, abstract=abstract,
            provider_id=req.provider, api_key_override=req.api_key,
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
            user_id=_get_user_id(user),
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
                  source_ip=get_remote_address(request), user_id=_get_user_id(user), db=db)

        return {"paper_id": paper.arxiv_id, "title": title, "analysis": analysis}

    except HTTPException:
        raise
    except Exception as e:
        log_audit(event="analyze_error", message=str(e), level="ERROR",
                  source_ip=get_remote_address(request))
        raise HTTPException(status_code=500, detail="Analysis service encountered an error. Please try again.")
    finally:
        db.close()


@app.post("/learn")
@limiter.limit(RATE_LIMIT_AUTH_SEARCH)
async def learn_endpoint(
    request: Request,
    req: LearnRequest,
    user: Optional[User] = Depends(get_current_user),
):
    if user is None and not is_authenticated(
        authorization=request.headers.get("authorization"),
        x_api_key=request.headers.get("x-api-key"),
    ):
        check_guest_limit(request, "search")

    db = SessionLocal()
    try:
        paper = _resolve_paper(db, req.paper_id)
        session = LearningSession(
            paper_id=paper.id, user_id=_get_user_id(user),
            insight=req.insight, agent=req.agent,
        )
        db.add(session)
        db.commit()
        log_audit(event="learn", message=f"paper={paper.arxiv_id} agent={req.agent}",
                  source_ip=get_remote_address(request), user_id=_get_user_id(user), db=db)
        return {"status": "ok", "paper_id": paper.arxiv_id, "session_id": session.id}
    finally:
        db.close()


@app.post("/cite")
@limiter.limit(RATE_LIMIT_AUTH_SEARCH)
async def cite_endpoint(
    request: Request,
    req: CiteRequest,
    user: Optional[User] = Depends(get_current_user),
):
    if user is None and not is_authenticated(
        authorization=request.headers.get("authorization"),
        x_api_key=request.headers.get("x-api-key"),
    ):
        check_guest_limit(request, "search")

    db = SessionLocal()
    try:
        paper = _resolve_paper(db, req.paper_id)
        citation = Citation(
            paper_id=paper.id, user_id=_get_user_id(user),
            project=req.project, context=req.context,
        )
        db.add(citation)
        paper.status = "cited"
        db.commit()
        log_audit(event="cite", message=f"paper={paper.arxiv_id} project={req.project}",
                  source_ip=get_remote_address(request), user_id=_get_user_id(user), db=db)
        return {"status": "ok", "paper_id": paper.arxiv_id, "citation_id": citation.id}
    finally:
        db.close()


@app.post("/recall")
@limiter.limit(RATE_LIMIT_AUTH_SEARCH)
async def recall_endpoint(
    request: Request,
    req: RecallRequest,
    user: Optional[User] = Depends(get_current_user),
):
    if user is None and not is_authenticated(
        authorization=request.headers.get("authorization"),
        x_api_key=request.headers.get("x-api-key"),
    ):
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
    user: Optional[User] = Depends(get_current_user),
):
    """View audit log entries."""
    db = SessionLocal()
    try:
        q = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
        if level:
            q = q.filter(AuditLog.level == level.upper())
        entries = q.limit(min(limit, 500)).all()
        return {"entries": [e.to_dict() for e in entries], "count": len(entries)}
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Static files (production: serve frontend from /app/static)
# ---------------------------------------------------------------------------

_static_dir = os.getenv("STATIC_DIR", os.path.join(os.path.dirname(__file__), "..", "static"))
if os.path.isdir(_static_dir):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        file_path = os.path.join(_static_dir, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(_static_dir, "index.html"))
