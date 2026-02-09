#!/usr/bin/env python3
"""
MACP Research Assistant - Paper Fetcher Module
===============================================
Core data access library for discovering and fetching research papers
from multiple sources: HF Daily Papers API, HF MCP Paper Search, and arXiv API.

Author: L (Godel), AI Agent & Project Founder
Date: February 10, 2026
"""

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, date
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
HF_DAILY_PAPERS_API = "https://huggingface.co/api/daily_papers"
ARXIV_API = "http://export.arxiv.org/api/query"
MACP_DIR = ".macp"
PAPERS_FILE = os.path.join(MACP_DIR, "research_papers.json")

# ---------------------------------------------------------------------------
# Utility: Normalize paper data to MACP schema
# ---------------------------------------------------------------------------

def normalize_paper(
    arxiv_id: str,
    title: str,
    authors: list[str] | None = None,
    url: str | None = None,
    abstract: str | None = None,
    discovered_by: str = "macp_cli",
    discovered_date: str | None = None,
    extra: dict | None = None,
) -> dict:
    """Normalize paper data from any source into the MACP research_papers schema."""
    if discovered_date is None:
        discovered_date = date.today().isoformat()
    if url is None:
        url = f"https://huggingface.co/papers/{arxiv_id}"

    paper = {
        "id": f"arxiv:{arxiv_id}",
        "title": title.strip(),
        "authors": authors or [],
        "url": url,
        "abstract": abstract or "",
        "discovered_by": discovered_by,
        "discovered_date": discovered_date,
        "status": "discovered",
        "insights": [],
    }
    if extra:
        paper["_meta"] = extra
    return paper


# ---------------------------------------------------------------------------
# Pipeline 1: HF Daily Papers API (date-based discovery)
# ---------------------------------------------------------------------------

def fetch_by_date(target_date: str) -> list[dict]:
    """
    Fetch papers from the Hugging Face Daily Papers API for a specific date.

    Args:
        target_date: Date string in YYYY-MM-DD format.

    Returns:
        List of normalized paper dicts.
    """
    params = {"date": target_date}
    try:
        resp = requests.get(HF_DAILY_PAPERS_API, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[ERROR] HF Daily Papers API request failed: {e}", file=sys.stderr)
        return []

    if isinstance(data, dict) and "error" in data:
        print(f"[WARN] HF API returned error: {data['error']}", file=sys.stderr)
        return []

    papers = []
    for entry in data:
        paper_data = entry.get("paper", {})
        arxiv_id = paper_data.get("id", "")
        title = paper_data.get("title", "Unknown Title")
        authors = [a.get("name", "") for a in paper_data.get("authors", [])]
        abstract = paper_data.get("summary", "")
        upvotes = paper_data.get("upvotes", 0)
        github_repo = paper_data.get("githubRepo", "")
        ai_keywords = paper_data.get("ai_keywords", [])

        extra = {}
        if upvotes:
            extra["hf_upvotes"] = upvotes
        if github_repo:
            extra["github_repo"] = github_repo
        if ai_keywords:
            extra["ai_keywords"] = ai_keywords

        papers.append(normalize_paper(
            arxiv_id=arxiv_id,
            title=title,
            authors=authors,
            abstract=abstract,
            discovered_by="hf_daily_papers",
            discovered_date=target_date,
            extra=extra if extra else None,
        ))
    return papers


def fetch_by_date_range(start_date: str, end_date: str) -> list[dict]:
    """
    Fetch papers across a date range by calling fetch_by_date for each day.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        List of normalized paper dicts.
    """
    from datetime import timedelta
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    all_papers = []
    current = start
    while current <= end:
        date_str = current.isoformat()
        print(f"  Fetching papers for {date_str}...")
        papers = fetch_by_date(date_str)
        all_papers.extend(papers)
        current += timedelta(days=1)
    return all_papers


# ---------------------------------------------------------------------------
# Pipeline 2: HF MCP Paper Search (semantic query-based discovery)
# ---------------------------------------------------------------------------

def fetch_by_query(query: str, limit: int = 10) -> list[dict]:
    """
    Search for papers using the Hugging Face MCP paper_search tool.

    Args:
        query: Natural language search query.
        limit: Maximum number of results.

    Returns:
        List of normalized paper dicts.
    """
    input_json = json.dumps({"query": query, "results_limit": limit})
    try:
        result = subprocess.run(
            [
                "manus-mcp-cli", "tool", "call", "paper_search",
                "--server", "hugging-face",
                "--input", input_json,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"[ERROR] MCP paper_search call failed: {e}", file=sys.stderr)
        return []

    output = result.stdout
    if not output:
        print("[WARN] MCP paper_search returned empty output.", file=sys.stderr)
        return []

    # Parse the MCP output (structured text with paper blocks)
    papers = _parse_mcp_paper_output(output, query)
    return papers


def _parse_mcp_paper_output(text: str, query: str) -> list[dict]:
    """Parse the text output from the MCP paper_search tool into normalized papers."""
    papers = []
    blocks = text.split("---")

    for block in blocks:
        block = block.strip()
        if not block or "papers matched" in block.lower():
            continue

        title = ""
        arxiv_id = ""
        authors = []
        abstract = ""
        link = ""

        lines = block.split("\n")
        in_abstract = False

        for line in lines:
            line = line.strip()
            if line.startswith("## "):
                title = line.lstrip("# ").strip()
                in_abstract = False
            elif line.startswith("**Authors:**"):
                author_text = line.replace("**Authors:**", "").strip()
                # Remove HF usernames in parentheses
                import re
                author_text = re.sub(r'\s*\([^)]*\)', '', author_text)
                authors = [a.strip() for a in author_text.split(",") if a.strip()]
                in_abstract = False
            elif line.startswith("### Abstract"):
                in_abstract = True
            elif line.startswith("**AI Keywords**"):
                in_abstract = False
            elif line.startswith("**Link to paper:**"):
                import re
                match = re.search(r'papers/(\d+\.\d+)', line)
                if match:
                    arxiv_id = match.group(1)
                link = line
                in_abstract = False
            elif in_abstract and line:
                abstract += line + " "

        if title and arxiv_id:
            papers.append(normalize_paper(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                abstract=abstract.strip(),
                discovered_by=f"hf_mcp_search:{query[:50]}",
            ))

    return papers


# ---------------------------------------------------------------------------
# Pipeline 3: arXiv API (direct ID-based fetch)
# ---------------------------------------------------------------------------

def fetch_by_id(arxiv_id: str) -> Optional[dict]:
    """
    Fetch a single paper's full metadata from the arXiv API.

    Args:
        arxiv_id: The arXiv identifier (e.g., "2602.06570").

    Returns:
        A normalized paper dict, or None if not found.
    """
    params = {"id_list": arxiv_id, "max_results": 1}
    try:
        resp = requests.get(ARXIV_API, params=params, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] arXiv API request failed: {e}", file=sys.stderr)
        return None

    # Parse the Atom XML response
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse arXiv XML: {e}", file=sys.stderr)
        return None

    entry = root.find("atom:entry", ns)
    if entry is None:
        print(f"[WARN] No entry found for arXiv ID: {arxiv_id}", file=sys.stderr)
        return None

    title = entry.findtext("atom:title", default="", namespaces=ns).strip().replace("\n", " ")
    abstract = entry.findtext("atom:summary", default="", namespaces=ns).strip().replace("\n", " ")
    authors = [a.findtext("atom:name", default="", namespaces=ns) for a in entry.findall("atom:author", ns)]
    published = entry.findtext("atom:published", default="", namespaces=ns)[:10]
    url = f"https://arxiv.org/abs/{arxiv_id}"

    return normalize_paper(
        arxiv_id=arxiv_id,
        title=title,
        authors=authors,
        url=url,
        abstract=abstract,
        discovered_by="arxiv_api",
        discovered_date=published if published else None,
    )


# ---------------------------------------------------------------------------
# MACP Storage: Read/Write research_papers.json
# ---------------------------------------------------------------------------

def load_papers(macp_dir: str = MACP_DIR) -> dict:
    """Load the current research_papers.json file."""
    filepath = os.path.join(macp_dir, "research_papers.json")
    if not os.path.exists(filepath):
        return {"papers": []}
    with open(filepath, "r") as f:
        return json.load(f)


def save_papers(data: dict, macp_dir: str = MACP_DIR) -> None:
    """Save the research_papers.json file."""
    filepath = os.path.join(macp_dir, "research_papers.json")
    os.makedirs(macp_dir, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved {len(data.get('papers', []))} papers to {filepath}")


def add_papers(new_papers: list[dict], macp_dir: str = MACP_DIR) -> tuple[int, int]:
    """
    Add new papers to research_papers.json, skipping duplicates.

    Returns:
        Tuple of (added_count, skipped_count).
    """
    data = load_papers(macp_dir)
    existing_ids = {p["id"] for p in data.get("papers", [])}

    added = 0
    skipped = 0
    for paper in new_papers:
        if paper["id"] in existing_ids:
            skipped += 1
        else:
            data["papers"].append(paper)
            existing_ids.add(paper["id"])
            added += 1

    if added > 0:
        save_papers(data, macp_dir)

    return added, skipped


# ---------------------------------------------------------------------------
# Main (for standalone testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("MACP Paper Fetcher - Standalone Test")
    print("=" * 60)

    # Test 1: Fetch by date
    print("\n[Test 1] Fetching papers for 2026-02-09...")
    papers = fetch_by_date("2026-02-09")
    print(f"  Found {len(papers)} papers")
    if papers:
        print(f"  First paper: {papers[0]['title'][:80]}...")

    # Test 2: Fetch by query
    print("\n[Test 2] Searching for 'memory augmented language model'...")
    papers = fetch_by_query("memory augmented language model", limit=3)
    print(f"  Found {len(papers)} papers")
    for p in papers:
        print(f"  - {p['title'][:80]}...")

    # Test 3: Fetch by ID
    print("\n[Test 3] Fetching arXiv:2602.06570...")
    paper = fetch_by_id("2602.06570")
    if paper:
        print(f"  Title: {paper['title'][:80]}...")
        print(f"  Authors: {', '.join(paper['authors'][:3])}...")

    print("\n" + "=" * 60)
    print("All tests complete.")
