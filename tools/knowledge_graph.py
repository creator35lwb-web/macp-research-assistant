#!/usr/bin/env python3
"""
MACP Research Assistant - Knowledge Graph Generator
====================================================
Generates a knowledge graph from the MACP data files, mapping relationships
between papers, learning sessions, citations, and projects.

The knowledge graph is a JSON structure that can be visualized or queried
to understand the full provenance chain of research insights.

Author: L (Godel), AI Agent & Project Founder
Date: February 10, 2026
"""

import json
import os
import sys
import tempfile
from collections import defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MACP_DIR = ".macp"
PAPERS_FILE = os.path.join(MACP_DIR, "research_papers.json")
LEARNING_LOG_FILE = os.path.join(MACP_DIR, "learning_log.json")
CITATIONS_FILE = os.path.join(MACP_DIR, "citations.json")
KNOWLEDGE_GRAPH_FILE = os.path.join(MACP_DIR, "knowledge_graph.json")


# ---------------------------------------------------------------------------
# Data Loaders
# ---------------------------------------------------------------------------

def _load_json(filepath: str, default: dict = None) -> dict:
    """Load a JSON file with a default fallback."""
    if default is None:
        default = {}
    if not os.path.exists(filepath):
        return default
    with open(filepath, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Graph Builder
# ---------------------------------------------------------------------------

def build_knowledge_graph() -> dict:
    """
    Build a knowledge graph from all MACP data sources.

    The graph consists of:
    - nodes: Papers, Learning Sessions, Citations, Projects, Agents
    - edges: Relationships between nodes (discovered_by, analyzed_in, cited_in, etc.)

    Returns:
        A dict representing the knowledge graph.
    """
    papers_data = _load_json(PAPERS_FILE, {"papers": []})
    log_data = _load_json(LEARNING_LOG_FILE, {"learning_sessions": []})
    citations_data = _load_json(CITATIONS_FILE, {"citations": []})

    nodes = []
    edges = []
    projects = set()
    agents = set()

    # --- Paper Nodes ---
    for paper in papers_data.get("papers", []):
        paper_id = paper.get("id", "")
        nodes.append({
            "id": paper_id,
            "type": "paper",
            "label": paper.get("title", "")[:80],
            "status": paper.get("status", "discovered"),
            "date": paper.get("discovered_date", ""),
            "url": paper.get("url", ""),
        })

        # Edge: discovered_by agent
        discovered_by = paper.get("discovered_by", "")
        if discovered_by:
            agents.add(discovered_by)
            edges.append({
                "source": discovered_by,
                "target": paper_id,
                "type": "discovered",
                "label": "discovered",
            })

    # --- Learning Session Nodes ---
    sessions = log_data.get("learning_sessions", log_data.get("sessions", []))
    for session in sessions:
        session_id = session.get("session_id", "")
        nodes.append({
            "id": session_id,
            "type": "learning_session",
            "label": session.get("summary", "")[:80],
            "date": session.get("date", ""),
            "agent": session.get("agent", "human"),
            "tags": session.get("tags", []),
        })

        # Edge: session -> paper (analyzed)
        for paper_id in session.get("papers", []):
            edges.append({
                "source": session_id,
                "target": paper_id,
                "type": "analyzed",
                "label": "synthesized from",
            })

        # Edge: agent -> session
        agent = session.get("agent", "human")
        agents.add(agent)
        edges.append({
            "source": agent,
            "target": session_id,
            "type": "created_by",
            "label": "created by",
        })

    # --- Citation Nodes ---
    for citation in citations_data.get("citations", []):
        cite_id = citation.get("citation_id", "")
        project = citation.get("cited_in", "")
        projects.add(project)

        nodes.append({
            "id": cite_id,
            "type": "citation",
            "label": f"Citation in {project}",
            "date": citation.get("date", ""),
            "context": citation.get("context", "")[:120],
        })

        # Edge: citation -> paper
        edges.append({
            "source": cite_id,
            "target": citation.get("paper_id", ""),
            "type": "cites",
            "label": "cites",
        })

        # Edge: citation -> project
        edges.append({
            "source": cite_id,
            "target": f"project:{project}",
            "type": "propagated_to",
            "label": "propagated to",
        })

        # Edge: agent -> citation
        cited_by = citation.get("cited_by", "human")
        agents.add(cited_by)
        edges.append({
            "source": cited_by,
            "target": cite_id,
            "type": "cited_by",
            "label": "cited by",
        })

    # --- Project Nodes ---
    for project in projects:
        nodes.append({
            "id": f"project:{project}",
            "type": "project",
            "label": project,
        })

    # --- Agent Nodes ---
    for agent in agents:
        nodes.append({
            "id": agent,
            "type": "agent",
            "label": agent,
        })

    # --- Graph Statistics ---
    node_types = defaultdict(int)
    for node in nodes:
        node_types[node["type"]] += 1

    edge_types = defaultdict(int)
    for edge in edges:
        edge_types[edge["type"]] += 1

    graph = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "generator": "macp_knowledge_graph",
            "version": "1.0.0",
        },
        "statistics": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "node_types": dict(node_types),
            "edge_types": dict(edge_types),
        },
        "nodes": nodes,
        "edges": edges,
    }

    return graph


def _atomic_write_json(filepath: str, data: dict) -> None:
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
        try:
            os.unlink(tmp_path)
        except OSError as cleanup_err:
            print(f"[WARN] Failed to clean up temp file: {cleanup_err}", file=sys.stderr)
        raise


def save_knowledge_graph(graph: dict) -> str:
    """Save the knowledge graph to the MACP directory with atomic write."""
    _atomic_write_json(KNOWLEDGE_GRAPH_FILE, graph)
    return KNOWLEDGE_GRAPH_FILE


# ---------------------------------------------------------------------------
# Provenance Tracer
# ---------------------------------------------------------------------------

def trace_provenance(paper_id: str, graph: dict) -> dict:
    """
    Trace the full provenance chain for a specific paper.

    Returns a dict showing:
    - How the paper was discovered
    - What insights were synthesized from it
    - Where it has been cited (propagated)
    """
    if not paper_id.startswith("arxiv:"):
        paper_id = f"arxiv:{paper_id}"

    # Find the paper node
    paper_node = None
    for node in graph.get("nodes", []):
        if node["id"] == paper_id:
            paper_node = node
            break

    if not paper_node:
        return {"error": f"Paper {paper_id} not found in knowledge graph"}

    # Find all edges involving this paper
    discovery_edges = []
    synthesis_edges = []
    propagation_edges = []

    for edge in graph.get("edges", []):
        if edge["target"] == paper_id and edge["type"] == "discovered":
            discovery_edges.append(edge)
        elif edge["target"] == paper_id and edge["type"] == "analyzed":
            synthesis_edges.append(edge)
        elif edge["type"] == "cites":
            # Check if this citation references our paper
            cite_node_id = edge["source"]
            if edge["target"] == paper_id:
                # Find the project this citation propagated to
                for e2 in graph.get("edges", []):
                    if e2["source"] == cite_node_id and e2["type"] == "propagated_to":
                        propagation_edges.append({**edge, "project": e2["target"]})

    # Resolve session summaries
    sessions = []
    for edge in synthesis_edges:
        for node in graph.get("nodes", []):
            if node["id"] == edge["source"] and node["type"] == "learning_session":
                sessions.append(node)

    provenance = {
        "paper": paper_node,
        "c_conflict": {
            "description": "How was this paper discovered?",
            "discovery_agents": [e["source"] for e in discovery_edges],
        },
        "s_synthesis": {
            "description": "What insights were synthesized from this paper?",
            "sessions": [{"id": s["id"], "summary": s["label"]} for s in sessions],
        },
        "p_propagation": {
            "description": "Where has this knowledge been applied?",
            "citations": [{"citation": e["source"], "project": e.get("project", "unknown")} for e in propagation_edges],
        },
    }

    return provenance


# ---------------------------------------------------------------------------
# Mermaid Diagram Generator
# ---------------------------------------------------------------------------

def generate_mermaid(graph: dict, max_nodes: int = 30) -> str:
    """Generate a Mermaid diagram string from the knowledge graph."""
    lines = ["graph LR"]

    # Add nodes (limited for readability)
    node_count = 0
    included_ids = set()

    for node in graph.get("nodes", []):
        if node_count >= max_nodes:
            break
        nid = node["id"].replace(":", "_").replace(" ", "_").replace("-", "_")
        label = node.get("label", node["id"])[:40]
        ntype = node.get("type", "unknown")

        if ntype == "paper":
            lines.append(f'    {nid}["{label}"]')
        elif ntype == "learning_session":
            lines.append(f'    {nid}("{label}")')
        elif ntype == "citation":
            lines.append(f'    {nid}{{"{label}"}}')
        elif ntype == "project":
            lines.append(f'    {nid}[["{label}"]]')
        elif ntype == "agent":
            lines.append(f'    {nid}(("{label}"))')
        else:
            lines.append(f'    {nid}["{label}"]')

        included_ids.add(node["id"])
        node_count += 1

    # Add edges for included nodes
    for edge in graph.get("edges", []):
        src = edge["source"]
        tgt = edge["target"]
        if src in included_ids and tgt in included_ids:
            src_id = src.replace(":", "_").replace(" ", "_").replace("-", "_")
            tgt_id = tgt.replace(":", "_").replace(" ", "_").replace("-", "_")
            label = edge.get("label", "")
            lines.append(f'    {src_id} -->|{label}| {tgt_id}')

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("MACP Knowledge Graph Generator")
    print("=" * 60)

    print("\n[1/3] Building knowledge graph from MACP data...")
    graph = build_knowledge_graph()

    print("\n[2/3] Graph Statistics:")
    stats = graph["statistics"]
    print(f"  Total Nodes: {stats['total_nodes']}")
    print(f"  Total Edges: {stats['total_edges']}")
    print(f"  Node Types: {json.dumps(stats['node_types'], indent=4)}")
    print(f"  Edge Types: {json.dumps(stats['edge_types'], indent=4)}")

    filepath = save_knowledge_graph(graph)
    print(f"\n[3/3] Knowledge graph saved to: {filepath}")

    # Demo: Trace provenance for a paper
    papers = _load_json(PAPERS_FILE, {"papers": []})
    cited_papers = [p for p in papers.get("papers", []) if p.get("status") == "cited"]
    if cited_papers:
        demo_id = cited_papers[0]["id"]
        print(f"\n--- Provenance Trace: {demo_id} ---")
        provenance = trace_provenance(demo_id, graph)
        print(json.dumps(provenance, indent=2))

    # Generate Mermaid diagram (atomic write)
    mermaid = generate_mermaid(graph, max_nodes=15)
    mermaid_file = os.path.join(MACP_DIR, "knowledge_graph.mmd")
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(mermaid_file) or ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(mermaid)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, mermaid_file)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError as cleanup_err:
            print(f"[WARN] Failed to clean up temp file: {cleanup_err}", file=sys.stderr)
        raise
    print(f"\n--- Mermaid diagram saved to: {mermaid_file} ---")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
