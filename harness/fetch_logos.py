#!/usr/bin/env python3
"""Fetch entity logos into assets/logos/ for static site build."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_MAP = os.path.join(ROOT, "contract", "entity_logos.json")
OUT_DIR = os.path.join(ROOT, "assets", "logos")
TIMEOUT = 12
MIN_BYTES = 200


def _fetch(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": "NFRI-build/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read()
            return data if len(data) >= MIN_BYTES else None
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def fetch_logo(entity_id: str, domain: str) -> bool:
    dest = os.path.join(OUT_DIR, f"{entity_id}.png")
    if os.path.exists(dest) and os.path.getsize(dest) >= MIN_BYTES:
        return True
    for url in (
        f"https://logo.clearbit.com/{domain}",
        f"https://www.google.com/s2/favicons?domain={domain}&sz=128",
    ):
        data = _fetch(url)
        if data:
            with open(dest, "wb") as f:
                f.write(data)
            return True
    return False


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    logos = json.load(open(LOGO_MAP))
    ok = fail = 0
    for eid, meta in logos.items():
        if eid.startswith("_"):
            continue
        domain = meta.get("domain")
        if not domain:
            fail += 1
            continue
        if fetch_logo(eid, domain):
            ok += 1
        else:
            fail += 1
    print(f"logos: {ok} fetched, {fail} missing → {OUT_DIR}")


if __name__ == "__main__":
    main()
