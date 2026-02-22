#!/usr/bin/env python3
"""
MACP Research Assistant - CLI Orchestrator
==========================================
The user-facing command-line interface for the MACP Research Assistant.
Provides commands for paper discovery, learning log management, citation
tracking, and knowledge recall.

Showcases the GODELAI C-S-P Framework:
  - Conflict (C): Multi-pipeline discovery surfaces discrepancies
  - Synthesis (S): Learning logs synthesize insights from papers
  - Propagation (P): Citations propagate knowledge into projects

Author: L (Godel), AI Agent & Project Founder
Date: February 10, 2026
"""

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, date

# Ensure the tools directory is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paper_fetcher import (
    fetch_by_date,
    fetch_by_date_range,
    fetch_by_query,
    fetch_by_id,
    fetch_from_hysts,
    fetch_hysts_by_date,
    load_papers,
    save_papers,
    add_papers,
    atomic_write_json,
    validate_json_data,
    validate_date,
    validate_arxiv_id,
    validate_query,
    MACP_DIR,
)
from llm_providers import (
    get_available_providers,
    select_provider,
    analyze_paper,
    PROVIDERS,
)
from risk_mitigation import check_for_sensitive_topics, warn_and_confirm

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LEARNING_LOG_FILE = os.path.join(MACP_DIR, "learning_log.json")
CITATIONS_FILE = os.path.join(MACP_DIR, "citations.json")
KNOWLEDGE_GRAPH_FILE = os.path.join(MACP_DIR, "knowledge_graph.json")
RESEARCH_DIR = os.path.join(MACP_DIR, "research")


# ---------------------------------------------------------------------------
# Knowledge Tree: Auto-create research directories
# ---------------------------------------------------------------------------

def slugify(title: str, max_length: int = 60) -> str:
    """Convert a paper title to a clean directory slug."""
    # Lowercase and strip
    slug = title.lower().strip()
    # Remove common prefixes/suffixes
    for prefix in ["a ", "an ", "the "]:
        if slug.startswith(prefix):
            slug = slug[len(prefix):]
    # Replace non-alphanumeric with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    # Truncate to max_length at a word boundary
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit("-", 1)[0]
    return slug or "untitled"


def get_research_dir(paper: dict) -> str:
    """Get or create the research directory for a paper."""
    title = paper.get("title", "Untitled")
    slug = slugify(title)
    research_path = os.path.join(RESEARCH_DIR, slug)
    os.makedirs(research_path, exist_ok=True)
    return research_path


def save_to_research_tree(paper: dict, analysis: dict = None, session: dict = None) -> str:
    """
    Save paper data to its research directory in the knowledge tree.
    Creates/updates: paper.json, analysis.json, README.md

    Returns the research directory path.
    """
    research_path = get_research_dir(paper)

    # Save paper metadata
    paper_file = os.path.join(research_path, "paper.json")
    atomic_write_json(paper_file, paper)

    # Save analysis if provided
    if analysis:
        analysis_file = os.path.join(research_path, "analysis.json")
        existing = {}
        if os.path.exists(analysis_file):
            with open(analysis_file, "r") as f:
                existing = json.load(f)
        # Merge: keep history of analyses
        analyses = existing.get("analyses", [])
        analysis_record = {
            "timestamp": datetime.now().isoformat(),
            "result": analysis,
        }
        if session:
            analysis_record["session_id"] = session.get("session_id")
            analysis_record["agent"] = session.get("agent")
        analyses.append(analysis_record)
        atomic_write_json(analysis_file, {"paper_id": paper["id"], "analyses": analyses})

    # Generate/update README.md for this research node
    _update_research_readme(research_path, paper, analysis, session)

    return research_path


def _update_research_readme(research_path: str, paper: dict, analysis: dict = None, session: dict = None):
    """Generate a README.md for the research directory."""
    lines = []
    lines.append(f"# {paper.get('title', 'Untitled')}")
    lines.append("")
    lines.append(f"**arXiv ID:** `{paper.get('id', 'N/A')}`")
    if paper.get("url"):
        lines.append(f"**URL:** {paper['url']}")
    lines.append(f"**Status:** {paper.get('status', 'unknown')}")
    lines.append(f"**Discovered:** {paper.get('discovered_date', 'N/A')}")
    lines.append("")

    authors = paper.get("authors", [])
    if authors:
        lines.append("## Authors")
        lines.append("")
        lines.append(f"{', '.join(authors)}")
        lines.append("")

    abstract = paper.get("abstract", "")
    if abstract:
        lines.append("## Abstract")
        lines.append("")
        lines.append(f"{abstract}")
        lines.append("")

    insights = paper.get("insights", [])
    if insights:
        lines.append("## Key Insights")
        lines.append("")
        for insight in insights:
            if isinstance(insight, str):
                lines.append(f"- {insight}")
        lines.append("")

    if analysis:
        lines.append("## Analysis")
        lines.append("")
        if analysis.get("summary"):
            lines.append(f"**Summary:** {analysis['summary']}")
            lines.append("")
        if analysis.get("methodology"):
            lines.append(f"**Methodology:** {analysis['methodology']}")
            lines.append("")
        if analysis.get("strength_score"):
            lines.append(f"**Strength Score:** {analysis['strength_score']}/10")
            lines.append("")
        gaps = analysis.get("research_gaps", [])
        if gaps:
            lines.append("### Research Gaps")
            lines.append("")
            for gap in gaps:
                lines.append(f"- {gap}")
            lines.append("")
        tags = analysis.get("relevance_tags", [])
        if tags:
            lines.append(f"**Tags:** {', '.join(tags)}")
            lines.append("")

    if session:
        lines.append("## Provenance")
        lines.append("")
        lines.append(f"- **Session:** `{session.get('session_id', 'N/A')}`")
        lines.append(f"- **Agent:** {session.get('agent', 'N/A')}")
        lines.append(f"- **Date:** {session.get('date', 'N/A')}")
        lines.append("")

    # List files in directory
    lines.append("## Files")
    lines.append("")
    for f in sorted(os.listdir(research_path)):
        if f != "README.md":
            lines.append(f"- `{f}`")
    lines.append("")
    lines.append("---")
    lines.append("*Part of MACP Research Knowledge Tree*")

    readme_path = os.path.join(research_path, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

# ---------------------------------------------------------------------------
# Input Sanitization
# ---------------------------------------------------------------------------

# Max lengths for free-text inputs
MAX_SUMMARY_LENGTH = 2000
MAX_CONTEXT_LENGTH = 2000
MAX_PROJECT_LENGTH = 200
MAX_TAG_LENGTH = 50


def sanitize_text(text: str, max_length: int, field_name: str) -> str:
    """Sanitize a free-text input: strip control chars, enforce length."""
    text = text.strip()
    # Strip control characters (keep newlines and tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    if len(text) > max_length:
        print(f"[WARN] {field_name} truncated to {max_length} chars.", file=sys.stderr)
        text = text[:max_length]
    if not text:
        raise ValueError(f"{field_name} cannot be empty after sanitization.")
    return text


def sanitize_tags(tags_str: str) -> list[str]:
    """Sanitize a comma-separated tags string."""
    tags = []
    for tag in tags_str.split(","):
        tag = tag.strip().lower()
        # Only allow alphanumeric, hyphens, underscores
        tag = re.sub(r"[^a-z0-9_\-]", "", tag)
        if tag and len(tag) <= MAX_TAG_LENGTH:
            tags.append(tag)
    return tags


# ---------------------------------------------------------------------------
# Learning Log Operations
# ---------------------------------------------------------------------------

def load_learning_log() -> dict:
    """Load the current learning_log.json file."""
    if not os.path.exists(LEARNING_LOG_FILE):
        return {"learning_sessions": []}
    with open(LEARNING_LOG_FILE, "r") as f:
        return json.load(f)


def save_learning_log(data: dict, force: bool = False) -> None:
    """Save the learning_log.json file with strict schema validation and atomic write."""
    try:
        validate_json_data(data, "learning_log_schema.json", strict=not force)
    except Exception as e:
        print(f"[ERROR] Schema validation blocked save: {e}", file=sys.stderr)
        print("  Use --force to bypass strict validation.", file=sys.stderr)
        return
    atomic_write_json(LEARNING_LOG_FILE, data)


# ---------------------------------------------------------------------------
# Citation Operations
# ---------------------------------------------------------------------------

def load_citations() -> dict:
    """Load the current citations.json file."""
    if not os.path.exists(CITATIONS_FILE):
        return {"citations": []}
    with open(CITATIONS_FILE, "r") as f:
        return json.load(f)


def save_citations(data: dict, force: bool = False) -> None:
    """Save the citations.json file with strict schema validation and atomic write."""
    try:
        validate_json_data(data, "citations_schema.json", strict=not force)
    except Exception as e:
        print(f"[ERROR] Schema validation blocked save: {e}", file=sys.stderr)
        print("  Use --force to bypass strict validation.", file=sys.stderr)
        return
    atomic_write_json(CITATIONS_FILE, data)


# ---------------------------------------------------------------------------
# Command: discover
# ---------------------------------------------------------------------------

def cmd_discover(args):
    """Discover new papers and add them to the MACP knowledge base."""
    print("=" * 60)
    print("MACP Research Assistant - DISCOVER")
    print("  C-S-P Phase: CONFLICT (multi-pipeline discovery)")
    print("=" * 60)

    all_papers = []

    # Validate inputs before any API calls
    try:
        # Pipeline 1: Date-based discovery
        if args.date:
            validated_date = validate_date(args.date)
            print(f"\n[Pipeline 1: HF Daily Papers] Date: {validated_date}")
            papers = fetch_by_date(validated_date)
            print(f"  Found {len(papers)} papers from HF Daily Papers")
            all_papers.extend(papers)

        if args.date_range:
            parts = args.date_range.split(":")
            if len(parts) != 2:
                print("[ERROR] --date-range must be YYYY-MM-DD:YYYY-MM-DD", file=sys.stderr)
                return
            start, end = validate_date(parts[0]), validate_date(parts[1])
            print(f"\n[Pipeline 1: HF Daily Papers] Range: {start} to {end}")
            papers = fetch_by_date_range(start, end)
            print(f"  Found {len(papers)} papers from HF Daily Papers")
            all_papers.extend(papers)

        # Pipeline 2: Query-based discovery
        if args.query:
            validated_query = validate_query(args.query)
            limit = max(1, min(args.limit or 10, 100))
            print(f"\n[Pipeline 2: HF Paper Search] Query: '{validated_query}' (limit: {limit})")
            papers = fetch_by_query(validated_query, limit=limit)
            print(f"  Found {len(papers)} papers from HF Search")
            all_papers.extend(papers)

        # Pipeline 3: Direct ID fetch
        if args.arxiv_id:
            validated_id = validate_arxiv_id(args.arxiv_id)
            print(f"\n[Pipeline 3: arXiv API] ID: {validated_id}")
            paper = fetch_by_id(validated_id)
            if paper:
                print(f"  Found: {paper['title'][:70]}...")
                all_papers.append(paper)
            else:
                print("  Paper not found.")

        # Pipeline 4: hysts/daily-papers dataset (12,700+ curated papers)
        if args.hysts:
            validated_query = validate_query(args.hysts)
            limit = max(1, min(args.limit or 10, 100))
            print(f"\n[Pipeline 4: hysts Dataset] Query: '{validated_query}' (limit: {limit})")
            papers = fetch_from_hysts(validated_query, limit=limit)
            print(f"  Found {len(papers)} papers from hysts/daily-papers")
            all_papers.extend(papers)

        if args.hysts_date:
            validated_date = validate_date(args.hysts_date)
            print(f"\n[Pipeline 4: hysts Dataset] Date: {validated_date}")
            papers = fetch_hysts_by_date(validated_date)
            print(f"  Found {len(papers)} papers from hysts/daily-papers")
            all_papers.extend(papers)
    except ValueError as e:
        print(f"[ERROR] Input validation failed: {e}", file=sys.stderr)
        return

    if not all_papers:
        print("\n[!] No papers discovered. Use --date, --query, or --arxiv-id.")
        return

    # Conflict Detection: Check for duplicates across pipelines
    seen_ids = {}
    conflicts = []
    for p in all_papers:
        pid = p["id"]
        if pid in seen_ids:
            conflicts.append(pid)
        else:
            seen_ids[pid] = p

    if conflicts:
        print(f"\n[C-S-P CONFLICT] {len(conflicts)} paper(s) found by multiple pipelines:")
        for cid in conflicts:
            print(f"  - {cid}: {seen_ids[cid]['title'][:60]}...")
        print("  This cross-validation strengthens discovery confidence.")

    # Add to MACP storage
    force = getattr(args, "force", False)
    print(f"\n[MACP Storage] Adding {len(all_papers)} papers to research_papers.json...")
    added, skipped = add_papers(all_papers, force=force)
    print(f"  Added: {added} | Skipped (duplicates): {skipped}")

    # Create research tree nodes for discovered papers
    for p in list(seen_ids.values()):
        save_to_research_tree(p)

    # Summary
    total = load_papers()
    print(f"\n[Summary] Total papers in knowledge base: {len(total.get('papers', []))}")
    print(f"  Research tree: {RESEARCH_DIR}/")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Command: analyze
# ---------------------------------------------------------------------------

def cmd_analyze(args):
    """Send a paper to an LLM for AI-powered analysis and insight extraction."""
    print("=" * 60)
    print("MACP Research Assistant - ANALYZE")
    print("  C-S-P Phase: SYNTHESIS (AI-powered deep analysis)")
    print("=" * 60)

    # --- Resolve the paper ---
    paper_id = args.arxiv_id.strip()
    if not paper_id.startswith("arxiv:"):
        paper_id = f"arxiv:{paper_id}"

    papers_data = load_papers()
    paper = None
    for p in papers_data.get("papers", []):
        if p["id"] == paper_id:
            paper = p
            break

    if not paper:
        print(f"\n[!] Paper {paper_id} not in knowledge base.")
        print("  Fetching from arXiv...")
        try:
            raw_id = paper_id.replace("arxiv:", "")
            validate_arxiv_id(raw_id)
            from paper_fetcher import fetch_by_id as _fetch
            paper = _fetch(raw_id)
            if paper:
                add_papers([paper])
                print(f"  Added: {paper['title'][:70]}...")
            else:
                print(f"  [ERROR] Could not fetch paper {raw_id} from arXiv.", file=sys.stderr)
                return
        except ValueError as e:
            print(f"  [ERROR] {e}", file=sys.stderr)
            return

    title = paper.get("title", "Unknown")
    abstract = paper.get("abstract", "")
    authors = paper.get("authors", [])

    if not abstract:
        print("\n[WARN] Paper has no abstract. Analysis quality will be limited.")

    # --- C4: Dual-use risk check ---
    sensitive_text = f"{title} {abstract}"
    matched_keywords = check_for_sensitive_topics(sensitive_text)
    if matched_keywords:
        if not warn_and_confirm(paper_id, matched_keywords):
            print("  Analysis aborted by user.")
            return

    # --- Select provider ---
    print(f"\n[Paper] {title[:70]}...")
    print(f"  ID: {paper_id}")
    print(f"  Authors: {', '.join(authors[:3])}" + ("..." if len(authors) > 3 else ""))

    available = get_available_providers()
    configured = [p for p in available if p["configured"]]

    if not configured:
        print("\n[ERROR] No LLM providers configured.", file=sys.stderr)
        print("  Set one of these environment variables:", file=sys.stderr)
        for p in available:
            env = PROVIDERS[p["id"]]["env_key"]
            tier = "(FREE tier)" if p["free_tier"] else "(paid)"
            print(f"    export {env}=your-key-here  # {p['name']} {tier}", file=sys.stderr)
        return

    provider_id = select_provider(args.provider)
    if not provider_id:
        print("\n[ERROR] Could not select a provider.", file=sys.stderr)
        return

    provider_info = PROVIDERS[provider_id]

    # --- Consent check ---
    if not args.yes:
        print(f"\n[CONSENT] About to send paper data to: {provider_info['name']}")
        print(f"  Model: {provider_info['model']}")
        print(f"  Free tier: {'Yes' if provider_info['free_tier'] else 'No (costs may apply)'}")
        print(f"  Data sent: title, authors, abstract ({len(abstract)} chars)")
        print()
        try:
            confirm = input("  Proceed? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            confirm = "n"
        if confirm != "y":
            print("  Aborted by user.")
            return

    # --- Call LLM ---
    print(f"\n[Analyzing] Sending to {provider_info['name']} ({provider_info['model']})...")

    analysis = analyze_paper(
        title=title,
        authors=authors,
        abstract=abstract,
        provider_id=provider_id,
    )

    if not analysis:
        print("[ERROR] Analysis failed. See errors above.", file=sys.stderr)
        return

    # --- Display results ---
    print("\n--- Analysis Results ---")
    print(f"  Summary: {analysis.get('summary', 'N/A')}")

    insights = analysis.get("key_insights", [])
    if insights:
        print("\n  Key Insights:")
        for i, insight in enumerate(insights, 1):
            print(f"    {i}. {insight}")

    methodology = analysis.get("methodology", "")
    if methodology:
        print(f"\n  Methodology: {methodology}")

    gaps = analysis.get("research_gaps", [])
    if gaps:
        print("\n  Research Gaps:")
        for gap in gaps:
            print(f"    - {gap}")

    tags = analysis.get("relevance_tags", [])
    score = analysis.get("strength_score", "N/A")
    print(f"\n  Strength Score: {score}/10")
    if tags:
        print(f"  Tags: {', '.join(tags)}")

    # --- Auto-create learning session ---
    summary_text = analysis.get("summary", title)
    insight_text = "; ".join(insights[:3]) if insights else summary_text

    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    session = {
        "session_id": session_id,
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat(),
        "summary": summary_text,
        "key_insight": insight_text,
        "papers": [paper_id],
        "agent": f"{provider_info['name'].lower().replace(' ', '_')}:{provider_info['model']}",
        "tags": [sanitize_tags(t)[0] if sanitize_tags(t) else t for t in tags] if tags else [],
        "analysis": {
            "provider": provider_id,
            "model": provider_info["model"],
            "methodology": methodology,
            "research_gaps": gaps,
            "strength_score": score,
        },
    }

    force = getattr(args, "force", False)
    log = load_learning_log()
    log.setdefault("learning_sessions", []).append(session)
    save_learning_log(log, force=force)

    # Update paper status + insights
    for p in papers_data.get("papers", []):
        if p["id"] == paper_id:
            p["status"] = "analyzed"
            existing_insights = p.get("insights", [])
            for insight in insights:
                if insight not in existing_insights:
                    existing_insights.append(insight)
            p["insights"] = existing_insights
            break
    save_papers(papers_data, force=force)

    # --- Save to knowledge tree ---
    research_path = save_to_research_tree(paper, analysis=analysis, session=session)

    print(f"\n[MACP] Learning session created: {session_id}")
    print("  Paper status updated to: analyzed")
    print(f"  Research tree: {research_path}")
    total = len(log.get("learning_sessions", []))
    print(f"  Total learning sessions: {total}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Command: handoff
# ---------------------------------------------------------------------------

HANDOFFS_FILE = os.path.join(MACP_DIR, "handoffs.json")


def load_handoffs() -> dict:
    """Load the current handoffs.json file."""
    if not os.path.exists(HANDOFFS_FILE):
        return {"handoffs": []}
    with open(HANDOFFS_FILE, "r") as f:
        return json.load(f)


def save_handoffs(data: dict, force: bool = False) -> None:
    """Save the handoffs.json file with strict schema validation and atomic write."""
    try:
        validate_json_data(data, "handoffs_schema.json", strict=not force)
    except Exception as e:
        print(f"[ERROR] Schema validation blocked save: {e}", file=sys.stderr)
        print("  Use --force to bypass strict validation.", file=sys.stderr)
        return
    atomic_write_json(HANDOFFS_FILE, data)


def cmd_handoff(args):
    """Create a structured research handoff between agents."""
    print("=" * 60)
    print("MACP Research Assistant - HANDOFF")
    print("  Proto-A2A: Structured multi-agent research handoff")
    print("=" * 60)

    # Sanitize inputs
    try:
        from_agent = sanitize_text(args.from_agent, MAX_PROJECT_LENGTH, "From agent")
        to_agent = sanitize_text(args.to_agent, MAX_PROJECT_LENGTH, "To agent")
        summary = sanitize_text(args.summary, MAX_SUMMARY_LENGTH, "Summary")
    except ValueError as e:
        print(f"[ERROR] Input validation failed: {e}", file=sys.stderr)
        return

    # Parse completed/pending items
    completed = [c.strip() for c in args.completed.split(";") if c.strip()] if args.completed else []
    pending = [p.strip() for p in args.pending.split(";") if p.strip()] if args.pending else []

    # Parse paper IDs
    paper_ids = []
    if args.papers:
        for pid in args.papers.split(","):
            pid = pid.strip()
            if not pid.startswith("arxiv:"):
                pid = f"arxiv:{pid}"
            paper_ids.append(pid)

    # Build knowledge state snapshot
    papers_data = load_papers()
    log = load_learning_log()
    citations_data = load_citations()
    knowledge_state = {
        "total_papers": len(papers_data.get("papers", [])),
        "total_sessions": len(log.get("learning_sessions", [])),
        "total_citations": len(citations_data.get("citations", [])),
    }

    # Create handoff record
    handoff_id = f"handoff_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    handoff = {
        "handoff_id": handoff_id,
        "timestamp": datetime.now().isoformat(),
        "from_agent": from_agent,
        "to_agent": to_agent,
        "task_summary": summary,
        "completed": completed,
        "pending": pending,
        "papers": paper_ids,
        "knowledge_state": knowledge_state,
    }

    force = getattr(args, "force", False)
    handoffs_data = load_handoffs()
    handoffs_data["handoffs"].append(handoff)
    save_handoffs(handoffs_data, force=force)

    # Display handoff
    print(f"\n[HANDOFF] {handoff_id}")
    print(f"  From: {from_agent}")
    print(f"  To:   {to_agent}")
    print(f"  Summary: {summary[:80]}...")
    if completed:
        print("\n  Completed:")
        for c in completed:
            print(f"    - {c}")
    if pending:
        print("\n  Pending:")
        for p in pending:
            print(f"    - {p}")
    if paper_ids:
        print(f"\n  Papers: {', '.join(paper_ids)}")
    print("\n  Knowledge Base State:")
    print(f"    Papers: {knowledge_state['total_papers']}")
    print(f"    Learning Sessions: {knowledge_state['total_sessions']}")
    print(f"    Citations: {knowledge_state['total_citations']}")
    print(f"\n[MACP] Handoff recorded ({len(handoffs_data['handoffs'])} total)")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Command: learn
# ---------------------------------------------------------------------------

def cmd_learn(args):
    """Record a learning insight linked to specific papers."""
    print("=" * 60)
    print("MACP Research Assistant - LEARN")
    print("  C-S-P Phase: SYNTHESIS (distilling insights)")
    print("=" * 60)

    # Sanitize inputs
    try:
        summary = sanitize_text(args.summary, MAX_SUMMARY_LENGTH, "Summary")
        insight = sanitize_text(args.insight, MAX_SUMMARY_LENGTH, "Insight") if args.insight else summary
        agent = sanitize_text(args.agent or "human", MAX_PROJECT_LENGTH, "Agent")
        tags = sanitize_tags(args.tags) if args.tags else []
    except ValueError as e:
        print(f"[ERROR] Input validation failed: {e}", file=sys.stderr)
        return

    # Validate paper IDs
    paper_ids = []
    for pid in args.papers.split(","):
        pid = pid.strip()
        if not pid.startswith("arxiv:"):
            pid = f"arxiv:{pid}"
        paper_ids.append(pid)

    papers_data = load_papers()
    existing_ids = {p["id"] for p in papers_data.get("papers", [])}

    missing = [pid for pid in paper_ids if pid not in existing_ids]
    if missing:
        print(f"\n[WARN] These paper IDs are not in the knowledge base: {missing}")
        print("  Run 'macp discover' first to add them.")
        if not args.force:
            print("  Use --force to add the learning entry anyway.")
            return
        print("  --force flag set, proceeding anyway.")

    # Create learning session
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    session = {
        "session_id": session_id,
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "key_insight": insight,
        "papers": paper_ids,
        "agent": agent,
        "tags": tags,
    }

    # Save to learning log
    force = getattr(args, "force", False)
    log = load_learning_log()
    key = "learning_sessions" if "learning_sessions" in log else "sessions"
    log.setdefault(key, []).append(session)
    save_learning_log(log, force=force)

    # Update paper status to "analyzed"
    for paper in papers_data.get("papers", []):
        if paper["id"] in paper_ids:
            paper["status"] = "analyzed"
            if args.summary not in paper.get("insights", []):
                paper.setdefault("insights", []).append(args.summary)
    save_papers(papers_data, force=force)

    print(f"\n[SYNTHESIS] Learning session created: {session_id}")
    print(f"  Summary: {args.summary[:80]}...")
    print(f"  Papers: {', '.join(paper_ids)}")
    print(f"  Agent: {session.get('agent', 'human')}")
    total_sessions = len(log.get('learning_sessions', log.get('sessions', [])))
    print(f"\n[MACP] Learning log updated ({total_sessions} total sessions)")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Command: cite
# ---------------------------------------------------------------------------

def cmd_cite(args):
    """Record a citation linking a paper to a project or document."""
    print("=" * 60)
    print("MACP Research Assistant - CITE")
    print("  C-S-P Phase: PROPAGATION (applying knowledge)")
    print("=" * 60)

    # Sanitize inputs
    try:
        arxiv_id = args.arxiv_id.strip()
        paper_id = f"arxiv:{arxiv_id}" if not arxiv_id.startswith("arxiv:") else arxiv_id
        project = sanitize_text(args.project, MAX_PROJECT_LENGTH, "Project")
        context = sanitize_text(args.context, MAX_CONTEXT_LENGTH, "Context")
        agent = sanitize_text(args.agent or "human", MAX_PROJECT_LENGTH, "Agent")
    except ValueError as e:
        print(f"[ERROR] Input validation failed: {e}", file=sys.stderr)
        return

    citation = {
        "citation_id": f"cite_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "paper_id": paper_id,
        "cited_in": project,
        "context": context,
        "date": date.today().isoformat(),
        "cited_by": agent,
    }

    force = getattr(args, "force", False)
    citations_data = load_citations()
    citations_data["citations"].append(citation)
    save_citations(citations_data, force=force)

    # Update paper status to "cited"
    papers_data = load_papers()
    for paper in papers_data.get("papers", []):
        if paper["id"] == paper_id:
            paper["status"] = "cited"
    save_papers(papers_data, force=force)

    print(f"\n[PROPAGATION] Citation recorded: {citation['citation_id']}")
    print(f"  Paper: {paper_id}")
    print(f"  Cited in: {args.project}")
    print(f"  Context: {args.context[:80]}...")
    print(f"\n[MACP] Citations file updated ({len(citations_data['citations'])} total citations)")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Command: recall
# ---------------------------------------------------------------------------

def _score_text(query_terms: set, text: str) -> int:
    """Score a text against query terms. Returns number of matching terms."""
    text_lower = text.lower()
    return sum(1 for term in query_terms if term in text_lower)


def cmd_recall(args):
    """Recall knowledge from the MACP knowledge base with enriched search."""
    print("=" * 60)
    print("MACP Research Assistant - RECALL")
    print("  'What have I learned?'")
    print("=" * 60)

    query = args.question.lower()
    query_terms = set(query.split())

    # Search across papers (title, abstract, insights)
    papers_data = load_papers()
    paper_matches = []
    for paper in papers_data.get("papers", []):
        score = 0
        score += _score_text(query_terms, paper.get("title", ""))
        score += _score_text(query_terms, paper.get("abstract", ""))
        # Search through insights
        for insight in paper.get("insights", []):
            if isinstance(insight, str):
                score += _score_text(query_terms, insight)
        if score > 0:
            paper_matches.append((score, paper))

    paper_matches.sort(key=lambda x: x[0], reverse=True)

    # Search across learning sessions (summary, key_insight, tags, analysis fields)
    log = load_learning_log()
    session_matches = []
    for session in log.get("learning_sessions", log.get("sessions", [])):
        score = 0
        score += _score_text(query_terms, session.get("summary", ""))
        score += _score_text(query_terms, session.get("key_insight", ""))
        # Search tags
        for tag in session.get("tags", []):
            score += _score_text(query_terms, tag)
        # Search analysis fields
        analysis = session.get("analysis", {})
        if analysis:
            score += _score_text(query_terms, analysis.get("methodology", ""))
            for gap in analysis.get("research_gaps", []):
                score += _score_text(query_terms, gap)
        if score > 0:
            session_matches.append((score, session))

    session_matches.sort(key=lambda x: x[0], reverse=True)

    # Search across citations (context, project)
    citations_data = load_citations()
    citation_matches = []
    for cite in citations_data.get("citations", []):
        score = 0
        score += _score_text(query_terms, cite.get("context", ""))
        score += _score_text(query_terms, cite.get("cited_in", ""))
        if score > 0:
            citation_matches.append((score, cite))

    citation_matches.sort(key=lambda x: x[0], reverse=True)

    # Search across handoffs (summary, completed, pending)
    handoffs_data = load_handoffs()
    handoff_matches = []
    for ho in handoffs_data.get("handoffs", []):
        score = 0
        score += _score_text(query_terms, ho.get("task_summary", ""))
        for item in ho.get("completed", []):
            score += _score_text(query_terms, item)
        for item in ho.get("pending", []):
            score += _score_text(query_terms, item)
        if score > 0:
            handoff_matches.append((score, ho))

    handoff_matches.sort(key=lambda x: x[0], reverse=True)

    # Present results
    limit = args.limit or 5

    if not paper_matches and not session_matches and not citation_matches and not handoff_matches:
        print(f"\n[RECALL] No results found for: '{args.question}'")
        print("  Try broader terms or discover more papers first.")
        return

    if paper_matches:
        print(f"\n--- Relevant Papers ({min(len(paper_matches), limit)} of {len(paper_matches)}) ---")
        for score, paper in paper_matches[:limit]:
            status_icon = {"discovered": "d", "analyzed": "a", "cited": "c"}.get(paper.get("status"), "?")
            print(f"  [{status_icon}] [{paper['id']}] {paper['title'][:70]}...")
            if paper.get("insights"):
                for insight in paper["insights"][:2]:
                    if isinstance(insight, str):
                        print(f"     > Insight: {insight[:60]}...")

    if session_matches:
        print(f"\n--- Learning Sessions ({min(len(session_matches), limit)} of {len(session_matches)}) ---")
        for score, session in session_matches[:limit]:
            print(f"  [s] [{session['session_id']}] {session['date']}")
            print(f"     Summary: {session['summary'][:70]}...")
            if session.get("tags"):
                print(f"     Tags: {', '.join(session['tags'])}")
            analysis = session.get("analysis", {})
            if analysis and analysis.get("strength_score"):
                print(f"     Score: {analysis['strength_score']}/10")
            print(f"     Papers: {', '.join(session.get('papers', []))}")

    if citation_matches:
        print(f"\n--- Citations ({min(len(citation_matches), limit)} of {len(citation_matches)}) ---")
        for score, cite in citation_matches[:limit]:
            print(f"  [c] [{cite['citation_id']}] in {cite['cited_in']}")
            print(f"     Context: {cite['context'][:70]}...")

    if handoff_matches:
        print(f"\n--- Handoffs ({min(len(handoff_matches), limit)} of {len(handoff_matches)}) ---")
        for score, ho in handoff_matches[:limit]:
            print(f"  [h] [{ho['handoff_id']}] {ho['from_agent']} -> {ho['to_agent']}")
            print(f"     Summary: {ho['task_summary'][:70]}...")

    total_results = len(paper_matches) + len(session_matches) + len(citation_matches) + len(handoff_matches)
    print(f"\n[RECALL] Total matches: {total_results} (papers: {len(paper_matches)}, "
          f"sessions: {len(session_matches)}, citations: {len(citation_matches)}, "
          f"handoffs: {len(handoff_matches)})")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Command: export
# ---------------------------------------------------------------------------

EXPORTS_DIR = os.path.join(MACP_DIR, "exports")


def cmd_export(args):
    """Export the MACP knowledge base to a Markdown research report."""
    print("=" * 60)
    print("MACP Research Assistant - EXPORT")
    print("  Generating Markdown research report")
    print("=" * 60)

    papers_data = load_papers()
    log = load_learning_log()
    citations_data = load_citations()
    handoffs_data = load_handoffs()

    paper_list = papers_data.get("papers", [])
    session_list = log.get("learning_sessions", [])
    citation_list = citations_data.get("citations", [])
    handoff_list = handoffs_data.get("handoffs", [])

    # Filter by tag if specified
    if args.tag:
        tag = args.tag.lower()
        filtered_sessions = [
            s for s in session_list if tag in [t.lower() for t in s.get("tags", [])]
        ]
        # Find papers linked from filtered sessions
        linked_paper_ids = set()
        for s in filtered_sessions:
            linked_paper_ids.update(s.get("papers", []))
        filtered_papers = [p for p in paper_list if p["id"] in linked_paper_ids]
        filtered_citations = [c for c in citation_list if c["paper_id"] in linked_paper_ids]
        paper_list = filtered_papers
        session_list = filtered_sessions
        citation_list = filtered_citations

    # Build report
    now = datetime.now()
    lines = []
    lines.append("# MACP Research Report")
    lines.append("")
    if args.tag:
        lines.append(f"**Filter:** tag = `{args.tag}`")
    lines.append(f"**Generated:** {now.strftime('%Y-%m-%d %H:%M')}")
    lines.append("**Agent:** RNA (Claude Code)")
    lines.append("**Protocol:** MACP v2.0 / GODELAI C-S-P Framework")
    lines.append("")

    # --- Summary ---
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Papers | {len(paper_list)} |")
    lines.append(f"| Learning Sessions | {len(session_list)} |")
    lines.append(f"| Citations | {len(citation_list)} |")
    lines.append(f"| Handoffs | {len(handoff_list)} |")
    lines.append("")

    # --- Papers ---
    if paper_list:
        lines.append("## Papers")
        lines.append("")
        for paper in sorted(paper_list, key=lambda p: p.get("discovered_date", ""), reverse=True):
            status = paper.get("status", "unknown")
            lines.append(f"### {paper['title']}")
            lines.append("")
            lines.append(f"- **ID:** `{paper['id']}`")
            lines.append(f"- **Authors:** {', '.join(paper.get('authors', ['Unknown']))}")
            if paper.get("url"):
                lines.append(f"- **URL:** {paper['url']}")
            lines.append(f"- **Status:** {status}")
            lines.append(f"- **Discovered:** {paper.get('discovered_date', 'N/A')}")
            if paper.get("abstract"):
                abstract = paper["abstract"]
                if len(abstract) > 300:
                    abstract = abstract[:300] + "..."
                lines.append("")
                lines.append(f"> {abstract}")
            if paper.get("insights"):
                lines.append("")
                lines.append("**Key Insights:**")
                for insight in paper["insights"]:
                    if isinstance(insight, str):
                        lines.append(f"- {insight}")
            lines.append("")

    # --- Learning Sessions ---
    if session_list:
        lines.append("## Learning Sessions")
        lines.append("")
        for session in sorted(session_list, key=lambda s: s.get("date", ""), reverse=True):
            lines.append(f"### Session: {session['session_id']}")
            lines.append("")
            lines.append(f"- **Date:** {session.get('date', 'N/A')}")
            lines.append(f"- **Agent:** {session.get('agent', 'N/A')}")
            if session.get("tags"):
                lines.append(f"- **Tags:** {', '.join(session['tags'])}")
            if session.get("papers"):
                lines.append(f"- **Papers:** {', '.join(session['papers'])}")
            lines.append("")
            lines.append(f"**Summary:** {session.get('summary', 'N/A')}")
            if session.get("key_insight"):
                lines.append("")
                lines.append(f"**Key Insight:** {session['key_insight']}")

            # Analysis details
            analysis = session.get("analysis", {})
            if analysis:
                lines.append("")
                lines.append("**Analysis Details:**")
                if analysis.get("provider"):
                    lines.append(f"- Provider: {analysis['provider']} ({analysis.get('model', 'N/A')})")
                if analysis.get("methodology"):
                    lines.append(f"- Methodology: {analysis['methodology']}")
                if analysis.get("strength_score"):
                    lines.append(f"- Strength Score: {analysis['strength_score']}/10")
                if analysis.get("research_gaps"):
                    lines.append("- Research Gaps:")
                    for gap in analysis["research_gaps"]:
                        lines.append(f"  - {gap}")
            lines.append("")

    # --- Citations ---
    if citation_list:
        lines.append("## Citations")
        lines.append("")
        lines.append("| Paper | Project | Context | Agent | Date |")
        lines.append("|-------|---------|---------|-------|------|")
        for cite in citation_list:
            context = cite.get("context", "")
            if len(context) > 60:
                context = context[:60] + "..."
            lines.append(f"| `{cite['paper_id']}` | {cite['cited_in']} | {context} | {cite.get('cited_by', 'N/A')} | {cite['date']} |")
        lines.append("")

    # --- Handoffs ---
    if handoff_list:
        lines.append("## Handoffs")
        lines.append("")
        for ho in handoff_list:
            lines.append(f"### {ho['handoff_id']}")
            lines.append("")
            lines.append(f"- **From:** {ho.get('from_agent', ho.get('from_agent_id', 'N/A'))}")
            lines.append(f"- **To:** {ho.get('to_agent', ho.get('to_agent_id', 'N/A'))}")
            ts = ho.get("timestamp", ho.get("date", "N/A"))
            lines.append(f"- **Timestamp:** {ts}")
            summary = ho.get("task_summary", ho.get("task", "N/A"))
            lines.append(f"- **Summary:** {summary}")
            if ho.get("completed"):
                lines.append(f"- **Completed:** {'; '.join(ho['completed'])}")
            if ho.get("pending"):
                lines.append(f"- **Pending:** {'; '.join(ho['pending'])}")
            ks = ho.get("knowledge_state")
            if ks:
                lines.append(f"- **KB State:** {ks.get('total_papers', 0)} papers, {ks.get('total_sessions', 0)} sessions, {ks.get('total_citations', 0)} citations")
            lines.append("")

    # --- Footer ---
    lines.append("---")
    lines.append("")
    lines.append("*Generated by MACP Research Assistant | YSenseAI Ecosystem | GODELAI C-S-P Framework*")
    lines.append("")

    report = "\n".join(lines)

    # Determine output path
    if args.output:
        output_path = args.output
    elif args.title:
        # Create named research directory
        slug = slugify(args.title)
        export_dir = os.path.join(RESEARCH_DIR, slug)
        os.makedirs(export_dir, exist_ok=True)
        output_path = os.path.join(export_dir, "report.md")
    else:
        os.makedirs(EXPORTS_DIR, exist_ok=True)
        tag_suffix = f"_{args.tag}" if args.tag else ""
        filename = f"research_report_{now.strftime('%Y%m%d_%H%M%S')}{tag_suffix}.md"
        output_path = os.path.join(EXPORTS_DIR, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n[EXPORT] Report generated: {output_path}")
    print(f"  Papers: {len(paper_list)}")
    print(f"  Sessions: {len(session_list)}")
    print(f"  Citations: {len(citation_list)}")
    print(f"  Handoffs: {len(handoff_list)}")
    print(f"  Size: {len(report)} chars")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Command: status
# ---------------------------------------------------------------------------

def cmd_status(args):
    """Show the current status of the MACP knowledge base."""
    print("=" * 60)
    print("MACP Research Assistant - STATUS")
    print("=" * 60)

    papers = load_papers()
    log = load_learning_log()
    citations = load_citations()

    paper_list = papers.get("papers", [])
    session_list = log.get("learning_sessions", log.get("sessions", []))
    citation_list = citations.get("citations", [])

    # Paper status breakdown
    status_counts = {}
    for p in paper_list:
        s = p.get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1

    print(f"\n  Papers:          {len(paper_list)}")
    for status, count in sorted(status_counts.items()):
        icon = {"discovered": "[d]", "analyzed": "[a]", "cited": "[c]", "validated": "[v]", "rejected": "[x]"}.get(status, "[?]")
        print(f"    {icon} {status}: {count}")
    print(f"  Learning Sessions: {len(session_list)}")
    print(f"  Citations:         {len(citation_list)}")

    # Recent activity
    if paper_list:
        recent = sorted(paper_list, key=lambda p: p.get("discovered_date", ""), reverse=True)[:3]
        print("\n  Recent Papers:")
        for p in recent:
            print(f"    - [{p['discovered_date']}] {p['title'][:60]}...")

    if session_list:
        recent = sorted(session_list, key=lambda s: s.get("date", ""), reverse=True)[:3]
        print("\n  Recent Learning:")
        for s in recent:
            print(f"    - [{s['date']}] {s['summary'][:60]}...")

    print("\n" + "=" * 60)


# ---------------------------------------------------------------------------
# Command: purge
# ---------------------------------------------------------------------------

def cmd_purge(args):
    """Purge research data from the MACP knowledge base."""
    import shutil
    from security_logger import log_data_purge

    print("=" * 60)
    print("MACP Research Assistant - PURGE")
    print("  Data retention: delete research data")
    print("=" * 60)

    dry_run = args.dry_run

    # Collect files/dirs that would be deleted
    targets = []

    # .macp/research/ directory
    if os.path.isdir(RESEARCH_DIR):
        targets.append(("dir", RESEARCH_DIR))

    # .macp/exports/ directory
    if os.path.isdir(EXPORTS_DIR):
        targets.append(("dir", EXPORTS_DIR))

    # JSON data files (preserve config.json if it exists)
    protected = {"config.json"}
    for fname in os.listdir(MACP_DIR):
        if fname.endswith(".json") and fname not in protected:
            targets.append(("file", os.path.join(MACP_DIR, fname)))

    # Security log
    security_log = os.path.join(MACP_DIR, "security.log")
    if os.path.isfile(security_log):
        targets.append(("file", security_log))

    if not targets:
        print("\n[PURGE] Nothing to delete. Knowledge base is empty.")
        return

    # Show what would be deleted
    print(f"\n  The following will be {'DELETED' if not dry_run else 'deleted (dry-run)'}:")
    for kind, path in targets:
        label = "[DIR] " if kind == "dir" else "[FILE]"
        print(f"    {label} {path}")

    if dry_run:
        print(f"\n[DRY-RUN] {len(targets)} item(s) would be deleted. No changes made.")
        log_data_purge(dry_run=True, files_affected=[p for _, p in targets])
        return

    # Require explicit multi-word confirmation
    print()
    print("  WARNING: This action is irreversible!")
    print()
    try:
        confirm = input("  Type 'Yes, delete all my research data' to confirm: ").strip()
    except (EOFError, KeyboardInterrupt):
        confirm = ""

    if confirm != "Yes, delete all my research data":
        print("  Purge aborted. Confirmation did not match.")
        return

    # Perform deletion
    deleted = []
    for kind, path in targets:
        try:
            if kind == "dir":
                shutil.rmtree(path)
            else:
                os.remove(path)
            deleted.append(path)
            print(f"    Deleted: {path}")
        except OSError as e:
            print(f"    [ERROR] Failed to delete {path}: {e}", file=sys.stderr)

    log_data_purge(dry_run=False, files_affected=deleted)
    print(f"\n[PURGE] {len(deleted)} item(s) deleted.")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Main: Argument Parser
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="macp",
        description="MACP Research Assistant - Intelligent AI Research with Full Traceability",
        epilog="Part of the YSenseAI Ecosystem | GODELAI C-S-P Framework",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- discover ---
    p_discover = subparsers.add_parser("discover", help="Discover new papers (C-S-P: Conflict)")
    p_discover.add_argument("--date", help="Fetch papers for a specific date (YYYY-MM-DD)")
    p_discover.add_argument("--date-range", help="Fetch papers for a date range (YYYY-MM-DD:YYYY-MM-DD)")
    p_discover.add_argument("--query", "-q", help="Semantic search query")
    p_discover.add_argument("--arxiv-id", help="Fetch a specific paper by arXiv ID")
    p_discover.add_argument("--hysts", help="Search the hysts/daily-papers dataset (12,700+ papers)")
    p_discover.add_argument("--hysts-date", help="Fetch from hysts dataset by date (YYYY-MM-DD)")
    p_discover.add_argument("--limit", "-l", type=int, default=10, help="Max results for query search")
    p_discover.add_argument("--force", action="store_true", help="Bypass strict schema validation")
    p_discover.set_defaults(func=cmd_discover)

    # --- analyze ---
    p_analyze = subparsers.add_parser("analyze", help="AI-powered paper analysis (C-S-P: Synthesis)")
    p_analyze.add_argument("arxiv_id", help="arXiv ID of the paper to analyze")
    p_analyze.add_argument("--provider", help="LLM provider: gemini, anthropic, openai (default: auto-select)")
    p_analyze.add_argument("--yes", "-y", action="store_true", help="Skip consent prompt")
    p_analyze.add_argument("--force", action="store_true", help="Bypass strict schema validation")
    p_analyze.set_defaults(func=cmd_analyze)

    # --- handoff ---
    p_handoff = subparsers.add_parser("handoff", help="Create a multi-agent research handoff")
    p_handoff.add_argument("--from", dest="from_agent", required=True, help="Agent initiating the handoff")
    p_handoff.add_argument("--to", dest="to_agent", required=True, help="Agent receiving the handoff")
    p_handoff.add_argument("--summary", "-s", required=True, help="Summary of the research task or context")
    p_handoff.add_argument("--completed", help="Semicolon-separated list of completed actions")
    p_handoff.add_argument("--pending", help="Semicolon-separated list of pending actions")
    p_handoff.add_argument("--papers", "-p", help="Comma-separated arXiv IDs relevant to this handoff")
    p_handoff.add_argument("--force", action="store_true", help="Bypass strict schema validation")
    p_handoff.set_defaults(func=cmd_handoff)

    # --- learn ---
    p_learn = subparsers.add_parser("learn", help="Record a learning insight (C-S-P: Synthesis)")
    p_learn.add_argument("summary", help="Summary of the key learning insight")
    p_learn.add_argument("--papers", "-p", required=True, help="Comma-separated arXiv IDs of related papers")
    p_learn.add_argument("--insight", "-i", help="Concise key insight (defaults to summary)")
    p_learn.add_argument("--agent", "-a", default="human", help="Agent that produced this insight")
    p_learn.add_argument("--tags", "-t", help="Comma-separated tags for categorization")
    p_learn.add_argument("--force", "-f", action="store_true", help="Force add even if papers not in KB")
    p_learn.set_defaults(func=cmd_learn)

    # --- cite ---
    p_cite = subparsers.add_parser("cite", help="Record a citation (C-S-P: Propagation)")
    p_cite.add_argument("arxiv_id", help="arXiv ID of the paper being cited")
    p_cite.add_argument("--project", "-p", required=True, help="Name of the project citing this paper")
    p_cite.add_argument("--context", "-c", required=True, help="Context of how the paper is being used")
    p_cite.add_argument("--agent", "-a", default="human", help="Agent making the citation")
    p_cite.add_argument("--force", action="store_true", help="Bypass strict schema validation")
    p_cite.set_defaults(func=cmd_cite)

    # --- recall ---
    p_recall = subparsers.add_parser("recall", help="Recall knowledge from the MACP knowledge base")
    p_recall.add_argument("question", help="Natural language question to search for")
    p_recall.add_argument("--limit", "-l", type=int, default=5, help="Max results per category")
    p_recall.set_defaults(func=cmd_recall)

    # --- export ---
    p_export = subparsers.add_parser("export", help="Export knowledge base to Markdown report")
    p_export.add_argument("--output", "-o", help="Output file path (default: .macp/exports/)")
    p_export.add_argument("--title", help="Research title — creates named directory in .macp/research/")
    p_export.add_argument("--tag", "-t", help="Filter report by tag")
    p_export.set_defaults(func=cmd_export)

    # --- status ---
    p_status = subparsers.add_parser("status", help="Show knowledge base status")
    p_status.set_defaults(func=cmd_status)

    # --- purge ---
    p_purge = subparsers.add_parser("purge", help="Delete research data (data retention)")
    p_purge.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    p_purge.set_defaults(func=cmd_purge)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
