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

  const sections=hashLinks.map(a=>{
    const id=(a.getAttribute('href')||'').slice(1);
    return document.getElementById(id);
  }).filter(Boolean);

  function setActive(id){
    links.forEach(a=>{
      const h=a.getAttribute('href')||'';
      const match=h===('#'+id)||(h.startsWith('#')&&h.slice(1)===id);
      a.classList.toggle('on',match);
    });
  }

  if(location.hash){
    const id=location.hash.slice(1);
    if(document.getElementById(id)) setActive(id);
  }

  const io=new IntersectionObserver(es=>{
    const visible=es.filter(e=>e.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio);
    if(visible[0]) setActive(visible[0].target.id);
  },{rootMargin:'-35% 0px -45% 0px',threshold:[0,0.12,0.35]});
  sections.forEach(s=>io.observe(s));

  hashLinks.forEach(a=>a.addEventListener('click',()=>{
    const id=(a.getAttribute('href')||'').slice(1);
    if(id) setActive(id);
  }));
})();
"""
