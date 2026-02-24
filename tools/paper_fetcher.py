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
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, date
from typing import Optional

import jsonschema
import requests

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import httpx as _httpx
except ImportError:
    _httpx = None

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
HF_DAILY_PAPERS_API = "https://huggingface.co/api/daily_papers"
HF_PAPER_SEARCH_API = "https://huggingface.co/api/papers/search"
ARXIV_API = "http://export.arxiv.org/api/query"
HYSTS_DATASET_API = "https://datasets-server.huggingface.co"
HYSTS_DATASET_NAME = "hysts-bot-data/daily-papers"
MACP_DIR = ".macp"
PAPERS_FILE = os.path.join(MACP_DIR, "research_papers.json")
SCHEMAS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schemas")

# Input validation patterns
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ARXIV_ID_PATTERN = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
QUERY_MAX_LENGTH = 500

# ---------------------------------------------------------------------------
# Input Validation
# ---------------------------------------------------------------------------

def validate_date(date_str: str) -> str:
    """Validate and return a date string in YYYY-MM-DD format."""
    if not DATE_PATTERN.match(date_str):
        raise ValueError(f"Invalid date format: {date_str!r}. Expected YYYY-MM-DD.")
    # Verify it's a real date
    datetime.strptime(date_str, "%Y-%m-%d")
    return date_str


def validate_arxiv_id(arxiv_id: str) -> str:
    """Validate and return a clean arXiv ID."""
    arxiv_id = arxiv_id.strip()
    if not ARXIV_ID_PATTERN.match(arxiv_id):
        raise ValueError(f"Invalid arXiv ID: {arxiv_id!r}. Expected format: YYMM.NNNNN")
    return arxiv_id


def validate_query(query: str) -> str:
    """Validate and sanitize a search query string."""
    query = query.strip()
    if not query:
        raise ValueError("Search query cannot be empty.")
    if len(query) > QUERY_MAX_LENGTH:
        raise ValueError(f"Query exceeds {QUERY_MAX_LENGTH} characters.")
    # Strip control characters
    query = re.sub(r"[\x00-\x1f\x7f]", "", query)
    return query


# ---------------------------------------------------------------------------
# Schema Validation
# ---------------------------------------------------------------------------

_schema_cache: dict[str, dict] = {}


def _load_schema(schema_name: str) -> dict:
    """Load a JSON schema from the schemas/ directory (cached)."""
    if schema_name in _schema_cache:
        return _schema_cache[schema_name]
    schema_path = os.path.join(SCHEMAS_DIR, schema_name)
    if not os.path.exists(schema_path):
        print(f"[WARN] Schema not found: {schema_path}", file=sys.stderr)
        return {}
    with open(schema_path, "r") as f:
        schema = json.load(f)
    _schema_cache[schema_name] = schema
    return schema


def validate_json_data(data: dict, schema_name: str, strict: bool = True) -> bool:
    """
    Validate data against a JSON schema.

    Args:
        data: The data to validate.
        schema_name: Schema filename in schemas/ directory.
        strict: If True (default), raises ValidationError on failure.
                If False, logs a warning and returns False.

    Returns:
        True if valid. If strict=False, returns False on failure.

    Raises:
        jsonschema.ValidationError: If strict=True and validation fails.
    """
    from security_logger import log_validation_failure

    schema = _load_schema(schema_name)
    if not schema:
        return True  # No schema found, skip validation
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True
    except jsonschema.ValidationError as e:
        log_validation_failure(schema_name, e.message)
        if strict:
            raise
        print(f"[WARN] Schema validation failed ({schema_name}): {e.message}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Atomic File I/O
# ---------------------------------------------------------------------------

def atomic_write_json(filepath: str, data: dict) -> None:
    """Write JSON data atomically: write to temp file, then rename."""
    dir_name = os.path.dirname(filepath) or "."
    os.makedirs(dir_name, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp", prefix=".macp_")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, filepath)
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError as cleanup_err:
            print(f"[WARN] Failed to clean up temp file: {cleanup_err}", file=sys.stderr)
        raise


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
    target_date = validate_date(target_date)
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
    Search for papers using the Hugging Face Papers Search API (HTTP).

    This replaces the previous subprocess-based approach that shelled out to
    manus-mcp-cli, eliminating the command injection attack surface entirely.

    Args:
        query: Natural language search query (validated before use).
        limit: Maximum number of results.

    Returns:
        List of normalized paper dicts.
    """
    query = validate_query(query)
    limit = max(1, min(limit, 100))

    try:
        resp = requests.get(
            HF_PAPER_SEARCH_API,
            params={"query": query, "limit": limit},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[ERROR] HF Paper Search API request failed: {e}", file=sys.stderr)
        return []

    if not isinstance(data, list):
        print("[WARN] HF Paper Search returned unexpected format.", file=sys.stderr)
        return []

    papers = []
    for entry in data:
        arxiv_id = entry.get("id", "")
        title = entry.get("title", "Unknown Title")
        authors = [a.get("name", "") for a in entry.get("authors", [])]
        abstract = entry.get("summary", "")

        if arxiv_id:
            papers.append(normalize_paper(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                abstract=abstract,
                discovered_by=f"hf_search:{query[:50]}",
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
    arxiv_id = validate_arxiv_id(arxiv_id)
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
# Pipeline 4: hysts/daily-papers HuggingFace Dataset (12,700+ papers)
# ---------------------------------------------------------------------------

def fetch_from_hysts(query: str, limit: int = 10, offset: int = 0) -> list[dict]:
    """
    Search the hysts-bot-data/daily-papers dataset via the HuggingFace
    Datasets Server API. This dataset contains 12,700+ curated papers
    with abstracts, providing a reliable discovery source.

    Args:
        query: Natural language search query.
        limit: Maximum number of results.
        offset: Number of results to skip (for pagination).

    Returns:
        List of normalized paper dicts.
    """
    query = validate_query(query)
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    try:
        resp = requests.get(
            f"{HYSTS_DATASET_API}/search",
            params={
                "dataset": HYSTS_DATASET_NAME,
                "config": "default",
                "split": "train",
                "query": query,
                "offset": offset,
                "length": limit,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[ERROR] hysts dataset search failed: {e}", file=sys.stderr)
        return []

    rows = data.get("rows", [])
    papers = []
    for row in rows:
        record = row.get("row", {})
        arxiv_id = record.get("arxiv_id", "")
        title = record.get("title", "")
        authors = record.get("authors", [])
        abstract = record.get("abstract", "")
        github = record.get("github", "")
        pub_date = record.get("date", "")

        if not arxiv_id or not title:
            continue

        # Parse date from timestamp format
        discovered_date = None
        if pub_date:
            try:
                discovered_date = pub_date[:10]
            except (IndexError, TypeError):
                discovered_date = None  # Date parsing failed — non-critical

        extra = {}
        if github:
            extra["github_repo"] = github

        papers.append(normalize_paper(
            arxiv_id=arxiv_id,
            title=title,
            authors=authors if isinstance(authors, list) else [],
            abstract=abstract,
            discovered_by="hysts_dataset",
            discovered_date=discovered_date,
            extra=extra if extra else None,
        ))
    return papers


def fetch_hysts_by_date(target_date: str, limit: int = 50) -> list[dict]:
    """
    Fetch papers from the hysts dataset for a specific date using the
    filter endpoint.

    Args:
        target_date: Date string in YYYY-MM-DD format.
        limit: Maximum number of results.

    Returns:
        List of normalized paper dicts.
    """
    target_date = validate_date(target_date)
    limit = max(1, min(limit, 100))

    try:
        resp = requests.get(
            f"{HYSTS_DATASET_API}/filter",
            params={
                "dataset": HYSTS_DATASET_NAME,
                "config": "default",
                "split": "train",
                "where": f"date >= timestamp '{target_date} 00:00:00' AND date < timestamp '{target_date} 23:59:59'",
                "length": limit,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[ERROR] hysts dataset filter failed: {e}", file=sys.stderr)
        return []

    rows = data.get("rows", [])
    papers = []
    for row in rows:
        record = row.get("row", {})
        arxiv_id = record.get("arxiv_id", "")
        title = record.get("title", "")
        authors = record.get("authors", [])
        abstract = record.get("abstract", "")
        github = record.get("github", "")

        if not arxiv_id or not title:
            continue

        extra = {}
        if github:
            extra["github_repo"] = github

        papers.append(normalize_paper(
            arxiv_id=arxiv_id,
            title=title,
            authors=authors if isinstance(authors, list) else [],
            abstract=abstract,
            discovered_by="hysts_dataset",
            discovered_date=target_date,
            extra=extra if extra else None,
        ))
    return papers


# ---------------------------------------------------------------------------
# PDF Download & Text Extraction (Phase 3E — Deep Analysis)
# ---------------------------------------------------------------------------

ARXIV_PDF_URL = "https://arxiv.org/pdf/{arxiv_id}"
MAX_PDF_PAGES = 50
MAX_SECTION_BYTES = 100_000  # 100KB per section

# Common section headings in academic papers
_SECTION_HEADINGS = [
    "abstract", "introduction", "related work", "background",
    "method", "methodology", "approach", "model", "architecture",
    "experiments", "experimental setup", "evaluation",
    "results", "discussion", "analysis",
    "conclusion", "conclusions", "future work",
    "limitations", "acknowledgments", "acknowledgements", "references",
]

# Regex: line that looks like a section heading (numbered or unnumbered, title case or all caps)
_HEADING_RE = re.compile(
    r"^(?:\d+\.?\s+)?"  # optional numbering: "1. " or "3 "
    r"("
    + "|".join(re.escape(h) for h in _SECTION_HEADINGS)
    + r")"
    r"[\s:]*$",
    re.IGNORECASE,
)


def download_pdf(arxiv_id: str, dest_dir: str | None = None) -> str:
    """
    Download a PDF from arXiv.

    Args:
        arxiv_id: Validated arXiv identifier (e.g. "2602.06570").
        dest_dir: Directory to save the PDF. Defaults to system temp dir.

    Returns:
        Path to the downloaded PDF file.

    Raises:
        RuntimeError: If download fails.
        ImportError: If httpx is not available.
    """
    arxiv_id = validate_arxiv_id(arxiv_id)

    if _httpx is None:
        raise ImportError("httpx is required for PDF download. Install with: pip install httpx")

    url = ARXIV_PDF_URL.format(arxiv_id=arxiv_id)
    dest_dir = dest_dir or tempfile.gettempdir()
    os.makedirs(dest_dir, exist_ok=True)
    pdf_path = os.path.join(dest_dir, f"{arxiv_id.replace('/', '_')}.pdf")

    # Skip download if already cached
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
        return pdf_path

    try:
        with _httpx.Client(timeout=120, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            with open(pdf_path, "wb") as f:
                f.write(resp.content)
    except Exception as e:
        raise RuntimeError(f"Failed to download PDF for {arxiv_id}: {e}") from e

    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 1000:
        raise RuntimeError(f"Downloaded PDF for {arxiv_id} is too small or missing")

    return pdf_path


def extract_text(pdf_path: str) -> dict:
    """
    Extract structured text from a PDF using PyMuPDF.

    Args:
        pdf_path: Path to a PDF file.

    Returns:
        {
            "sections": [{"title": str, "content": str}],
            "full_text": str,
            "page_count": int
        }

    Raises:
        ImportError: If PyMuPDF (fitz) is not installed.
        RuntimeError: If extraction fails.
    """
    if fitz is None:
        raise ImportError("PyMuPDF is required for PDF extraction. Install with: pip install PyMuPDF")

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}") from e

    page_count = len(doc)
    if page_count > MAX_PDF_PAGES:
        print(f"[WARN] PDF has {page_count} pages, truncating to {MAX_PDF_PAGES}", file=sys.stderr)

    # Extract text from all pages (up to limit)
    all_text = []
    for page_num in range(min(page_count, MAX_PDF_PAGES)):
        page = doc[page_num]
        all_text.append(page.get_text("text"))
    doc.close()

    full_text = "\n".join(all_text)

    # Split into sections by detecting headings
    sections = _split_into_sections(full_text)

    return {
        "sections": sections,
        "full_text": full_text[:MAX_SECTION_BYTES * 10],  # cap total at ~1MB
        "page_count": page_count,
    }


def _split_into_sections(text: str) -> list[dict]:
    """Split extracted text into sections based on heading detection."""
    lines = text.split("\n")
    sections = []
    current_title = "Preamble"
    current_content = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_content.append("")
            continue

        match = _HEADING_RE.match(stripped)
        if match:
            # Save previous section
            content = "\n".join(current_content).strip()
            if content:
                sections.append({
                    "title": current_title,
                    "content": content[:MAX_SECTION_BYTES],
                })
            current_title = stripped.rstrip(":")
            current_content = []
        else:
            current_content.append(line)

    # Save final section
    content = "\n".join(current_content).strip()
    if content:
        sections.append({
            "title": current_title,
            "content": content[:MAX_SECTION_BYTES],
        })

    return sections


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


def save_papers(data: dict, macp_dir: str = MACP_DIR, force: bool = False) -> None:
    """Save the research_papers.json file with schema validation and atomic write.

    Args:
        data: Papers data to save.
        macp_dir: MACP directory path.
        force: If True, save even if schema validation fails.
    """
    filepath = os.path.join(macp_dir, "research_papers.json")
    try:
        validate_json_data(data, "research_papers_schema.json", strict=not force)
    except jsonschema.ValidationError as e:
        print(f"[ERROR] Schema validation blocked save: {e.message}", file=sys.stderr)
        print("  Use --force to bypass strict validation.", file=sys.stderr)
        return
    atomic_write_json(filepath, data)
    print(f"  Saved {len(data.get('papers', []))} papers to {filepath}")


def add_papers(new_papers: list[dict], macp_dir: str = MACP_DIR, force: bool = False) -> tuple[int, int]:
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
        save_papers(data, macp_dir, force=force)

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
