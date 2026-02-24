"""
MACP Research Assistant — GitHub Storage Layer (Sprint 3D.2)
=============================================================
GitHub-first persistence: GitHub is the write-ahead log, SQLite is a cache.

MACP v2.0 Directory Standard:
  .macp/
  ├── manifest.json              ← Master index of all papers, analyses, notes
  ├── papers/{arxiv_id}.json     ← One JSON file per paper
  ├── analyses/{arxiv_id}.json   ← Analysis results per paper
  ├── notes/note_{id}.md         ← Research notes as Markdown
  └── graph/knowledge-graph.json ← Knowledge graph data

Hydration: On cold start (empty SQLite), reads manifest.json from GitHub
and re-populates the local database cache.
"""

import asyncio
import base64
import json
import logging
import re
from datetime import datetime, timezone
from typing import Optional

import httpx

from database import SessionLocal, User, Paper, Analysis, Note
from github_auth import decrypt_token

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
REPO_PREFIX = ".macp"  # MACP v2.0 standard

# Strict validation: owner/repo must be alphanumeric, hyphens, underscores, dots only
_REPO_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$")


def _validate_repo(repo: str) -> str:
    """Validate and sanitize a GitHub repo identifier to prevent SSRF."""
    if not repo or not _REPO_PATTERN.match(repo):
        raise ValueError(f"Invalid GitHub repo format: {repo!r}")
    return repo


class GitHubStorageService:
    """Manages dual-write to a user's connected GitHub repository."""

    def __init__(self, user: User):
        self.user = user
        self.repo = _validate_repo(user.connected_repo) if user.connected_repo else ""
        self._token = decrypt_token(user.github_access_token) if user.github_access_token else ""

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def _put_file(self, path: str, content: str, message: str, max_retries: int = 3) -> bool:
        """Create or update a file via GitHub Contents API with retry logic."""
        if not self.repo or not self._token:
            return False

        url = f"{GITHUB_API}/repos/{self.repo}/contents/{path}"

        for attempt in range(1, max_retries + 1):
            try:
                # Check if file exists (to get sha for update)
                sha = None
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.get(url, headers=self._headers())
                    if resp.status_code == 200:
                        sha = resp.json().get("sha")

                    body = {
                        "message": message,
                        "content": base64.b64encode(content.encode()).decode(),
                    }
                    if sha:
                        body["sha"] = sha

                    resp = await client.put(url, json=body, headers=self._headers())
                    if resp.status_code in (200, 201):
                        logger.info("GitHub PUT %s succeeded (attempt %d)", path, attempt)
                        return True

                    # Don't retry on auth errors
                    if resp.status_code in (401, 403, 404, 422):
                        logger.warning("GitHub PUT %s failed (non-retryable): %s", path, resp.status_code)
                        return False

                    logger.warning("GitHub PUT %s failed (attempt %d/%d): %s", path, attempt, max_retries, resp.status_code)

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                logger.warning("GitHub PUT %s error (attempt %d/%d): %s", path, attempt, max_retries, e)

            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)  # exponential backoff: 2s, 4s

        logger.error("GitHub PUT %s failed after %d attempts", path, max_retries)
        return False

    async def _get_file(self, path: str) -> Optional[str]:
        """Read a file from the GitHub repo."""
        if not self.repo or not self._token:
            return None

        url = f"{GITHUB_API}/repos/{self.repo}/contents/{path}"
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=self._headers())
            if resp.status_code != 200:
                return None
            data = resp.json()
            return base64.b64decode(data["content"]).decode()

    async def _list_dir(self, path: str) -> list[str]:
        """List filenames in a GitHub directory."""
        if not self.repo or not self._token:
            return []

        url = f"{GITHUB_API}/repos/{self.repo}/contents/{path}"
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=self._headers())
            if resp.status_code != 200:
                return []
            items = resp.json()
            if isinstance(items, list):
                return [item["name"] for item in items]
        return []

    # -----------------------------------------------------------------------
    # Repository initialization
    # -----------------------------------------------------------------------

    async def init_repo_structure(self) -> bool:
        """Create the .macp/ directory structure in the connected repo (MACP v2.0)."""
        manifest = {
            "version": "2.0",
            "schema": "macp-research",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "owner": self.user.github_login,
            "papers": {},
            "analyses": {},
            "notes": {},
        }
        return await self._put_file(
            f"{REPO_PREFIX}/manifest.json",
            json.dumps(manifest, indent=2),
            "Initialize MACP v2.0 research data directory",
        )

    # -----------------------------------------------------------------------
    # Save operations (fire-and-forget from BackgroundTasks)
    # -----------------------------------------------------------------------

    async def save_paper(self, paper: Paper) -> bool:
        """Save a paper to GitHub."""
        arxiv_id = paper.arxiv_id.replace(":", "_")
        data = paper.to_dict()
        return await self._put_file(
            f"{REPO_PREFIX}/papers/{arxiv_id}.json",
            json.dumps(data, indent=2),
            f"Save paper: {paper.title[:60]}",
        )

    async def save_analysis(self, paper: Paper, analysis: Analysis) -> bool:
        """Save an analysis to GitHub."""
        arxiv_id = paper.arxiv_id.replace(":", "_")
        data = {
            "paper": paper.to_dict(),
            "analysis": analysis.to_dict(),
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        return await self._put_file(
            f"{REPO_PREFIX}/analyses/{arxiv_id}.json",
            json.dumps(data, indent=2),
            f"Save analysis: {paper.title[:60]}",
        )

    async def save_note(self, note: Note) -> bool:
        """Save a note as Markdown to GitHub."""
        tags = json.loads(note.tags) if note.tags else []
        tag_str = ", ".join(tags) if tags else "none"
        content = f"# Research Note #{note.id}\n\n"
        content += f"**Tags:** {tag_str}\n"
        content += f"**Created:** {note.created_at.isoformat() if note.created_at else 'unknown'}\n\n"
        content += note.content
        return await self._put_file(
            f"{REPO_PREFIX}/notes/note_{note.id}.md",
            content,
            f"Save note #{note.id}",
        )

    async def save_graph(self, graph_data: dict) -> bool:
        """Save knowledge graph data to GitHub."""
        return await self._put_file(
            f"{REPO_PREFIX}/graph/knowledge-graph.json",
            json.dumps(graph_data, indent=2),
            "Update knowledge graph",
        )

    # -----------------------------------------------------------------------
    # Manifest
    # -----------------------------------------------------------------------

    async def get_manifest(self) -> Optional[dict]:
        """Read the manifest from GitHub. Checks both v2.0 (.macp/) and v1.0 (.macp-research/)."""
        # Try MACP v2.0 location first
        content = await self._get_file(f"{REPO_PREFIX}/manifest.json")
        if content:
            return json.loads(content)

        # Fall back to legacy v1.0 location
        content = await self._get_file(".macp-research/manifest.json")
        if content:
            return json.loads(content)

        return None

    async def update_manifest(self, updates: dict) -> bool:
        """Merge updates into the manifest (deprecated — use update_manifest_entry)."""
        manifest = await self.get_manifest()
        if not manifest:
            manifest = {"version": "2.0", "schema": "macp-research", "papers": {}, "analyses": {}, "notes": {}}

        # Deep merge for papers/analyses/notes sections
        for section in ("papers", "analyses", "notes"):
            if section in updates:
                manifest.setdefault(section, {}).update(updates[section])

        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        return await self._put_file(
            f"{REPO_PREFIX}/manifest.json",
            json.dumps(manifest, indent=2),
            "Update manifest",
        )

    async def update_manifest_entry(self, section: str, key: str, data: dict) -> bool:
        """Update a single entry in the manifest. Atomic read-modify-write."""
        manifest = await self.get_manifest()
        if not manifest:
            manifest = {"version": "2.0", "schema": "macp-research", "papers": {}, "analyses": {}, "notes": {}}

        manifest.setdefault(section, {})[key] = data
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()

        return await self._put_file(
            f"{REPO_PREFIX}/manifest.json",
            json.dumps(manifest, indent=2),
            f"Update manifest: {section}/{key}",
        )

    # -----------------------------------------------------------------------
    # Hydration (pull from GitHub → DB on cold start)
    # -----------------------------------------------------------------------

    async def hydrate_from_github(self) -> dict:
        """Pull all data from GitHub repo into the database. GitHub wins on conflicts.

        Strategy:
        1. Read manifest.json for indexed entries
        2. Also scan papers/ and analyses/ directories for any files not in manifest
        3. Populate SQLite cache from GitHub data
        """
        stats = {"papers": 0, "analyses": 0, "notes": 0, "errors": 0}

        db = SessionLocal()
        try:
            # Determine which prefix has data (v2.0 or legacy v1.0)
            prefix = REPO_PREFIX
            manifest = await self.get_manifest()

            # Try to discover papers from directory listing if manifest is sparse
            paper_files = set()
            if manifest:
                # Add manifest-indexed papers
                for arxiv_id in manifest.get("papers", {}):
                    paper_files.add(arxiv_id.replace(":", "_"))

            # Also scan papers/ directory for any files not in manifest
            for p in (prefix, ".macp-research"):
                dir_files = await self._list_dir(f"{p}/papers")
                for fname in dir_files:
                    if fname.endswith(".json"):
                        paper_files.add(fname.replace(".json", ""))
                if dir_files:
                    prefix = p  # use whichever prefix has data
                    break

            # Hydrate papers
            from database import upsert_paper
            for arxiv_file_id in paper_files:
                try:
                    content = await self._get_file(f"{prefix}/papers/{arxiv_file_id}.json")
                    if content:
                        paper_data = json.loads(content)
                        paper = upsert_paper(db, paper_data, user_id=self.user.id)
                        # Mark as saved if it came from the saved papers directory
                        if paper.status == "discovered":
                            paper.status = "saved"
                            db.commit()
                        stats["papers"] += 1
                except Exception as e:
                    logger.warning("Hydrate paper %s failed: %s", arxiv_file_id, e)
                    stats["errors"] += 1

            # Hydrate analyses
            analysis_files = await self._list_dir(f"{prefix}/analyses")
            for fname in analysis_files:
                if not fname.endswith(".json"):
                    continue
                try:
                    content = await self._get_file(f"{prefix}/analyses/{fname}")
                    if content:
                        data = json.loads(content)
                        paper_data = data.get("paper", {})
                        analysis_data = data.get("analysis", {})
                        arxiv_id = paper_data.get("id", "")
                        if arxiv_id:
                            paper = db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()
                            if paper:
                                # Check if analysis already exists
                                existing = db.query(Analysis).filter(
                                    Analysis.paper_id == paper.id,
                                    Analysis.provider == analysis_data.get("provenance", {}).get("provider", "unknown"),
                                ).first()
                                if not existing:
                                    provenance = analysis_data.get("_meta", analysis_data.get("provenance", {}))
                                    db_analysis = Analysis(
                                        paper_id=paper.id,
                                        user_id=self.user.id,
                                        provider=provenance.get("provider", "unknown") if isinstance(provenance, dict) else "unknown",
                                        summary=analysis_data.get("summary", ""),
                                        key_insights=json.dumps(analysis_data.get("key_insights", [])),
                                        methodology=analysis_data.get("methodology", ""),
                                        research_gaps=json.dumps(analysis_data.get("research_gaps", [])),
                                        relevance_tags=json.dumps(analysis_data.get("relevance_tags", [])),
                                        score=analysis_data.get("strength_score", 0),
                                        provenance=json.dumps(provenance) if isinstance(provenance, dict) else "{}",
                                    )
                                    db.add(db_analysis)
                                    paper.status = "analyzed"
                                    stats["analyses"] += 1
                except Exception as e:
                    logger.warning("Hydrate analysis %s failed: %s", fname, e)
                    stats["errors"] += 1

            # Hydrate notes
            note_files = await self._list_dir(f"{prefix}/notes")
            for fname in note_files:
                if not fname.endswith(".md"):
                    continue
                try:
                    content = await self._get_file(f"{prefix}/notes/{fname}")
                    if content:
                        # Parse Markdown note: extract content after the header
                        lines = content.split("\n")
                        note_content = ""
                        tags = []
                        for line in lines:
                            if line.startswith("**Tags:**"):
                                tag_str = line.replace("**Tags:**", "").strip()
                                if tag_str and tag_str != "none":
                                    tags = [t.strip() for t in tag_str.split(",")]
                            elif not line.startswith("#") and not line.startswith("**Created:**"):
                                note_content += line + "\n"
                        note_content = note_content.strip()
                        if note_content:
                            # Check for duplicate by content
                            existing = db.query(Note).filter(
                                Note.user_id == self.user.id,
                                Note.content == note_content,
                            ).first()
                            if not existing:
                                note = Note(
                                    user_id=self.user.id,
                                    content=note_content,
                                    tags=json.dumps(tags),
                                )
                                db.add(note)
                                stats["notes"] += 1
                except Exception as e:
                    logger.warning("Hydrate note %s failed: %s", fname, e)
                    stats["errors"] += 1

            db.commit()
            logger.info("Hydration complete: %s", stats)
        finally:
            db.close()

        return stats


# ---------------------------------------------------------------------------
# Helper: get storage service for a user
# ---------------------------------------------------------------------------

def get_storage_service(user: User) -> Optional[GitHubStorageService]:
    """Return a GitHubStorageService if the user has a connected repo."""
    if user and user.connected_repo:
        return GitHubStorageService(user)
    return None
