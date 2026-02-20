"""
MACP Research Assistant — GitHub Storage Layer (Phase 3C)
=========================================================
Dual-write: every save goes to DB (cache) AND user's GitHub repo (source of truth).
GitHub writes are fire-and-forget via BackgroundTasks — they don't block API responses.

Repo structure:
  .macp-research/
  ├── papers/{arxiv_id}.json
  ├── analyses/{arxiv_id}.json
  ├── graph/knowledge-graph.json
  ├── notes/{note_id}.md
  └── manifest.json
"""

import base64
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

from database import SessionLocal, User, Paper, Analysis, Note
from github_auth import decrypt_token

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
REPO_PREFIX = ".macp-research"


class GitHubStorageService:
    """Manages dual-write to a user's connected GitHub repository."""

    def __init__(self, user: User):
        self.user = user
        self.repo = user.connected_repo  # "owner/repo"
        self._token = decrypt_token(user.github_access_token) if user.github_access_token else ""

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def _put_file(self, path: str, content: str, message: str) -> bool:
        """Create or update a file via GitHub Contents API."""
        if not self.repo or not self._token:
            return False

        url = f"{GITHUB_API}/repos/{self.repo}/contents/{path}"

        # Check if file exists (to get sha for update)
        sha = None
        async with httpx.AsyncClient() as client:
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
                return True

            logger.warning("GitHub PUT %s failed: %s %s", path, resp.status_code, resp.text[:200])
            return False

    async def _get_file(self, path: str) -> Optional[str]:
        """Read a file from the GitHub repo."""
        if not self.repo or not self._token:
            return None

        url = f"{GITHUB_API}/repos/{self.repo}/contents/{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers())
            if resp.status_code != 200:
                return None
            data = resp.json()
            return base64.b64decode(data["content"]).decode()

    # -----------------------------------------------------------------------
    # Repository initialization
    # -----------------------------------------------------------------------

    async def init_repo_structure(self) -> bool:
        """Create the .macp-research/ directory structure in the connected repo."""
        manifest = {
            "version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "owner": self.user.github_login,
            "papers": {},
            "analyses": {},
            "notes": {},
        }
        return await self._put_file(
            f"{REPO_PREFIX}/manifest.json",
            json.dumps(manifest, indent=2),
            "Initialize MACP Research data directory",
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
        """Read the manifest from GitHub."""
        content = await self._get_file(f"{REPO_PREFIX}/manifest.json")
        if content:
            return json.loads(content)
        return None

    async def update_manifest(self, updates: dict) -> bool:
        """Merge updates into the manifest."""
        manifest = await self.get_manifest()
        if not manifest:
            manifest = {"version": "1.0", "papers": {}, "analyses": {}, "notes": {}}
        manifest.update(updates)
        return await self._put_file(
            f"{REPO_PREFIX}/manifest.json",
            json.dumps(manifest, indent=2),
            "Update manifest",
        )

    # -----------------------------------------------------------------------
    # Hydration (pull from GitHub → DB)
    # -----------------------------------------------------------------------

    async def hydrate_from_github(self) -> dict:
        """Pull all data from GitHub repo into the database. GitHub wins on conflicts."""
        stats = {"papers": 0, "analyses": 0, "notes": 0, "errors": 0}

        manifest = await self.get_manifest()
        if not manifest:
            return stats

        db = SessionLocal()
        try:
            # Hydrate papers
            for arxiv_id in manifest.get("papers", {}):
                try:
                    content = await self._get_file(f"{REPO_PREFIX}/papers/{arxiv_id}.json")
                    if content:
                        from database import upsert_paper
                        paper_data = json.loads(content)
                        upsert_paper(db, paper_data, user_id=self.user.id)
                        stats["papers"] += 1
                except Exception as e:
                    logger.warning("Hydrate paper %s failed: %s", arxiv_id, e)
                    stats["errors"] += 1

            db.commit()
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
