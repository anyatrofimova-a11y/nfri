#!/usr/bin/env python3
"""Query the NFRI knowledge graph (contract/knowledge/graph.json).

    python3 harness/knowledge_graph.py topics
    python3 harness/knowledge_graph.py nodes [--topic dc_exposure]
    python3 harness/knowledge_graph.py node <node_id>
    python3 harness/knowledge_graph.py topic <topic_id>
    python3 harness/knowledge_graph.py neighbours <node_id>
    python3 harness/knowledge_graph.py path <from_id> <to_id>
"""
from __future__ import annotations

import json
import os
import sys
from collections import deque
from typing import Dict, List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH_PATH = os.path.join(ROOT, "contract", "knowledge", "graph.json")


def load_graph() -> dict:
    with open(GRAPH_PATH) as f:
        return json.load(f)


def nodes_by_id(g: dict) -> Dict[str, dict]:
    return {n["id"]: n for n in g["nodes"]}


def edges_from(g: dict) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = {}
    for e in g["edges"]:
        out.setdefault(e["from"], []).append(e)
    return out


def edges_to(g: dict) -> Dict[str, List[dict]]:
    inc: Dict[str, List[dict]] = {}
    for e in g["edges"]:
        inc.setdefault(e["to"], []).append(e)
    return inc


def cmd_topics(g: dict) -> None:
    for t in g["topics"]:
        print(f"{t['id']:<20} {t['label']}")
        if t.get("description"):
            print(f"  {t['description']}")


def cmd_nodes(g: dict, topic: Optional[str]) -> None:
    for n in g["nodes"]:
        if topic and topic not in n.get("topics", []):
            continue
        cid = n.get("citation_id", "")
        print(f"{n['id']:<30} [{n['type']:<16}] {n['label'][:60]}  {cid}")


def cmd_node(g: dict, nid: str) -> None:
    n = nodes_by_id(g).get(nid)
    if not n:
        print(f"unknown node: {nid}")
        sys.exit(1)
    print(json.dumps(n, indent=2))
    ext = n.get("extract")
    if ext:
        path = os.path.join(ROOT, "contract", "knowledge", ext)
        if os.path.exists(path):
            print(f"\n--- extract: {ext} ---")
            with open(path) as f:
                print(f.read()[:3000])


def cmd_topic(g: dict, tid: str) -> None:
    topics = {t["id"]: t for t in g["topics"]}
    if tid not in topics:
        print(f"unknown topic: {tid}")
        sys.exit(1)
    print(json.dumps(topics[tid], indent=2))
    print("\nNodes:")
    cmd_nodes(g, tid)


def cmd_neighbours(g: dict, nid: str) -> None:
    if nid not in nodes_by_id(g):
        print(f"unknown node: {nid}")
        sys.exit(1)
    for e in g["edges"]:
        if e["from"] == nid:
            print(f"  → {e['to']:<28} [{e['relation']}]  {e.get('note', '')}")
        elif e["to"] == nid:
            print(f"  ← {e['from']:<28} [{e['relation']}]  {e.get('note', '')}")


def cmd_path(g: dict, src: str, dst: str) -> None:
    by_id = nodes_by_id(g)
    if src not in by_id or dst not in by_id:
        print("unknown endpoint")
        sys.exit(1)
    adj: Dict[str, List[str]] = {}
    for e in g["edges"]:
        adj.setdefault(e["from"], []).append(e["to"])
        adj.setdefault(e["to"], []).append(e["from"])
    q = deque([(src, [src])])
    seen = {src}
    while q:
        cur, path = q.popleft()
        if cur == dst:
            for i, nid in enumerate(path):
                label = by_id[nid]["label"]
                print(f"  {i+1}. {nid} — {label}")
            return
        for nb in adj.get(cur, []):
            if nb not in seen:
                seen.add(nb)
                q.append((nb, path + [nb]))
    print(f"no path between {src} and {dst}")


def main() -> int:
    g = load_graph()
    if len(sys.argv) < 2:
        print(__doc__)
        return 0
    cmd = sys.argv[1]
    if cmd == "topics":
        cmd_topics(g)
    elif cmd == "nodes":
        topic = None
        if "--topic" in sys.argv:
            topic = sys.argv[sys.argv.index("--topic") + 1]
        cmd_nodes(g, topic)
    elif cmd == "node" and len(sys.argv) >= 3:
        cmd_node(g, sys.argv[2])
    elif cmd == "topic" and len(sys.argv) >= 3:
        cmd_topic(g, sys.argv[2])
    elif cmd == "neighbours" and len(sys.argv) >= 3:
        cmd_neighbours(g, sys.argv[2])
    elif cmd == "path" and len(sys.argv) >= 4:
        cmd_path(g, sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
