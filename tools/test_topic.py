#!/usr/bin/env python3
"""
Behavior tests for the Phase 5 Component 2 Topic Taxonomy (`macp topic`).

Offline, isolated temp MACP_DIR. Run: python tools/test_topic.py
"""

import json
import os
import sys
import tempfile
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import macp_cli as cli  # noqa: E402


def _isolate(tmp):
    cli.MACP_DIR = tmp
    cli.TOPICS_DIR = os.path.join(tmp, "topics")
    cli.TOPICS_INDEX = os.path.join(cli.TOPICS_DIR, "index.json")
    cli.ANALYSES_DIR = os.path.join(tmp, "analyses")


def _args(**kw):
    base = dict(topic_action=None, name=None, parent=None, paper=None, agent="human", tags=None)
    base.update(kw)
    return SimpleNamespace(**base)


def _index(tmp):
    with open(os.path.join(tmp, "topics", "index.json"), encoding="utf-8") as fh:
        return json.load(fh)


def test_add_root_topic():
    with tempfile.TemporaryDirectory() as tmp:
        _isolate(tmp)
        cli.cmd_topic(_args(topic_action="add", name="Large Language Models"))
        idx = _index(tmp)
        assert "large-language-models" in idx["topics"]
        t = idx["topics"]["large-language-models"]
        assert t["depth"] == 0 and t["parent"] is None
        assert os.path.isfile(os.path.join(tmp, "topics", "large-language-models", "topic.json"))


def test_add_child_nests_and_links_parent():
    with tempfile.TemporaryDirectory() as tmp:
        _isolate(tmp)
        cli.cmd_topic(_args(topic_action="add", name="Large Language Models"))
        cli.cmd_topic(_args(topic_action="add", name="Transformer Architecture", parent="Large Language Models"))
        idx = _index(tmp)
        child = idx["topics"]["transformer-architecture"]
        assert child["depth"] == 1
        assert child["parent"] == "large-language-models"
        assert child["path"] == "large-language-models/transformer-architecture"
        # nested directory exists
        assert os.path.isfile(os.path.join(tmp, "topics", "large-language-models", "transformer-architecture", "topic.json"))
        # parent links the child
        with open(os.path.join(tmp, "topics", "large-language-models", "topic.json"), encoding="utf-8") as fh:
            parent = json.load(fh)
        assert "transformer-architecture" in parent["child_topics"]


def test_add_rejects_missing_parent():
    with tempfile.TemporaryDirectory() as tmp:
        _isolate(tmp)
        cli.cmd_topic(_args(topic_action="add", name="Child", parent="nonexistent"))
        # nothing created
        assert not os.path.isdir(os.path.join(tmp, "topics", "child"))


def test_classify_from_explicit_tags_attaches_paper():
    with tempfile.TemporaryDirectory() as tmp:
        _isolate(tmp)
        cli.cmd_topic(_args(topic_action="classify", paper="2402.05120",
                            tags="multi-agent, reinforcement-learning", agent="claude_code"))
        idx = _index(tmp)
        assert "multi-agent" in idx["topics"]
        assert "reinforcement-learning" in idx["topics"]
        with open(os.path.join(tmp, "topics", "multi-agent", "topic.json"), encoding="utf-8") as fh:
            t = json.load(fh)
        assert "arxiv:2402.05120" in t["papers"]
        assert "claude_code" in t["agents_contributed"]


def test_classify_reads_relevance_tags_from_analysis():
    with tempfile.TemporaryDirectory() as tmp:
        _isolate(tmp)
        # seed a saved analysis with relevance_tags (as `macp submit` would write)
        pdir = os.path.join(tmp, "analyses", "2402.05120")
        os.makedirs(pdir, exist_ok=True)
        with open(os.path.join(pdir, "gemini_20260628.json"), "w", encoding="utf-8") as fh:
            json.dump({"summary": "x", "relevance_tags": ["alignment", "safety"]}, fh)
        cli.cmd_topic(_args(topic_action="classify", paper="2402.05120"))
        idx = _index(tmp)
        assert "alignment" in idx["topics"] and "safety" in idx["topics"]


def test_classify_under_parent():
    with tempfile.TemporaryDirectory() as tmp:
        _isolate(tmp)
        cli.cmd_topic(_args(topic_action="add", name="AI Safety"))
        cli.cmd_topic(_args(topic_action="classify", paper="2402.05120",
                            tags="reward-modeling", parent="AI Safety"))
        idx = _index(tmp)
        assert idx["topics"]["reward-modeling"]["parent"] == "ai-safety"
        assert idx["topics"]["reward-modeling"]["path"] == "ai-safety/reward-modeling"


def test_paper_count_tracked():
    with tempfile.TemporaryDirectory() as tmp:
        _isolate(tmp)
        cli.cmd_topic(_args(topic_action="classify", paper="2402.05120", tags="agents"))
        cli.cmd_topic(_args(topic_action="classify", paper="1706.03762", tags="agents"))
        idx = _index(tmp)
        assert idx["topics"]["agents"]["paper_count"] == 2


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
