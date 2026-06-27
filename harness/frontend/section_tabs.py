"""Section tabs — scroll-spy for sticky top nav."""

SECTION_TABS_JS = r"""
/* ---------- section tabs (top nav) ---------- */
(function initSectionTabs(){
  const nav=$('#section-tabs'); if(!nav)return;
  const links=[...nav.querySelectorAll('.section-tab')];
  const hashLinks=links.filter(a=>{
    const h=a.getAttribute('href')||'';
    return h.startsWith('#')&&h.length>1;
  });
  if(!hashLinks.length) return;

  function spyTarget(id){
    const el=document.getElementById(id);
    if(!el) return null;
    if(el.tagName==='DETAILS') return el.querySelector('summary')||el;
    return el;
  }

  const sections=hashLinks.map(a=>spyTarget((a.getAttribute('href')||'').slice(1))).filter(Boolean);

  function setActive(id){
    links.forEach(a=>{
      const h=a.getAttribute('href')||'';
      const match=h===('#'+id)||(h.startsWith('#')&&h.slice(1)===id);
      a.classList.toggle('on',match);
    });
  }

  function openDisclosure(id){
    const el=document.getElementById(id);
    if(el?.tagName==='DETAILS') el.open=true;
  }

  if(location.hash){
    const id=location.hash.slice(1);
    if(document.getElementById(id)){
      openDisclosure(id);
      setActive(id);
    }
  }

  const io=new IntersectionObserver(es=>{
    const visible=es.filter(e=>e.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio);
    if(!visible[0]) return;
    const t=visible[0].target;
    const id=t.tagName==='SUMMARY'&&t.parentElement?.id?t.parentElement.id:t.id;
    if(id) setActive(id);
  },{rootMargin:'-35% 0px -45% 0px',threshold:[0,0.12,0.35]});
  sections.forEach(s=>io.observe(s));

  hashLinks.forEach(a=>a.addEventListener('click',()=>{
    const id=(a.getAttribute('href')||'').slice(1);
    if(id){
      openDisclosure(id);
      setActive(id);
    }
  }));

  $('#analytics-deep')?.addEventListener('toggle',()=>{
    if($('#analytics-deep')?.open) requestAnimationFrame(()=>initIndexTerminal?.());
  });
})();
"""
