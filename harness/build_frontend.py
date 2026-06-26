#!/usr/bin/env python3
"""NFRI Stage 6: build a self-contained static front-end (the 2x2 index) from the
scored dataset. No external dependencies — embeds data inline, renders an SVG
scatter + ranked table. Output: site/index.html + site/data/* for download."""
import csv
import json
import os
import re
import shutil
from typing import Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SITE_DIR = os.path.join(ROOT, "site")
SITE_DATA = os.path.join(SITE_DIR, "data")


def first_source(rec):
    for axis in ("preparedness_inputs", "exposure_inputs"):
        for sf in rec[axis].values():
            if sf.get("sources"):
                return sf["sources"][0]
    return ""


CONF = {"high": 3, "medium": 2, "low": 1}
CONF_NAME = {3: "high", 2: "medium", 1: "low"}


def overall_conf(rec):
    ranks = [CONF[sf["confidence"]] for ax in ("exposure_inputs", "preparedness_inputs") for sf in rec[ax].values()]
    return CONF_NAME.get(round(sum(ranks) / len(ranks)), "low")


def parse_calibration(calibration: Optional[str]) -> Tuple[float, float]:
    if calibration:
        m = re.search(r"exp>=([\d.]+)\s+prep>=([\d.]+)", calibration)
        if m:
            return float(m.group(1)), float(m.group(2))
    return 50.0, 50.0


def load_records():
    opt = os.path.join(DATA_DIR, "records.optimized.json")
    src = opt if os.path.exists(opt) else os.path.join(DATA_DIR, "records.scored.json")
    return json.load(open(src)), src


def export_downloads(records_src: str) -> None:
    os.makedirs(SITE_DATA, exist_ok=True)
    for name in ("records.optimized.json", "records.scored.json", "dataset.csv"):
        src = os.path.join(DATA_DIR, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(SITE_DATA, name))
    if not os.path.exists(os.path.join(SITE_DATA, "dataset.csv")):
        csv_path = os.path.join(SITE_DATA, "dataset.csv")
        with open(csv_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["entity_id", "name", "layer", "entity_type", "exposure", "preparedness",
                        "margin_of_safety", "quadrant", "confidence", "calibration"])
            for r in json.load(open(records_src)):
                s = r.get("scores") or {}
                w.writerow([r["entity_id"], r["name"], r["layer"], r["entity_type"],
                            s.get("exposure_0_100"), s.get("preparedness_0_100"),
                            s.get("margin_of_safety"), s.get("quadrant"),
                            s.get("overall_confidence"), s.get("calibration")])


def main():
    RECS, records_src = load_records()
    export_downloads(records_src)

    cut_exp, cut_prep = 50.0, 50.0
    pts = []
    for r in RECS:
        s = r.get("scores") or {}
        if not s:
            continue
        if "overall_confidence" not in s:
            s["overall_confidence"] = overall_conf(r)
        ce, cp = parse_calibration(s.get("calibration"))
        cut_exp, cut_prep = ce, cp
        pts.append({
            "id": r["entity_id"], "name": r["name"], "layer": r["layer"],
            "type": r["entity_type"], "exp": s["exposure_0_100"], "prep": s["preparedness_0_100"],
            "mos": s["margin_of_safety"], "quad": s["quadrant"], "conf": s["overall_confidence"],
            "note": r.get("notes") or "", "src": first_source(r),
        })

    DATA_JSON = json.dumps(pts)
    CAL_JSON = json.dumps({"cutExp": cut_exp, "cutPrep": cut_prep})
    SNAPSHOT = RECS[0]["provenance"]["last_checked"]
    N = len(pts)

    HTML = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Non-Firm Power Risk Index — prototype</title>
<style>
  :root{ --ink:#16323b; --accent:#1F4E5C; --accent2:#2E7D8A; --muted:#5a6b72; --line:#d7dee1; --bg:#fbfdfd;
         --exposed:#d9534f; --earning:#3f9e57; --whitespace:#3f7fb0; --sidelined:#9aa7ad; }
  *{box-sizing:border-box} body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);background:var(--bg)}
  .wrap{max-width:1060px;margin:0 auto;padding:28px 20px 60px}
  h1{font-size:26px;margin:0 0 2px} .sub{color:var(--muted);font-size:14px;margin:0 0 4px}
  .tag{display:inline-block;background:#e7f0f2;color:var(--accent);border-radius:20px;padding:2px 10px;font-size:12px;margin-top:6px}
  .dl{margin:14px 0 0;display:flex;gap:10px;flex-wrap:wrap}
  .dl a{font-size:13px;color:var(--accent);text-decoration:none;border:1px solid var(--line);border-radius:8px;padding:6px 12px;background:#fff}
  .dl a:hover{border-color:var(--accent2)}
  .controls{margin:18px 0 6px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  .controls button{border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:8px;padding:6px 12px;font-size:13px;cursor:pointer}
  .controls button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
  .panel{background:#fff;border:1px solid var(--line);border-radius:12px;padding:10px;margin-top:10px}
  svg{width:100%;height:auto;display:block}
  .legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;color:var(--muted);margin:10px 4px 0}
  .legend i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:5px;vertical-align:-1px}
  table{width:100%;border-collapse:collapse;font-size:13px;margin-top:8px}
  th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line)}
  th{color:var(--muted);font-weight:600;cursor:pointer;user-select:none}
  td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
  .pill{font-size:11px;padding:1px 7px;border-radius:10px;color:#fff}
  .conf{font-size:11px;color:var(--muted)}
  #tip{position:fixed;pointer-events:none;opacity:0;transition:opacity .12s;background:#fff;border:1px solid var(--line);
       box-shadow:0 6px 24px rgba(0,0,0,.12);border-radius:10px;padding:10px 12px;max-width:300px;font-size:12.5px;z-index:9}
  #tip h4{margin:0 0 4px;font-size:13px} #tip .q{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.04em}
  #tip a{color:var(--accent2)} .foot{color:var(--muted);font-size:12px;margin-top:22px;line-height:1.5}
</style></head>
<body><div class="wrap">
  <h1>The Non-Firm Power Risk Index</h1>
  <p class="sub">Who carries — and who is prepared for — interruptible-power risk across UK energy &amp; data-centre infrastructure.</p>
  <span class="tag">Prototype · __N__ entities · snapshot __SNAPSHOT__ · median cut exposure≥__CUTEXP__ prep≥__CUTPREP__</span>
  <div class="dl">
    <a href="data/dataset.csv" download>Download CSV ↓</a>
    <a href="data/records.optimized.json" download>Download JSON ↓</a>
  </div>

  <div class="controls">
    <span style="font-size:13px;color:var(--muted)">Layer:</span>
    <button data-layer="all" class="on">All</button>
    <button data-layer="1">Carriers &amp; syndicates</button>
    <button data-layer="2">MGAs &amp; brokers</button>
    <button data-layer="3">Assets</button>
  </div>

  <div class="panel">
    <svg id="plot" viewBox="0 0 920 560" role="img" aria-label="Scatter of preparedness versus exposure"></svg>
    <div class="legend">
      <span><i style="background:var(--earning)"></i>Earning it (high exp · high prep)</span>
      <span><i style="background:var(--exposed)"></i>Exposed (high exp · low prep)</span>
      <span><i style="background:var(--whitespace)"></i>Whitespace (low exp · high prep)</span>
      <span><i style="background:var(--sidelined)"></i>Sidelined (low · low)</span>
      <span>· point size = data confidence · dashed lines = in-sample medians</span>
    </div>
  </div>

  <div class="panel">
    <table id="tbl"><thead><tr>
      <th data-k="name">Entity</th><th data-k="layer" class="num">L</th>
      <th data-k="exp" class="num">Exposure</th><th data-k="prep" class="num">Prepared</th>
      <th data-k="mos" class="num">Margin of Safety</th><th data-k="quad">Quadrant</th><th data-k="conf">Conf.</th>
    </tr></thead><tbody></tbody></table>
  </div>

  <p class="foot">
    <b>How to read it.</b> Margin of Safety = Preparedness − Exposure. Quadrants use <b>median cut-lines</b>
    (not fixed 50/50). Scores fuse <b>latent</b> (research) and <b>deterministic</b> (register/filing) inputs
    per <code>contract/MODEL_SPEC.md</code> — credibility-weighted, fully cited in <code>contract/citations.json</code>.
    Not investment advice.
  </p>
</div>
<div id="tip"></div>

<script>
const DATA = __DATA__;
const CAL = __CAL__;
const QCOL = {exposed:'#d9534f', earning_it:'#3f9e57', whitespace:'#3f7fb0', sidelined:'#9aa7ad'};
const QLAB = {exposed:'Exposed', earning_it:'Earning it', whitespace:'Whitespace', sidelined:'Sidelined'};
const CSIZE = {high:9, medium:7, low:5};
let layerFilter = 'all', sortK = 'mos', sortDir = -1;

const svg = document.getElementById('plot');
const NS = 'http://www.w3.org/2000/svg';
const PAD = {l:64, r:24, t:24, b:54}, W=920, H=560;
const x = v => PAD.l + (v/100)*(W-PAD.l-PAD.r);
const y = v => H-PAD.b - (v/100)*(H-PAD.t-PAD.b);
function el(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}

function drawPlot(){
  svg.innerHTML='';
  const mx=x(CAL.cutExp), my=y(CAL.cutPrep);
  const quads=[['whitespace',PAD.l,PAD.t,mx-PAD.l,my-PAD.t],['earning_it',mx,PAD.t,x(100)-mx,my-PAD.t],
               ['sidelined',PAD.l,my,mx-PAD.l,y(0)-my],['exposed',mx,my,x(100)-mx,y(0)-my]];
  quads.forEach(([q,xx,yy,w,h])=>{svg.appendChild(el('rect',{x:xx,y:yy,width:w,height:h,fill:QCOL[q],opacity:.07}));});
  svg.appendChild(el('line',{x1:mx,y1:PAD.t,x2:mx,y2:y(0),stroke:'#c2cdd1','stroke-dasharray':'4 4'}));
  svg.appendChild(el('line',{x1:PAD.l,y1:my,x2:x(100),y2:my,stroke:'#c2cdd1','stroke-dasharray':'4 4'}));
  const ql=[['whitespace',PAD.l+10,PAD.t+18,'start'],['earning_it',x(100)-10,PAD.t+18,'end'],
            ['sidelined',PAD.l+10,y(0)-10,'start'],['exposed',x(100)-10,y(0)-10,'end']];
  ql.forEach(([q,xx,yy,anc])=>{const t=el('text',{x:xx,y:yy,'text-anchor':anc,'font-size':12,'font-weight':700,fill:QCOL[q],opacity:.8});t.textContent=QLAB[q];svg.appendChild(t);});
  svg.appendChild(el('line',{x1:PAD.l,y1:y(0),x2:x(100),y2:y(0),stroke:'#9aa7ad'}));
  svg.appendChild(el('line',{x1:PAD.l,y1:PAD.t,x2:PAD.l,y2:y(0),stroke:'#9aa7ad'}));
  for(let v=0;v<=100;v+=25){
    const tx=el('text',{x:x(v),y:y(0)+20,'text-anchor':'middle','font-size':11,fill:'#5a6b72'});tx.textContent=v;svg.appendChild(tx);
    const ty=el('text',{x:PAD.l-10,y:y(v)+4,'text-anchor':'end','font-size':11,fill:'#5a6b72'});ty.textContent=v;svg.appendChild(ty);
  }
  const axl=el('text',{x:(PAD.l+x(100))/2,y:H-14,'text-anchor':'middle','font-size':12.5,'font-weight':600,fill:'#16323b'});axl.textContent='Exposure  →';svg.appendChild(axl);
  const ayl=el('text',{x:18,y:(PAD.t+y(0))/2,'text-anchor':'middle','font-size':12.5,'font-weight':600,fill:'#16323b',transform:`rotate(-90 18 ${(PAD.t+y(0))/2})`});ayl.textContent='Preparedness  →';svg.appendChild(ayl);
  const cutLbl=el('text',{x:mx+4,y:my-6,'font-size':10,fill:'#5a6b72'});cutLbl.textContent=`med ${CAL.cutExp}/${CAL.cutPrep}`;svg.appendChild(cutLbl);
  DATA.filter(p=>layerFilter==='all'||p.layer==+layerFilter).forEach(p=>{
    const g=el('g',{cursor:'pointer'});
    const c=el('circle',{cx:x(p.exp),cy:y(p.prep),r:CSIZE[p.conf]||5,fill:QCOL[p.quad],stroke:'#fff','stroke-width':1.5,'fill-opacity':.92});
    const lab=el('text',{x:x(p.exp)+ (CSIZE[p.conf]||5)+3,y:y(p.prep)+3,'font-size':10.5,fill:'#16323b'});lab.textContent=shortName(p.name);
    g.appendChild(c);g.appendChild(lab);
    g.addEventListener('mousemove',e=>showTip(e,p)); g.addEventListener('mouseleave',hideTip);
    svg.appendChild(g);
  });
}
function shortName(n){return n.replace(' — ',' ').replace(' (Willis Towers Watson)','').replace('Data Centres','DC').slice(0,22);}

const tip=document.getElementById('tip');
function showTip(e,p){
  tip.innerHTML=`<div class="q" style="color:${QCOL[p.quad]}">${QLAB[p.quad]}</div>
    <h4>${p.name}</h4>
    <div style="color:#5a6b72;margin-bottom:5px">Layer ${p.layer} · ${p.type} · conf: ${p.conf}</div>
    <div>Exposure <b>${p.exp}</b> · Preparedness <b>${p.prep}</b> · MoS <b>${p.mos>0?'+':''}${p.mos}</b></div>
    <div style="margin-top:6px;color:#33474e">${p.note?p.note.slice(0,180):''}</div>
    ${p.src?`<div style="margin-top:6px"><a href="${p.src}" target="_blank" rel="noopener">source ↗</a></div>`:''}`;
  tip.style.left=Math.min(e.clientX+14, window.innerWidth-320)+'px';
  tip.style.top=(e.clientY+14)+'px'; tip.style.opacity=1;
}
function hideTip(){tip.style.opacity=0;}

function drawTable(){
  const tb=document.querySelector('#tbl tbody'); tb.innerHTML='';
  const rows=DATA.filter(p=>layerFilter==='all'||p.layer==+layerFilter)
    .sort((a,b)=>{const av=a[sortK],bv=b[sortK];return (av>bv?1:av<bv?-1:0)*sortDir;});
  rows.forEach(p=>{
    const tr=document.createElement('tr');
    tr.innerHTML=`<td>${p.name}</td><td class="num">${p.layer}</td>
      <td class="num">${p.exp}</td><td class="num">${p.prep}</td>
      <td class="num"><b>${p.mos>0?'+':''}${p.mos}</b></td>
      <td><span class="pill" style="background:${QCOL[p.quad]}">${QLAB[p.quad]}</span></td>
      <td class="conf">${p.conf}</td>`;
    tb.appendChild(tr);
  });
}
document.querySelectorAll('#tbl th').forEach(th=>th.addEventListener('click',()=>{
  const k=th.dataset.k; sortDir = (sortK===k)?-sortDir:(k==='name'||k==='quad'||k==='conf'?1:-1); sortK=k; drawTable();
}));
document.querySelectorAll('.controls button').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('.controls button').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); layerFilter=b.dataset.layer; drawPlot(); drawTable();
}));
drawPlot(); drawTable();
</script>
</body></html>"""

    HTML = (HTML.replace("__DATA__", DATA_JSON).replace("__CAL__", CAL_JSON)
            .replace("__SNAPSHOT__", SNAPSHOT).replace("__N__", str(N))
            .replace("__CUTEXP__", str(cut_exp)).replace("__CUTPREP__", str(cut_prep)))

    os.makedirs(SITE_DIR, exist_ok=True)
    out = os.path.join(SITE_DIR, "index.html")
    open(out, "w").write(HTML)
    print("wrote", out, "(", len(HTML), "bytes,", len(pts), "points )")


if __name__ == "__main__":
    main()
