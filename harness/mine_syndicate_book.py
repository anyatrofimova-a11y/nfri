#!/usr/bin/env python3
"""Pull named Energy class GWP from Lloyd's Q4 2024 syndicate iXBRL accounts.

Writes data/book_mining/batch*.json for extract_book_inputs.py --merge.

  python3 harness/mine_syndicate_book.py --write-batches
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SYNDICATE_URLS: dict[str, tuple[str, str]] = {
    "markel": (
        "GBP",
        "https://assets.lloyds.com/media/5b02701e-8066-477c-ba4b-cf5ca11d6808/"
        "3000%20Markel%20Syndicate%20-%203000%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r2.html",
    ),
    "brit": (
        "USD",
        "https://assets.lloyds.com/media/62b826cb-f3e1-4c0b-b726-8657c72282b7/"
        "2987%20Brit%20Syndicate%20-%202987%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1.html",
    ),
    "canopius": (
        "USD",
        "https://assets.lloyds.com/media/fb991510-1c4b-4bfa-8445-9d0794c890c8/"
        "4444%20Canopius%20Syndicate%20-%204444%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1.html",
    ),
    "talbot-1183": (
        "USD",
        "https://assets.lloyds.com/media/0eddca92-557a-4b61-9a7f-7692d82deb8d/"
        "1183%20TAL%20Syndicate%20-%201183%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1.html",
    ),
    "lancashire-3010": (
        "USD",
        "https://assets.lloyds.com/media/a0b54745-ea22-47a7-bae3-ea466ba830f2/"
        "3010%20Lancashire%20Syndicate%20-%203010%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r2.html",
    ),
    "axis-1686": (
        "USD",
        "https://assets.lloyds.com/media/d33b75ae-31c2-4b22-b888-3b8c91ff48fe/"
        "1686%20Axis%20Syndicate%20-%201686%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1%20(1).html",
    ),
    "apollo-1969": (
        "USD",
        "https://assets.lloyds.com/media/67b970dc-d836-4910-be89-e0a60f768be1/"
        "1969%20Apollo%20Syndicate%20-%201969%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1.html",
    ),
    "atrium-609": (
        "GBP",
        "https://assets.lloyds.com/media/4cd15bcf-89ec-4db1-8eb5-cf9572146b4a/"
        "609%20Atrium%20Syndicate%20-%20609%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1.html",
    ),
    "aspen": (
        "GBP",
        "https://assets.lloyds.com/media/0cb0aae6-b567-49d4-892f-267228d505b2/"
        "4711%20Aspen%20Syndicate%20-%204711%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1%20(1).html",
    ),
    "qbe-europe": (
        "GBP",
        "https://assets.lloyds.com/media/f26e946b-ec92-4ad8-b98a-c942ea4d1806/"
        "2999%20QBE%20Europe%20Syndicate%20-%202999%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r2.html",
    ),
    "inigo-1301": (
        "USD",
        "https://assets.lloyds.com/media/9520bfff-fb54-4aa5-abbe-03367ae08023/"
        "1301%20Inigo%20Syndicate%20-%201301%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1.html",
    ),
    "travelers-5000": (
        "USD",
        "https://assets.lloyds.com/media/f8d83ade-084c-4398-b110-891cae306414/"
        "5000%20Travelers%20Syndicate%20-%205000%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1%20(1).html",
    ),
}

NUM = re.compile(r"^[\d,]+(?:\.\d+)?$")
SKIP = {"&#160;", "", "-"}


def _lines(html: str) -> list[str]:
    text = re.sub(r"<[^>]+>", "\n", html)
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def _to_millions(raw: str) -> float:
    clean = raw.replace(",", "").strip()
    if not clean or clean == ".":
        raise ValueError(f"empty numeric token: {raw!r}")
    if "." in clean:
        val = float(clean)
        return round(val, 3) if val < 10_000 else round(val / 1000.0, 3)
    return round(int(clean) / 1000.0, 3)


def _next_amount(lines: list[str], start: int, max_ahead: int = 8) -> float | None:
    for j in range(start, min(start + max_ahead, len(lines))):
        ln = lines[j]
        if ln in SKIP or ln.startswith("("):
            continue
        if NUM.match(ln):
            try:
                return _to_millions(ln)
            except ValueError:
                continue
    return None


def _is_gpw_line(ln: str) -> bool:
    return ln in ("Gross premiums written", "Gross premium written") or ln.startswith(
        "Gross premiums writ"
    )


def _section_year(lines: list[str], idx: int) -> int | None:
    for j in range(idx, max(idx - 50, -1), -1):
        if lines[j] == "December 2024" or "December 2024" in lines[j]:
            return 2024
        if lines[j] == "December 2023" or "December 2023" in lines[j]:
            return 2023
    return None


def parse_syndicate(html: str) -> tuple[float | None, float | None, str | None]:
    """Return (total_gwp_m, energy_gwp_m, energy_line_name) from class-of-business table."""
    lines = _lines(html)
    total_m = None
    energy_m = None
    energy_line = None

    candidates: list[float] = []
    for i, ln in enumerate(lines):
        if _is_gpw_line(ln):
            for j in range(i + 1, min(i + 12, len(lines))):
                if NUM.match(lines[j]):
                    try:
                        val = _to_millions(lines[j])
                    except ValueError:
                        continue
                    if val >= 100:
                        candidates.append(val)
    if candidates:
        total_m = max(candidates)

    if total_m is None:
        big: list[float] = []
        for ln in lines:
            clean = ln.replace(",", "").strip()
            if not clean.isdigit():
                continue
            v = int(clean)
            if v >= 100_000:
                big.append(v / 1000.0)
        if big:
            total_m = max(big)

    energy_labels = (
        "Energy",
        "Marine & Energy",
        "Marine and energy",
        "Marine &amp; Energy",
    )
    energy_hits: list[tuple[str, float, int]] = []
    for i, ln in enumerate(lines):
        m = re.match(r"^(Energy(?: \(including Power Utility\))?)\s+([\d,]+)$", ln)
        if m:
            prev = lines[i - 1].lower() if i else ""
            if "which is" not in prev and "third party" not in prev:
                energy_hits.append((m.group(1), _to_millions(m.group(2)), i))
                continue
        if ln in energy_labels:
            prev = lines[i - 1].lower() if i else ""
            if "which is" in prev or "third party" in prev:
                continue
            amt = _next_amount(lines, i + 1)
            if amt is not None and amt > 0:
                energy_hits.append((ln.replace("&amp;", "&"), amt, i))

    if energy_hits:
        narrow = [h for h in energy_hits if h[0] == "Energy"]
        pick = narrow if narrow else energy_hits
        y2024 = [h for h in pick if _section_year(lines, h[2]) == 2024]
        pool = y2024 or pick
        substantial = [h for h in pool if h[1] >= 1]
        energy_line, energy_m, _ = max(substantial or pool, key=lambda h: h[1])

    return total_m, energy_m, energy_line


def fetch_row(eid: str, currency: str, url: str) -> dict | None:
    try:
        html = urllib.request.urlopen(url, timeout=45).read().decode("utf-8", "replace")
    except Exception as exc:
        print(f"  skip {eid}: fetch failed ({exc})")
        return None
    total_m, energy_m, line = parse_syndicate(html)
    if not total_m or energy_m is None:
        print(f"  skip {eid}: no named energy class (total={total_m}, energy={energy_m})")
        return None
    return {
        "total_gwp": total_m,
        "energy_power_gwp": energy_m,
        "datacentre_tech_gwp": 0,
        "currency": currency,
        "lines_counted": [line or "Energy"],
        "source": url,
        "as_of": "2024-12-31",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entity", nargs="*", help="subset of entity_ids")
    ap.add_argument("--write-batches", action="store_true", help="write data/book_mining/batch*.json")
    args = ap.parse_args()

    manifest = json.load(open(os.path.join(ROOT, "data", "book_mining", "manifest.json")))
    targets = args.entity or [e for ids in manifest["batches"].values() for e in ids]
    inputs: dict[str, dict] = {}

    for eid in targets:
        if eid not in SYNDICATE_URLS:
            continue
        currency, url = SYNDICATE_URLS[eid]
        print(f"mining {eid}…")
        row = fetch_row(eid, currency, url)
        if row:
            inputs[eid] = row
            sh = row["energy_power_gwp"] / row["total_gwp"]
            print(f"  + {eid}: {row['energy_power_gwp']}/{row['total_gwp']} {currency} ({sh:.1%})")

    if args.write_batches:
        out_dir = os.path.join(ROOT, "data", "book_mining")
        for bk, ids in manifest["batches"].items():
            path = os.path.join(out_dir, f"{bk}.json")
            existing = {}
            if os.path.isfile(path):
                existing = json.load(open(path)).get("inputs") or {}
            chunk = {**existing, **{e: inputs[e] for e in ids if e in inputs}}
            if not chunk:
                continue
            json.dump(
                {"batch": bk, "researched_by": "mine_syndicate_book", "inputs": chunk},
                open(path, "w"),
                indent=2,
            )
            print(f"wrote {path} ({len(chunk)} rows)")

    print(f"\nmined {len(inputs)} carriers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
