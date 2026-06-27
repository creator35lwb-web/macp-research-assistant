#!/usr/bin/env python3
"""
Tests for OriginGuardMiddleware (Cloudflare origin protection).

Run: python phase3_prototype/backend/test_origin_guard.py
"""

import os
import sys

os.environ.setdefault("JWT_SECRET", "test-secret-not-used-for-real-auth")

_BACKEND = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BACKEND)

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from security import OriginGuardMiddleware  # noqa: E402

app = FastAPI()
app.add_middleware(OriginGuardMiddleware)


@app.get("/api/ping")
def api_ping():
    return {"ok": True}


@app.get("/")
def root():
    return {"ok": True}


client = TestClient(app)
SECRET = "test-origin-secret-123"


def _set(secret):
    if secret is None:
        os.environ.pop("CF_ORIGIN_SECRET", None)
    else:
        os.environ["CF_ORIGIN_SECRET"] = secret


def test_noop_when_secret_unset():
    _set(None)
    assert client.get("/api/ping").status_code == 200


def test_api_blocked_without_header_when_set():
    _set(SECRET)
    try:
        r = client.get("/api/ping")
        assert r.status_code == 403, r.text
    finally:
        _set(None)


def test_api_blocked_with_wrong_header():
    _set(SECRET)
    try:
        r = client.get("/api/ping", headers={"X-Origin-Secret": "nope"})
        assert r.status_code == 403
    finally:
        _set(None)


def test_api_allowed_with_correct_header():
    _set(SECRET)
    try:
        r = client.get("/api/ping", headers={"X-Origin-Secret": SECRET})
        assert r.status_code == 200, r.text
    finally:
        _set(None)


def test_non_api_path_always_allowed():
    _set(SECRET)
    try:
        # root (e.g. SPA / health) must stay reachable even without the header
        assert client.get("/").status_code == 200
    finally:
        _set(None)


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
            os.environ.pop("CF_ORIGIN_SECRET", None)
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
