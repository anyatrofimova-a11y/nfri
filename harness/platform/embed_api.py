#!/usr/bin/env python3
"""Phase 4 — CSaaS embed API /embed/policy-offer (IC-07, ADR-002).

Mandatory broker_id on every policy offer — no consumer-direct bypass.
Static export to site/api/v1/embed/.

  python3 harness/platform/embed_api.py --export
  python3 harness/platform/embed_api.py --verify
  python3 harness/platform/embed_api.py --serve
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EMBED_ROOT = os.path.join(ROOT, "site", "api", "v1", "embed")
SEATS = os.path.join(ROOT, "contract", "platform", "value_chain_seats.json")
DEMO_FIX = os.path.join(ROOT, "data", "fixtures", "active_bundle_demo.json")


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _broker_handoff_required() -> bool:
    seats = _load(SEATS)
    wedge = seats.get("distribution_wedges", {}).get("csaas_embed", {})
    return bool(wedge.get("broker_handoff_required", True))


def policy_offer(body: dict) -> tuple[int, dict]:
    """POST /embed/policy-offer — returns (status_code, response_body)."""
    broker_id = body.get("broker_id")
    if not broker_id:
        return 400, {
            "error": "broker_id required",
            "code": "ADR-002_BROKER_HANDOFF",
            "detail": "CSaaS embed routes through broker_id on policy linkage — no consumer-direct bypass.",
        }

    facility_id = body.get("facility_id")
    entity_id = body.get("entity_id")
    if not facility_id or not entity_id:
        return 400, {"error": "facility_id and entity_id required"}

    offer_id = body.get("offer_id") or f"offer-{uuid.uuid4().hex[:12]}"
    token = f"nfri-offer-{uuid.uuid4().hex}"

    response: dict[str, Any] = {
        "offer_id": offer_id,
        "offer_token": token,
        "facility_id": facility_id,
        "entity_id": entity_id,
        "broker_id": broker_id,
        "value_chain_seat": "csaas_embed",
        "broker_handoff_required": _broker_handoff_required(),
        "placement_chain": ["csaas_embed", "broker", "mga", "carrier"],
        "broker_handoff": {
            "broker_id": broker_id,
            "status": "pending_acceptance",
            "handoff_url": f"/embed/broker-handoff/{broker_id}/{offer_id}",
        },
        "generated_at": _now_iso(),
        "data_source": body.get("data_source", "fixture"),
    }
    if body.get("policy_id"):
        response["policy_id"] = body["policy_id"]
    if body.get("cover_type"):
        response["cover_type"] = body["cover_type"]
    return 200, response


def export_static() -> None:
    os.makedirs(EMBED_ROOT, exist_ok=True)
    demo = _load(DEMO_FIX) if os.path.isfile(DEMO_FIX) else {}

    req = {
        "facility_id": demo.get("facility_id", "fac-latos-bridgend"),
        "entity_id": demo.get("entity_id", "asset-latos-bridgend"),
        "broker_id": demo.get("broker_id", "miller"),
        "policy_id": (demo.get("policy") or {}).get("policy_id"),
        "cover_type": (demo.get("policy") or {}).get("cover_type", "parametric"),
        "data_source": "fixture",
    }
    _, offer = policy_offer(req)

    handoff = {
        "handoff_id": f"handoff-{offer['offer_id']}",
        "offer_id": offer["offer_id"],
        "broker_id": offer["broker_id"],
        "status": "accepted",
        "value_chain_seat": "broker",
        "placement_chain": offer["placement_chain"],
        "policy_id": req.get("policy_id"),
        "accepted_at": _now_iso(),
        "data_source": "fixture",
    }

    meta = {
        "generated": date.today().isoformat(),
        "routes": ["/embed/policy-offer"],
        "adr": "002-value-chain-seat",
        "wedge": "csaas_embed",
        "broker_handoff_required": True,
    }

    json.dump(meta, open(os.path.join(EMBED_ROOT, "meta.json"), "w"), indent=2)
    json.dump(offer, open(os.path.join(EMBED_ROOT, "policy-offer.example.json"), "w"), indent=2)
    json.dump(handoff, open(os.path.join(EMBED_ROOT, "broker_handoff.example.json"), "w"), indent=2)
    print(f"exported embed API → {EMBED_ROOT}/")


def verify() -> int:
    print("NFRI embed API verification (ADR-002)")
    print("=" * 48)
    fails = 0

    code, resp = policy_offer({"facility_id": "fac-x", "entity_id": "asset-x"})
    ok_reject = code == 400 and resp.get("code") == "ADR-002_BROKER_HANDOFF"
    print(f"[{'PASS' if ok_reject else 'FAIL'}] rejects missing broker_id (HTTP {code})")
    if not ok_reject:
        fails += 1
        print(f"       response: {resp}")

    code2, resp2 = policy_offer(
        {"facility_id": "fac-latos-bridgend", "entity_id": "asset-latos-bridgend", "broker_id": "miller"}
    )
    ok_accept = code2 == 200 and resp2.get("broker_id") == "miller" and resp2.get("value_chain_seat") == "csaas_embed"
    print(f"[{'PASS' if ok_accept else 'FAIL'}] accepts offer with broker_id")
    if not ok_accept:
        fails += 1

    chain = resp2.get("placement_chain") if ok_accept else []
    ok_chain = chain and chain[0] == "csaas_embed" and "broker" in chain
    print(f"[{'PASS' if ok_chain else 'FAIL'}] placement chain preserves broker (no bypass)")
    if not ok_chain:
        fails += 1

    print("=" * 48)
    return 1 if fails else 0


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj: dict, code: int = 200) -> None:
        body = json.dumps(obj, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Data-Source", "fixture")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = self.path.split("?")[0]
        if path not in ("/api/v1/embed/policy-offer", "/embed/policy-offer"):
            self._json({"error": "not found"}, 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json({"error": "invalid JSON"}, 400)
            return
        code, resp = policy_offer(body)
        self._json(resp, code)

    def log_message(self, fmt: str, *args: object) -> None:
        return


def serve(port: int = 8788) -> None:
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


def main() -> int:
    if "--export" in sys.argv:
        export_static()
        return 0
    if "--verify" in sys.argv:
        return verify()
    if "--serve" in sys.argv:
        print("serving embed API on http://127.0.0.1:8788/embed/policy-offer")
        serve()
        return 0
    print("Usage: embed_api.py --export | --verify | --serve")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
