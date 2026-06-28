#!/usr/bin/env python3
"""
Tests for smart model routing (select_model). Run: python tools/test_routing.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm_providers as lp  # noqa: E402


def _routing(mode):
    if mode is None:
        os.environ.pop("MODEL_ROUTING", None)
    else:
        os.environ["MODEL_ROUTING"] = mode


def test_abstract_routes_to_lite():
    _routing("balanced")
    model, reason = lp.select_model("gemini", "abstract")
    assert model == "gemini-3.1-flash-lite", model
    assert reason == "abstract->lite"


def test_deep_short_is_standard():
    _routing("balanced")
    model, reason = lp.select_model("gemini", "deep", {"chars": 5000, "sections": 4})
    assert model == lp.PROVIDERS["gemini"]["model"]  # standard
    assert reason == "deep->standard"


def test_deep_complex_routes_to_pro():
    _routing("balanced")
    # deepseek has a real pro tier
    model, reason = lp.select_model("deepseek", "deep", {"chars": 80000, "sections": 20})
    assert model == "deepseek-v4-pro", model
    assert reason == "deep+complex->pro"


def test_pro_falls_back_to_standard_when_undefined():
    _routing("balanced")
    # gemini has no pro default -> falls back to standard
    model, reason = lp.select_model("gemini", "deep", {"chars": 99999, "sections": 30})
    assert model == lp.PROVIDERS["gemini"]["model"]
    assert reason == "deep+complex->pro"


def test_routing_off_returns_standard():
    _routing("off")
    try:
        model, reason = lp.select_model("gemini", "abstract")
        assert model == lp.PROVIDERS["gemini"]["model"]
        assert reason == "routing_off"
    finally:
        _routing(None)


def test_provider_without_tiers_uses_standard():
    _routing("balanced")
    # anthropic has no tier map -> abstract lite falls back to standard
    model, reason = lp.select_model("anthropic", "abstract")
    assert model == lp.PROVIDERS["anthropic"]["model"]


def test_complexity_threshold_by_sections():
    _routing("balanced")
    # mistral: small chars but many sections -> complex -> pro (mistral-large-latest)
    model, _ = lp.select_model("mistral", "deep", {"chars": 1000, "sections": 15})
    assert model == "mistral-large-latest"


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
        finally:
            _routing(None)
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
