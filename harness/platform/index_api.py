#!/usr/bin/env python3
"""Phase 1 index API — static export + optional local server (IC-04).

  python3 harness/platform/index_api.py --export     # site/api/v1/
  python3 harness/platform/index_api.py --serve      # localhost:8787
"""
from __future__ import annotations

import json
import os
import shutil
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
API_ROOT = os.path.join(ROOT, "site", "api", "v1")


def _load_records() -> list:
    for name in ("records.measured.json", "records.scored.json", "records.json"):
        path = os.path.join(ROOT, "data", name)
        if os.path.isfile(path):
            return json.load(open(path, encoding="utf-8"))
    return []


def _provenance_headers(data_source: str = "live") -> dict:
    return {
        "X-Data-Source": data_source,
        "X-Snapshot-As-Of": date.today().isoformat(),
        "X-Evidence-Tier": "mixed",
        "X-Model-Version": "risk_model-0.2",
    }


def export_static() -> None:
    os.makedirs(API_ROOT, exist_ok=True)
    recs = _load_records()
    graph_path = os.path.join(ROOT, "data", "fixtures", "graph_edges.json")
    in_force = os.path.join(ROOT, "data", "l5_in_force.json")

    meta = {
        "generated": date.today().isoformat(),
        "provenance": _provenance_headers(),
        "entity_count": len(recs),
    }
    json.dump(meta, open(os.path.join(API_ROOT, "meta.json"), "w"), indent=2)

    scored = [r for r in recs if r.get("scores")]
    json.dump(scored, open(os.path.join(API_ROOT, "entities.json"), "w"), indent=2)

    # CSV dataset
    if scored:
        import csv
        rows = []
        for r in scored:
            s = r.get("scores") or {}
            rows.append({
                "entity_id": r["entity_id"],
                "name": r["name"],
                "layer": r["layer"],
                "entity_type": r["entity_type"],
                "value_chain_seat": r.get("value_chain_seat", ""),
                "exposure_0_100": s.get("exposure_0_100"),
                "preparedness_0_100": s.get("preparedness_0_100"),
                "margin_of_safety": s.get("margin_of_safety"),
                "quadrant": s.get("quadrant"),
            })
        with open(os.path.join(API_ROOT, "dataset.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    if os.path.isfile(graph_path):
        shutil.copy(graph_path, os.path.join(API_ROOT, "graph.json"))
    if os.path.isfile(in_force):
        shutil.copy(in_force, os.path.join(API_ROOT, "l5_in_force.json"))

    open(os.path.join(API_ROOT, "openapi.yaml"), "w").write(
        open(os.path.join(ROOT, "contract", "platform", "openapi.index.yaml"), encoding="utf-8").read()
    )
    print(f"exported index API → {API_ROOT}/ ({len(scored)} entities)")


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj: dict, code: int = 200) -> None:
        body = json.dumps(obj, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        for k, v in _provenance_headers().items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path in ("/api/v1/entities", "/entities"):
            recs = _load_records()
            self._json({"entities": recs, "count": len(recs)})
        elif path in ("/api/v1/dataset", "/dataset"):
            self._json({"path": "site/api/v1/dataset.csv"})
        elif path in ("/api/v1/graph", "/graph"):
            gp = os.path.join(ROOT, "data", "fixtures", "graph_edges.json")
            self._json(json.load(open(gp)) if os.path.isfile(gp) else {"nodes": [], "edges": []})
        else:
            self._json({"routes": ["/entities", "/dataset", "/graph"]})


def serve(port: int = 8787) -> None:
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


def main() -> int:
    if "--export" in sys.argv:
        export_static()
        return 0
    if "--serve" in sys.argv:
        print(f"serving index API on http://127.0.0.1:8787/api/v1/entities")
        serve()
        return 0
    print("Usage: index_api.py --export | --serve")
    return 1


if __name__ == "__main__":
    import sys
    raise SystemExit(main())
