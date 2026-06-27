#!/usr/bin/env python3
"""
Integration tests for POST /api/mcp/submit-analysis (Phase 5A web endpoint).

Isolated: points MACP_DIR + DATABASE_URL at a temp dir BEFORE importing the
backend, mounts only the mcp_router on a bare FastAPI app, and exercises the
endpoint unauthenticated (DB-write path; no GitHub/network).

Run:  python phase3_prototype/backend/test_submit_endpoint.py
Or:   pytest phase3_prototype/backend/test_submit_endpoint.py
"""

import json
import os
import sys
import tempfile

_TMP = tempfile.mkdtemp(prefix="macp_submit_test_")
os.environ["MACP_DIR"] = _TMP
os.environ["MACP_DATABASE_URL"] = f"sqlite:///{_TMP}/test.db"
os.environ.setdefault("JWT_SECRET", "test-secret-not-used-for-real-auth")

_BACKEND = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BACKEND)
sys.path.insert(0, os.path.abspath(os.path.join(_BACKEND, "..", "..", "tools")))

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from database import init_db, SessionLocal, Paper, Analysis  # noqa: E402
from webmcp import mcp_router  # noqa: E402

init_db()
_db = SessionLocal()
if not _db.query(Paper).filter(Paper.arxiv_id == "arxiv:2402.05120").first():
    _db.add(Paper(arxiv_id="arxiv:2402.05120", title="Test Paper", abstract="abc", status="new"))
    _db.commit()
_db.close()

_app = FastAPI()
_app.include_router(mcp_router)
client = TestClient(_app)


def _post(payload):
    r = client.post("/api/mcp/submit-analysis", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["isError"] is False, body
    return json.loads(body["content"][0]["text"])


def test_submit_creates_analysis_and_sanitizes_agent():
    out = _post({
        "paper_id": "2402.05120",
        "agent_id": "Claude Code",  # -> sanitized to claude-code
        "analysis_type": "abstract",
        "content": {"summary": "Strong multi-agent work.", "key_findings": ["f1", "f2"], "strength_score": 8.5},
    })
    assert out["agent_id"] == "claude-code"
    assert out["analysis_type"] == "abstract"
    assert out["github_synced"] is False  # unauthenticated -> DB only
    assert out["stored_path"].startswith(".macp/analyses/arxiv_2402.05120/claude-code_")

    db = SessionLocal()
    row = db.query(Analysis).filter(Analysis.id == out["analysis_id"]).first()
    assert row is not None
    assert row.provider == "claude-code"
    assert json.loads(row.key_insights) == ["f1", "f2"]
    prov = json.loads(row.provenance)
    assert prov["submitted_via"] == "api/mcp/submit-analysis"
    db.close()


def test_continuation_chain_recorded_in_provenance():
    out = _post({
        "paper_id": "2402.05120",
        "agent_id": "manus_ai",
        "analysis_type": "deep",
        "content": {"summary": "Deeper read.", "key_insights": ["scales to 5 agents"], "relevance_score": 0.75},
        "continues_from": {"analysis_id": "claude-code_abstract", "agent_id": "claude_code"},
    })
    assert out["continues_from"] == "claude-code_abstract"
    db = SessionLocal()
    row = db.query(Analysis).filter(Analysis.id == out["analysis_id"]).first()
    prov = json.loads(row.provenance)
    assert prov["continues_from"]["analysis_id"] == "claude-code_abstract"
    # relevance_score 0.75 -> score 7.5
    assert abs(row.score - 7.5) < 1e-6
    db.close()


def test_unknown_paper_is_rejected():
    r = client.post("/api/mcp/submit-analysis", json={
        "paper_id": "9999.99999", "agent_id": "x", "content": {"summary": "s"},
    })
    body = r.json()
    assert body["isError"] is True


def test_missing_summary_is_422():
    r = client.post("/api/mcp/submit-analysis", json={
        "paper_id": "2402.05120", "agent_id": "x", "content": {"key_findings": ["a"]},
    })
    assert r.status_code == 422  # pydantic: summary required


def test_appears_in_discovery():
    r = client.get("/api/mcp/")
    names = [t["name"] for t in r.json()["tools"]]
    assert "macp.submit-analysis" in names


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
