#!/usr/bin/env python3
"""
Behavior tests for the Phase 5A Agent Submission Layer (`macp submit`).

Runs fully offline against an isolated temp MACP_DIR — never touches real
research data or the network.

Run directly:  python tools/test_submit.py
Or via pytest: pytest tools/test_submit.py
"""

import json
import os
import sys
import tempfile
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _fresh_cli(macp_dir):
    """Import macp_cli with MACP_DIR pointed at an isolated temp dir."""
    import paper_fetcher
    paper_fetcher.MACP_DIR = macp_dir
    import macp_cli
    # Re-point the module-level paths derived from MACP_DIR.
    macp_cli.MACP_DIR = macp_dir
    macp_cli.ANALYSES_DIR = os.path.join(macp_dir, "analyses")
    return macp_cli


def _submit_args(**kw):
    base = dict(
        paper="2402.05120", agent="claude_code", type="abstract",
        file=None, summary=None, findings=None, score=None,
        continues_from=None, continues_from_agent=None, force=False,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def _read_only_analysis(analyses_dir, arxiv_bare):
    paper_dir = os.path.join(analyses_dir, arxiv_bare)
    files = [f for f in os.listdir(paper_dir) if f.endswith(".json")]
    assert len(files) == 1, f"expected 1 analysis file, found {files}"
    with open(os.path.join(paper_dir, files[0]), encoding="utf-8") as fh:
        return json.load(fh), files[0]


def test_inline_submission_writes_provenance_record():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _fresh_cli(tmp)
        cli.cmd_submit(_submit_args(
            summary="Strong multi-agent coordination framework.",
            findings="Handoff reduces context loss; Consensus is robust",
            score=8.5,
        ))
        record, fname = _read_only_analysis(cli.ANALYSES_DIR, "2402.05120")
        assert record["agent_id"] == "claude_code"
        assert record["arxiv_id"] == "arxiv:2402.05120"
        assert record["analysis_type"] == "abstract"
        assert record["summary"].startswith("Strong multi-agent")
        assert record["key_findings"] == ["Handoff reduces context loss", "Consensus is robust"]
        assert record["strength_score"] == 8.5
        # Provenance + bias disclosure are mandatory.
        assert record["_provenance"]["submitted_via"] == "macp_cli.submit"
        assert "bias_disclaimer" in record["_meta"]
        assert fname.startswith("claude_code_")


def test_continuation_chain_is_recorded():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _fresh_cli(tmp)
        cli.cmd_submit(_submit_args(
            agent="manus_ai", type="deep",
            summary="Deeper read flags scalability limits.",
            continues_from="claude_code_abstract",
            continues_from_agent="claude_code",
        ))
        record, _ = _read_only_analysis(cli.ANALYSES_DIR, "2402.05120")
        assert record["continues_from"]["analysis_id"] == "claude_code_abstract"
        assert record["continues_from"]["agent_id"] == "claude_code"


def test_manifest_registers_submission():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _fresh_cli(tmp)
        cli.cmd_submit(_submit_args(summary="A summary."))
        with open(os.path.join(tmp, "manifest.json"), encoding="utf-8") as fh:
            manifest = json.load(fh)
        entry = manifest["analyses"]["arxiv:2402.05120"]
        assert "claude_code" in entry["agents"]
        assert len(entry["submissions"]) == 1
        assert entry["submissions"][0]["analysis_type"] == "abstract"


def test_file_based_submission():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _fresh_cli(tmp)
        analysis_path = os.path.join(tmp, "analysis.json")
        with open(analysis_path, "w", encoding="utf-8") as fh:
            json.dump({
                "summary": "From a file.",
                "key_insights": ["insight A", "insight B"],
                "methodology": "ablation study",
                "strength_score": 6,
            }, fh)
        cli.cmd_submit(_submit_args(agent="cursor", file=analysis_path, summary=None))
        record, _ = _read_only_analysis(cli.ANALYSES_DIR, "2402.05120")
        assert record["summary"] == "From a file."
        assert record["key_insights"] == ["insight A", "insight B"]
        assert record["methodology"] == "ablation study"


def test_rejects_missing_summary(capsys=None):
    with tempfile.TemporaryDirectory() as tmp:
        cli = _fresh_cli(tmp)
        # No --file and no --summary -> nothing written.
        cli.cmd_submit(_submit_args(summary=None, file=None))
        assert not os.path.isdir(cli.ANALYSES_DIR), "must not write without content"


def test_paper_id_normalized_to_arxiv_prefix():
    with tempfile.TemporaryDirectory() as tmp:
        cli = _fresh_cli(tmp)
        cli.cmd_submit(_submit_args(paper="arxiv:2402.05120", summary="ok"))
        record, _ = _read_only_analysis(cli.ANALYSES_DIR, "2402.05120")
        assert record["arxiv_id"] == "arxiv:2402.05120"


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
