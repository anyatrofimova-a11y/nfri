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
  (root||document).querySelectorAll('.reveal,.stagger,.essay-reveal').forEach(el=>{
    if(reduced||inView(el)){el.classList.add('in');return;}
    if(el._motionBound)return; el._motionBound=true;
    if(!motionIO){
      motionIO=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');motionIO.unobserve(e.target);}});},{threshold:0.02,rootMargin:'0px 0px -8% 0px'});
    }
    motionIO.observe(el);
  });
}
function initMotion(){observeMotion();}
function splashLogoReady(img){
  if(!img) return Promise.resolve();
  if(img.complete&&img.naturalWidth>0) return img.decode?.()??Promise.resolve();
  return new Promise(res=>{
    const done=()=>{(img.decode?.()??Promise.resolve()).then(res,res);};
    img.addEventListener('load',done,{once:true});
    img.addEventListener('error',done,{once:true});
  });
}
function initSplash(){
  const splash=$('#splash');
  if(!splash||document.documentElement.classList.contains('splash-skip')){
    splash?.remove();
    return;
  }
  document.body.classList.add('splash-active');
  const KEY='nfri-splash-v1';
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const minShow=reduced?300:1500;
  const start=Date.now();
  const finish=()=>{
    document.documentElement.classList.add('splash-skip');
    if(reduced){
      splash.remove();
      document.body.classList.remove('splash-active');
      try{localStorage.setItem(KEY,'1');}catch(e){}
      return;
    }
    splash.classList.add('is-out');
    const cleanup=()=>{
      splash.remove();
      document.body.classList.remove('splash-active');
      try{localStorage.setItem(KEY,'1');}catch(e){}
    };
    splash.addEventListener('transitionend',cleanup,{once:true});
    setTimeout(cleanup,1000);
  };
  const img=splash.querySelector('.splash-logo');
  const failsafe=setTimeout(finish,5000);
  Promise.all([
    document.fonts?.ready??Promise.resolve(),
    splashLogoReady(img),
  ]).then(()=>setTimeout(()=>{clearTimeout(failsafe);finish();},Math.max(0,minShow-(Date.now()-start))));
}
function el(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}
function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function initials(n){return (n||'?').split(/\s+/).map(w=>w[0]).join('').slice(0,2).toUpperCase();}
function logoErr(img){
  if(img.dataset.fb&&!img._fb){img._fb=1;img.src=img.dataset.fb;return;}
  img.style.display='none';if(img.nextElementSibling)img.nextElementSibling.style.display='flex';
}
function logoHtml(p, cls='', eager){
  const ini=initials(p.name);
  const fb=p.logoFb?` data-fb="${esc(p.logoFb)}"`:'';
  const load=eager?'':' loading="lazy"';
  return `<span class="ent-logo-wrap ${cls}"><img class="ent-logo" src="${esc(p.logo)}" alt=""${load}${fb} onerror="logoErr(this)"><span class="ent-logo-fallback" style="display:none">${ini}</span></span>`;
}
function avatarHtml(p){
  const ini=initials(p.name);
  const fb=p.logoFb?` data-fb="${esc(p.logoFb)}"`:'';
  return `<div class="ent-avatar"><img src="${esc(p.logo)}" alt="" loading="lazy"${fb} onerror="logoErr(this)"><span class="ent-logo-fallback" style="display:none">${ini}</span></div>`;
}
function cssVar(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim();}
initMotion();
initSplash();

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
function normQ(s){
  return (s||'').toLowerCase().replace(/[\u2019'`]/g,'').replace(/\s+/g,' ').trim();
}
function entityMatches(p,q){
  if(!q) return true;
  const n=normQ(q);
  const hay=normQ([p.name,p.id,p.type,p.parent||''].join(' '));
  if(hay.includes(n)) return true;
  if(/\blloyd/.test(n)&&(p.type==='lloyds_syndicate'||p.id==='lloyds-market'||hay.includes('lloyd'))) return true;
  return false;
}
const shown=()=>D.pts.filter(p=>
  (layerF==='all'||p.layer==+layerF)&&(quadF==='all'||p.quad===quadF)&&entityMatches(p,searchQ.trim())
);
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
    const div=document.createElement('div'); div.className='ent-card fund-card';
    const m=Math.round(meas(p)*100);
    const port=p.portfolio;
    const portHtml=port?`<div class="fund-portfolio">${port.n} linked assets · MoS ${port.mosMin>0?'+':''}${port.mosMin} … ${port.mosMax>0?'+':''}${port.mosMax} (avg ${port.mosAvg>0?'+':''}${port.mosAvg})</div>`:'';
    const mosCls=p.mos>=0?'pos':'neg';
    div.innerHTML=`<div class="ent-id">${avatarHtml(p)}
      <div><div class="ent-name">${esc(p.name)}<span class="quad-tag">${QLAB[p.quad]}</span></div>
      <div class="ent-meta">L${p.layer} · ${esc(LAYER[p.layer]||p.type)}${p.parent?' · '+esc(p.parent):''}</div></div></div>
      <div class="fund-stats">
        <div><span>Exposure</span><b>${p.exp}</b></div>
        <div><span>Prepared</span><b>${p.prep}</b></div>
        <div><span>MoS</span><b class="ent-mos ${mosCls}">${p.mos>0?'+':''}${p.mos}</b></div>
      </div>
      ${portHtml}
      <div class="ent-meta">Measured ${m}% · ${p.conf} confidence</div>
      ${scoreBars(p)}`;
    div.onclick=()=>openProfile(p.id); list.appendChild(div);
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
    g.onclick=()=>openProfile(g.dataset.id);
    g.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openProfile(g.dataset.id);}};
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
  list.querySelectorAll('.bench-row').forEach(row=>row.onclick=()=>openProfile(row.dataset.id));
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

/* ---------- index terminal (Ciridae-style analytics) ---------- */
const IX=()=>D.indexCharts||D.thesisCharts||{};
let termBoard='layer';

function layoutTermScatter(pts,xKey,yKey,round){
  round=round||2;
  const buckets={};
  pts.forEach(p=>{
    const key=`${Math.round(p[xKey]*round)/round}|${Math.round(p[yKey]*round)/round}`;
    (buckets[key]=buckets[key]||[]).push(p);
  });
  return pts.map(p=>{
    const key=`${Math.round(p[xKey]*round)/round}|${Math.round(p[yKey]*round)/round}`;
    const group=buckets[key], idx=group.indexOf(p), n=group.length;
    if(n<=1) return {p,ox:0,oy:0};
    const angle=(idx/n)*Math.PI*2-Math.PI/2;
    const spread=Math.min(20,4+n*2.8);
    return {p,ox:Math.cos(angle)*spread,oy:-Math.sin(angle)*spread};
  });
}

function termNiceTicks(lo,hi,count){
  const span=hi-lo||1, rough=span/(count||4);
  const mag=Math.pow(10,Math.floor(Math.log10(rough)));
  const step=Math.ceil(rough/mag)*mag;
  const start=Math.floor(lo/step)*step, out=[];
  for(let v=start; v<=hi+step*0.01; v+=step) out.push(Math.round(v*10)/10);
  return out;
}

function drawIndexRegression(){
  const mount=$('#term-regression'), statsEl=$('#term-reg-stats');
  if(!mount)return;
  drawMosRegression(mount);
  const reg=IX().mos_regression, st=reg&&reg.stats;
  if(!statsEl||!st)return;
  const sparse=reg&&reg.pts&&reg.pts.every(p=>p.y<0.02);
  if(sparse){
    statsEl.innerHTML=`<span class="term-note">Measured evidence still sparse</span> · ${st.n} entities · regression pending`;
    return;
  }
  const ci=st.ci_lo!==undefined&&st.ci_hi!==undefined?` · 95% CI [${st.ci_lo}, ${st.ci_hi}]`:'';
  statsEl.textContent=`Slope: ${st.slope>0?'+':''}${st.slope} pp/point · R²: ${st.r2}${ci} · n=${st.n}`;
}

function drawIndexScoreboard(){
  const mount=$('#term-scoreboard'); if(!mount)return;
  const bars=termBoard==='layer'
    ?IX().mos_by_layer&&IX().mos_by_layer.bars
    :IX().mos_by_segment&&IX().mos_by_segment.bars;
  drawScoreboard(mount,bars);
}

function drawStrategyMap(){
  const data=IX().strategy_map, mount=$('#term-strategy');
  if(!mount||!data||!data.pts.length)return;
  const pts=data.pts, W=520, H=340, PAD={l:52,r:16,t:28,b:48};
  const X=v=>PAD.l+(v/100)*(W-PAD.l-PAD.r), Y=v=>H-PAD.b-(v/100)*(H-PAD.t-PAD.b);
  const mx=X(D.cal.cutExp), my=Y(D.cal.cutPrep);
  const svg=thesisEl('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart term-strategy-svg',role:'img','aria-label':'Carrier strategy map'});
  [['whitespace',PAD.l,PAD.t,mx-PAD.l,my-PAD.t],['earning_it',mx,PAD.t,W-PAD.r-mx,my-PAD.t],
   ['sidelined',PAD.l,my,mx-PAD.l,H-PAD.b-my],['exposed',mx,my,W-PAD.r-mx,H-PAD.b-my]]
   .forEach(([q,x,y,w,h])=>svg.appendChild(thesisEl('rect',{x,y,width:Math.max(0,w),height:Math.max(0,h),fill:qColor(q),opacity:.07})));
  svg.appendChild(thesisEl('line',{x1:mx,y1:PAD.t,x2:mx,y2:H-PAD.b,stroke:cssVar('--chart-grid'),'stroke-dasharray':'4 4'}));
  svg.appendChild(thesisEl('line',{x1:PAD.l,y1:my,x2:W-PAD.r,y2:my,stroke:cssVar('--chart-grid'),'stroke-dasharray':'4 4'}));
  for(let v=0;v<=100;v+=25){
    svg.appendChild(thesisEl('text',{x:X(v),y:H-PAD.b+16,'text-anchor':'middle','font-size':10,fill:cssVar('--muted')}));
    svg.lastChild.textContent=v;
    svg.appendChild(thesisEl('text',{x:PAD.l-6,y:Y(v)+3,'text-anchor':'end','font-size':10,fill:cssVar('--muted')}));
    svg.lastChild.textContent=v;
  }
  [['Whitespace',PAD.l+4,PAD.t+12],['Earning it',W-PAD.r-4,PAD.t+12],
   ['Sidelined',PAD.l+4,H-PAD.b-6],['Exposed',W-PAD.r-4,H-PAD.b-6]]
   .forEach(([lbl,x,y])=>{
    const t=thesisEl('text',{x,y,'text-anchor':x<PAD.l+20?'start':'end','font-size':9,'font-weight':600,fill:cssVar('--muted')});
    t.textContent=lbl; svg.appendChild(t);
  });
  let ax=thesisEl('text',{x:(PAD.l+W-PAD.r)/2,y:H-6,'text-anchor':'middle','font-size':11,'font-weight':600,fill:cssVar('--ink')});
  ax.textContent='Exposure →'; svg.appendChild(ax);
  let ay=thesisEl('text',{x:14,y:(PAD.t+H-PAD.b)/2,'text-anchor':'middle','font-size':11,'font-weight':600,fill:cssVar('--ink'),
    transform:`rotate(-90 14 ${(PAD.t+H-PAD.b)/2})`}); ay.textContent='Preparedness →'; svg.appendChild(ay);
  layoutTermScatter(pts,'exp','prep').forEach(({p,ox,oy})=>{
    const cx=X(p.exp)+ox, cy=Y(p.prep)+oy, r=CSIZE[p.conf]||5;
    const g=thesisEl('g',{class:'plot-dot'});
    g.appendChild(thesisEl('circle',{cx,cy,r,fill:cssVar('--bg-default'),stroke:qColor(p.quad),'stroke-width':1.5}));
    g.appendChild(thesisEl('circle',{cx,cy,r:Math.max(2,r-2),fill:qColor(p.quad),opacity:.88}));
    g.addEventListener('mouseenter',e=>tip(e,{...p,layer:1,type:'carrier',conf:p.conf||'low',detExp:0,detPrep:0}));
    g.addEventListener('mouseleave',hideTip);
    g.addEventListener('click',()=>openProfile(p.id));
    svg.appendChild(g);
  });
  mount.innerHTML=''; mount.appendChild(svg);
}

function renderAlphaTable(){
  const el=$('#term-alpha'), rows=IX().alpha_targets&&IX().alpha_targets.rows;
  if(!el)return;
  if(!rows||!rows.length){
    el.innerHTML='<p class="term-empty">No whitespace alpha targets in current universe.</p>';
    return;
  }
  el.innerHTML=`<div class="alpha-list">${rows.map((r,i)=>`
    <button type="button" class="alpha-row" data-id="${esc(r.id)}">
      <span class="alpha-rank">${i+1}</span>
      <span class="alpha-id">
        <span class="alpha-name">${esc(r.name)}</span>
        <span class="alpha-bars">
          <span class="alpha-bar" title="Preparedness ${r.prep}"><i style="width:${r.prep}%"></i></span>
          <span class="alpha-bar exp" title="Exposure ${r.exp}"><i style="width:${r.exp}%"></i></span>
        </span>
      </span>
      <span class="alpha-gap">+${r.gap}</span>
      <span class="alpha-meas">${r.meas>0?r.meas+'%':'—'}</span>
    </button>`).join('')}</div>
    <p class="alpha-legend"><span class="leg-swatch leg-prep">Prep</span><span class="leg-swatch leg-exp">Exp</span><span>Gap = MoS</span><span>Meas = measured share</span></p>`;
  el.querySelectorAll('.alpha-row').forEach(btn=>btn.onclick=()=>openProfile(btn.dataset.id));
}

function renderComparePanel(){
  const pool=IX().compare_pool&&IX().compare_pool.entities;
  const pick=$('#term-compare-pick'), body=$('#term-compare');
  if(!pool||!pick||!body)return;
  const opts=pool.map(e=>`<option value="${esc(e.id)}">${esc(e.name)}</option>`).join('');
  pick.innerHTML=`<label>A <select id="cmp-a">${opts}</select></label>
    <label>B <select id="cmp-b">${opts}</select></label>`;
  const selA=$('#cmp-a'), selB=$('#cmp-b');
  if(selB&&pool.length>1)selB.value=pool[1].id;
  function render(){
    const a=pool.find(x=>x.id===selA.value), b=pool.find(x=>x.id===selB.value);
    if(!a||!b)return;
    body.innerHTML=`<table class="term-table"><thead><tr><th>Metric</th><th>${esc(a.name.slice(0,24))}</th><th>${esc(b.name.slice(0,24))}</th></tr></thead><tbody>
      <tr><td>MoS</td><td class="num"><b>${a.mos>0?'+':''}${a.mos}</b></td><td class="num"><b>${b.mos>0?'+':''}${b.mos}</b></td></tr>
      <tr><td>Exposure</td><td class="num">${a.exp}</td><td class="num">${b.exp}</td></tr>
      <tr><td>Preparedness</td><td class="num">${a.prep}</td><td class="num">${b.prep}</td></tr>
      <tr><td>Measured</td><td class="num">${a.meas}%</td><td class="num">${b.meas}%</td></tr>
      <tr><td>Quadrant</td><td>${QLAB[a.quad]}</td><td>${QLAB[b.quad]}</td></tr>
    </tbody></table>`;
  }
  selA.onchange=selB.onchange=render; render();
}

function initIndexTerminal(){
  if(!$('#terminal'))return;
  drawIndexRegression();
  drawIndexScoreboard();
  drawStrategyMap();
  renderAlphaTable();
  renderComparePanel();
  drawCarrierSwarm($('#term-swarm'));
  drawCarrierQuadStack($('#term-quad-stack'));
  $('#term-board-tabs')?.querySelectorAll('.term-tab').forEach(b=>b.onclick=()=>{
    termBoard=b.dataset.b;
    $('#term-board-tabs').querySelectorAll('.term-tab').forEach(x=>x.classList.toggle('on',x===b));
    drawIndexScoreboard();
  });
  initTermViewTabs();
}

function initTermViewTabs(){
  const root=$('#term-grid-bento');
  const tabs=$('#term-view-tabs');
  if(!root||!tabs)return;
  const panels=[...root.querySelectorAll('[data-term-view]')];
  function show(view){
    tabs.querySelectorAll('.term-view-tab').forEach(b=>b.classList.toggle('on',b.dataset.view===view));
    panels.forEach(p=>p.classList.toggle('on',p.dataset.termView===view));
    if(view==='carriers'){
      drawCarrierSwarm($('#term-swarm'));
      drawCarrierQuadStack($('#term-quad-stack'));
    }
  }
  tabs.querySelectorAll('.term-view-tab').forEach(b=>b.onclick=()=>show(b.dataset.view));
  show('overview');
}

function initHeroLayerChart(){
  const m=$('#hero-layer-chart');
  if(m) drawMosByLayer(m);
}

function refreshIndex(){renderBenchmark();renderCards();draw();table();initIndexTerminal();initHeroLayerChart();}

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
    g.addEventListener('click',()=>openProfile(p.id));
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
    const tr=document.createElement('tr'); tr.className='row'; tr.onclick=()=>openProfile(p.id);
    const m=Math.round(meas(p)*100);
    tr.innerHTML=`<td><span class="tbl-name">${logoHtml(p,'xs',true)}<span class="tbl-entity-name">${esc(p.name)}</span></span></td><td class="num">${p.layer}</td>
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

/* ---------- entity profile (#/carrier/:id) ---------- */
let profilesCache=null;
async function loadProfiles(){
  if(profilesCache)return profilesCache;
  try{
    const r=await fetch('data/profiles.json');
    profilesCache=await r.json();
  }catch(e){profilesCache={};}
  return profilesCache;
}
function profileSwarmHtml(portfolio){
  if(!portfolio||!portfolio.assets||!portfolio.assets.length)return '';
  const W=640,H=100,PAD={l:40,r:16,t:16,b:28};
  const mos=portfolio.assets.map(a=>a.mos);
  const xMin=Math.min(...mos,portfolio.mosAvg||0)-5,xMax=Math.max(...mos,...mos,portfolio.mosAvg||0)+5;
  const X=x=>PAD.l+((x-xMin)/(xMax-xMin||1))*(W-PAD.l-PAD.r);
  let svg=`<svg viewBox="0 0 ${W} ${H}" class="chart" role="img"><title>Linked assets by MoS</title>`;
  portfolio.assets.forEach((a,i)=>{
    const cx=X(a.mos), cy=36+(i%4)*12;
    svg+=`<circle cx="${cx}" cy="${cy}" r="4.5" fill="${qColor(a.quad)}" opacity=".85"/>`;
  });
  if(portfolio.mosAvg!=null){
    const lx=X(portfolio.mosAvg);
    svg+=`<line x1="${lx}" y1="${PAD.t}" x2="${lx}" y2="${H-PAD.b}" stroke="${cssVar('--accent')}" stroke-width="2" stroke-dasharray="5 4"/>`;
  }
  svg+='</svg>';
  return `<div class="profile-swarm"><h4 class="sf-head">Linked assets (${portfolio.n})</h4>${svg}</div>`;
}
function renderProfileBody(p){
  const dec=(lat,det,eff,lbl)=>`<div class="score-decomp"><b>${lbl}</b> latent ${lat??'—'} · deterministic ${det??'—'} → <b>${eff}</b></div>`;
  const m=Math.round(((p.detExp||0)+(p.detPrep||0))/2*100);
  const exec=p.executive_summary?`<div class="profile-block profile-exec"><h4 class="sf-head">Analysis</h4><p class="profile-prose">${esc(p.executive_summary)}</p></div>`:'';
  const placements=(p.placements&&p.placements.length)?`<div class="profile-block"><h4 class="sf-head">Products &amp; placements</h4><div class="chip-row">${p.placements.map(pl=>`<a class="chip" href="${esc(pl.url||'#')}" target="_blank" rel="noopener">${esc(pl.label||pl.id)}</a>`).join('')}</div></div>`:'';
  const portN=p.portfolio_narrative?`<div class="profile-block"><h4 class="sf-head">Portfolio shape</h4><p class="profile-prose">${esc(p.portfolio_narrative)}</p></div>`:'';
  return `
    ${exec}
    <div class="score-row">
      <div class="score-cell">Exposure<b>${p.exp}</b></div><div class="score-cell">Preparedness<b>${p.prep}</b></div>
      <div class="score-cell">Margin of Safety<b style="color:${qColor(p.quad)}">${p.mos>0?'+':''}${p.mos}</b></div>
      <div class="score-cell">Measured<b>${m}%</b></div></div>
    ${dec(p.expLat,p.expDet,p.exp,'Exposure axis:')}${dec(p.prepLat,p.prepDet,p.prep,'Preparedness axis:')}
    ${profileAxisRationale(p)}
    ${profileRegisterFacts(p)}
    ${profileEntityAnalysis(p)}
    ${portN}${placements}
    ${profileSwarmHtml(p.portfolio)}
    <div class="sf-head"><span>Exposure sub-factors</span><span class="text-muted">measured ${Math.round((p.detExp||0)*100)}%</span></div>
    ${(p.exposure||[]).map(sfBlock).join('')}
    <div class="sf-head"><span>Preparedness sub-factors</span><span class="text-muted">measured ${Math.round((p.detPrep||0)*100)}%</span></div>
    ${(p.preparedness||[]).map(sfBlock).join('')}
    <p class="profile-method-strip text-muted">Scores fuse latent research and register/filing inputs: <code>r_eff = λ·r_det + (1−λ)·r_lat</code>. <a href="methodology.html">Full methodology →</a></p>
    ${p.note?`<p class="text-muted" style="margin-top:12px">${esc(p.note)}</p>`:''}
    ${p.provenance&&p.provenance.last_checked?`<p class="text-muted" style="margin-top:8px">Last checked ${esc(p.provenance.last_checked)}</p>`:''}`;
}
async function openProfile(id){
  const slim=D.pts.find(x=>x.id===id);
  if(!slim)return;
  const profs=await loadProfiles();
  const full=profs[id];
  if(!full){openDrawer(id);return;}
  const p=full;
  $('#profile-hero').innerHTML=`<div class="profile-hero-row">${logoHtml(p,'sm',true)}
    <div><h2 class="profile-hero-title">${esc(p.name)}</h2>
    <div class="text-muted">${LAYER[p.layer]||'L'+p.layer} · ${esc(p.type)}${p.parent?' · '+esc(p.parent):''}</div></div></div>`;
  $('#profile-body').innerHTML=renderProfileBody(p);
  $('#profile').classList.add('on'); $('#profile').setAttribute('aria-hidden','false');
  $('#scrim').classList.add('on');
  closeDrawer();
  if(location.hash!==`#/carrier/${id}`)history.pushState(null,'',`#/carrier/${id}`);
}
function closeProfile(){
  $('#profile').classList.remove('on'); $('#profile').setAttribute('aria-hidden','true');
  if(!$('#drawer').classList.contains('on'))$('#scrim').classList.remove('on');
  if(location.hash.startsWith('#/carrier/'))history.pushState(null,'',location.pathname+location.search);
}
function closeAllPanels(){closeProfile();closeDrawer();}
function initProfileRouter(){
  async function route(){
    const m=location.hash.match(/^#\/carrier\/([^/]+)/);
    if(m)await openProfile(decodeURIComponent(m[1]));
    else closeProfile();
  }
  addEventListener('hashchange',route);
  route();
}

/* ---------- entity drawer (methodology + quick peek) ---------- */
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
  const q=s.question?`<p class="sf-question"><b>Mining question:</b> ${esc(s.question)}</p>`:'';
  const mv=s.measured_value?`<p class="sf-measured"><b>Register / filing:</b> ${esc(s.measured_value)}</p>`:'';
  const gap=s.tier==='assessed'?'<p class="sf-gap-note">Assessed — no register or filing row yet for this line.</p>':'';
  return `<div class="sf-card"><div class="sf-top"><span class="sf-name">${s.label}</span>
    <span class="sf-mode ${s.mode}">${s.mode}</span><span class="sf-weight">w ${s.weight}</span></div>
    ${q}${mv}
    <div class="sf-rationale">${esc(s.rationale)}</div>
    ${gap}
    <div class="sf-evidence"><span class="text-muted">lat ${ratbar(s.lat)} · det ${s.det==null?'—':ratbar(s.det)} · <b>eff ${s.eff}</b>${s.lambda?` · λ ${s.lambda}`:''}</span>
      <span class="ev-tier">${s.tier}</span> ${srcs} ${cites}</div></div>`;
}
function profileRegisterFacts(p){
  const al=p.asset_link; if(!al)return '';
  const rows=[];
  if(al.gate_status)rows.push(['Gate status',al.gate_status.replace(/_/g,' ')]);
  if(al.mw&&al.mw!=='unknown')rows.push(['Capacity',al.mw]);
  if(al.connection&&al.connection!=='unknown')rows.push(['Connection',al.connection]);
  if(al.curtailment_exposure)rows.push(['Curtailment exposure',al.curtailment_exposure]);
  if(al.backup_generation)rows.push(['Backup generation',al.backup_generation]);
  if(!rows.length)return '';
  return `<div class="profile-block"><h4 class="sf-head">Register facts</h4><dl class="profile-facts">${rows.map(([k,v])=>`<div><dt>${esc(k)}</dt><dd>${esc(String(v))}</dd></div>`).join('')}</dl></div>`;
}
function profileEntityAnalysis(p){
  const ea=p.entity_analysis; if(!ea)return '';
  let html='';
  const gp=ea.grid_posture;
  if(gp){
    const bits=[gp.mw_phase1!=null?`${gp.mw_phase1} MW phase 1`:null,gp.mw_max!=null?`${gp.mw_max} MW max`:null,gp.dno,gp.connection?`connection: ${gp.connection}`:null,gp.gate_status?`gate: ${gp.gate_status}`:null].filter(Boolean);
    html+=`<div class="profile-block"><h4 class="sf-head">Grid posture</h4><p class="profile-prose">${esc(bits.join(' · '))}${gp.constraint_zone?` — ${esc(gp.constraint_zone)}`:''}</p></div>`;
  }
  if(ea.risk_manifestation&&ea.risk_manifestation.length){
    html+=`<div class="profile-block"><h4 class="sf-head">How risk manifests</h4>${ea.risk_manifestation.map(r=>`<div class="risk-card"><b>${esc(r.headline)}</b><p>${esc(r.mechanism)}</p><p class="text-muted"><b>Insured today:</b> ${esc(r.insured_today||'unknown')}</p></div>`).join('')}</div>`;
  }
  const cs=ea.cover_stack;
  if(cs){
    html+=`<div class="profile-block"><h4 class="sf-head">Insurance &amp; cover stack <span class="text-muted">(${esc(cs.placement_status||'unknown')})</span></h4>`;
    if(cs.evidenced&&cs.evidenced.length){
      html+=`<p class="profile-kicker">Evidenced</p><ul class="cover-list">${cs.evidenced.map(c=>`<li><b>${esc(c.cover)}</b>${c.carrier_or_broker?' · '+esc(c.carrier_or_broker):''} — ${esc(c.trigger||'')}</li>`).join('')}</ul>`;
    }else html+=`<p class="profile-prose text-muted">No named insurer, broker or policy schedule in public sources.</p>`;
    if(cs.inferred_typical&&cs.inferred_typical.length){
      html+=`<p class="profile-kicker">Inferred (typical for stage)</p><ul class="cover-list cover-inferred">${cs.inferred_typical.map(c=>`<li><b>${esc(c.cover)}</b> (${esc(c.stage||'')}) — ${esc(c.trigger||'')}. <span class="text-muted">${esc(c.basis||'')}</span></li>`).join('')}</ul>`;
    }
    if(cs.absent&&cs.absent.length){
      html+=`<p class="profile-kicker">Absent / gap</p><ul class="cover-list cover-absent">${cs.absent.map(c=>`<li><b>${esc(c.cover)}</b> → ${esc(c.maps_to_subfactor||'')} — ${esc(c.note||'')}</li>`).join('')}</ul>`;
    }
    if(cs.gaps&&cs.gaps.length){
      html+=`<p class="profile-kicker">Still to mine</p><ul class="cover-list">${cs.gaps.map(g=>`<li>${esc(g)}</li>`).join('')}</ul>`;
    }
    html+='</div>';
  }
  if(ea.mining&&ea.mining.method_note){
    html+=`<p class="profile-mining-note text-muted">${esc(ea.mining.method_note)}${ea.mining.last_checked?' · checked '+esc(ea.mining.last_checked):''}</p>`;
  }
  return html;
}
function profileAxisRationale(p){
  const ar=p.axis_rationale; if(!ar)return '';
  let html='';
  if(ar.exposure)html+=`<div class="profile-block"><h4 class="sf-head">Exposure rationale</h4><p class="profile-prose">${esc(ar.exposure)}</p></div>`;
  if(ar.preparedness)html+=`<div class="profile-block"><h4 class="sf-head">Preparedness rationale</h4><p class="profile-prose">${esc(ar.preparedness)}</p></div>`;
  return html;
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
function closeDrawer(){$('#drawer').classList.remove('on');if(!$('#profile').classList.contains('on'))$('#scrim').classList.remove('on');}
function citePop(id){const c=D.cites[id];if(!c){alert(id);return;}
  alert(`${id}\n\n${c.t}\n${c.a} (${c.y})\n\n${c.use}\n\n${c.u}`);}
addEventListener('keydown',e=>{if(e.key==='Escape')closeAllPanels();});

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
  g0.appendChild(el('circle',{cx:String(cx),cy:String(cy),r:'10',fill:KTYPE[n.type]||'#B85A32',stroke:'#fff','stroke-width':'2'}));
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
initProfileRouter();
initThesisTOC();
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
  const charts=D.indexCharts||D.thesisCharts;
  const data=charts&&charts.mos_regression;
  if(!mount||!data||!data.pts.length)return;
  const pts=data.pts, stats=data.stats;
  const W=520,H=300,PAD={l:48,r:20,t:36,b:52};
  const xs=pts.map(p=>p.x), ys=pts.map(p=>p.y);
  const xMin=Math.min(...xs)-5, xMax=Math.max(...xs)+5;
  const yMaxRaw=Math.max(...ys,0);
  const sparseMeas=yMaxRaw<0.02;
  const yMin=0, yMax=sparseMeas?0.14:Math.max(0.2,Math.ceil(yMaxRaw*20)/20);
  const X=x=>PAD.l+((x-xMin)/(xMax-xMin||1))*(W-PAD.l-PAD.r);
  const Y=y=>H-PAD.b-((y-yMin)/(yMax-yMin))*(H-PAD.t-PAD.b);
  const svg=thesisEl('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img','aria-label':'MoS vs measured share'});
  for(let i=0;i<=4;i++){
    const yv=yMin+(yMax-yMin)*i/4;
    const gy=Y(yv);
    svg.appendChild(thesisEl('line',{x1:PAD.l,y1:gy,x2:W-PAD.r,y2:gy,stroke:cssVar('--chart-grid'),opacity:.5}));
    const t=thesisEl('text',{x:PAD.l-6,y:gy+3,'text-anchor':'end','font-size':10,fill:cssVar('--muted')});
    t.textContent=Math.round(yv*100)+'%'; svg.appendChild(t);
  }
  termNiceTicks(xMin,xMax,5).forEach(v=>{
    const gx=X(v);
    svg.appendChild(thesisEl('line',{x1:gx,y1:PAD.t,x2:gx,y2:H-PAD.b,stroke:cssVar('--chart-grid'),opacity:.35}));
    const t=thesisEl('text',{x:gx,y:H-PAD.b+16,'text-anchor':'middle','font-size':10,fill:cssVar('--muted')});
    t.textContent=(v>0?'+':'')+v; svg.appendChild(t);
  });
  if(stats&&stats.slope!==undefined&&!sparseMeas){
    const y0=stats.intercept+stats.slope*xMin, y1=stats.intercept+stats.slope*xMax;
    svg.appendChild(thesisEl('line',{x1:X(xMin),y1:Y(Math.max(yMin,Math.min(yMax,y0))),x2:X(xMax),y2:Y(Math.max(yMin,Math.min(yMax,y1))),
      stroke:cssVar('--accent'),'stroke-width':2,opacity:.75}));
  }
  if(sparseMeas){
    const note=thesisEl('text',{x:(PAD.l+W-PAD.r)/2,y:PAD.t+14,'text-anchor':'middle','font-size':10,fill:cssVar('--muted')});
    note.textContent='Dots spread for visibility — all at 0% measured'; svg.appendChild(note);
  }
  layoutTermScatter(pts,'x','y',1).forEach(({p,ox,oy})=>{
    let cy=Y(p.y);
    if(sparseMeas) cy=Y(0.02)+oy*0.6;
    const g=thesisEl('g',{class:'plot-dot'});
    g.appendChild(thesisEl('circle',{cx:X(p.x)+ox,cy,r:5,fill:qColor(p.quad),opacity:.88,stroke:'#fff','stroke-width':1}));
    g.addEventListener('mouseenter',e=>tip(e,{...p,name:p.name||p.id,layer:p.layer||0,type:'',conf:'low',exp:0,prep:0,mos:p.x,detExp:p.y,detPrep:p.y}));
    g.addEventListener('mouseleave',hideTip);
    g.addEventListener('click',()=>openProfile(p.id));
    svg.appendChild(g);
  });
  let ax=thesisEl('text',{x:(PAD.l+W-PAD.r)/2,y:H-8,'text-anchor':'middle','font-size':11,'font-weight':600,fill:cssVar('--ink')});
  ax.textContent='Margin of Safety →'; svg.appendChild(ax);
  let ay=thesisEl('text',{x:14,y:(PAD.t+H-PAD.b)/2,'text-anchor':'middle','font-size':11,'font-weight':600,fill:cssVar('--ink'),
    transform:`rotate(-90 14 ${(PAD.t+H-PAD.b)/2})`}); ay.textContent='Measured share →'; svg.appendChild(ay);
  mount.innerHTML=''; mount.appendChild(svg);
}

function drawScoreboard(mount,bars){
  if(!mount||!bars||!bars.length)return;
  const sorted=[...bars].sort((a,b)=>b.mean-a.mean);
  const mx=Math.max(...sorted.map(b=>Math.abs(b.mean)),1);
  const labelW=Math.max(108,...sorted.map(b=>(b.label||'').length*6.5));
  const W=520, rowH=32, barH=14, PAD={l:labelW+12,r:72,t:12,b:8};
  const xMin=-mx*1.15, xMax=mx*1.15;
  const zeroX=PAD.l+((0-xMin)/(xMax-xMin))*(W-PAD.l-PAD.r);
  const X=v=>PAD.l+((v-xMin)/(xMax-xMin))*(W-PAD.l-PAD.r);
  const svg=thesisEl('svg',{viewBox:`0 0 ${W} ${sorted.length*rowH+PAD.t+PAD.b}`,class:'chart term-score-svg',role:'img','aria-label':'MoS scoreboard'});
  svg.appendChild(thesisEl('line',{x1:zeroX,y1:PAD.t,x2:zeroX,y2:PAD.t+sorted.length*rowH,stroke:cssVar('--chart-grid'),'stroke-dasharray':'3 3'}));
  sorted.forEach((b,i)=>{
    const y=PAD.t+i*rowH;
    const t=thesisEl('text',{x:0,y:y+rowH*0.62,'font-size':11,fill:cssVar('--ink2')});
    t.textContent=b.label.length>18?b.label.slice(0,16)+'…':b.label; svg.appendChild(t);
    const col=b.mean>=0?cssVar('--earning-s'):cssVar('--exposed');
    const x0=b.mean>=0?zeroX:X(b.mean), bw=Math.max(2,Math.abs(X(b.mean)-zeroX));
    svg.appendChild(thesisEl('rect',{x:Math.min(x0,zeroX),y:y+4,width:bw,height:barH,rx:3,fill:col,opacity:.88}));
    if(b.std>0){
      const sLo=X(b.mean-b.std), sHi=X(b.mean+b.std);
      svg.appendChild(thesisEl('line',{x1:sLo,y1:y+barH/2+4,x2:sHi,y2:y+barH/2+4,stroke:col,'stroke-width':2,opacity:.5}));
    }
    const val=`${b.mean>0?'+':''}${b.mean}`;
    const tx=b.mean>=0?zeroX+bw+6:zeroX-bw-6;
    const t2=thesisEl('text',{x:tx,y:y+rowH*0.62,'text-anchor':b.mean>=0?'start':'end','font-size':11,fill:cssVar('--ink'),'font-weight':600});
    t2.textContent=`${val} · n=${b.n}`; svg.appendChild(t2);
  });
  mount.innerHTML=''; mount.appendChild(svg);
}

function drawMosByLayer(mount){
  const charts=D.indexCharts||D.thesisCharts;
  const bars=charts&&charts.mos_by_layer&&charts.mos_by_layer.bars;
  drawScoreboard(mount,bars);
}

function drawMosBySegment(mount){
  const charts=D.indexCharts||D.thesisCharts;
  const bars=charts&&charts.mos_by_segment&&charts.mos_by_segment.bars;
  drawScoreboard(mount,bars);
}

function drawCarrierSwarm(mount){
  const charts=D.indexCharts||D.thesisCharts;
  const sw=charts&&charts.carrier_swarm;
  if(!mount||!sw)return;
  const carriers=sw.carriers||[];
  if(!carriers.length){
    mount.innerHTML='<p class="term-empty">No carrier–asset links in the current universe.</p>';
    return;
  }
  let sel=sw.default||carriers[0].id;
  const wrap=document.createElement('div');
  wrap.className='term-swarm-wrap';
  const seg=document.createElement('div');
  seg.className='term-swarm-seg';
  seg.innerHTML=carriers.slice(0,12).map(c=>{
    const label=(c.name||'').split('/')[0].split(' ')[0].slice(0,16);
    return `<button type="button" class="term-swarm-btn${c.id===sel?' on':''}" data-c="${esc(c.id)}" title="${esc(c.name)}">${esc(label)}${c.n?` (${c.n})`:''}</button>`;
  }).join('');
  const meta=document.createElement('p');
  meta.className='term-hint term-swarm-meta';
  const chart=document.createElement('div');
  chart.className='term-chart term-swarm-chart';
  wrap.appendChild(seg); wrap.appendChild(meta); wrap.appendChild(chart);
  mount.innerHTML=''; mount.appendChild(wrap);
  function render(){
    const carrier=carriers.find(c=>c.id===sel)||carriers[0];
    const assets=(sw.byCarrier&&sw.byCarrier[sel])||[];
    if(!assets.length){
      meta.textContent='No linked assets for this entity yet.';
      chart.innerHTML='<p class="term-empty">Link assets via coverage evidence to populate this view.</p>';
      return;
    }
    meta.textContent=`${assets.length} linked asset${assets.length===1?'':'s'} · dashed line = entity MoS (${carrier.mos>0?'+':''}${carrier.mos})`;
    const W=520,H=Math.max(140,Math.min(280,assets.length*22+56)),labelW=168,PAD={l:labelW+8,r:16,t:16,b:40};
    const mosVals=assets.map(a=>a.mos);
    const cMos=carrier.mos;
    const xMin=Math.min(...mosVals,cMos)-8, xMax=Math.max(...mosVals,cMos)+8;
    const X=x=>PAD.l+((x-xMin)/(xMax-xMin||1))*(W-PAD.l-PAD.r);
    const svg=thesisEl('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart term-swarm-svg',role:'img','aria-label':'Linked assets by margin of safety'});
    for(let i=0;i<=4;i++){
      const xv=xMin+(xMax-xMin)*i/4;
      const gx=X(xv);
      svg.appendChild(thesisEl('line',{x1:gx,y1:PAD.t,x2:gx,y2:H-PAD.b,stroke:cssVar('--chart-grid'),opacity:.35}));
      const t=thesisEl('text',{x:gx,y:H-8,'text-anchor':'middle','font-size':10,fill:cssVar('--muted')});
      t.textContent=(xv>0?'+':'')+Math.round(xv); svg.appendChild(t);
    }
    assets.forEach((a,i)=>{
      const rowH=(H-PAD.t-PAD.b)/Math.max(assets.length,1);
      const cy=PAD.t+rowH*i+rowH/2;
      const cx=X(a.mos);
      const lbl=thesisEl('text',{x:8,y:cy+3,'font-size':10,fill:cssVar('--ink2')});
      lbl.textContent=(a.name||'').slice(0,24); svg.appendChild(lbl);
      const g=thesisEl('g',{class:'plot-dot'});
      g.appendChild(thesisEl('circle',{cx,cy,r:5,fill:qColor(a.quad),opacity:.9,stroke:'#fff','stroke-width':1}));
      g.addEventListener('click',()=>openProfile(a.id));
      svg.appendChild(g);
    });
    const lx=X(cMos);
    svg.appendChild(thesisEl('line',{x1:lx,y1:PAD.t,x2:lx,y2:H-PAD.b,stroke:cssVar('--accent'),'stroke-width':2,'stroke-dasharray':'5 4'}));
    let ax=thesisEl('text',{x:(PAD.l+W-PAD.r)/2,y:H-22,'text-anchor':'middle','font-size':11,'font-weight':600,fill:cssVar('--ink')});
    ax.textContent='Margin of Safety →'; svg.appendChild(ax);
    chart.innerHTML=''; chart.appendChild(svg);
  }
  seg.querySelectorAll('.term-swarm-btn').forEach(b=>b.onclick=()=>{
    sel=b.dataset.c;
    seg.querySelectorAll('.term-swarm-btn').forEach(x=>x.classList.toggle('on',x===b));
    render();
  });
  render();
}

function drawCarrierQuadStack(mount){
  const charts=D.indexCharts||D.thesisCharts;
  const bars=charts&&charts.carrier_quad_stack&&charts.carrier_quad_stack.bars;
  if(!mount)return;
  if(!bars||!bars.length){
    mount.innerHTML='<p class="term-empty">No linked portfolios to stack — add coverage links to populate.</p>';
    return;
  }
  const W=520, rowH=28, labelW=130, order=['earning_it','whitespace','sidelined','exposed'];
  const labels={earning_it:'Earning',whitespace:'Whitespace',sidelined:'Sidelined',exposed:'Exposed'};
  const H=rowH*bars.length+36;
  const svg=thesisEl('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart term-quad-svg',role:'img','aria-label':'Linked asset quadrant mix by entity'});
  bars.forEach((b,i)=>{
    const y=8+i*rowH;
    const t=thesisEl('text',{x:0,y:y+17,'font-size':10.5,fill:cssVar('--ink2')});
    t.textContent=(b.name||'').slice(0,22); svg.appendChild(t);
    let x=labelW, trackW=W-labelW-8;
    order.forEach(q=>{
      const frac=b.counts&&b.counts[q]?b.counts[q]:0;
      if(frac<=0)return;
      const w=Math.max(2,frac*trackW);
      svg.appendChild(thesisEl('rect',{x,y:y+6,width:w,height:14,rx:2,fill:qColor(q),opacity:.9}));
      if(frac>=0.18){
        const pct=thesisEl('text',{x:x+w/2,y:y+16,'text-anchor':'middle','font-size':9,fill:'#fff','font-weight':600});
        pct.textContent=Math.round(frac*100)+'%'; svg.appendChild(pct);
      }
      x+=w;
    });
    const nt=thesisEl('text',{x:W-4,y:y+17,'text-anchor':'end','font-size':10,fill:cssVar('--muted')});
    nt.textContent=`n=${b.n}`; svg.appendChild(nt);
  });
  let lx=labelW;
  order.forEach(q=>{
    svg.appendChild(thesisEl('rect',{x:lx,y:H-14,width:10,height:10,rx:2,fill:qColor(q)}));
    const lt=thesisEl('text',{x:lx+14,y:H-5,'font-size':9,fill:cssVar('--muted')});
    lt.textContent=labels[q]; svg.appendChild(lt);
    lx+=72;
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
    if(kind==='quadrant_scatter')drawThesisScatter(mount,fig.dataset.readonly==='1');
    else if(kind==='mos_by_layer')drawMosByLayer(mount);
    else if(kind==='inforce_rail')drawThesisRail(mount);
  });
  const ev=$('#thesis-eval');
  if(ev&&D.evals)ev.innerHTML=D.evals.map(e=>`<span class="eval-chip ${e.status}" title="${esc(e.metric)}">
    <span class="eval-dot"></span><b>L${e.level}</b> ${e.status}</span>`).join('');
  initThesisTabs();
  initThesisTOC();
  observeMotion(document);
}

if(document.body.classList.contains('site--thesis'))initThesisCharts();
else if(document.body.classList.contains('site--methodology'))initMethodologyPage();
else observeMotion(document);"""
