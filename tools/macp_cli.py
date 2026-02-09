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
    load_papers,
    save_papers,
    add_papers,
    MACP_DIR,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LEARNING_LOG_FILE = os.path.join(MACP_DIR, "learning_log.json")
CITATIONS_FILE = os.path.join(MACP_DIR, "citations.json")
KNOWLEDGE_GRAPH_FILE = os.path.join(MACP_DIR, "knowledge_graph.json")

# ---------------------------------------------------------------------------
# Learning Log Operations
# ---------------------------------------------------------------------------

def load_learning_log() -> dict:
    """Load the current learning_log.json file."""
    if not os.path.exists(LEARNING_LOG_FILE):
        return {"learning_sessions": []}
    with open(LEARNING_LOG_FILE, "r") as f:
        return json.load(f)


def save_learning_log(data: dict) -> None:
    """Save the learning_log.json file."""
    os.makedirs(MACP_DIR, exist_ok=True)
    with open(LEARNING_LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Citation Operations
# ---------------------------------------------------------------------------

def load_citations() -> dict:
    """Load the current citations.json file."""
    if not os.path.exists(CITATIONS_FILE):
        return {"citations": []}
    with open(CITATIONS_FILE, "r") as f:
        return json.load(f)


def save_citations(data: dict) -> None:
    """Save the citations.json file."""
    os.makedirs(MACP_DIR, exist_ok=True)
    with open(CITATIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)


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

    # Pipeline 1: Date-based discovery
    if args.date:
        print(f"\n[Pipeline 1: HF Daily Papers] Date: {args.date}")
        papers = fetch_by_date(args.date)
        print(f"  Found {len(papers)} papers from HF Daily Papers")
        all_papers.extend(papers)

    if args.date_range:
        start, end = args.date_range.split(":")
        print(f"\n[Pipeline 1: HF Daily Papers] Range: {start} to {end}")
        papers = fetch_by_date_range(start, end)
        print(f"  Found {len(papers)} papers from HF Daily Papers")
        all_papers.extend(papers)

    # Pipeline 2: Query-based discovery
    if args.query:
        limit = args.limit or 10
        print(f"\n[Pipeline 2: HF MCP Search] Query: '{args.query}' (limit: {limit})")
        papers = fetch_by_query(args.query, limit=limit)
        print(f"  Found {len(papers)} papers from MCP Search")
        all_papers.extend(papers)

    # Pipeline 3: Direct ID fetch
    if args.arxiv_id:
        print(f"\n[Pipeline 3: arXiv API] ID: {args.arxiv_id}")
        paper = fetch_by_id(args.arxiv_id)
        if paper:
            print(f"  Found: {paper['title'][:70]}...")
            all_papers.append(paper)
        else:
            print("  Paper not found.")

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
    print(f"\n[MACP Storage] Adding {len(all_papers)} papers to research_papers.json...")
    added, skipped = add_papers(all_papers)
    print(f"  Added: {added} | Skipped (duplicates): {skipped}")

    # Summary
    total = load_papers()
    print(f"\n[Summary] Total papers in knowledge base: {len(total.get('papers', []))}")
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

    # Validate paper IDs exist
    papers_data = load_papers()
    existing_ids = {p["id"] for p in papers_data.get("papers", [])}
    paper_ids = [f"arxiv:{pid}" if not pid.startswith("arxiv:") else pid for pid in args.papers.split(",")]

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
        "summary": args.summary,
        "key_insight": args.insight if args.insight else args.summary,
        "papers": paper_ids,
        "agent": args.agent or "human",
        "tags": args.tags.split(",") if args.tags else [],
    }

    # Save to learning log
    log = load_learning_log()
    key = "learning_sessions" if "learning_sessions" in log else "sessions"
    log.setdefault(key, []).append(session)
    save_learning_log(log)

    # Update paper status to "analyzed"
    for paper in papers_data.get("papers", []):
        if paper["id"] in paper_ids:
            paper["status"] = "analyzed"
            if args.summary not in paper.get("insights", []):
                paper.setdefault("insights", []).append(args.summary)
    save_papers(papers_data)

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

    paper_id = f"arxiv:{args.arxiv_id}" if not args.arxiv_id.startswith("arxiv:") else args.arxiv_id

    citation = {
        "citation_id": f"cite_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "paper_id": paper_id,
        "cited_in": args.project,
        "context": args.context,
        "date": date.today().isoformat(),
        "cited_by": args.agent or "human",
    }

    citations_data = load_citations()
    citations_data["citations"].append(citation)
    save_citations(citations_data)

    # Update paper status to "cited"
    papers_data = load_papers()
    for paper in papers_data.get("papers", []):
        if paper["id"] == paper_id:
            paper["status"] = "cited"
    save_papers(papers_data)

    print(f"\n[PROPAGATION] Citation recorded: {citation['citation_id']}")
    print(f"  Paper: {paper_id}")
    print(f"  Cited in: {args.project}")
    print(f"  Context: {args.context[:80]}...")
    print(f"\n[MACP] Citations file updated ({len(citations_data['citations'])} total citations)")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Command: recall
# ---------------------------------------------------------------------------

def cmd_recall(args):
    """Recall knowledge from the MACP knowledge base."""
    print("=" * 60)
    print("MACP Research Assistant - RECALL")
    print("  'What have I learned?'")
    print("=" * 60)

    query = args.question.lower()
    query_terms = set(query.split())

    # Search across papers
    papers_data = load_papers()
    paper_matches = []
    for paper in papers_data.get("papers", []):
        title_lower = paper.get("title", "").lower()
        abstract_lower = paper.get("abstract", "").lower()
        score = sum(1 for term in query_terms if term in title_lower or term in abstract_lower)
        if score > 0:
            paper_matches.append((score, paper))

    paper_matches.sort(key=lambda x: x[0], reverse=True)

    # Search across learning sessions
    log = load_learning_log()
    session_matches = []
    for session in log.get("learning_sessions", log.get("sessions", [])):
        summary_lower = session.get("summary", "").lower()
        insight_lower = session.get("key_insight", "").lower()
        score = sum(1 for term in query_terms if term in summary_lower or term in insight_lower)
        if score > 0:
            session_matches.append((score, session))

    session_matches.sort(key=lambda x: x[0], reverse=True)

    # Search across citations
    citations_data = load_citations()
    citation_matches = []
    for cite in citations_data.get("citations", []):
        context_lower = cite.get("context", "").lower()
        score = sum(1 for term in query_terms if term in context_lower)
        if score > 0:
            citation_matches.append((score, cite))

    citation_matches.sort(key=lambda x: x[0], reverse=True)

    # Present results
    limit = args.limit or 5

    if not paper_matches and not session_matches and not citation_matches:
        print(f"\n[RECALL] No results found for: '{args.question}'")
        print("  Try broader terms or discover more papers first.")
        return

    if paper_matches:
        print(f"\n--- Relevant Papers ({min(len(paper_matches), limit)} of {len(paper_matches)}) ---")
        for score, paper in paper_matches[:limit]:
            status_icon = {"discovered": "🔍", "analyzed": "📖", "cited": "📌"}.get(paper.get("status"), "?")
            print(f"  {status_icon} [{paper['id']}] {paper['title'][:70]}...")
            if paper.get("insights"):
                for insight in paper["insights"][:2]:
                    print(f"     → Insight: {insight[:60]}...")

    if session_matches:
        print(f"\n--- Learning Sessions ({min(len(session_matches), limit)} of {len(session_matches)}) ---")
        for score, session in session_matches[:limit]:
            print(f"  📝 [{session['session_id']}] {session['date']}")
            print(f"     Summary: {session['summary'][:70]}...")
            print(f"     Papers: {', '.join(session.get('papers', []))}")

    if citation_matches:
        print(f"\n--- Citations ({min(len(citation_matches), limit)} of {len(citation_matches)}) ---")
        for score, cite in citation_matches[:limit]:
            print(f"  📌 [{cite['citation_id']}] in {cite['cited_in']}")
            print(f"     Context: {cite['context'][:70]}...")

    total_results = len(paper_matches) + len(session_matches) + len(citation_matches)
    print(f"\n[RECALL] Total matches: {total_results} (papers: {len(paper_matches)}, "
          f"sessions: {len(session_matches)}, citations: {len(citation_matches)})")
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
        icon = {"discovered": "🔍", "analyzed": "📖", "cited": "📌"}.get(status, "?")
        print(f"    {icon} {status}: {count}")
    print(f"  Learning Sessions: {len(session_list)}")
    print(f"  Citations:         {len(citation_list)}")

    # Recent activity
    if paper_list:
        recent = sorted(paper_list, key=lambda p: p.get("discovered_date", ""), reverse=True)[:3]
        print(f"\n  Recent Papers:")
        for p in recent:
            print(f"    - [{p['discovered_date']}] {p['title'][:60]}...")

    if session_list:
        recent = sorted(session_list, key=lambda s: s.get("date", ""), reverse=True)[:3]
        print(f"\n  Recent Learning:")
        for s in recent:
            print(f"    - [{s['date']}] {s['summary'][:60]}...")

    print("\n" + "=" * 60)


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
    p_discover.add_argument("--limit", "-l", type=int, default=10, help="Max results for query search")
    p_discover.set_defaults(func=cmd_discover)

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
    p_cite.set_defaults(func=cmd_cite)

    # --- recall ---
    p_recall = subparsers.add_parser("recall", help="Recall knowledge from the MACP knowledge base")
    p_recall.add_argument("question", help="Natural language question to search for")
    p_recall.add_argument("--limit", "-l", type=int, default=5, help="Max results per category")
    p_recall.set_defaults(func=cmd_recall)

    # --- status ---
    p_status = subparsers.add_parser("status", help="Show knowledge base status")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
