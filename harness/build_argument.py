#!/usr/bin/env python3
"""NFRI — Argument harness.

Renders the narrative 'Argument' section of the index site from the content
contract at contract/argument.json. This is the piece that sets out the case in
prose before the interactive explorer — modelled on the narrative-led layout of
a narrative-led public index: an editorial essay (serif headings, drop-cap,
pull-quotes, a framework 2×2, inline references) that frames the chart below it.

Content lives in the contract (regenerable, version-controlled, auditable);
this module is a pure renderer. build_frontend.py imports render_argument() and
injects the fragment as <section id="argument">.

Usage:
  python3 harness/build_argument.py --check      # validate the contract, print block summary
  python3 harness/build_argument.py --preview     # write site/argument.preview.html (standalone)
  (imported)  render_argument(arg) -> str         # HTML fragment for the section body
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARG_PATH = os.path.join(ROOT, "contract", "argument.json")

QCLASS = {"whitespace": "whitespace", "earning_it": "earning", "sidelined": "sidelined", "exposed": "exposed"}
VALID_TYPES = {"kicker", "h", "lead", "p", "pull", "framework", "refs"}


def load_argument(path=ARG_PATH):
    with open(path) as f:
        return json.load(f)


# --- block renderers (prose fields carry trusted inline HTML by contract; rendered raw) ---

def _kicker(b):
    return f'<p class="arg-kicker">{b["text"]}</p>'


def _h(b):
    return f'<h3 class="arg-h">{b["text"]}</h3>'


def _lead(b):
    cls = "arg-lead" + (" dropcap" if b.get("dropcap") else "")
    return f'<p class="{cls}">{b["text"]}</p>'


def _p(b):
    return f'<p class="arg-p">{b["text"]}</p>'


def _pull(b):
    return f'<blockquote class="arg-pull">{b["text"]}</blockquote>'


def _framework(b):
    """Render the 2×2 quadrant framework as a labelled grid (matches the explorer's quadrants)."""
    cells = {c["quad"]: c for c in b.get("cells", [])}
    order = ["whitespace", "earning_it", "exposed", "sidelined"]  # visual TL, TR, BR, BL
    grid_pos = {"whitespace": "tl", "earning_it": "tr", "exposed": "br", "sidelined": "bl"}
    parts = []
    for q in order:
        c = cells.get(q)
        if not c:
            continue
        parts.append(
            f'<div class="arg-cell {QCLASS.get(q, q)} {grid_pos[q]}">'
            f'<span class="arg-cell-tag">{c["label"]}</span>'
            f'<p>{c["note"]}</p></div>'
        )
    axx = b.get("axes", {}).get("x", "Exposure →")
    axy = b.get("axes", {}).get("y", "Preparedness →")
    cap = f'<figcaption class="arg-cap">{b["caption"]}</figcaption>' if b.get("caption") else ""
    return (
        '<figure class="arg-fw">'
        '<div class="arg-fw-frame">'
        f'<div class="arg-fw-y" aria-hidden="true">{axy}</div>'
        '<div class="arg-fw-body"><div class="arg-fw-grid">'
        + "".join(parts) +
        f'</div><div class="arg-fw-x" aria-hidden="true">{axx}</div></div></div>'
        + cap + '</figure>'
    )


def _refs(b):
    items = "".join(
        f'<li><a href="{r["url"]}" target="_blank" rel="noopener">{r["title"]}</a>'
        f' <span class="arg-ref-a">{r.get("authors", "")}</span></li>'
        for r in b.get("items", [])
    )
    return f'<ul class="arg-refs">{items}</ul>'


_RENDER = {"kicker": _kicker, "h": _h, "lead": _lead, "p": _p, "pull": _pull,
           "framework": _framework, "refs": _refs}


def render_argument(arg):
    """Return the inner HTML for <section id='argument'> from a loaded argument contract."""
    out = []
    for b in arg.get("blocks", []):
        fn = _RENDER.get(b.get("type"))
        if fn:
            out.append(fn(b))
    # Append a references strip from the top-level `references` if present.
    refs = arg.get("references")
    if refs:
        out.append(_refs({"items": refs}))
    return "\n".join(out)


# CSS for the argument section — editorial idiom, scoped under #argument so it
# composes cleanly with build_frontend.py's stylesheet.
ARGUMENT_CSS = r"""
  /* ---------- argument (narrative essay) ---------- */
  #argument{padding:40px 0 38px}
  #argument .col{max-width:46rem}
  .arg-kicker{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent2);
    font-weight:700;margin:30px 0 6px}
  #argument .arg-kicker:first-child{margin-top:0}
  .arg-h{font-family:Georgia,serif;font-size:25px;line-height:1.15;letter-spacing:-.01em;margin:2px 0 14px}
  .arg-lead{font-size:20px;line-height:1.5;color:var(--ink);margin:0 0 16px}
  .arg-lead.dropcap::first-letter{float:left;font-family:Georgia,serif;font-size:62px;line-height:.82;
    padding:6px 10px 0 0;color:var(--accent)}
  .arg-p{font-size:16px;line-height:1.62;color:var(--ink2);margin:0 0 15px}
  .arg-p cite{font-style:italic;color:var(--ink2)}
  .arg-pull{margin:22px 0;padding:4px 0 4px 20px;border-left:3px solid var(--accent);
    font-family:Georgia,serif;font-size:21px;line-height:1.34;color:var(--ink);font-style:italic}
  .arg-pull em{font-style:normal}
  /* framework 2×2 */
  .arg-fw{margin:26px 0 22px}
  .arg-fw-frame{display:grid;grid-template-columns:auto minmax(0,1fr);column-gap:14px;align-items:stretch}
  .arg-fw-y{
    display:flex;align-items:center;justify-content:center;writing-mode:vertical-rl;
    transform:rotate(180deg);font-size:11.5px;font-weight:600;color:var(--muted);
    padding:10px 0;white-space:nowrap;
  }
  .arg-fw-body{display:flex;flex-direction:column;gap:10px;min-width:0}
  .arg-fw-x{text-align:center;font-size:11.5px;font-weight:600;color:var(--muted);padding:0 6px}
  .arg-fw-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:0}
  .arg-cell{border:1px solid var(--line);border-radius:13px;padding:14px 16px;background:#fff;min-height:108px}
  .arg-cell.tl{border-top-width:3px}.arg-cell.tr{border-top-width:3px}
  .arg-cell-tag{display:inline-block;font-size:11px;font-weight:700;text-transform:uppercase;
    letter-spacing:.05em;padding:2px 9px;border-radius:10px;color:#fff;margin-bottom:8px}
  .arg-cell p{margin:0;font-size:13px;line-height:1.5;color:var(--ink2)}
  .arg-cell.whitespace{border-color:#cfe0ec}.arg-cell.whitespace .arg-cell-tag{background:var(--whitespace)}
  .arg-cell.earning{border-color:#cfe6d4}.arg-cell.earning .arg-cell-tag{background:var(--earning-s)}
  .arg-cell.exposed{border-color:#f0cfcd}.arg-cell.exposed .arg-cell-tag{background:var(--exposed)}
  .arg-cell.sidelined{border-color:var(--line)}.arg-cell.sidelined .arg-cell-tag{background:var(--sidelined)}
  .arg-cap{font-size:12.5px;color:var(--muted);margin-top:4px}
  .arg-refs{list-style:none;padding:0;margin:24px 0 0;display:flex;flex-direction:column;gap:5px;
    border-top:1px solid var(--line);padding-top:14px}
  .arg-refs li{font-size:13px}.arg-refs a{font-weight:600;text-decoration:none}
  .arg-refs a:hover{text-decoration:underline}.arg-ref-a{color:var(--muted)}
  @media(max-width:780px){.arg-lead{font-size:18px}.arg-fw-frame{grid-template-columns:1fr}.arg-fw-y{display:none}.arg-fw-grid{grid-template-columns:1fr}
    .arg-ax-y{display:none}}
"""


def _preview(arg):
    body = render_argument(arg)
    html = (
        '<!doctype html><meta charset="utf-8">'
        '<style>:root{--ink:#15282e;--ink2:#33474e;--muted:#647077;--line:#dde4e6;--bg:#fbfcfc;'
        '--accent:#1F4E5C;--accent2:#2E7D8A;--exposed:#cf4a45;--earning-s:#34894b;--whitespace:#3f7fb0;'
        '--sidelined:#9aa7ad}body{font-family:ui-sans-serif,system-ui,sans-serif;background:var(--bg);'
        'color:var(--ink);margin:0}.wrap{max-width:1120px;margin:0 auto;padding:0 22px}</style>'
        + ARGUMENT_CSS.replace("/* ---------- argument (narrative essay) ---------- */", "<style>") + "</style>"
        '<div class="wrap"><section id="argument"><div class="col">' + body + '</div></section></div>'
    )
    out = os.path.join(ROOT, "site", "argument.preview.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(html)
    return out


def _check(arg):
    problems = []
    blocks = arg.get("blocks", [])
    if not blocks:
        problems.append("no blocks")
    for i, b in enumerate(blocks):
        t = b.get("type")
        if t not in VALID_TYPES:
            problems.append(f"block {i}: unknown type {t!r}")
        if t in ("kicker", "h", "lead", "p", "pull") and not b.get("text"):
            problems.append(f"block {i} ({t}): empty text")
        if t == "framework":
            quads = {c.get("quad") for c in b.get("cells", [])}
            missing = {"whitespace", "earning_it", "sidelined", "exposed"} - quads
            if missing:
                problems.append(f"block {i} (framework): missing quadrants {sorted(missing)}")
    from collections import Counter
    counts = Counter(b.get("type") for b in blocks)
    print(f"argument contract v{arg.get('version','?')} — {len(blocks)} blocks: "
          + ", ".join(f"{k}×{v}" for k, v in counts.items()))
    print(f"references: {len(arg.get('references', []))}  grounding: {', '.join(arg.get('grounding', []))}")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  - " + p)
    else:
        print("OK — contract is renderable.")
    return not problems


if __name__ == "__main__":
    arg = load_argument()
    if "--preview" in sys.argv:
        print("wrote", _preview(arg))
    else:
        ok = _check(arg)
        sys.exit(0 if ok else 1)
