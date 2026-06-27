"""Client bundle — single init, see ARCHITECTURE.md."""

CLIENT_JS = r"""const D = /*__PAYLOAD__*/null;
const QCOL={exposed:'#cf4a45',earning_it:'#34894b',whitespace:'#3f7fb0',sidelined:'#9aa7ad'};
const QLAB={exposed:'Exposed',earning_it:'Earning it',whitespace:'Whitespace',sidelined:'Sidelined'};
const CSIZE={high:10,medium:7.5,low:5.5};
const LAYER={1:'Carriers & syndicates',2:'MGAs & brokers',3:'Assets',4:'Capacity & reins.'};
let layerF='all', quadF='all', sortK='mos', sortDir=-1;
const $=s=>document.querySelector(s), NS='http://www.w3.org/2000/svg';
let motionIO=null;
function observeMotion(root){
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  (root||document).querySelectorAll('.reveal,.stagger').forEach(el=>{
    if(reduced){el.classList.add('in');return;}
    if(el._motionBound)return; el._motionBound=true;
    if(!motionIO){
      motionIO=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');motionIO.unobserve(e.target);}});},{threshold:0.06,rootMargin:'0px 0px -32px 0px'});
    }
    motionIO.observe(el);
  });
}
function initMotion(){observeMotion();}
function el(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}
function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
initMotion();

/* ---------- banner + meta ---------- */
(function(){
  const pct=Math.round(D.share*100), ok=D.share>=0.60;
  $('#banner').className='banner'+(ok?' ok':'');
  $('#banner').innerHTML=`<div>${ok?'✓':'⚠'}</div><div>${ok
    ? `<b>Publishable.</b> Blended measured/disclosed share ${pct}% ≥ 60% gate.`
    : `<b>PROVISIONAL — assessed-tier prototype.</b> Blended measured/disclosed share is ${pct}%; the publication
       gate (≥60%) is not yet met, so scores are an honest research estimate, not a measurement. Direction is
       defensible; magnitudes move as live registers and filings land.`}</div>`;
  $('#status-meta').innerHTML=`<span><b>${D.n}</b> entities scored</span>
    <span>snapshot ${esc(D.snapshot)}</span>
    <span>median cut · exposure ≥ ${D.cal.cutExp} · prep ≥ ${D.cal.cutPrep}</span>
    <span>${D.graph.nodes.length} knowledge nodes</span>`;
})();

/* ---------- filters ---------- */
(function(){
  const f=$('#scatter-filters');
  const layers=[['all','All layers'],['1','Carriers'],['2','MGAs & brokers'],['3','Assets']];
  const quads=[['all','All'],['exposed','Exposed'],['earning_it','Earning it'],['whitespace','Whitespace'],['sidelined','Sidelined']];
  f.innerHTML=`<div class="filter-grp"><span class="filter-label">Layer</span>${layers.map(([v,l],i)=>
    `<button type="button" data-t="layer" data-v="${v}" class="filter-btn${i===0?' on':''}">${l}</button>`).join('')}</div>
    <div class="filter-grp"><span class="filter-label">Quadrant</span>${quads.map(([v,l],i)=>
    `<button type="button" data-t="quad" data-v="${v}" class="filter-btn${i===0?' on':''}">${l}</button>`).join('')}</div>`;
  f.querySelectorAll('.filter-btn').forEach(b=>b.onclick=()=>{
    const t=b.dataset.t;
    f.querySelectorAll(`.filter-btn[data-t="${t}"]`).forEach(x=>x.classList.remove('on'));
    b.classList.add('on'); if(t==='layer')layerF=b.dataset.v; else quadF=b.dataset.v;
    draw(); table();
  });
})();
const shown=()=>D.pts.filter(p=>(layerF==='all'||p.layer==+layerF)&&(quadF==='all'||p.quad===quadF));

/* ---------- scatter ---------- */
const W=960,H=580,PAD={l:68,r:28,t:26,b:58};
const X=v=>PAD.l+(v/100)*(W-PAD.l-PAD.r), Y=v=>H-PAD.b-(v/100)*(H-PAD.t-PAD.b);
function draw(){
  const svg=$('#plot'); svg.innerHTML='';
  const mx=X(D.cal.cutExp), my=Y(D.cal.cutPrep);
  [['whitespace',PAD.l,PAD.t,mx-PAD.l,my-PAD.t],['earning_it',mx,PAD.t,X(100)-mx,my-PAD.t],
   ['sidelined',PAD.l,my,mx-PAD.l,Y(0)-my],['exposed',mx,my,X(100)-mx,Y(0)-my]]
   .forEach(([q,x,y,w,h])=>svg.appendChild(el('rect',{x,y,width:Math.max(0,w),height:Math.max(0,h),fill:QCOL[q],opacity:.06})));
  svg.appendChild(el('line',{x1:mx,y1:PAD.t,x2:mx,y2:Y(0),stroke:'#c2cdd1','stroke-dasharray':'4 4'}));
  svg.appendChild(el('line',{x1:PAD.l,y1:my,x2:X(100),y2:my,stroke:'#c2cdd1','stroke-dasharray':'4 4'}));
  [['whitespace',PAD.l+10,PAD.t+18,'start'],['earning_it',X(100)-10,PAD.t+18,'end'],
   ['sidelined',PAD.l+10,Y(0)-12,'start'],['exposed',X(100)-10,Y(0)-12,'end']].forEach(([q,x,y,a])=>{
    const t=el('text',{x,y,'text-anchor':a,'font-size':12,'font-weight':700,fill:QCOL[q],opacity:.85});t.textContent=QLAB[q];svg.appendChild(t);});
  svg.appendChild(el('line',{x1:PAD.l,y1:Y(0),x2:X(100),y2:Y(0),stroke:'#9aa7ad'}));
  svg.appendChild(el('line',{x1:PAD.l,y1:PAD.t,x2:PAD.l,y2:Y(0),stroke:'#9aa7ad'}));
  for(let v=0;v<=100;v+=25){
    let t=el('text',{x:X(v),y:Y(0)+20,'text-anchor':'middle','font-size':11,fill:'#647077'});t.textContent=v;svg.appendChild(t);
    let u=el('text',{x:PAD.l-10,y:Y(v)+4,'text-anchor':'end','font-size':11,fill:'#647077'});u.textContent=v;svg.appendChild(u);
  }
  let ax=el('text',{x:(PAD.l+X(100))/2,y:H-14,'text-anchor':'middle','font-size':12.5,'font-weight':600,fill:'#15282e'});ax.textContent='Exposure →';svg.appendChild(ax);
  let ay=el('text',{x:18,y:(PAD.t+Y(0))/2,'text-anchor':'middle','font-size':12.5,'font-weight':600,fill:'#15282e',transform:`rotate(-90 18 ${(PAD.t+Y(0))/2})`});ay.textContent='Preparedness →';svg.appendChild(ay);
  shown().forEach(p=>{
    const g=el('g',{class:'kgnode'}), r=CSIZE[p.conf]||5.5, meas=(p.detExp+p.detPrep)/2;
    const c=el('circle',{cx:X(p.exp),cy:Y(p.prep),r,fill:QCOL[p.quad],stroke:QCOL[p.quad],'stroke-width':1.6,
      'fill-opacity':(0.18+0.82*meas).toFixed(2)});
    const t=el('text',{x:X(p.exp)+r+3,y:Y(p.prep)+3.5,'font-size':10.5,fill:'#15282e'});t.textContent=shortName(p.name);
    g.appendChild(c);g.appendChild(t);
    g.style.cursor='pointer'; g.onmousemove=e=>tip(e,p); g.onmouseleave=hideTip; g.onclick=()=>openDrawer(p.id);
    svg.appendChild(g);
  });
}
function shortName(n){return n.replace(' — ',' ').replace(' (Willis Towers Watson)','').replace('Data Centres','DC').slice(0,22);}

/* ---------- tooltip ---------- */
let tipEl;
function tip(e,p){
  if(!tipEl){tipEl=document.createElement('div');tipEl.id='tip';
    tipEl.style.cssText='position:fixed;pointer-events:none;background:#fff;border:1px solid var(--line);box-shadow:0 6px 24px rgba(0,0,0,.14);border-radius:10px;padding:9px 11px;max-width:280px;font-size:12.5px;z-index:50;transition:opacity .1s';
    document.body.appendChild(tipEl);}
  tipEl.innerHTML=`<div style="font-weight:700;font-size:11px;text-transform:uppercase;color:${QCOL[p.quad]}">${QLAB[p.quad]}</div>
    <div style="font-weight:600">${esc(p.name)}</div>
    <div style="color:#647077">L${p.layer} · ${esc(p.type)} · conf ${p.conf}</div>
    <div style="margin-top:4px">Exp <b>${p.exp}</b> · Prep <b>${p.prep}</b> · MoS <b>${p.mos>0?'+':''}${p.mos}</b></div>
    <div style="color:#647077;margin-top:3px">measured ${Math.round((p.detExp+p.detPrep)/2*100)}% · click for detail</div>`;
  tipEl.style.left=Math.min(e.clientX+14,innerWidth-300)+'px';tipEl.style.top=(e.clientY+14)+'px';tipEl.style.opacity=1;
}
function hideTip(){if(tipEl)tipEl.style.opacity=0;}

/* ---------- table ---------- */
function meas(p){return (p.detExp+p.detPrep)/2;}
function table(){
  const tb=$('#tbl tbody'); tb.innerHTML='';
  const key=p=>sortK==='meas'?meas(p):p[sortK];
  const rows=shown().sort((a,b)=>{const x=key(a),y=key(b);return (x>y?1:x<y?-1:0)*sortDir;});
  rows.forEach(p=>{
    const tr=document.createElement('tr'); tr.className='row'; tr.onclick=()=>openDrawer(p.id);
    const m=Math.round(meas(p)*100);
    tr.innerHTML=`<td>${esc(p.name)}</td><td class="num">${p.layer}</td>
      <td class="num">${p.exp}</td><td class="num">${p.prep}</td>
      <td class="num"><b>${p.mos>0?'+':''}${p.mos}</b></td>
      <td><span class="quad-pill" style="background:${QCOL[p.quad]}">${QLAB[p.quad]}</span></td>
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
  $('#drawer-name').textContent=p.name;
  $('#drawer-meta').innerHTML=`${LAYER[p.layer]||'L'+p.layer} · ${esc(p.type)}${p.parent?' · '+esc(p.parent):''} · confidence ${p.conf}`;
  const dec=(lat,det,eff,lbl)=>`<div class="score-decomp"><b>${lbl}</b> latent ${lat??'—'} · deterministic ${det??'—'} → <b>${eff}</b></div>`;
  $('#drawer-body').innerHTML=`
    <div class="score-row">
      <div class="score-cell">Exposure<b>${p.exp}</b></div><div class="score-cell">Preparedness<b>${p.prep}</b></div>
      <div class="score-cell">Margin of Safety<b style="color:${QCOL[p.quad]}">${p.mos>0?'+':''}${p.mos}</b></div>
      <div class="score-cell">Quadrant<b style="font-size:15px;color:${QCOL[p.quad]}">${QLAB[p.quad]}</b></div></div>
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
  <div class="chip-row"><span class="chip">re-prices · ${r.sub}</span>${r.url?`<a class="chip" href="${r.url}" target="_blank" rel="noopener">${r.cite} ↗</a>`:''}</div>
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
    <div class="kg-block"><h4>Related sources</h4>${relHtml}</div>
    <div class="kg-mini"><p class="kg-mini-label">Connections</p><svg id="kgmini" viewBox="0 0 400 140"></svg></div>`;
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

draw(); table();
observeMotion(document);"""
