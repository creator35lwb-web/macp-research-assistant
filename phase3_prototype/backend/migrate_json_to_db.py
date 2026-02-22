#!/usr/bin/env python3
"""
MACP Research Assistant — JSON-to-SQLite Migration (P3B-01)
============================================================
One-time script to import existing .macp/*.json data into the new SQLite DB.

Usage:
    python migrate_json_to_db.py [--dry-run]
"""

import argparse
import json
import os
import sys

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import MACP_DIR
from database import (
    Citation,
    LearningSession,
    Paper,
    SessionLocal,
    init_db,
    log_audit,
)


def load_json(filename: str) -> dict:
    path = os.path.join(MACP_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def migrate(dry_run: bool = False):
    print("=" * 60)
    print("MACP JSON → SQLite Migration")
    print(f"  Source: {MACP_DIR}")
    print(f"  Dry run: {dry_run}")
    print("=" * 60)

    # Initialize the database
    if not dry_run:
        init_db()

    db = SessionLocal()

    try:
        # --- Papers ---
        papers_data = load_json("research_papers.json")
        papers = papers_data.get("papers", [])
        print(f"\n[Papers] Found {len(papers)} papers")
        paper_map = {}  # arxiv_id -> Paper.id

        for p in papers:
            arxiv_id = p.get("id", "")
            if not arxiv_id:
                continue
            if dry_run:
                print(f"  [DRY] Would insert paper: {arxiv_id}")
                continue

            existing = db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()
            if existing:
                paper_map[arxiv_id] = existing.id
                continue

            paper = Paper(
                arxiv_id=arxiv_id,
                title=p.get("title", ""),
                authors=json.dumps(p.get("authors", [])),
                abstract=p.get("abstract", ""),
                url=p.get("url", ""),
                source=p.get("discovered_by", "migration"),
                status=p.get("status", "discovered"),
            )
            db.add(paper)
            db.flush()
            paper_map[arxiv_id] = paper.id

        if not dry_run:
            db.commit()
            print(f"  Migrated {len(paper_map)} papers")

        # --- Learning Sessions ---
        log_data = load_json("learning_log.json")
        sessions = log_data.get("learning_sessions", [])
        print(f"\n[Learning Sessions] Found {len(sessions)} sessions")
        session_count = 0

        for s in sessions:
            paper_ids = s.get("papers", [])
            insight = s.get("key_insight", s.get("summary", ""))
            agent = s.get("agent", "human")

            for pid in paper_ids:
                pk = paper_map.get(pid)
                if not pk:
                    continue
                if dry_run:
                    print(f"  [DRY] Would insert session for {pid}")
                    continue
                ls = LearningSession(paper_id=pk, insight=insight, agent=agent)
                db.add(ls)
                session_count += 1

        if not dry_run:
            db.commit()
            print(f"  Migrated {session_count} learning session entries")

        # --- Citations ---
        cit_data = load_json("citations.json")
        citations = cit_data.get("citations", [])
        print(f"\n[Citations] Found {len(citations)} citations")
        cit_count = 0

        for c in citations:
            pid = c.get("paper_id", "")
            pk = paper_map.get(pid)
            if not pk:
                continue
            if dry_run:
                print(f"  [DRY] Would insert citation for {pid}")
                continue
            ct = Citation(
                paper_id=pk,
                project=c.get("cited_in", ""),
                context=c.get("context", ""),
                cited_by=c.get("cited_by", "human"),
            )
            db.add(ct)
            cit_count += 1

        if not dry_run:
            db.commit()
            print(f"  Migrated {cit_count} citations")

        # --- Audit log entry ---
        if not dry_run:
            log_audit(
                event="migration_complete",
                message=f"Migrated {len(paper_map)} papers, {session_count} sessions, {cit_count} citations from JSON",
                level="INFO",
                db=db,
            )

        print(f"\n{'[DRY-RUN] No changes made.' if dry_run else '[DONE] Migration complete.'}")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate MACP JSON data to SQLite")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()
    migrate(dry_run=args.dry_run)
