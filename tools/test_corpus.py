#!/usr/bin/env python3
"""
Tests for Semantic Scholar corpus integration (fetch_from_semantic_scholar).
Mocks the HTTP call — no network. Run: python tools/test_corpus.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paper_fetcher as pf  # noqa: E402

_FAKE = {
    "data": [
        {  # has an arXiv id -> should map into the arxiv pipeline
            "paperId": "abc123",
            "title": "Attention Is All You Need",
            "abstract": "We propose the Transformer...",
            "authors": [{"name": "A. Vaswani"}, {"name": "N. Shazeer"}],
            "year": 2017,
            "externalIds": {"ArXiv": "1706.03762", "DOI": "10.5555/x"},
            "url": "https://www.semanticscholar.org/paper/abc123",
            "openAccessPdf": {"url": "https://arxiv.org/pdf/1706.03762.pdf"},
        },
        {  # no arXiv id -> s2: id, abstract-level
            "paperId": "def456",
            "title": "Some Non-arXiv Paper",
            "abstract": "Abstract here.",
            "authors": [{"name": "J. Doe"}],
            "year": 2024,
            "externalIds": {"DOI": "10.1000/y"},
            "url": "https://www.semanticscholar.org/paper/def456",
            "openAccessPdf": None,
        },
        {"paperId": "ghost", "title": None},  # no title -> filtered out
    ]
}


class _FakeResp:
    def __init__(self, payload, ok=True):
        self._p = payload
        self._ok = ok

    def raise_for_status(self):
        if not self._ok:
            raise pf.requests.RequestException("boom")

    def json(self):
        return self._p


def _patch_get(resp):
    pf.requests.get = lambda *a, **k: resp  # type: ignore


def test_arxiv_paper_maps_into_arxiv_pipeline():
    _patch_get(_FakeResp(_FAKE))
    papers = pf.fetch_from_semantic_scholar("transformer", limit=10)
    arxiv = next(p for p in papers if p["title"].startswith("Attention"))
    assert arxiv["id"] == "arxiv:1706.03762"
    assert arxiv["authors"] == ["A. Vaswani", "N. Shazeer"]
    assert arxiv["pdf_url"].endswith("1706.03762.pdf")
    assert arxiv["source"] == "semanticscholar"


def test_non_arxiv_paper_gets_s2_id():
    _patch_get(_FakeResp(_FAKE))
    papers = pf.fetch_from_semantic_scholar("x", limit=10)
    s2 = next(p for p in papers if p["title"] == "Some Non-arXiv Paper")
    assert s2["id"] == "s2:def456"
    assert s2["pdf_url"] == ""  # openAccessPdf was None


def test_titleless_results_filtered():
    _patch_get(_FakeResp(_FAKE))
    papers = pf.fetch_from_semantic_scholar("x", limit=10)
    assert len(papers) == 2  # the title=None entry is dropped


def test_http_error_returns_empty():
    _patch_get(_FakeResp({}, ok=False))
    assert pf.fetch_from_semantic_scholar("x") == []


def test_empty_query_raises():
    try:
        pf.fetch_from_semantic_scholar("   ")
        assert False, "expected ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    _orig = pf.requests.get
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
            pf.requests.get = _orig
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
