#!/usr/bin/env python3
"""
Behavior tests for the semantic-consensus upgrade (compute_agreement_detail).

No network is used: embed_texts is monkeypatched with deterministic fakes.
Run directly:  python tools/test_consensus.py
Or via pytest: pytest tools/test_consensus.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import llm_providers as lp  # noqa: E402


# --- Fixtures -------------------------------------------------------------

# Two agents with paraphrased findings: near-zero lexical word overlap,
# but semantically equivalent. This is the exact case the lexical-only
# scorer got wrong.
PARAPHRASED = [
    {
        "agent_id": "gemini",
        "key_findings": ["The transformer attains state-of-the-art translation accuracy."],
        "methodology": "Self-attention encoder-decoder trained on parallel corpora.",
        "relevance_score": 0.8,
    },
    {
        "agent_id": "claude",
        "key_findings": ["This architecture achieves leading results on machine-translation benchmarks."],
        "methodology": "An attention-based seq2seq model fit on bilingual datasets.",
        "relevance_score": 0.8,
    },
]


def _fake_embed_identical(texts, provider, api_key, timeout=60):
    """Findings docs -> vector A; methodology docs -> vector B.

    Simulates an embedder that recognizes both paraphrase pairs as
    semantically identical (cosine = 1.0).
    """
    n = len(texts) // 2
    return [[1.0, 0.0, 0.0]] * n + [[0.0, 1.0, 0.0]] * n


def _fake_embed_unavailable(texts, provider, api_key, timeout=60):
    return None  # simulates missing key / network failure


# --- Tests ----------------------------------------------------------------

def test_semantic_beats_lexical_on_paraphrase(monkeypatch=None):
    _patch(monkeypatch, lp, "resolve_embed_provider", lambda *a, **k: ("gemini", "fake-key"))
    _patch(monkeypatch, lp, "embed_texts", _fake_embed_identical)

    semantic = lp.compute_agreement_detail(PARAPHRASED, semantic=True)
    lexical = lp.compute_agreement_detail(PARAPHRASED, semantic=False)

    assert semantic["method"].startswith("semantic:gemini")
    assert lexical["method"] == "lexical"
    # Paraphrases: semantic findings ~1.0, lexical findings near 0.
    assert semantic["components"]["key_findings_overlap"] > 0.9
    assert lexical["components"]["key_findings_overlap"] < 0.2
    assert semantic["agreement_score"] > lexical["agreement_score"]
    assert semantic["fallback_reason"] is None


def test_falls_back_to_lexical_when_no_provider(monkeypatch=None):
    _patch(monkeypatch, lp, "resolve_embed_provider", lambda *a, **k: (None, None))

    detail = lp.compute_agreement_detail(PARAPHRASED, semantic=True)
    assert detail["method"] == "lexical"
    assert detail["fallback_reason"] == "no_embedding_provider_configured"
    assert 0.0 <= detail["agreement_score"] <= 1.0


def test_falls_back_when_embed_call_fails(monkeypatch=None):
    _patch(monkeypatch, lp, "resolve_embed_provider", lambda *a, **k: ("gemini", "fake-key"))
    _patch(monkeypatch, lp, "embed_texts", _fake_embed_unavailable)

    detail = lp.compute_agreement_detail(PARAPHRASED, semantic=True)
    assert detail["method"] == "lexical"
    assert detail["fallback_reason"] == "embedding_call_failed:gemini"


def test_single_analysis_is_trivial():
    detail = lp.compute_agreement_detail(PARAPHRASED[:1], semantic=True)
    assert detail["method"] == "trivial"
    assert detail["agreement_score"] == 1.0


def test_backward_compatible_float_api_is_lexical_and_offline(monkeypatch=None):
    # Must NOT call the network even though semantic embedders exist.
    def _boom(*a, **k):
        raise AssertionError("compute_agreement_score must not embed")

    _patch(monkeypatch, lp, "embed_texts", _boom)
    score = lp.compute_agreement_score(PARAPHRASED)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_custom_weights_respected(monkeypatch=None):
    _patch(monkeypatch, lp, "resolve_embed_provider", lambda *a, **k: ("gemini", "fake-key"))
    _patch(monkeypatch, lp, "embed_texts", _fake_embed_identical)

    weights = {
        "key_findings_overlap": 1.0,
        "relevance_score_alignment": 0.0,
        "methodology_consistency": 0.0,
    }
    detail = lp.compute_agreement_detail(PARAPHRASED, weights=weights, semantic=True)
    # All weight on findings, which the fake embedder scores at ~1.0.
    assert detail["agreement_score"] > 0.95


# --- Minimal runner (no pytest required) ----------------------------------

def _patch(monkeypatch, target, name, value):
    """Use pytest's monkeypatch when present, else patch directly and
    rely on _restore() for the standalone runner."""
    if monkeypatch is not None:
        monkeypatch.setattr(target, name, value)
    else:
        _ORIGINALS.setdefault((target, name), getattr(target, name))
        setattr(target, name, value)


_ORIGINALS: dict = {}


def _restore():
    for (target, name), value in _ORIGINALS.items():
        setattr(target, name, value)
    _ORIGINALS.clear()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()  # monkeypatch defaults to None -> standalone patch path
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
        finally:
            _restore()
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
