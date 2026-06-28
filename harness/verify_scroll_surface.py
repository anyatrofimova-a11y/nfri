#!/usr/bin/env python3
"""Verify a16z Dynamism scroll + essay typography surface is baked into built site.

  python3 harness/verify_scroll_surface.py
  python3 harness/verify_scroll_surface.py --strict
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site", "index.html")
SPEC = os.path.join(ROOT, "contract", "scroll_typography.json")


def main() -> int:
    strict = "--strict" in sys.argv
    errors: list[str] = []

    if not os.path.exists(SITE):
        print(f"FAIL — run harness/build_frontend.py first ({SITE} missing)")
        return 1

    html = open(SITE, encoding="utf-8").read()
    spec = json.load(open(SPEC)) if os.path.exists(SPEC) else {}

    for marker in spec.get("verify", {}).get("css_markers", []):
        if marker not in html:
            errors.append(f"missing CSS marker: {marker}")

    for cls in spec.get("verify", {}).get("classes", []):
        if cls not in html:
            errors.append(f"missing class: {cls}")

    if "scroll-behavior:smooth" not in html:
        errors.append("missing scroll-behavior:smooth on html")
    if "essay-reveal" not in html:
        errors.append("missing essay-reveal scroll animation hooks")
    if "--font-essay" not in html:
        errors.append("missing --font-essay token")
    if "section.essay .arg-p" not in html:
        errors.append("missing essay body typography rules")

    print("SCROLL SURFACE VERIFY — a16z Dynamism mapping")
    print("=" * 52)
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
        print("=" * 52)
        print(f"FAIL — {len(errors)} error(s)")
        return 1 if strict else 0
    print("  ✓ smooth scroll, essay serif surface, reveal hooks")
    print("=" * 52)
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
