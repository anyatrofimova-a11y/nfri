"""Client bundle — single init, see ARCHITECTURE.md."""

CLIENT_JS = r"""const D = /*__PAYLOAD__*/null;
const QLAB={exposed:'Exposed',earning_it:'Earning it',whitespace:'Whitespace',sidelined:'Sidelined'};
const QVAR={exposed:'--exposed',earning_it:'--earning-s',whitespace:'--whitespace',sidelined:'--sidelined'};
function qColor(q){return cssVar(QVAR[q])||cssVar('--muted');}
const CSIZE={high:10,medium:7.5,low:5.5};
const LAYER={1:'Carriers & syndicates',2:'MGAs & brokers',3:'Assets',4:'Capacity & reins.'};
let layerF='all', quadF='all', sortK='mos', sortDir=-1;
let searchQ='', benchMetric='mos', benchFilter='l1';
const $=s=>document.querySelector(s), NS='http://www.w3.org/2000/svg';
let motionIO=null;
function observeMotion(root){
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const vh=window.innerHeight||800;
  const inView=el=>{
    const r=el.getBoundingClientRect();
    return r.bottom>0&&r.top<vh;
  };
  (root||document).querySelectorAll('.reveal,.stagger').forEach(el=>{
    if(reduced||inView(el)){el.classList.add('in');return;}
    if(el._motionBound)return; el._motionBound=true;
    if(!motionIO){
      motionIO=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');motionIO.unobserve(e.target);}});},{threshold:0.02,rootMargin:'0px 0px -8% 0px'});
    }
    motionIO.observe(el);
  });
}
function initMotion(){observeMotion();}
function el(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}
function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function initials(n){return (n||'?').split(/\s+/).map(w=>w[0]).join('').slice(0,2).toUpperCase();}
function logoHtml(p, cls=''){
  const ini=initials(p.name);
  return `<span class="ent-logo-wrap ${cls}"><img class="ent-logo" src="${esc(p.logo)}" alt="" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';"><span class="ent-logo-fallback" style="display:none">${ini}</span></span>`;
}
function avatarHtml(p){
  const ini=initials(p.name);
  return `<div class="ent-avatar"><img src="${esc(p.logo)}" alt="" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';"><span class="ent-logo-fallback" style="display:none">${ini}</span></div>`;
}
function cssVar(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim();}
initMotion();

/* ---------- banner + meta ---------- */
(function(){
  const pct=Math.round(D.share*100), ok=D.share>=0.60;
  // Per-entity provenance, not a blanket warning: state the evidence share as a neutral fact and
  // point to each entity's own provenance (drill-down). Granular honesty replaces the global banner.
  const sourced = (D.pts||[]).filter(p=>(p.detExp+p.detPrep)>0).length;
  $('#banner').className='banner'+(ok?' ok':'');
  $('#banner').innerHTML = ok
    ? `<div>✓</div><div><b>Measured.</b> ${pct}% of the blended score rests on measured/disclosed evidence (≥60% gate).</div>`
    : `<div></div><div><b>Outside-in estimate.</b> ${pct}% of the blended score rests on measured/disclosed evidence`
      + `${sourced?` · ${sourced} of ${D.n} entities carry measured/disclosed sub-factors`:''}; the rest is sourced`
      + ` research judgement. Every rating links to its source — open any entity for its provenance.</div>`;
  $('#status-meta').innerHTML=`<span><b>${D.n}</b> entities scored</span>
    <span>snapshot ${esc(D.snapshot)}</span>
    <span>median cut · exposure ≥ ${D.cal.cutExp} · prep ≥ ${D.cal.cutPrep}</span>
    <span>${D.graph.nodes.length} knowledge nodes</span>`;
})();

/* ---------- filters ---------- */
(function(){
  const f=$('#scatter-filters'); if(!f)return;
  const layers=[['all','All layers'],['1','Carriers'],['2','MGAs & brokers'],['3','Assets']];
  const quads=[['all','All'],['exposed','Exposed'],['earning_it','Earning it'],['whitespace','Whitespace'],['sidelined','Sidelined']];
  f.innerHTML=`<div class="filter-grp"><span class="filter-label">Layer</span><span class="filter-seg">${layers.map(([v,l],i)=>
    `<button type="button" data-t="layer" data-v="${v}" class="filter-btn${i===0?' on':''}">${l}</button>`).join('')}</span></div>
    <div class="filter-grp"><span class="filter-label">Quadrant</span><span class="filter-seg">${quads.map(([v,l],i)=>
    `<button type="button" data-t="quad" data-v="${v}" class="filter-btn${i===0?' on':''}">${l}</button>`).join('')}</span></div>`;
  f.querySelectorAll('.filter-btn').forEach(b=>b.onclick=()=>{
    const t=b.dataset.t;
    f.querySelectorAll(`.filter-btn[data-t="${t}"]`).forEach(x=>x.classList.remove('on'));
    b.classList.add('on'); if(t==='layer')layerF=b.dataset.v; else quadF=b.dataset.v;
    plotHoverId=null; refreshIndex();
    if(b.dataset.v!=='all')openMethodDrawer(t,b.dataset.v); else closeDrawer();
  });
})();
const shown=()=>D.pts.filter(p=>{
  const q=searchQ.trim().toLowerCase();
  return (layerF==='all'||p.layer==+layerF)&&(quadF==='all'||p.quad===quadF)
    &&(!q||p.name.toLowerCase().includes(q)||p.id.toLowerCase().includes(q)||(p.type||'').toLowerCase().includes(q));
});
function sorted(list){
  const key=p=>sortK==='meas'?(p.detExp+p.detPrep)/2:p[sortK];
  return [...list].sort((a,b)=>{const x=key(a),y=key(b);return (x>y?1:x<y?-1:0)*sortDir;});
}

/* ---------- index toolbar + entity cards ---------- */
(function(){
  const tb=$('#idx-toolbar'); if(!tb)return;
  tb.querySelector('#idx-search')?.addEventListener('input',e=>{searchQ=e.target.value;refreshIndex();});
    tb.querySelectorAll('.idx-btn').forEach(b=>b.onclick=()=>{
    const t=b.dataset.t,v=b.dataset.v;
    if(t==='sort'){sortK=v==='mos'?'mos':v;sortDir=-1;refreshIndex();return;}
    tb.querySelectorAll(`.idx-btn[data-t="${t}"]`).forEach(x=>x.classList.remove('on'));
    b.classList.add('on');
    if(t==='layer')layerF=v; else if(t==='quad')quadF=v;
    refreshIndex();
    if((t==='layer'||t==='quad')&&v!=='all')openMethodDrawer(t,v); else if(t==='layer'||t==='quad')closeDrawer();
  });
})();

function scoreBars(p){
  const mosCls=p.mos>=0?'pos':'neg';
  const lo=Math.min(p.exp,p.prep), hi=Math.max(p.exp,p.prep);
  const bar=(lbl,val,cls)=>`<div class="ent-bar-row">
    <span class="ent-bar-lbl">${lbl}</span>
    <div class="ent-bar-track"><span class="ent-bar-fill ${cls}" style="width:${val}%"></span></div>
    <span class="ent-bar-val">${val}</span></div>`;
  return `<div class="ent-viz">
    <div class="ent-mos-row">
      <span class="ent-mos-label">Margin of safety</span>
      <span class="ent-mos ${mosCls}">${p.mos>0?'+':''}${p.mos}</span>
    </div>
    ${bar('Exp',p.exp,'exp')}${bar('Prep',p.prep,'prep')}
    <div class="spread-wrap">
      <div class="spread-label">Exposure ↔ Preparedness gap</div>
      <div class="spread-track">
        <span class="spread-band" style="left:${lo}%;width:${Math.max(hi-lo,0.5)}%;background:${p.mos>=0?'var(--earning-s)':'var(--exposed)'}"></span>
        <span class="spread-tick exp" style="left:${p.exp}%"></span>
        <span class="spread-tick prep" style="left:${p.prep}%"></span>
      </div>
    </div>
  </div>`;
}

function renderCards(){
  const list=$('#card-list'); if(!list)return; list.innerHTML='';
  const rows=sorted(shown());
  $('#idx-count').textContent=`${rows.length} of ${D.n}`;
  rows.forEach(p=>{
    const div=document.createElement('div'); div.className='ent-card';
    div.innerHTML=`<div class="ent-id">${avatarHtml(p)}
      <div><div class="ent-name">${esc(p.name)}<span class="quad-tag">${QLAB[p.quad]}</span></div>
      <div class="ent-meta">L${p.layer} · ${esc(LAYER[p.layer]||p.type)}</div></div></div>
      ${scoreBars(p)}`;
    div.onclick=()=>openDrawer(p.id); list.appendChild(div);
  });
}

function meas(p){return (p.detExp+p.detPrep)/2;}
function shortName(n){
  return n.replace(' — ',' ').replace(' (Willis Towers Watson)','').replace('Data Centres','DC')
    .replace('Corporate Solutions','Corp Sol').replace('Specialty Markets','Spec Mkts').trim();
}

const BENCH={
  mos:{label:'Margin of Safety',axis:'MoS',note:'MoS = Preparedness − Exposure. Positive margin means preparedness exceeds exposure.',fmt:v=>(v>0?'+':'')+v,pick:p=>p.mos,min:-30,max:80},
  exp:{label:'Exposure',axis:'Score (0–100)',note:'Gross exposure to non-firm power risk before underwriting mitigation.',fmt:v=>v,pick:p=>p.exp,min:0,max:100},
  prep:{label:'Preparedness',axis:'Score (0–100)',note:'Capacity to underwrite, price, and manage interruptible power risk.',fmt:v=>v,pick:p=>p.prep,min:0,max:100},
  meas:{label:'Measured share',axis:'Measured (%)',note:'Share of sub-factor weight backed by register or filing evidence.',fmt:v=>Math.round(v)+'%',pick:p=>Math.round(meas(p)*100),min:0,max:100},
};

function benchPool(){
  if(benchFilter==='all') return D.pts;
  if(benchFilter==='l1') return D.pts.filter(p=>p.layer===1);
  return D.pts.filter(p=>p.type===benchFilter);
}

function benchPct(val, cfg){
  const lo=cfg.min, hi=cfg.max, span=Math.max(hi-lo,1);
  return Math.max(2, Math.min(100, ((val-lo)/span)*100));
}

function renderBenchChart(pts, cfg){
  const chart=$('#bench-chart'); if(!chart)return;
  const top=pts.slice(0, Math.min(12, pts.length));
  if(!top.length){ chart.innerHTML=''; return; }
  const lo=cfg.min, hi=cfg.max, span=Math.max(hi-lo,1);
  const W=Math.max(640, top.length*72), H=260;
  const pad={l:44,r:16,t:28,b:52}, pw=W-pad.l-pad.r, ph=H-pad.t-pad.b;
  const slot=pw/top.length, barW=Math.min(44, slot*0.55);
  let svg=`<svg class="bench-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="Top entities by ${cfg.label}">`;
  const ticks=benchMetric==='mos'?[-20,0,20,40,60,80]:[0,25,50,75,100];
  ticks.forEach(t=>{
    const y=pad.t+ph-((t-lo)/span)*ph;
    svg+=`<line x1="${pad.l}" y1="${y}" x2="${W-pad.r}" y2="${y}" stroke="#E8E8E8" stroke-width="1"/>`;
    svg+=`<text x="${pad.l-8}" y="${y+4}" text-anchor="end" font-size="10" fill="#737373">${t}${benchMetric==='meas'?'%':''}</text>`;
  });
  if(benchMetric==='mos'){
    const zy=pad.t+ph-((0-lo)/span)*ph;
    svg+=`<line x1="${pad.l}" y1="${zy}" x2="${W-pad.r}" y2="${zy}" stroke="#B8B8B8" stroke-width="1.5" stroke-dasharray="4 3"/>`;
  }
  svg+=`<text x="12" y="${pad.t+ph/2}" font-size="10" fill="#737373" transform="rotate(-90 12 ${pad.t+ph/2})" text-anchor="middle">${cfg.axis}</text>`;
  top.forEach((p,i)=>{
    const val=cfg.pick(p);
    const barH=Math.max(4, ((val-lo)/span)*ph);
    const cx=pad.l+i*slot+slot/2;
    const x=cx-barW/2, y=pad.t+ph-barH;
    svg+=`<g class="bench-svg-col" data-id="${p.id}" tabindex="0" role="button" aria-label="${esc(p.name)} ${cfg.fmt(val)}">
      <rect x="${x}" y="${y}" width="${barW}" height="${barH}" rx="4" fill="${qColor(p.quad)}"/>
      <text x="${cx}" y="${y-8}" text-anchor="middle" font-size="12" font-weight="600" fill="#141414">${cfg.fmt(val)}</text>
      <rect x="${cx-14}" y="${y+6}" width="28" height="28" rx="4" fill="#fff" stroke="#E8E8E8"/>
      <image href="${esc(p.logo)}" x="${cx-11}" y="${y+9}" width="22" height="22" preserveAspectRatio="xMidYMid meet"/>
      <text x="${cx}" y="${H-16}" text-anchor="middle" font-size="10" fill="#737373">${esc(shortName(p.name).slice(0,14))}</text>
    </g>`;
  });
  svg+='</svg>';
  chart.innerHTML=svg;
  chart.querySelectorAll('[data-id]').forEach(g=>{
    g.onclick=()=>openDrawer(g.dataset.id);
    g.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openDrawer(g.dataset.id);}};
  });
}

function renderBenchmark(){
  const list=$('#bench-list'); if(!list)return;
  const cfg=BENCH[benchMetric];
  const pts=[...benchPool()].sort((a,b)=>cfg.pick(b)-cfg.pick(a));
  $('#bench-note').textContent=cfg.note;
  $('#bench-metric-label').innerHTML=`Sorted by <b>${cfg.label}</b> · ${pts.length} entities`;
  $('#bench-count').textContent=`${pts.length} total`;
  const leg=$('#bench-legend');
  if(leg) leg.innerHTML=Object.entries(QLAB).map(([k,l])=>`<span><i style="background:${qColor(k)}"></i>${l}</span>`).join('');
  renderBenchChart(pts, cfg);
  list.innerHTML=pts.length?pts.map((p,i)=>{
    const val=cfg.pick(p);
    const pct=benchPct(val, cfg);
    return `<button type="button" class="bench-row" data-id="${p.id}" role="listitem">
      <span class="bench-rank">${i+1}</span>
      ${logoHtml(p,'sm')}
      <div class="bench-row-id">
        <span class="bench-row-name">${esc(p.name)}</span>
        <span class="bench-row-tag quad-${p.quad}">${QLAB[p.quad]}</span>
      </div>
      <div class="bench-row-track">
        <div class="bench-row-fill quad-${p.quad}" style="width:${pct}%"></div>
        <span class="bench-row-val">${cfg.fmt(val)}</span>
      </div>
      <div class="bench-row-stats">
        <span>Exp <b>${p.exp}</b></span>
        <span>Prep <b>${p.prep}</b></span>
        <span>MoS <b>${p.mos>0?'+':''}${p.mos}</b></span>
      </div>
      <span class="bench-row-action" aria-hidden="true">→</span>
    </button>`;
  }).join(''):'<p style="padding:16px;color:var(--muted);font-size:14px">No entities match this filter.</p>';
  list.querySelectorAll('.bench-row').forEach(row=>row.onclick=()=>openDrawer(row.dataset.id));
}

(function(){
  $('#bench-tabs')?.querySelectorAll('.bench-tab').forEach(b=>b.onclick=()=>{
    benchMetric=b.dataset.m;
    $('#bench-tabs').querySelectorAll('.bench-tab').forEach(x=>x.classList.toggle('on',x===b));
    renderBenchmark();
  });
  $('#bench-filters')?.querySelectorAll('.bench-filter').forEach(b=>b.onclick=()=>{
    benchFilter=b.dataset.f;
    $('#bench-filters').querySelectorAll('.bench-filter').forEach(x=>x.classList.toggle('on',x===b));
    renderBenchmark();
  });
})();

function refreshIndex(){renderBenchmark();renderCards();draw();table();}

/* ---------- scatter ---------- */
const W=960,H=580,PAD={l:68,r:28,t:26,b:58};
const X=v=>PAD.l+(v/100)*(W-PAD.l-PAD.r), Y=v=>H-PAD.b-(v/100)*(H-PAD.t-PAD.b);
let plotHoverId=null;

function layoutPlotPoints(pts){
  const buckets={};
  pts.forEach(p=>{
    const key=`${Math.round(p.exp*2)/2}|${Math.round(p.prep*2)/2}`;
    (buckets[key]=buckets[key]||[]).push(p);
  });
  return pts.map(p=>{
    const key=`${Math.round(p.exp*2)/2}|${Math.round(p.prep*2)/2}`;
    const group=buckets[key], idx=group.indexOf(p), n=group.length;
    if(n<=1) return {p,ox:0,oy:0};
    const angle=(idx/n)*Math.PI*2-Math.PI/2;
    const spread=Math.min(26,5+n*3.5);
    return {p,ox:Math.cos(angle)*spread,oy:-Math.sin(angle)*spread};
  });
}

function plotLabel(g,cx,cy,text,above){
  const padX=6,padY=4,fs=11;
  const label=text.length>24?text.slice(0,22)+'…':text;
  const tw=Math.min(label.length*5.8+padX*2,168);
  const th=fs+padY*2;
  const lx=cx-tw/2, ly=above?cy-12-th:cy+12;
  g.appendChild(el('rect',{x:lx,y:ly,width:tw,height:th,rx:4,fill:cssVar('--bg-default'),stroke:cssVar('--line-subtle'),'stroke-width':1}));
  const t=el('text',{x:cx,y:ly+th-padY-1,'text-anchor':'middle','font-size':fs,'font-weight':600,fill:cssVar('--ink')});
  t.textContent=label; g.appendChild(t);
}

function draw(){
  const svg=$('#plot'); if(!svg)return; svg.innerHTML='';
  const mx=X(D.cal.cutExp), my=Y(D.cal.cutPrep);
  [['whitespace',PAD.l,PAD.t,mx-PAD.l,my-PAD.t],['earning_it',mx,PAD.t,X(100)-mx,my-PAD.t],
   ['sidelined',PAD.l,my,mx-PAD.l,Y(0)-my],['exposed',mx,my,X(100)-mx,Y(0)-my]]
   .forEach(([q,x,y,w,h])=>svg.appendChild(el('rect',{x,y,width:Math.max(0,w),height:Math.max(0,h),fill:qColor(q),opacity:.06})));
  svg.appendChild(el('line',{x1:mx,y1:PAD.t,x2:mx,y2:Y(0),stroke:cssVar('--chart-grid'),'stroke-dasharray':'4 4'}));
  svg.appendChild(el('line',{x1:PAD.l,y1:my,x2:X(100),y2:my,stroke:cssVar('--chart-grid'),'stroke-dasharray':'4 4'}));
  [['whitespace',PAD.l+10,PAD.t+18,'start'],['earning_it',X(100)-10,PAD.t+18,'end'],
   ['sidelined',PAD.l+10,Y(0)-12,'start'],['exposed',X(100)-10,Y(0)-12,'end']].forEach(([q,x,y,a])=>{
    const t=el('text',{x,y,'text-anchor':a,'font-size':12,'font-weight':700,fill:qColor(q),opacity:.85});t.textContent=QLAB[q];svg.appendChild(t);});
  svg.appendChild(el('line',{x1:PAD.l,y1:Y(0),x2:X(100),y2:Y(0),stroke:cssVar('--sidelined')}));
  svg.appendChild(el('line',{x1:PAD.l,y1:PAD.t,x2:PAD.l,y2:Y(0),stroke:cssVar('--sidelined')}));
  for(let v=0;v<=100;v+=25){
    let t=el('text',{x:X(v),y:Y(0)+20,'text-anchor':'middle','font-size':11,fill:cssVar('--muted')});t.textContent=v;svg.appendChild(t);
    let u=el('text',{x:PAD.l-10,y:Y(v)+4,'text-anchor':'end','font-size':11,fill:cssVar('--muted')});u.textContent=v;svg.appendChild(u);
  }
  let ax=el('text',{x:(PAD.l+X(100))/2,y:H-14,'text-anchor':'middle','font-size':12.5,'font-weight':600,fill:cssVar('--ink')});ax.textContent='Exposure →';svg.appendChild(ax);
  let ay=el('text',{x:18,y:(PAD.t+Y(0))/2,'text-anchor':'middle','font-size':12.5,'font-weight':600,fill:cssVar('--ink'),transform:`rotate(-90 18 ${(PAD.t+Y(0))/2})`});ay.textContent='Preparedness →';svg.appendChild(ay);

  layoutPlotPoints(shown()).forEach(({p,ox,oy})=>{
    const cx=X(p.exp)+ox, cy=Y(p.prep)+oy;
    const r=CSIZE[p.conf]||5.5, meas=(p.detExp+p.detPrep)/2;
    const hi=plotHoverId===p.id;
    const g=el('g',{class:'plot-dot','data-id':p.id});
    g.appendChild(el('circle',{cx,cy,r,fill:cssVar('--bg-default'),stroke:qColor(p.quad),'stroke-width':hi?2.5:1.5}));
    const ri=Math.max(1.4,(r-2)*Math.sqrt(Math.max(0,Math.min(1,meas))));
    if(ri>1.1){
      g.appendChild(el('circle',{cx,cy,r:ri,fill:qColor(p.quad),opacity:.85}));
    }
    if(hi){
      plotLabel(g,cx,cy,shortName(p.name),cy>Y(0)-72);
    }
    g.addEventListener('mouseenter',e=>{plotHoverId=p.id;draw();tip(e,p);});
    g.addEventListener('mouseleave',()=>{plotHoverId=null;draw();hideTip();});
    g.addEventListener('click',()=>openDrawer(p.id));
    svg.appendChild(g);
  });
}

/* ---------- tooltip ---------- */
let tipEl;
function tip(e,p){
  if(!tipEl){tipEl=document.createElement('div');tipEl.id='tip';tipEl.className='plot-tip';
    document.body.appendChild(tipEl);}
  tipEl.innerHTML=`<div class="tip-quad" style="color:${qColor(p.quad)}">${QLAB[p.quad]}</div>
    <div class="tip-name">${esc(p.name)}</div>
    <div class="tip-meta">L${p.layer} · ${esc(p.type)} · conf ${p.conf}</div>
    <div style="margin-top:4px">Exp <b>${p.exp}</b> · Prep <b>${p.prep}</b> · MoS <b>${p.mos>0?'+':''}${p.mos}</b></div>
    <div class="tip-meta" style="margin-top:3px">measured ${Math.round((p.detExp+p.detPrep)/2*100)}% · click for detail</div>`;
  tipEl.style.left=Math.min(e.clientX+14,innerWidth-300)+'px';tipEl.style.top=(e.clientY+14)+'px';tipEl.style.opacity=1;
}
function hideTip(){if(tipEl)tipEl.style.opacity=0;}

/* ---------- table ---------- */
function table(){
  const tb=$('#tbl tbody'); tb.innerHTML='';
  const rows=sorted(shown());
  rows.forEach(p=>{
    const tr=document.createElement('tr'); tr.className='row'; tr.onclick=()=>openDrawer(p.id);
    const m=Math.round(meas(p)*100);
    tr.innerHTML=`<td><span class="tbl-name">${logoHtml(p,'xs')}${esc(p.name)}</span></td><td class="num">${p.layer}</td>
      <td class="num">${p.exp}</td><td class="num">${p.prep}</td>
      <td class="num"><b>${p.mos>0?'+':''}${p.mos}</b></td>
      <td><span class="quad-label" style="color:${qColor(p.quad)}">${QLAB[p.quad]}</span></td>
      <td class="num"><span class="meas-track"><span class="meas-bar" style="width:${m}%"></span></span> ${m}%</td>
      <td class="text-muted">${p.conf}</td>`;
    tb.appendChild(tr);
  });
  tb.classList.add('stagger');
  observeMotion(tb);
}
document.querySelectorAll('#tbl th').forEach(th=>th.onclick=()=>{
  const k=th.dataset.k; sortDir=(sortK===k)?-sortDir:(['name','quad','conf'].includes(k)?1:-1); sortK=k; table();
});

/* ---------- entity drawer ---------- */
function quadCriteria(q){
  const e=D.cal.cutExp,p=D.cal.cutPrep;
  if(q==='exposed')return `Exposure ≥ ${e} · Preparedness < ${p}`;
  if(q==='earning_it')return `Exposure ≥ ${e} · Preparedness ≥ ${p}`;
  if(q==='whitespace')return `Exposure < ${e} · Preparedness ≥ ${p}`;
  if(q==='sidelined')return `Exposure < ${e} · Preparedness < ${p}`;
  return '';
}
function openMethodDrawer(kind,value){
  const m=(D.scatterMethod||{})[kind]?.[value]; if(!m)return;
  const count=D.pts.filter(p=>kind==='layer'?p.layer==+value:p.quad===value).length;
  const label=kind==='quad'?QLAB[value]:(m.title||LAYER[+value]||('L'+value));
  const tag=kind==='quad'?'Quadrant':'Layer';
  const color=kind==='quad'?qColor(value):'var(--accent2)';
  $('#drawer-name').innerHTML=`<span class="drawer-method-tag">${tag}</span> <span style="color:${color}">${esc(label)}</span>`;
  $('#drawer-meta').innerHTML=kind==='quad'?esc(quadCriteria(value)):`L${value} · ${count} of ${D.n} entities in this layer`;
  const anchor=m.anchor||(kind==='quad'?'two-axes':'layers');
  $('#drawer-body').innerHTML=`
    <p class="method-drawer-lead">${esc(m.lead||label)}</p>
    <p class="method-drawer-body">${esc(m.body||'')}</p>
    ${kind==='quad'?`<p class="method-drawer-criteria"><b>Cut rule.</b> ${esc(quadCriteria(value))}</p>`:''}
    ${m.role?`<p class="method-drawer-role">${esc(m.role)}</p>`:''}
    <div class="score-row method-drawer-stats">
      <div class="score-cell">In slice<b>${count}</b></div>
      <div class="score-cell">Share<b>${D.n?Math.round(count/D.n*100):0}%</b></div>
    </div>
    <p class="method-drawer-foot"><a href="methodology.html#${anchor}">Full methodology →</a></p>`;
  $('#drawer').classList.add('on'); $('#scrim').classList.add('on');
}
function ratbar(v){let s='<span class="ratbar">';for(let i=0;i<4;i++)s+=`<i class="${v>i?'on':''}"></i>`;return s+'</span>';}
function sfBlock(s){
  const cites=s.cites.map(c=>`<a href="#" onclick="citePop('${c}');return false">${c}</a>`).join(' ');
  const srcs=s.sources.map(u=>`<a href="${u}" target="_blank" rel="noopener">source ↗</a>`).join(' ');
  return `<div class="sf-card"><div class="sf-top"><span class="sf-name">${s.label}</span>
    <span class="sf-mode ${s.mode}">${s.mode}</span><span class="sf-weight">w ${s.weight}</span></div>
    <div class="sf-rationale">${esc(s.rationale)}</div>
    <div class="sf-evidence"><span class="text-muted">lat ${ratbar(s.lat)} · det ${s.det==null?'—':ratbar(s.det)} · <b>eff ${s.eff}</b>${s.lambda?` · λ ${s.lambda}`:''}</span>
      <span class="ev-tier">${s.tier}</span> ${srcs} ${cites}</div></div>`;
}
function openDrawer(id){
  const p=D.pts.find(x=>x.id===id); if(!p)return;
  $('#drawer-name').innerHTML=`<div class="drawer-logo-row">${logoHtml(p,'sm')}<span>${esc(p.name)}</span></div>`;
  $('#drawer-meta').innerHTML=`${LAYER[p.layer]||'L'+p.layer} · ${esc(p.type)}${p.parent?' · '+esc(p.parent):''} · confidence ${p.conf}`;
  const dec=(lat,det,eff,lbl)=>`<div class="score-decomp"><b>${lbl}</b> latent ${lat??'—'} · deterministic ${det??'—'} → <b>${eff}</b></div>`;
  $('#drawer-body').innerHTML=`
    <div class="score-row">
      <div class="score-cell">Exposure<b>${p.exp}</b></div><div class="score-cell">Preparedness<b>${p.prep}</b></div>
      <div class="score-cell">Margin of Safety<b style="color:${qColor(p.quad)}">${p.mos>0?'+':''}${p.mos}</b></div>
      <div class="score-cell">Quadrant<b style="font-size:15px;color:${qColor(p.quad)}">${QLAB[p.quad]}</b></div></div>
    ${dec(p.expLat,p.expDet,p.exp,'Exposure axis:')}${dec(p.prepLat,p.prepDet,p.prep,'Preparedness axis:')}
    <div class="sf-head"><span>Exposure sub-factors</span><span class="text-muted">measured ${Math.round(p.detExp*100)}%</span></div>
    ${p.exposure.map(sfBlock).join('')}
    <div class="sf-head"><span>Preparedness sub-factors</span><span class="text-muted">measured ${Math.round(p.detPrep*100)}%</span></div>
    ${p.preparedness.map(sfBlock).join('')}`;
  $('#drawer').classList.add('on'); $('#scrim').classList.add('on');
}
function closeDrawer(){$('#drawer').classList.remove('on');$('#scrim').classList.remove('on');}
function citePop(id){const c=D.cites[id];if(!c){alert(id);return;}
  alert(`${id}\n\n${c.t}\n${c.a} (${c.y})\n\n${c.use}\n\n${c.u}`);}
addEventListener('keydown',e=>{if(e.key==='Escape')closeDrawer();});

/* ---------- in-force rail ---------- */
$('#railcards').innerHTML=D.rail.map(r=>`<div class="rail-card">
  <div style="display:flex;justify-content:space-between;align-items:baseline"><span class="rail-id">${r.id}</span><span class="rail-status">● in force ${r.inforce}</span></div>
  <div style="font-size:12.5px;font-weight:600;margin-top:3px">${esc(r.title)}</div>
  <p>${esc(r.reprices)}</p>
  <div class="chip-row"><span class="chip">re-prices · ${r.sub}</span>${r.url?`<span class="chip"><a href="${r.url}" target="_blank" rel="noopener">${r.cite} ↗</a></span>`:''}</div>
</div>`).join('');
observeMotion($('#railcards'));

/* ---------- evidence index (knowledge graph) ---------- */
const KTYPE={academic:'#5b6fa6',model:'#2E7D8A',register:'#3a945e',regulatory:'#b07b2e',broker:'#a05a8f',
  product:'#c2715a',industry_practice:'#7a8a93',carrier:'#9a6a12',market_guidance:'#7a8a93',cri:'#3f7fb0'};
const KTYPELAB={academic:'Academic',model:'Model',register:'Register',regulatory:'Regulatory',broker:'Broker',
  product:'Product',industry_practice:'Industry',carrier:'Carrier',market_guidance:'Guidance',cri:'CRI'};
let kgTopic='all',kgActiveId=null,kgSearchQ='';
function kgTopicDesc(){
  const t=kgTopic==='all'?null:D.graph.topics.find(x=>x.id===kgTopic);
  $('#kgtopicdesc').textContent=t?(t.description||''):'All curated sources across grid firmness, data-centre exposure, pricing models, and placement.';
}
function kgVisible(){
  const q=kgSearchQ.trim();
  return D.graph.nodes.filter(n=>{
    if(kgTopic!=='all'&&!(n.topics||[]).includes(kgTopic))return false;
    if(!q)return true;
    const hay=[n.label,n.id,n.type,n.citation_id,...(n.juice||[]),...(n.nfri_sub_factors||[])].join(' ').toLowerCase();
    return hay.includes(q);
  }).sort((a,b)=>(a.label||'').localeCompare(b.label||''));
}
function sfLabel(k){return (D.sfLabels&&D.sfLabels[k])||k.replace(/_/g,' ');}
function kgNeighbors(id){
  const ids=new Set();
  D.graph.edges.forEach(e=>{if(e.from===id)ids.add(e.to);if(e.to===id)ids.add(e.from);});
  return [...ids].map(i=>D.graph.nodes.find(n=>n.id===i)).filter(Boolean);
}
function renderKGList(){
  const list=$('#kglist'), nodes=kgVisible();
  list.innerHTML=nodes.map(n=>{
    const sf=(n.nfri_sub_factors||[]).length;
    const yr=n.year||'';
    return `<li><button type="button" class="kg-row${n.id===kgActiveId?' on':''}" data-id="${esc(n.id)}" role="option">
      <span class="kg-row-type" style="background:${KTYPE[n.type]||'#7a8a93'}22;color:${KTYPE[n.type]||'#7a8a93'}">${KTYPELAB[n.type]||n.type}</span>
      <span class="kg-row-title">${esc(n.label||n.id)}</span>
      <span class="kg-row-meta">${sf?sf+' sub-factor'+(sf>1?'s':''):'linked'}${yr?' · '+yr:''}</span>
    </button></li>`;
  }).join('')||'<li><p class="kg-row-meta" style="padding:12px 16px">No sources match.</p></li>';
  list.querySelectorAll('.kg-row').forEach(b=>b.onclick=()=>kgPick(b.dataset.id));
}
function renderKGDetail(n){
  const c=n.citation_id?D.cites[n.citation_id]:null;
  const col=KTYPE[n.type]||'#7a8a93';
  const auth=c&&c.a?`${esc(c.a)}${c.y?' ('+c.y+')':''}`:'';
  const citeLink=n.citation_id?`<a href="#foundations" onclick="setTimeout(()=>document.getElementById('ref-${n.citation_id}')?.scrollIntoView({behavior:'smooth'}),100);return true">${esc(n.citation_id)}</a>`:'';
  const srcLink=c&&c.u?`<a href="${c.u}" target="_blank" rel="noopener">Read source ↗</a>`:'';
  const sfs=(n.nfri_sub_factors||[]).map(s=>`<span class="kg-sf" title="${esc(sfLabel(s))}">${esc(sfLabel(s))}</span>`).join('');
  const findings=(n.juice||[]).length?`<ul class="kg-findings">${n.juice.map(j=>`<li>${esc(j)}</li>`).join('')}</ul>`:'<p class="text-muted">No extracted findings for this node.</p>';
  const rel=kgNeighbors(n.id);
  const relHtml=rel.length?`<div class="kg-related">${rel.slice(0,12).map(r=>`<button type="button" class="kg-rel" data-id="${esc(r.id)}">${esc((r.label||r.id).slice(0,42))}</button>`).join('')}</div>`:'<p class="text-muted">No direct graph links.</p>';
  $('#kgdetail').innerHTML=`
    <div class="kg-detail-head">
      <span class="kg-type-pill" style="background:${col}22;color:${col}">${KTYPELAB[n.type]||n.type}</span>
      <h3>${esc(n.label||n.id)}</h3>
      <p class="kg-detail-meta">${auth}${auth&&citeLink?' · ':''}${citeLink}${srcLink?(auth||citeLink?' · ':'')+srcLink:''}</p>
    </div>
    ${sfs?`<div class="kg-block"><h4>Informs</h4><div class="kg-sf-chips">${sfs}</div></div>`:''}
    <div class="kg-block"><h4>Key findings</h4>${findings}</div>
    <div class="kg-detail-grid">
      <div class="kg-block"><h4>Related sources</h4>${relHtml}</div>
      <div class="kg-mini"><p class="kg-mini-label">Connections</p><svg id="kgmini" viewBox="0 0 400 120"></svg></div>
    </div>`;
  $('#kgdetail').querySelectorAll('.kg-rel').forEach(b=>b.onclick=()=>kgPick(b.dataset.id));
  drawKGMini(n);
}
function kgPick(id){
  kgActiveId=id;
  const n=D.graph.nodes.find(x=>x.id===id);
  if(!n)return;
  renderKGList();
  renderKGDetail(n);
  const row=$('#kglist').querySelector(`[data-id="${CSS.escape(id)}"]`);
  if(row)row.scrollIntoView({block:'nearest',behavior:'smooth'});
}
function drawKGMini(n){
  const svg=$('#kgmini'); if(!svg)return;
  svg.innerHTML='';
  const cx=200,cy=70, rel=kgNeighbors(n.id).slice(0,8);
  if(!rel.length){
    const t=document.createElementNS(NS,'text');
    t.setAttribute('x',String(cx));t.setAttribute('y',String(cy));t.setAttribute('text-anchor','middle');
    t.setAttribute('fill','#737373');t.setAttribute('font-size','11');
    t.textContent='No linked nodes'; svg.appendChild(t); return;
  }
  rel.forEach((r,i)=>{
    const a=i/rel.length*2*Math.PI-Math.PI/2;
    const x=cx+Math.cos(a)*88,y=cy+Math.sin(a)*52;
    svg.appendChild(el('line',{x1:String(cx),y1:String(cy),x2:String(x),y2:String(y),stroke:'#dcdcdc','stroke-width':'1'}));
    const g=el('g',{class:'kgmini-node'});
    g.appendChild(el('circle',{cx:String(x),cy:String(y),r:'7',fill:KTYPE[r.type]||'#7a8a93',stroke:'#fff','stroke-width':'1.2'}));
    const tx=el('text',{x:String(x),y:String(y+16),'text-anchor':'middle'});tx.textContent=(r.label||'').slice(0,18);g.appendChild(tx);
    g.onclick=()=>kgPick(r.id); svg.appendChild(g);
  });
  const g0=el('g',{class:'kgmini-node'});
  g0.appendChild(el('circle',{cx:String(cx),cy:String(cy),r:'10',fill:KTYPE[n.type]||'#1B3A6B',stroke:'#fff','stroke-width':'2'}));
  svg.appendChild(g0);
}
(function initKG(){
  const f=$('#kgfilters');
  const topics=[['all','All'],...D.graph.topics.map(t=>[t.id,t.label.split(' ')[0]])];
  f.innerHTML=topics.map(([v,l],i)=>`<button type="button" data-v="${v}" class="kg-topic${i===0?' on':''}">${esc(l)}</button>`).join('');
  f.querySelectorAll('.kg-topic').forEach(b=>b.onclick=()=>{
    f.querySelectorAll('.kg-topic').forEach(x=>x.classList.remove('on'));
    b.classList.add('on'); kgTopic=b.dataset.v; kgTopicDesc(); renderKGList();
    const vis=kgVisible();
    if(kgActiveId&&!vis.find(n=>n.id===kgActiveId)&&vis[0])kgPick(vis[0].id);
  });
  $('#kgsearch').addEventListener('input',e=>{kgSearchQ=e.target.value.toLowerCase();renderKGList();
    const vis=kgVisible(); if(vis[0]&&!vis.find(n=>n.id===kgActiveId))kgPick(vis[0].id);});
  kgTopicDesc();
  const anchor=D.graph.nodes.find(n=>n.id==='che-castaldo-grid-cri-sri')||D.graph.nodes[0];
  if(anchor)kgPick(anchor.id);
})();

/* ---------- eval chips ---------- */
$('#eval-chips').innerHTML=D.evals.map(e=>`<span class="eval-chip ${e.status}" title="${esc(e.metric)}">
  <span class="eval-dot"></span><b>L${e.level}</b> ${e.status} · ${esc(e.name.replace(/\s*\(.*\)/,''))}</span>`).join('');

refreshIndex();
observeMotion(document);
(function(){
  const v=new URLSearchParams(location.search).get('v');
  if(v==='design-system')document.body.classList.add('ds-review');
})();

/* ---------- thesis page (on-non-firm-risk) ---------- */
function thesisEl(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}
function thesisMeas(p){return (p.detExp+p.detPrep)/2;}

function drawThesisScatter(mount, readonly){
  if(!mount||!D.thesisCharts)return;
  const W=880,H=480,PAD={l:58,r:20,t:22,b:48};
  const X=v=>PAD.l+(v/100)*(W-PAD.l-PAD.r), Y=v=>H-PAD.b-(v/100)*(H-PAD.t-PAD.b);
  const svg=thesisEl('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img','aria-label':'Exposure vs Preparedness'});
  const mx=X(D.cal.cutExp), my=Y(D.cal.cutPrep);
  [['whitespace',PAD.l,PAD.t,mx-PAD.l,my-PAD.t],['earning_it',mx,PAD.t,X(100)-mx,my-PAD.t],
   ['sidelined',PAD.l,my,mx-PAD.l,Y(0)-my],['exposed',mx,my,X(100)-mx,Y(0)-my]]
   .forEach(([q,x,y,w,h])=>svg.appendChild(thesisEl('rect',{x,y,width:Math.max(0,w),height:Math.max(0,h),fill:qColor(q),opacity:.06})));
  svg.appendChild(thesisEl('line',{x1:mx,y1:PAD.t,x2:mx,y2:Y(0),stroke:cssVar('--chart-grid'),'stroke-dasharray':'4 4'}));
  svg.appendChild(thesisEl('line',{x1:PAD.l,y1:my,x2:X(100),y2:my,stroke:cssVar('--chart-grid'),'stroke-dasharray':'4 4'}));
  (D.pts||[]).forEach(p=>{
    const cx=X(p.exp), cy=Y(p.prep), r=CSIZE[p.conf]||5.5;
    const g=thesisEl('g',{class:'plot-dot'});
    g.appendChild(thesisEl('circle',{cx,cy,r,fill:cssVar('--bg-default'),stroke:qColor(p.quad),'stroke-width':1.5}));
    const ri=Math.max(1.4,(r-2)*Math.sqrt(Math.max(0,Math.min(1,thesisMeas(p)))));
    if(ri>1.1)g.appendChild(thesisEl('circle',{cx,cy,r:ri,fill:qColor(p.quad),opacity:.85}));
    if(!readonly)g.addEventListener('click',()=>openDrawer(p.id));
    svg.appendChild(g);
  });
  mount.innerHTML=''; mount.appendChild(svg);
}

function drawMosRegression(mount){
  const data=D.thesisCharts&&D.thesisCharts.mos_regression;
  if(!mount||!data||!data.pts.length)return;
  const pts=data.pts, stats=data.stats;
  const W=880,H=360,PAD={l:52,r:24,t:24,b:44};
  const xs=pts.map(p=>p.x), ys=pts.map(p=>p.y);
  const xMin=Math.min(...xs)-8, xMax=Math.max(...xs)+8;
  const yMin=0, yMax=1;
  const X=x=>PAD.l+((x-xMin)/(xMax-xMin))*(W-PAD.l-PAD.r);
  const Y=y=>H-PAD.b-((y-yMin)/(yMax-yMin))*(H-PAD.t-PAD.b);
  const svg=thesisEl('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'MoS vs measured share'});
  if(stats&&stats.slope!==undefined){
    const y0=stats.intercept+stats.slope*xMin, y1=stats.intercept+stats.slope*xMax;
    svg.appendChild(thesisEl('line',{x1:X(xMin),y1:Y(Math.max(0,Math.min(1,y0))),x2:X(xMax),y2:Y(Math.max(0,Math.min(1,y1))),
      stroke:cssVar('--accent'),'stroke-width':2,opacity:.7}));
  }
  pts.forEach(p=>{
    const g=thesisEl('g');
    g.appendChild(thesisEl('circle',{cx:X(p.x),cy:Y(p.y),r:5.5,fill:qColor(p.quad),opacity:.85,stroke:'#fff','stroke-width':1}));
    g.addEventListener('click',()=>openDrawer(p.id));
    svg.appendChild(g);
  });
  let ax=thesisEl('text',{x:(PAD.l+X(xMax))/2,y:H-12,'text-anchor':'middle','font-size':12,fill:cssVar('--ink'),'font-weight':600});
  ax.textContent='Margin of Safety →'; svg.appendChild(ax);
  let ay=thesisEl('text',{x:16,y:(PAD.t+Y(yMax))/2,'text-anchor':'middle','font-size':12,fill:cssVar('--ink'),'font-weight':600,
    transform:`rotate(-90 16 ${(PAD.t+Y(yMax))/2})`}); ay.textContent='Measured share →'; svg.appendChild(ay);
  mount.innerHTML=''; mount.appendChild(svg);
}

function drawMosByLayer(mount){
  const bars=D.thesisCharts&&D.thesisCharts.mos_by_layer&&D.thesisCharts.mos_by_layer.bars;
  if(!mount||!bars||!bars.length)return;
  const mx=Math.max(...bars.map(b=>Math.abs(b.mean)),1);
  const W=560, rowH=36;
  const svg=thesisEl('svg',{viewBox:`0 0 ${W} ${bars.length*rowH+16}`,role:'img','aria-label':'MoS by layer'});
  bars.forEach((b,i)=>{
    const y=8+i*rowH, bw=(Math.abs(b.mean)/mx)*(W-180);
    const col=b.mean>=0?cssVar('--earning-s'):cssVar('--exposed');
    svg.appendChild(thesisEl('text',{x:0,y:y+18,'font-size':12,fill:cssVar('--ink2')}));
    svg.lastChild.textContent=b.label;
    svg.appendChild(thesisEl('rect',{x:120,y:y+6,width:Math.max(bw,2),height:16,rx:2,fill:col}));
    const t=thesisEl('text',{x:120+Math.max(bw,2)+8,y:y+18,'font-size':11.5,fill:cssVar('--muted'),'font-weight':600});
    t.textContent=`${b.mean>0?'+':''}${b.mean} (n=${b.n})`; svg.appendChild(t);
  });
  mount.innerHTML=''; mount.appendChild(svg);
}

function drawCarrierSwarm(mount, fig){
  const sw=D.thesisCharts&&D.thesisCharts.carrier_swarm;
  if(!mount||!sw)return;
  let sel=sw.default||'';
  const wrap=document.createElement('div');
  const seg=document.createElement('div');
  seg.className='filter-seg thesis-swarm-seg';
  seg.innerHTML=(sw.carriers||[]).slice(0,12).map(c=>
    `<button type="button" class="filter-btn${c.id===sel?' on':''}" data-c="${c.id}">${esc(c.name.split(' ')[0])}</button>`).join('');
  const chart=document.createElement('div');
  chart.className='thesis-swarm-chart';
  wrap.appendChild(seg); wrap.appendChild(chart);
  mount.innerHTML=''; mount.appendChild(wrap);
  function render(){
    const carrier=(sw.carriers||[]).find(c=>c.id===sel)||sw.carriers[0];
    const assets=sw.assets||[];
    const W=860,H=120,PAD={l:48,r:20,t:20,b:36};
    const mosVals=assets.map(a=>a.mos);
    const xMin=Math.min(...mosVals,carrier?carrier.mos:0)-5, xMax=Math.max(...mosVals,carrier?carrier.mos:0)+5;
    const X=x=>PAD.l+((x-xMin)/(xMax-xMin))*(W-PAD.l-PAD.r);
    const svg=thesisEl('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Carrier portfolio swarm'});
    assets.forEach((a,i)=>{
      const cx=X(a.mos), cy=40+(i%5)*14;
      const g=thesisEl('g');
      g.appendChild(thesisEl('circle',{cx,cy,r:4.5,fill:qColor(a.quad),opacity:.8}));
      g.addEventListener('click',()=>openDrawer(a.id));
      svg.appendChild(g);
    });
    if(carrier){
      const lx=X(carrier.mos);
      svg.appendChild(thesisEl('line',{x1:lx,y1:PAD.t,x2:lx,y2:H-PAD.b,stroke:cssVar('--accent'),'stroke-width':2,'stroke-dasharray':'6 4'}));
      const lab=thesisEl('text',{x:lx,y:PAD.t-4,'text-anchor':'middle','font-size':11,fill:cssVar('--accent'),'font-weight':700});
      lab.textContent=carrier.name.split(' ')[0]+' avg'; svg.appendChild(lab);
    }
    let ax=thesisEl('text',{x:(PAD.l+W-PAD.r)/2,y:H-8,'text-anchor':'middle','font-size':11.5,fill:cssVar('--muted')});
    ax.textContent='Margin of Safety →'; svg.appendChild(ax);
    chart.innerHTML=''; chart.appendChild(svg);
  }
  seg.querySelectorAll('.filter-btn').forEach(b=>b.onclick=()=>{
    sel=b.dataset.c;
    seg.querySelectorAll('.filter-btn').forEach(x=>x.classList.remove('on'));
    b.classList.add('on'); render();
  });
  render();
}

function drawCarrierQuadStack(mount){
  const bars=D.thesisCharts&&D.thesisCharts.carrier_quad_stack&&D.thesisCharts.carrier_quad_stack.bars;
  if(!mount||!bars||!bars.length)return;
  const W=860, rowH=22, order=['earning_it','whitespace','sidelined','exposed'];
  const svg=thesisEl('svg',{viewBox:`0 0 ${W} ${bars.length*rowH+12}`,role:'img','aria-label':'Quadrant by carrier'});
  bars.forEach((b,i)=>{
    const y=6+i*rowH;
    svg.appendChild(thesisEl('text',{x:0,y:y+14,'font-size':11,fill:cssVar('--ink2')}));
    svg.lastChild.textContent=(b.name||'').slice(0,28);
    let x=140;
    order.forEach(q=>{
      const v=b.counts&&b.counts[q]?1:0;
      if(!v)return;
      const w=Math.max(24,(W-160)/order.length-4);
      svg.appendChild(thesisEl('rect',{x,y:y+2,width:w,height:14,rx:2,fill:qColor(q)}));
      x+=w+4;
    });
  });
  mount.innerHTML=''; mount.appendChild(svg);
}

function drawMosBySegment(mount){
  const bars=D.thesisCharts&&D.thesisCharts.mos_by_segment&&D.thesisCharts.mos_by_segment.bars;
  if(!mount||!bars||!bars.length)return;
  const mx=Math.max(...bars.map(b=>Math.abs(b.mean)),1);
  const W=560, rowH=34;
  const svg=thesisEl('svg',{viewBox:`0 0 ${W} ${bars.length*rowH+16}`,role:'img','aria-label':'MoS by segment'});
  bars.forEach((b,i)=>{
    const y=8+i*rowH, bw=(Math.abs(b.mean)/mx)*(W-180);
    const col=b.mean>=0?cssVar('--earning-s'):cssVar('--exposed');
    const t1=thesisEl('text',{x:0,y:y+18,'font-size':12,fill:cssVar('--ink2')}); t1.textContent=b.label; svg.appendChild(t1);
    svg.appendChild(thesisEl('rect',{x:120,y:y+6,width:Math.max(bw,2),height:16,rx:2,fill:col}));
    const t2=thesisEl('text',{x:120+Math.max(bw,2)+8,y:y+18,'font-size':11.5,fill:cssVar('--muted'),'font-weight':600});
    t2.textContent=`${b.mean>0?'+':''}${b.mean} (n=${b.n})`; svg.appendChild(t2);
  });
  mount.innerHTML=''; mount.appendChild(svg);
}

function drawThesisRail(mount){
  if(!mount||!D.rail)return;
  mount.className='thesis-rail-grid';
  mount.innerHTML=D.rail.map(r=>`<div class="rail-card">
    <div style="display:flex;justify-content:space-between;align-items:baseline"><span class="rail-id">${r.id}</span><span class="rail-status">● in force ${r.inforce}</span></div>
    <div style="font-size:12.5px;font-weight:600;margin-top:3px">${esc(r.title)}</div>
    <p>${esc(r.reprices)}</p></div>`).join('');
}

function initThesisTabs(){
  document.querySelectorAll('[data-thesis-tabs]').forEach(root=>{
    const btns=root.querySelectorAll('.thesis-tab-btn');
    const panels=root.querySelectorAll('.thesis-tab-panel');
    btns.forEach(b=>b.onclick=()=>{
      btns.forEach(x=>x.classList.remove('on'));
      panels.forEach(x=>x.classList.remove('on'));
      b.classList.add('on');
      root.querySelector(`[data-panel="${b.dataset.tab}"]`)?.classList.add('on');
    });
  });
}

function initThesisTOC(){
  const links=[...document.querySelectorAll('.thesis-toc-link')];
  if(!links.length)return;
  const sections=links.map(a=>document.getElementById(a.getAttribute('href').slice(1))).filter(Boolean);
  const io=new IntersectionObserver(es=>{
    es.forEach(e=>{
      if(e.isIntersecting){
        const id=e.target.id;
        links.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+id));
      }
    });
  },{rootMargin:'-40% 0px -50% 0px',threshold:0});
  sections.forEach(s=>io.observe(s));
}

function initThesisCharts(){
  if(!document.body.classList.contains('site--thesis')||!D.thesisCharts)return;
  document.querySelectorAll('.thesis-viz[data-chart]').forEach(fig=>{
    const kind=fig.dataset.chart;
    const mount=fig.querySelector('.thesis-viz-mount');
    if(kind==='quadrant_scatter')drawThesisScatter(mount,fig.dataset.readonly==='1');
    else if(kind==='mos_regression')drawMosRegression(mount);
    else if(kind==='mos_by_layer')drawMosByLayer(mount);
    else if(kind==='carrier_swarm')drawCarrierSwarm(mount,fig);
    else if(kind==='carrier_quad_stack')drawCarrierQuadStack(mount);
    else if(kind==='mos_by_segment')drawMosBySegment(mount);
    else if(kind==='inforce_rail')drawThesisRail(mount);
  });
  const ev=$('#thesis-eval');
  if(ev&&D.evals)ev.innerHTML=D.evals.map(e=>`<span class="eval-chip ${e.status}" title="${esc(e.metric)}">
    <span class="eval-dot"></span><b>L${e.level}</b> ${e.status}</span>`).join('');
  initThesisTabs();
  initThesisTOC();
  observeMotion(document);
}

function initMethodologyPage(){
  document.querySelectorAll('.thesis-viz[data-chart]').forEach(fig=>{
    const kind=fig.dataset.chart;
    const mount=fig.querySelector('.thesis-viz-mount');
    if(kind==='inforce_rail')drawThesisRail(mount);
  });
  const ev=$('#thesis-eval');
  if(ev&&D.evals)ev.innerHTML=D.evals.map(e=>`<span class="eval-chip ${e.status}" title="${esc(e.metric)}">
    <span class="eval-dot"></span><b>L${e.level}</b> ${e.status}</span>`).join('');
  initThesisTOC();
  observeMotion(document);
}

if(document.body.classList.contains('site--thesis'))initThesisCharts();
else if(document.body.classList.contains('site--methodology'))initMethodologyPage();
else observeMotion(document);"""
