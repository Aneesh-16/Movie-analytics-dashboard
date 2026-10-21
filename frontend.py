"""Frontend: HTML, CSS and JavaScript kept as Python strings and served by FastAPI (no separate web files)."""

CSS = """
:root{--navy:#0b1426;--navy2:#16233f;--blue:#2563eb;--violet:#7c3aed;--bg:#eef2f8;--card:#fff;--tx:#0f172a;--mut:#64748b;--bd:#e2e8f0}
*{box-sizing:border-box}body{margin:0;font:14px/1.45 Inter,"Segoe UI",system-ui,Arial,sans-serif;color:var(--tx);background:var(--bg)}
.app{display:flex;min-height:100vh}
aside{width:232px;background:linear-gradient(180deg,#0b1426,#101d38 60%,#1a1650);color:#cbd5e1;padding:16px 12px;position:fixed;top:0;bottom:0;overflow:auto;z-index:20;display:flex;flex-direction:column}
.brand{display:flex;align-items:center;gap:10px;color:#fff;font-weight:700;font-size:16px;padding:4px 8px 18px}.brand i{font-style:normal;width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,var(--blue),var(--violet));display:grid;place-items:center}
.nav a{display:flex;gap:11px;align-items:center;color:#b6c2d9;text-decoration:none;padding:9px 12px;border-radius:10px;margin-bottom:3px;font-size:13px}
.nav a span{width:20px;text-align:center}.nav a:hover{background:#ffffff14;color:#fff}.nav a.on{background:linear-gradient(90deg,var(--blue),#4f46e5);color:#fff;box-shadow:0 6px 16px #2563eb55}
.credit{margin-top:auto;font-size:10.5px;color:#7d8ba8;padding:14px 8px 0;line-height:1.35}
main{margin-left:232px;flex:1;min-width:0;padding-bottom:70px}
.top{display:flex;gap:12px;align-items:center;padding:12px 22px;background:#fff;border-bottom:1px solid var(--bd);position:sticky;top:0;z-index:10;flex-wrap:wrap}
.top form{display:flex;flex:1;max-width:460px}.top input{flex:1;padding:9px 14px;border:1px solid #cbd5e1;border-right:0;border-radius:10px 0 0 10px;min-width:0;background:#f8fafc}
.btn{background:var(--blue);color:#fff;border:0;padding:9px 16px;border-radius:10px;cursor:pointer;font-weight:600;font-size:13px}.btn:hover{filter:brightness(1.08)}
.top form .btn{border-radius:0 10px 10px 0}.btn.o{background:#fff;color:var(--blue);border:1px solid #bfd0f7;padding:6px 11px;font-size:12px}.btn.o.on{background:#eaf1ff;border-color:var(--blue)}.btn:disabled{opacity:.45;cursor:default}
#auth{display:flex;gap:8px;align-items:center;margin-left:auto;flex-wrap:wrap}#auth small{color:var(--mut)}#burger{display:none;background:none;border:0;font-size:22px;cursor:pointer}
.content{padding:0 22px 24px}
.ph{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap;padding:22px 0 14px}.ph h1{margin:0;font-size:26px;letter-spacing:-.3px}.ph p{margin:3px 0 0;color:var(--mut)}
.pf{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap}.pf label,.flt label{font-size:11px;font-weight:600;color:#475569;display:block}.pf select,.pf input,.flt input,.flt select,.sel{padding:8px 10px;border:1px solid #cbd5e1;border-radius:9px;background:#fff;font:inherit;display:block;margin-top:3px}
.hero{margin:18px 22px 0;border-radius:18px;padding:26px 28px 70px;color:#fff;background:radial-gradient(circle at 85% 20%,#7c3aed99,transparent 45%),linear-gradient(120deg,#0b1426,#1e3a8a 70%,#312e81)}
.hero h1{margin:0 0 4px;font-size:30px}.hero p{margin:0;color:#c7d2fe}.chip2{display:inline-block;margin-top:12px;background:#ffffff1f;border:1px solid #ffffff33;border-radius:99px;padding:3px 12px;font-size:12px}
.hero .pf label{color:#c7d2fe}.hero .btn{background:#fff;color:#1e3a8a}.hero+.content{margin-top:-52px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:14px;margin-bottom:16px}
.kpi{background:var(--card);border-radius:16px;padding:15px;display:flex;gap:12px;align-items:center;box-shadow:0 6px 18px #0f172a1a}
.ico{width:48px;height:48px;border-radius:13px;display:grid;place-items:center;font-size:22px;flex:none}.kpi b{font-size:22px;display:block;line-height:1.1}.kpi small{color:var(--mut);font-size:12px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px;margin-bottom:16px}
.panel{background:var(--card);border-radius:16px;padding:16px;border:1px solid var(--bd);box-shadow:0 2px 10px #0f172a0d;min-width:0}
.panel h3{margin:0;font-size:15px}.panel .sub{margin:2px 0 10px;color:var(--mut);font-size:12px}.cv{position:relative;height:290px}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.note{padding:9px 13px;border-radius:10px;margin-bottom:12px;font-size:13px}.note.ok{background:#dcfce7;color:#166534}.note.bad{background:#fef2f2;color:#991b1b}.note.info{background:#eef2ff;color:#3730a3}
table{width:100%;border-collapse:collapse;background:#fff}th{text-align:left;background:#f8fafc;padding:9px 12px;font-size:12px;color:#334155;border-bottom:1px solid var(--bd)}
td{padding:8px 12px;border-bottom:1px solid var(--bd);vertical-align:middle}.tw{overflow-x:auto;border:1px solid var(--bd);border-radius:14px;background:#fff;margin-bottom:16px}
.pt{width:42px;height:62px;border-radius:6px;object-fit:cover;display:block;background:#1e293b}.pt.sm{width:38px;height:56px}
.lnk{color:var(--tx);cursor:pointer;font-weight:600}.lnk:hover{color:var(--blue)}
.chip{display:inline-block;background:#f1f5f9;color:#475569;border:1px solid var(--bd);border-radius:6px;padding:1px 8px;font-size:11px;margin:0 3px 3px 0}
.flt{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;align-items:end;margin-bottom:16px;background:#fff;border:1px solid var(--bd);border-radius:14px;padding:14px}.flt input,.flt select{width:100%}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(176px,1fr));gap:16px}
.mc{background:#fff;border:1px solid var(--bd);border-radius:14px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 2px 8px #0f172a0d;transition:.15s}.mc:hover{transform:translateY(-3px);box-shadow:0 10px 24px #0f172a26}
.pw{position:relative}.pc{width:100%;aspect-ratio:2/3;object-fit:cover;display:block;background:#1e293b}.rt{position:absolute;top:8px;right:8px;background:#0b1426cc;color:#fbbf24;font-weight:700;font-size:12px;padding:2px 8px;border-radius:99px}
.mi{padding:10px;display:flex;flex-direction:column;gap:3px;flex:1}.mi h4{margin:0;font-size:13.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.mi small{color:var(--mut);font-size:11.5px}
.ba{display:flex;gap:5px;flex-wrap:wrap;margin-top:auto;padding-top:8px}
.pager{display:flex;gap:10px;align-items:center;justify-content:flex-end;margin:12px 0;color:var(--mut)}
.muted{color:var(--mut)}.empty,.err{padding:34px;text-align:center;color:var(--mut)}
#banner .err{background:#fef2f2;color:#991b1b;border:1px solid #fecaca;border-radius:12px;margin:16px 22px;padding:12px;text-align:left}
#loader{position:fixed;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#2563eb,#8b5cf6,#2563eb);background-size:200%;animation:ld 1s linear infinite;display:none;z-index:99}#loader.on{display:block}@keyframes ld{to{background-position:-200%}}
.skel{height:120px;border-radius:14px;background:linear-gradient(90deg,#e6ebf3 25%,#f3f6fb 50%,#e6ebf3 75%);background-size:200%;animation:ld 1.2s linear infinite;margin:22px}
#modal{position:fixed;inset:0;background:#0f172acc;display:none;place-items:center;z-index:50;padding:16px}#modal.on{display:grid}
.md{background:#fff;border-radius:16px;max-width:780px;width:100%;max-height:92vh;overflow:auto;padding:22px;position:relative}.md .x{position:absolute;top:8px;right:14px;border:0;background:none;font-size:26px;cursor:pointer}
.head{display:flex;gap:18px}.head .pc{width:130px;border-radius:10px;flex:none}.facts{margin-top:12px}.facts td:first-child{color:var(--mut);width:150px}
.act{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:10px 0;padding:10px;background:#f5f7fd;border-radius:12px}.act input{width:64px}
.fm label{display:block;font-size:12px;font-weight:600;margin-bottom:10px}.fm input,.fm textarea{width:100%;padding:8px;border:1px solid #cbd5e1;border-radius:9px;font:inherit;margin-top:3px}.fm .two{display:grid;grid-template-columns:1fr 1fr;gap:0 12px}
#tray{position:fixed;left:232px;right:0;bottom:0;background:#0b1426;color:#fff;padding:10px 22px;display:none;gap:10px;align-items:center;z-index:15;flex-wrap:wrap}#tray.on{display:flex}#tray .tc{background:#ffffff1a;border-radius:99px;padding:3px 10px;font-size:12px}
.cmp td:first-child{color:var(--mut);width:130px;font-weight:600}.bar{height:7px;border-radius:4px;background:#e2e8f0;margin-top:4px}.bar i{display:block;height:100%;border-radius:4px;background:linear-gradient(90deg,var(--blue),var(--violet))}.best{font-weight:700;color:#166534}
.hl{margin:0;padding-left:18px}.hl li{margin:4px 0}.li{display:flex;gap:10px;align-items:center;padding:7px 0;border-bottom:1px solid var(--bd)}.li small{display:block;color:var(--mut)}
@media(max-width:900px){aside{transform:translateX(-100%);transition:.2s}aside.open{transform:none}main{margin-left:0}#burger{display:block}#tray{left:0}.grid2{grid-template-columns:1fr}.hero h1{font-size:22px}.head{flex-direction:column}.fm .two{grid-template-columns:1fr}}
"""

BODY = """
<div class="app">
<aside id="side"><div class="brand"><i>🎬</i> Movie Intelligence</div><nav class="nav" id="nav"></nav>
<div class="credit">Movie data: TMDB 5000 dataset, stored in a shared PostgreSQL database.<br><br>Poster images courtesy of TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB.</div></aside>
<main>
 <div class="top"><button id="burger" aria-label="menu">☰</button>
  <form id="gs"><input id="gq" placeholder="Search any movie title..."><button class="btn">Search</button></form><div id="auth"></div></div>
 <div id="banner"></div><div id="view"></div>
</main></div>
<div id="tray"></div><div id="loader"></div>
<div id="modal"><div class="md"><button class="x" onclick="closeModal()" aria-label="Close">&times;</button><div id="mbody"></div></div></div>
"""

JS = r"""
const $=s=>document.querySelector(s);
const PB='https://image.tmdb.org/t/p/w342';
const COLORS=['#2563eb','#7c3aed','#10b981','#f59e0b','#ef4444','#ec4899','#14b8a6','#f97316','#64748b','#eab308'];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fN=n=>n==null?'—':Number(n).toLocaleString();
const fR=n=>n==null?'—':Number(n).toFixed(1);
const fM=n=>n==null?'—':n>=1e9?'$'+(n/1e9).toFixed(2)+'B':n>=1e6?'$'+(n/1e6).toFixed(1)+'M':'$'+fN(n);
const fMm=v=>'$'+fN(Math.round(v))+'M', fB=v=>'$'+Number(v).toFixed(1)+'B', fP=v=>fN(Math.round(v))+'%';
const fD=s=>s?String(s).replace('T',' ').slice(0,16):'—';
let langName=c=>c;try{const dn=new Intl.DisplayNames(['en'],{type:'language'});langName=c=>{try{return dn.of(c)||c}catch{return c}}}catch{}
let pending=0;function busy(d){pending+=d;$('#loader').classList.toggle('on',pending>0)}

// ---- API helpers ----
let TOKEN=sessionStorage.getItem('tok'),USER=sessionStorage.getItem('usr'),ROLE=sessionStorage.getItem('role');
const isEditor=()=>ROLE==='editor';
const authH=()=>TOKEN?{Authorization:'Bearer '+TOKEN}:{};
async function apiError(r){let m=r.statusText;try{const d=(await r.json()).detail;
  m=typeof d==='string'?d:Array.isArray(d)?d.map(x=>((x.loc||[]).slice(-1)[0]||'')+': '+x.msg).join('; '):m}catch{}
  const e=new Error(m);e.status=r.status;return e}
async function api(path,params={}){
  const qs=new URLSearchParams(Object.entries(params).filter(([k,v])=>v!==''&&v!=null)).toString();
  busy(1);try{const r=await fetch('/api/'+path+(qs?'?'+qs:''),{headers:authH()});if(!r.ok)throw await apiError(r);return await r.json()}finally{busy(-1)}
}
async function sendJSON(method,path,body){
  busy(1);try{const r=await fetch('/api/'+path,{method,headers:{'Content-Type':'application/json',...authH()},body:JSON.stringify(body)});
    if(!r.ok)throw await apiError(r);return await r.json()}finally{busy(-1)}
}
function showErr(e){$('#banner').innerHTML='<div class="err"><b>Something went wrong:</b> '+esc(e.message||e)+'</div>'}
function clearErr(){$('#banner').innerHTML=''}

// ---- posters: real TMDB image when poster_path is stored, generated placeholder otherwise / on load error ----
function ph(title){
  let h=0;for(const c of title)h=(h*31+c.charCodeAt(0))%360;
  const ini=(title.split(/\s+/).filter(w=>/^[A-Za-z0-9]/.test(w)).slice(0,2).map(w=>w[0]).join('')||'?').toUpperCase();
  const svg=`<svg xmlns='http://www.w3.org/2000/svg' width='120' height='180'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='hsl(${h},55%,38%)'/><stop offset='1' stop-color='hsl(${(h+40)%360},60%,14%)'/></linearGradient></defs><rect width='120' height='180' fill='url(#g)'/><text x='60' y='104' font-size='38' font-family='Arial' font-weight='bold' fill='white' fill-opacity='.85' text-anchor='middle'>${esc(ini)}</text></svg>`;
  return 'data:image/svg+xml;utf8,'+encodeURIComponent(svg);
}
const pimg=(m,c='pt')=>`<img class="${c}" loading="lazy" alt="${esc(m.title)}" src="${m.poster_path?PB+m.poster_path:ph(m.title)}" onerror="this.onerror=null;this.src=ph(this.alt)">`;
const chips=g=>(g||[]).slice(0,3).map(x=>`<span class="chip">${esc(x)}</span>`).join('');
const yr=m=>m.year?` (${m.year})`:'';
const SEEN={};const reg=items=>items.forEach(m=>SEEN[m.id]=m);

// ---- charts ----
const charts={};
function destroyCharts(){Object.values(charts).forEach(c=>c.destroy());for(const k in charts)delete charts[k]}
function draw(id,cfg){
  const el=document.getElementById(id);if(!el)return;
  if(typeof Chart==='undefined'){el.parentNode.innerHTML='<p class="muted">Chart library could not load (no internet for the CDN). Data remains available through /docs.</p>';return}
  cfg.options=Object.assign({responsive:true,maintainAspectRatio:false},cfg.options||{});
  charts[id]=new Chart(el,cfg);
}
const panel=(id,t,sub='')=>`<div class="panel"><h3>${t}</h3><p class="sub">${sub}</p><div class="cv"><canvas id="${id}"></canvas></div></div>`;
function mk(type,labels,data,label,o={}){
  const c=o.color||'#2563eb',vax=o.h?'x':'y',cax=o.h?'y':'x';
  const ds={label,data,backgroundColor:o.multi?labels.map((_,i)=>COLORS[i%COLORS.length]):c};
  if(type==='line'){Object.assign(ds,{borderColor:c,backgroundColor:c+'22',fill:true,tension:.3,pointRadius:0,spanGaps:true})}
  return {type,data:{labels,datasets:[ds]},options:{indexAxis:o.h?'y':'x',plugins:{legend:{display:false},
    tooltip:{callbacks:{label:x=>`${label}: ${o.fmt?o.fmt(x.parsed[vax]):fN(x.parsed[vax])}`}}},
    scales:{[vax]:{beginAtZero:true,title:{display:!!o.vt,text:o.vt},ticks:o.fmt?{callback:v=>o.fmt(v)}:{}},[cax]:{title:{display:!!o.ct,text:o.ct},ticks:{autoSkip:true,maxTicksLimit:o.h?undefined:14}}}}};
}
const dough=(labels,data)=>({type:'doughnut',data:{labels,datasets:[{data,backgroundColor:COLORS}]},options:{plugins:{legend:{position:'right',labels:{boxWidth:12}}}}});
const scat=(pts,xl,yl,color,xf,yf)=>({type:'scatter',data:{datasets:[{label:'Movies',data:pts,backgroundColor:color+'99'}]},options:{plugins:{legend:{display:false},
  tooltip:{callbacks:{label:c=>`${c.raw.t}: ${xl} ${xf?xf(c.raw.x):c.raw.x}, ${yl} ${yf?yf(c.raw.y):c.raw.y}`}}},
  scales:{x:{title:{display:true,text:xl}},y:{title:{display:true,text:yl}}}}});

// ---- global state ----
let META={year_min:1900,year_max:2020,last_updated:null};
let P={from:'',to:''};                              // period filter shared by analytics pages
const pp=()=>({start:P.from,end:P.to});
const periodLabel=()=>(P.from||P.to)?`${P.from||META.year_min}–${P.to||META.year_max}`:'all years';
const head=(t,sub,right='')=>`<div class="ph"><div><h1>${t}</h1><p>${sub}</p></div><div class="pf">${right}</div></div>`;
function periodCtl(){
  const ys=[];for(let y=META.year_min;y<=META.year_max;y++)ys.push(y);
  const o=s=>'<option value="">Any</option>'+ys.map(y=>`<option ${String(y)===String(s)?'selected':''}>${y}</option>`).join('');
  return `<label>From<select id="pfrom">${o(P.from)}</select></label><label>To<select id="pto">${o(P.to)}</select></label><button class="btn" id="papply">Apply period</button>`;
}
function bindPeriod(){const b=$('#papply');if(!b)return;b.onclick=()=>{P.from=$('#pfrom').value;P.to=$('#pto').value;
  if(P.from&&P.to&&+P.from>+P.to){showErr(new Error('"From" year cannot be after "To" year'));return}route()}}
const kpi=(ic,bg,v,l,sub='')=>`<div class="kpi"><div class="ico" style="background:${bg}">${ic}</div><div><b>${v}</b><small>${l}</small>${sub?`<br><small>${sub}</small>`:''}</div></div>`;
const updated=()=>`Last updated: ${fD(META.last_updated)} (latest change in the database)`;

// ---- navigation ----
const NAV=[['overview','Overview','◧'],['explorer','Movie Explorer','🎞'],['industry','Industry Analytics','📈'],['financial','Financial Insights','💰'],
 ['genres','Genre Intelligence','🎭'],['ratings','Ratings & Popularity','⭐'],['production','Production Insights','🏢'],['engagement','User Engagement','👥'],['data','Data Management','🛠']];
$('#nav').innerHTML=NAV.map(([id,l,i])=>`<a href="#${id}" data-id="${id}"><span>${i}</span>${l}</a>`).join('');
$('#burger').onclick=()=>$('#side').classList.toggle('open');
$('#gs').onsubmit=e=>{e.preventDefault();E={...E0,q:$('#gq').value.trim()};location.hash==='#explorer'?route():location.hash='explorer'};
const VIEWS={overview:viewOverview,explorer:viewExplorer,compare:viewCompare,industry:viewIndustry,financial:viewFinancial,genres:viewGenres,
  ratings:viewRatings,production:viewProduction,engagement:viewEngagement,data:viewData};
async function route(){
  const id=location.hash.slice(1)||'overview';const v=VIEWS[id]||viewOverview;
  document.querySelectorAll('#nav a').forEach(a=>a.classList.toggle('on',a.dataset.id===id));
  $('#side').classList.remove('open');destroyCharts();clearErr();window.scrollTo(0,0);
  $('#view').innerHTML='<div class="skel"></div><div class="skel"></div>';renderTray();
  try{await v()}catch(e){$('#view').innerHTML='';showErr(e)}
}
window.addEventListener('hashchange',route);

// ---- shared list pieces ----
function pager(r,st,load){
  const a=r.total?st.offset+1:0,b=Math.min(st.offset+st.limit,r.total);
  $('#pg').innerHTML=`<span>${a}–${b} of ${fN(r.total)}</span><button class="btn o" id="pv" ${st.offset<=0?'disabled':''}>Prev</button><button class="btn o" id="nx" ${b>=r.total?'disabled':''}>Next</button>`;
  $('#pv').onclick=()=>{st.offset=Math.max(0,st.offset-st.limit);load().catch(showErr)};
  $('#nx').onclick=()=>{st.offset+=st.limit;load().catch(showErr)};
}
function mtable(items,offset=0){
  reg(items);
  return items.length?`<div class="tw"><table><tr><th>#</th><th>Poster</th><th>Title</th><th>Genre</th><th>Rating</th><th>Votes</th><th>Popularity</th></tr>${items.map((m,i)=>
   `<tr><td>${offset+i+1}</td><td>${pimg(m)}</td><td><a class="lnk" onclick="details(${m.id})">${esc(m.title)}${yr(m)}</a>${isEditor()?` <a class="lnk" style="color:#2563eb;font-size:12px" onclick="editMovie(${m.id})">✎ Edit</a>`:''}</td><td>${chips(m.genres)}</td><td>${fR(m.rating)}</td><td>${fN(m.votes)}</td><td>${fR(m.popularity)}</td></tr>`).join('')}</table></div>`:'<div class="empty">No movies match.</div>';
}

// ---- 1. Overview ----
async function viewOverview(){
  const [s,g,y,r,f,tr]=await Promise.all([api('analytics/summary',pp()),api('analytics/genres',pp()),api('analytics/years',pp()),
    api('analytics/ratings',pp()),api('analytics/financials',pp()),api('movies/top-rated',{limit:6,year_from:P.from,year_to:P.to})]);
  Object.assign(META,{year_min:s.year_min,year_max:s.year_max,last_updated:s.last_updated});reg(tr.items);
  $('#view').innerHTML=`<div class="hero"><h1>Movie Intelligence Overview</h1><p>Live analytics from ${fN(s.catalogue_total)} movies in the shared database · ${esc(s.dataset)}</p>
   <span class="chip2">${updated()}</span><div class="pf" style="margin-top:14px">${periodCtl()}</div></div>
  <div class="content"><div class="kpis">
   ${kpi('🎞️','#fee2e2',fN(s.catalogue_total),'Total movies','whole catalogue')}${kpi('⭐','#fef3c7',fR(s.average_rating),'Average rating',`${fN(s.rated_movies)} rated · ${periodLabel()}`)}
   ${kpi('🎭','#dcfce7',fN(s.total_genres),'Genres',periodLabel())}${kpi('$','#dbeafe',fM(s.total_revenue),'Recorded revenue',`USD · ${fN(s.movies_with_revenue)} movies with revenue`)}
   ${kpi('🔥','#ede9fe',fR(s.average_popularity),'Average popularity',periodLabel())}${kpi('📅','#fce7f3',fN(s.total_movies),'Released in period',periodLabel())}</div>
  <div class="grid2">${panel('c1','Movies released per year','How has production volume changed?')}${panel('c2','Genre distribution','Which genres dominate? (multi-genre movies count in each genre)')}
   ${panel('c3','Rating distribution','Where do most TMDB ratings fall?')}${panel('c4','Revenue trend','Total recorded revenue by release year')}
   ${panel('c5','Budget vs revenue','Do bigger budgets earn more? (top 300 by revenue)')}${panel('c6','Popularity vs rating','Are highly rated movies also popular? (50+ votes)')}
   ${panel('c7','Highest-revenue movies','Top 10 by recorded revenue')}
   <div class="panel"><h3>Highest-rated movies</h3><p class="sub">Rating-ranked, only movies with at least 500 votes</p>${tr.items.map(m=>`<div class="li">${pimg(m,'pt sm')}<div><a class="lnk" onclick="details(${m.id})">${esc(m.title)}${yr(m)}</a><small>★ ${fR(m.rating)} · ${fN(m.votes)} votes</small></div></div>`).join('')||'<div class="empty">No movies with enough votes in this period.</div>'}</div></div></div>`;
  bindPeriod();
  draw('c1',mk('bar',y.years.map(x=>x.year),y.years.map(x=>x.count),'Movies',{vt:'Number of movies',ct:'Release year'}));
  const top=g.genres.slice(0,9),oth=g.genres.slice(9).reduce((a,x)=>a+x.count,0);draw('c2',dough([...top.map(x=>x.genre),'Others'],[...top.map(x=>x.count),oth]));
  draw('c3',mk('bar',r.bins.map(b=>b.range),r.bins.map(b=>b.count),'Movies',{vt:'Number of movies',ct:'TMDB rating',color:'#7c3aed'}));
  const yy=y.years.filter(x=>x.total_revenue!=null);draw('c4',mk('line',yy.map(x=>x.year),yy.map(x=>x.total_revenue/1e9),'Revenue',{fmt:fB,vt:'Revenue (USD billions)',ct:'Release year',color:'#10b981'}));
  draw('c5',scat(f.scatter.map(p=>({x:p.budget/1e6,y:p.revenue/1e6,t:p.title})),'Budget ($M)','Revenue ($M)','#7c3aed',fMm,fMm));
  draw('c6',scat(r.scatter.map(p=>({x:p.rating,y:p.popularity,t:p.title})),'Rating','Popularity','#2563eb'));
  draw('c7',mk('bar',f.top_revenue.map(m=>m.title),f.top_revenue.map(m=>m.revenue/1e6),'Revenue',{h:1,multi:1,fmt:fMm,vt:'Revenue (USD millions)'}));
}

// ---- 2. Movie Explorer + comparison ----
const E0={q:'',genre:'',language:'',from:'',to:'',minr:'',minv:'',sort:'popularity',order:'desc',offset:0};let E={...E0};
let CMP=JSON.parse(sessionStorage.getItem('cmp')||'[]');
const inCmp=id=>CMP.some(c=>c.id===id);
function toggleCmp(id){
  if(inCmp(id))CMP=CMP.filter(c=>c.id!==id);
  else{if(CMP.length>=4){showErr(new Error('You can compare up to 4 movies.'));return}CMP.push({id,title:(SEEN[id]||{}).title||('Movie '+id)})}
  sessionStorage.setItem('cmp',JSON.stringify(CMP));renderTray();
  document.querySelectorAll(`[data-cmp="${id}"]`).forEach(b=>{b.textContent=inCmp(id)?'✓ Compare':'＋ Compare';b.classList.toggle('on',inCmp(id))});
}
function renderTray(){
  const t=$('#tray');t.classList.toggle('on',CMP.length>0&&location.hash!=='#compare');
  t.innerHTML=`<b>Compare:</b>${CMP.map(c=>`<span class="tc">${esc(c.title)} <a style="cursor:pointer" onclick="toggleCmp(${c.id})">✕</a></span>`).join('')}
   <button class="btn" ${CMP.length<2?'disabled':''} onclick="location.hash='compare'">Compare ${CMP.length} movies</button><button class="btn o" onclick="CMP=[];sessionStorage.removeItem('cmp');renderTray();document.querySelectorAll('[data-cmp]').forEach(b=>{b.textContent='＋ Compare';b.classList.remove('on')})">Clear</button>`;
}
const card=m=>`<div class="mc"><div class="pw">${pimg(m,'pc')}<span class="rt">★ ${fR(m.rating)}</span></div><div class="mi"><h4 title="${esc(m.title)}">${esc(m.title)}</h4>
 <small>${m.year??'—'} · ${esc((m.genres||[]).slice(0,2).join(', ')||'No genre')}</small><small>Popularity ${fR(m.popularity)}</small>
 <div class="ba"><button class="btn o" onclick="details(${m.id})">Details</button><button class="btn o ${inCmp(m.id)?'on':''}" data-cmp="${m.id}" onclick="toggleCmp(${m.id})">${inCmp(m.id)?'✓ Compare':'＋ Compare'}</button>${isEditor()?`<button class="btn o" onclick="editMovie(${m.id})">✎ Edit</button>`:''}</div></div></div>`;
async function viewExplorer(){
  const [g,l]=await Promise.all([api('analytics/genres'),api('analytics/languages')]);
  const opts=(a,sel,fn=x=>x)=>a.map(x=>`<option value="${esc(x)}" ${x===sel?'selected':''}>${esc(fn(x))}</option>`).join('');
  const ys=[];for(let y=META.year_max;y>=META.year_min;y--)ys.push(String(y));
  $('#view').innerHTML=`<div class="content">${head('Movie Explorer','Search the shared catalogue, open details, and pick movies to compare.')}
  <div class="flt"><label>Title<input id="e_q" value="${esc(E.q)}" placeholder="e.g. batman"></label>
   <label>Genre<select id="e_genre"><option value="">All genres</option>${opts(g.genres.map(x=>x.genre).sort(),E.genre)}</select></label>
   <label>Language<select id="e_language"><option value="">All (top 15)</option>${opts(l.languages.map(x=>x.original_language),E.language,langName)}</select></label>
   <label>Year from<select id="e_from"><option value="">Any</option>${opts(ys.slice().reverse(),E.from)}</select></label><label>Year to<select id="e_to"><option value="">Any</option>${opts(ys,E.to)}</select></label>
   <label>Min rating<select id="e_minr"><option value="">Any</option>${opts(['5','6','7','8'],E.minr,x=>x+'+')}</select></label>
   <label>Min votes<input id="e_minv" type="number" min="0" value="${esc(E.minv)}" placeholder="0"></label>
   <label>Sort by<select id="e_sort">${['popularity','rating','revenue','year','votes'].map(s=>`<option value="${s}" ${E.sort===s?'selected':''}>${s[0].toUpperCase()+s.slice(1)}</option>`).join('')}</select></label>
   <label>Order<select id="e_order"><option value="desc" ${E.order==='desc'?'selected':''}>High → low</option><option value="asc" ${E.order==='asc'?'selected':''}>Low → high</option></select></label>
   <button class="btn" id="e_go">Search</button></div><div id="res"></div><div class="pager" id="pg"></div></div>`;
  const st={limit:20};
  async function load(){
    for(const k of ['q','genre','language','from','to','minr','minv','sort','order'])E[k]=$('#e_'+k).value.trim();
    st.offset=E.offset;
    const r=await api('movies/search',{q:E.q,genre:E.genre,language:E.language,year_from:E.from,year_to:E.to,min_rating:E.minr,min_votes:E.minv,sort:E.sort,order:E.order,offset:E.offset,limit:st.limit});
    reg(r.items);$('#res').innerHTML=r.items.length?`<div class="cards">${r.items.map(card).join('')}</div>`:'<div class="empty">No movies found. Try relaxing the filters.</div>';
    pager(r,{get offset(){return E.offset},set offset(v){E.offset=v},limit:st.limit},load);
  }
  const go=()=>{E.offset=0;load().catch(showErr)};
  $('#e_go').onclick=go;$('#e_q').onkeydown=e=>{if(e.key==='Enter')go()};
  await load();
}
async function viewCompare(){
  if(CMP.length<2){$('#view').innerHTML=`<div class="content">${head('Compare Movies','Pick 2-4 movies in the Movie Explorer first.')}<div class="empty">Nothing to compare yet. <a class="lnk" href="#explorer">Open Movie Explorer</a> and use "＋ Compare".</div></div>`;return}
  const r=await api('analytics/compare',{ids:CMP.map(c=>c.id).join(',')}),M=r.movies;
  const row=(label,key,fmt)=>{const vals=M.map(m=>m[key]),mx=Math.max(...vals.filter(v=>v!=null),0);
    return `<tr><td>${label}</td>${M.map(m=>`<td class="${m[key]!=null&&m[key]===mx&&mx>0&&M.length>1?'best':''}">${m[key]!=null?fmt(m[key]):'<span class="muted">unknown</span>'}${m[key]!=null&&mx>0?`<div class="bar"><i style="width:${Math.max(3,m[key]/mx*100)}%"></i></div>`:''}</td>`).join('')}</tr>`};
  $('#view').innerHTML=`<div class="content">${head('Movie Comparison','Side-by-side comparison. The best value in each row is highlighted.','<button class="btn o" onclick="location.hash=\'explorer\'">← Back to Explorer</button>')}
  <div class="tw"><table class="cmp"><tr><td></td>${M.map(m=>`<td style="width:${70/M.length}%">${pimg(m,'pc')}<h4 style="margin:8px 0 0">${esc(m.title)}${yr(m)}</h4><a class="lnk" style="font-size:12px" onclick="toggleCmp(${m.id});viewCompare()">remove</a></td>`).join('')}</tr>
   ${row('Rating','rating',fR)}${row('Votes','votes',fN)}${row('Popularity','popularity',fR)}${row('Budget','budget',fM)}${row('Revenue','revenue',fM)}${row('Runtime','runtime',v=>Math.round(v)+' min')}
   <tr><td>Release year</td>${M.map(m=>`<td>${m.year??'—'}</td>`).join('')}</tr><tr><td>Genres</td>${M.map(m=>`<td>${chips(m.genres)}</td>`).join('')}</tr></table></div>
  <div class="panel"><h3>Summary of differences</h3><ul class="hl">${r.highlights.map(h=>`<li>${esc(h)}</li>`).join('')}</ul></div></div>`;
}

// ---- 3. Industry ----
async function viewIndustry(){
  const [y,l]=await Promise.all([api('analytics/years',pp()),api('analytics/languages',pp())]);const Y=y.years,L=Y.map(x=>x.year);
  const dec={};Y.forEach(x=>{const d=Math.floor(x.year/10)*10;dec[d]=(dec[d]||0)+x.count});
  $('#view').innerHTML=`<div class="content">${head('Industry Analytics',`Release volume, quality and revenue over time · ${periodLabel()}`,periodCtl())}<div class="grid2">
   ${panel('a1','Movies released per year','Production volume')}${panel('a2','Releases by decade','Which decades produced the most titles?')}${panel('a3','Average rating per year','Has average audience rating changed?')}
   ${panel('a4','Total revenue per year','Recorded revenue (movies with known revenue only)')}${panel('a5','Original languages','Top languages by movie count')}</div></div>`;bindPeriod();
  draw('a1',mk('bar',L,Y.map(x=>x.count),'Movies',{vt:'Number of movies',ct:'Release year'}));
  draw('a2',mk('bar',Object.keys(dec).map(d=>d+'s'),Object.values(dec),'Movies',{multi:1,vt:'Number of movies'}));
  draw('a3',mk('line',L,Y.map(x=>x.avg_rating),'Average rating',{color:'#ef4444',vt:'Average rating (0-10)'}));
  draw('a4',mk('line',L,Y.map(x=>x.total_revenue==null?null:x.total_revenue/1e9),'Revenue',{fmt:fB,color:'#10b981',vt:'USD billions'}));
  const t=l.languages.slice(0,10);draw('a5',mk('bar',t.map(x=>langName(x.original_language)),t.map(x=>x.count),'Movies',{multi:1,vt:'Number of movies'}));
}

// ---- 4. Financial ----
async function viewFinancial(){
  const [f,g,y]=await Promise.all([api('analytics/financials',pp()),api('analytics/genres',pp()),api('analytics/years',pp())]);
  const st=(l,o)=>kpi('💵','#e0e7ff',fM(o.median),l,`${fN(o.count)} movies · max ${fM(o.max)}`);
  $('#view').innerHTML=`<div class="content">${head('Financial Insights',`Budget, revenue, profit and ROI · ${periodLabel()}`,periodCtl())}
  <div class="note info"><b>Simplified estimates, not audited results.</b> Estimated profit = ${esc(f.formulas.estimated_profit)}. Estimated ROI % = ${esc(f.formulas.estimated_roi_percent)}. ${esc(f.formulas.note)} Missing budget/revenue (0 in TMDB) is treated as <i>unknown</i>, never as zero. Values: ${esc(f.currency)}.</div>
  <div class="kpis">${st('Median budget',f.budget)}${st('Median revenue',f.revenue)}${kpi('🔗','#dcfce7',fN(f.movies_with_both),'Movies with both','used for profit / ROI')}</div>
  <div class="grid2">${panel('f1','Budget vs revenue','Top 300 movies by revenue')}${panel('f2','Revenue by year','Recorded revenue, USD billions')}${panel('f3','Revenue by genre','Multi-genre movies count in each genre')}
   ${panel('f4','Highest-grossing movies','Top 10 by revenue')}${panel('f5','Highest-budget movies','Top 10 by budget')}${panel('f6','Highest estimated profit','revenue − budget')}
   ${panel('f7','Highest estimated ROI','Budgets ≥ $1M only, to avoid distorted ratios')}${panel('f8','Budget distribution','How many movies per budget band?')}${panel('f9','Revenue distribution','How many movies per revenue band?')}</div></div>`;bindPeriod();
  draw('f1',scat(f.scatter.map(p=>({x:p.budget/1e6,y:p.revenue/1e6,t:p.title})),'Budget ($M)','Revenue ($M)','#7c3aed',fMm,fMm));
  const yy=y.years.filter(x=>x.total_revenue!=null);draw('f2',mk('line',yy.map(x=>x.year),yy.map(x=>x.total_revenue/1e9),'Revenue',{fmt:fB,color:'#10b981',vt:'USD billions'}));
  const gg=g.genres.filter(x=>x.total_revenue!=null).sort((a,b)=>b.total_revenue-a.total_revenue).slice(0,10);draw('f3',mk('bar',gg.map(x=>x.genre),gg.map(x=>x.total_revenue/1e9),'Revenue',{multi:1,fmt:fB,vt:'USD billions'}));
  const hb=(id,list,key,lab,fmt,div=1)=>draw(id,mk('bar',list.map(m=>m.title),list.map(m=>m[key]/div),lab,{h:1,multi:1,fmt}));
  hb('f4',f.top_revenue,'revenue','Revenue',fMm,1e6);hb('f5',f.top_budget,'budget','Budget',fMm,1e6);hb('f6',f.top_profit,'profit','Profit',fMm,1e6);hb('f7',f.top_roi,'roi','ROI',fP);
  draw('f8',mk('bar',f.budget_distribution.map(b=>b.range),f.budget_distribution.map(b=>b.count),'Movies',{vt:'Number of movies',ct:'Budget band',color:'#2563eb'}));
  draw('f9',mk('bar',f.revenue_distribution.map(b=>b.range),f.revenue_distribution.map(b=>b.count),'Movies',{vt:'Number of movies',ct:'Revenue band',color:'#10b981'}));
}

// ---- 5. Genres ----
async function viewGenres(){
  const g=await api('analytics/genres',pp()),G=g.genres;
  $('#view').innerHTML=`<div class="content">${head('Genre Intelligence',`Compare genres by volume, quality, revenue and popularity · ${periodLabel()}`,periodCtl())}
  <div class="note info"><b>How counting works:</b> ${esc(g.note)} Averages are taken over the movies in each genre.</div>
  <div class="grid2">${panel('g1','Movies per genre','Which genres have the most titles?')}${panel('g2','Average rating by genre','Genres with at least 20 movies')}${panel('g3','Revenue by genre','Total recorded revenue')}${panel('g4','Average popularity by genre','Which genres attract attention?')}</div>
  <div class="tw"><table><tr><th>Genre</th><th>Movies</th><th>Avg rating</th><th>Total revenue</th><th>Avg popularity</th></tr>${G.map(r=>`<tr><td>${esc(r.genre)}</td><td>${fN(r.count)}</td><td>${fR(r.avg_rating)}</td><td>${fM(r.total_revenue)}</td><td>${fR(r.avg_popularity)}</td></tr>`).join('')}</table></div></div>`;bindPeriod();
  const c=G.slice(0,12);draw('g1',mk('bar',c.map(x=>x.genre),c.map(x=>x.count),'Movies',{h:1,multi:1}));
  const r=G.filter(x=>x.count>=20&&x.avg_rating!=null).sort((a,b)=>b.avg_rating-a.avg_rating).slice(0,12);draw('g2',mk('bar',r.map(x=>x.genre),r.map(x=>x.avg_rating),'Avg rating',{h:1,multi:1,vt:'Average rating'}));
  const v=G.filter(x=>x.total_revenue!=null).sort((a,b)=>b.total_revenue-a.total_revenue).slice(0,10);draw('g3',mk('bar',v.map(x=>x.genre),v.map(x=>x.total_revenue/1e9),'Revenue',{h:1,multi:1,fmt:fB}));
  const p=G.filter(x=>x.avg_popularity!=null).sort((a,b)=>b.avg_popularity-a.avg_popularity).slice(0,10);draw('g4',mk('bar',p.map(x=>x.genre),p.map(x=>x.avg_popularity),'Avg popularity',{h:1,multi:1}));
}

// ---- 6. Ratings & popularity ----
let MINV=500;
async function viewRatings(){
  const [r,tr,pop]=await Promise.all([api('analytics/ratings',pp()),api('movies/top-rated',{min_votes:MINV,year_from:P.from,year_to:P.to,limit:10}),
    api('movies',{sort:'popularity',year_from:P.from,year_to:P.to,limit:10})]);
  $('#view').innerHTML=`<div class="content">${head('Ratings and Popularity',`Audience scores and attention · ${periodLabel()}`,periodCtl()+`<label>Minimum votes<input id="mv" type="number" min="0" value="${MINV}" style="width:100px"></label>`)}
  <div class="note info"><b>Ranking rules:</b> Top rated = highest TMDB average rating (ties broken by vote count), only for movies with at least <b>${fN(MINV)}</b> votes, so a 10.0 from three voters cannot dominate. Popularity = TMDB's popularity score. Rating charts exclude unrated movies (0 votes).</div>
  <div class="kpis">${kpi('⭐','#fef3c7',fR(r.mean),'Mean rating')}${kpi('📊','#e0e7ff',fR(r.median),'Median rating')}${kpi('🗳️','#dcfce7',fN(r.rated_movies),'Rated movies')}</div>
  <div class="grid2">${panel('r1','Rating distribution','How are ratings spread?')}${panel('r2','Rating vs popularity','Movies with 50+ votes')}${panel('r3','Most-voted movies','Vote-count comparison')}</div>
  <h3>Top rated (min ${fN(MINV)} votes)</h3>${mtable(tr.items)}<h3>Most popular</h3>${mtable(pop.items)}</div>`;bindPeriod();
  $('#mv').onchange=()=>{MINV=Math.max(0,+$('#mv').value||0);route()};
  draw('r1',mk('bar',r.bins.map(b=>b.range),r.bins.map(b=>b.count),'Movies',{color:'#7c3aed',vt:'Number of movies',ct:'Rating'}));
  draw('r2',scat(r.scatter.map(p=>({x:p.rating,y:p.popularity,t:p.title})),'Rating','Popularity','#2563eb'));
  draw('r3',mk('bar',r.most_voted.map(m=>m.title),r.most_voted.map(m=>m.votes),'Votes',{h:1,multi:1}));
}

// ---- 7. Production ----
async function viewProduction(){
  const [p,l]=await Promise.all([api('analytics/production',pp()),api('analytics/languages',pp())]);
  $('#view').innerHTML=`<div class="content">${head('Production Insights',`Who makes the movies, and where? · ${periodLabel()}`,periodCtl())}
  <div class="grid2">${panel('p1','Production companies','Most movies produced')}${panel('p2','Production countries','Movies per country')}${panel('p3','Original language share','Top 10 languages')}${panel('p4','Directors with most movies','From crew data')}</div>
  <div class="tw"><table><tr><th>Director</th><th>Movies</th><th>Avg rating</th><th>Total revenue</th></tr>${p.directors.map(d=>`<tr><td>${esc(d.director)}</td><td>${d.count}</td><td>${fR(d.avg_rating)}</td><td>${fM(d.total_revenue)}</td></tr>`).join('')}</table></div></div>`;bindPeriod();
  draw('p1',mk('bar',p.companies.map(x=>x.company),p.companies.map(x=>x.count),'Movies',{h:1,multi:1}));
  draw('p2',mk('bar',p.countries.map(x=>x.country),p.countries.map(x=>x.count),'Movies',{h:1,multi:1}));
  const t=l.languages.slice(0,10);draw('p3',dough(t.map(x=>langName(x.original_language)),t.map(x=>x.count)));
  draw('p4',mk('bar',p.directors.map(x=>x.director),p.directors.map(x=>x.count),'Movies',{h:1,multi:1}));
}

// ---- 8. User engagement (from the shared interactions table) ----
async function viewEngagement(){
  const s=await api('interactions/summary');
  if(!s.total_interactions){$('#view').innerHTML=`<div class="content">${head('User Engagement','Ratings, likes, watchlists and recommendation activity')}<div class="empty"><b>No interactions recorded yet.</b><br>Log in as a user, open a movie and rate it or add it to a watchlist, or let the recommendation app post to <code>POST /api/interactions</code>.</div></div>`;return}
  const rec=s.recommendations;
  $('#view').innerHTML=`<div class="content">${head('User Engagement',`Computed from ${fN(s.total_interactions)} recorded interactions · last: ${fD(s.last_interaction)}`)}
  <div class="kpis">${kpi('🧾','#e0e7ff',fN(s.total_interactions),'Interactions')}${kpi('👤','#dcfce7',fN(s.unique_users),'Active users')}${kpi('⭐','#fef3c7',fR(s.ratings.average),'Avg personal rating',`${fN(s.ratings.count)} ratings`)}
   ${kpi('📌','#fce7f3',fN(s.watchlist.active),'On watchlists',`${fN(s.watchlist.removed)} removed`)}${kpi('🖱️','#dbeafe',rec.click_through_rate==null?'—':(rec.click_through_rate*100).toFixed(1)+'%','Recommendation CTR',`${fN(rec.clicks)} clicks / ${fN(rec.impressions)} shown`)}
   ${kpi('👍','#ede9fe',rec.relevance_rate==null?'—':(rec.relevance_rate*100).toFixed(0)+'%','Feedback "relevant"',`${fN(rec.feedback)} responses`)}</div>
  <div class="grid2">${panel('u1','Interactions by type','What are users doing?')}${panel('u2','Personal rating distribution','Users’ own 1-10 ratings (separate from TMDB ratings)')}${panel('u3','Daily activity','Interactions per day (last 30 active days)')}
   ${panel('u4','Genres users engage with','Likes, watchlist adds, clicks, ratings ≥ 7')}${panel('u5','Most watchlisted','Movies currently on watchlists')}${panel('u6','Most liked','Movies with most likes')}</div>
  <h3>Most-rated movies: users vs TMDB</h3><div class="tw"><table><tr><th>Movie</th><th>User ratings</th><th>Avg personal rating</th><th>TMDB rating</th></tr>${s.ratings.most_rated.map(m=>`<tr><td><a class="lnk" onclick="details(${m.movie_id})">${esc(m.title)}</a></td><td>${m.count}</td><td>${fR(m.avg_personal_rating)}</td><td>${fR(m.tmdb_rating)}</td></tr>`).join('')||'<tr><td colspan=4 class="muted">No personal ratings yet</td></tr>'}</table></div></div>`;
  draw('u1',mk('bar',s.by_type.map(x=>x.type.replace(/_/g,' ')),s.by_type.map(x=>x.count),'Interactions',{multi:1,vt:'Count'}));
  draw('u2',mk('bar',s.ratings.distribution.map(x=>x.score),s.ratings.distribution.map(x=>x.count),'Ratings',{color:'#7c3aed',vt:'Number of ratings',ct:'Personal rating'}));
  draw('u3',mk('line',s.daily_activity.map(x=>x.date),s.daily_activity.map(x=>x.count),'Interactions',{color:'#2563eb',vt:'Interactions'}));
  draw('u4',mk('bar',s.genre_engagement.map(x=>x.genre),s.genre_engagement.map(x=>x.count),'Engagements',{h:1,multi:1}));
  draw('u5',mk('bar',s.watchlist.top_movies.map(x=>x.title),s.watchlist.top_movies.map(x=>x.count),'Watchlists',{h:1,multi:1}));
  draw('u6',mk('bar',s.likes.top_liked.map(x=>x.title),s.likes.top_liked.map(x=>x.count),'Likes',{h:1,multi:1}));
}

// ---- 9. Data management (editors) ----
async function viewData(){
  if(!isEditor()){$('#view').innerHTML=`<div class="content">${head('Data Management','Catalogue health, recent edits and exports')}<div class="empty">Editor login required.<br><br><button class="btn" onclick="loginForm()">Editor login</button></div></div>`;return}
  const q=await api('data/quality');
  const cov=(l,n,ic)=>kpi(ic,'#e0e7ff',fN(n),l,`${(n/q.total*100).toFixed(1)}% of ${fN(q.total)}`);
  $('#view').innerHTML=`<div class="content">${head('Data Management','The shared PostgreSQL catalogue is the source of truth. Edits here are visible to every connected application.')}
  <div class="kpis">${cov('With poster',q.with_poster,'🖼️')}${cov('Missing budget',q.missing_budget,'💸')}${cov('Missing revenue',q.missing_revenue,'💰')}${cov('Unrated (0 votes)',q.unrated,'⭐')}${cov('Missing runtime',q.missing_runtime,'⏱️')}${cov('Edited by editors',q.edited_by_editors,'✎')}</div>
  <div class="note info">Missing budget/revenue means <i>unknown</i>, not zero. Posters are filled by <code>python manage.py enrich-posters</code> (official TMDB API, run once; results are cached in the database).</div>
  <div class="panel" style="margin-bottom:16px"><h3>Export current database</h3><p class="sub">Generated fresh from PostgreSQL, including all edits.</p><button class="btn" onclick="exportCsv('movies')">Download movies.csv</button> <button class="btn o" onclick="exportCsv('credits')">Download credits.csv</button> <a class="btn o" style="text-decoration:none;display:inline-block" href="/docs" target="_blank">Open API docs</a></div>
  <h3>Recent catalogue edits</h3><div class="tw"><table><tr><th>Movie</th><th>Edited by</th><th>When</th><th></th></tr>${q.recent_edits.map(e=>`<tr><td><a class="lnk" onclick="details(${e.id})">${esc(e.title)}</a></td><td>${esc(e.last_edited_by)}</td><td>${fD(e.updated_at)}</td><td><a class="lnk" onclick="editMovie(${e.id})">✎ Edit</a></td></tr>`).join('')||'<tr><td colspan=4 class="muted">No edits yet. Open a movie in the Explorer and press Edit.</td></tr>'}</table></div></div>`;
}

// ---- movie details (+ user activity) ----
function closeModal(){$('#modal').classList.remove('on')}
$('#modal').onclick=e=>{if(e.target.id==='modal')closeModal()};
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()});
async function details(id,note=''){
  $('#mbody').innerHTML='<div class="empty">Loading…</div>';$('#modal').classList.add('on');
  try{
    const m=await api('movies/'+id);SEEN[id]=m;
    const rows=[['Release date',m.release_date],['Runtime',m.runtime?Math.round(m.runtime)+' min':null],['Language',m.language?langName(m.language):null],['Budget',m.budget?fM(m.budget):null],['Revenue',m.revenue?fM(m.revenue):null],
      ['Est. profit (revenue − budget)',m.estimated_profit!=null?fM(m.estimated_profit):null],['Director',m.director],['Cast',(m.cast||[]).join(', ')],['Production companies',(m.production_companies||[]).join(', ')],['Countries',(m.production_countries||[]).join(', ')],
      ['Last saved',m.updated_at?fD(m.updated_at)+(m.last_edited_by?' by '+m.last_edited_by:''):null]].filter(r=>r[1]);
    $('#mbody').innerHTML=`<div id="dnote">${note?`<div class="note ok">${esc(note)}</div>`:''}</div><div class="head">${pimg(m,'pc')}<div style="flex:1"><h2 style="margin:0">${esc(m.title)}${yr(m)}</h2>${m.tagline?`<i class="muted">${esc(m.tagline)}</i>`:''}
      <div style="margin:8px 0">${(m.genres||[]).map(x=>`<span class="chip">${esc(x)}</span>`).join('')}</div><div>★ <b>${fR(m.rating)}</b> TMDB · ${fN(m.votes)} votes · Popularity ${fR(m.popularity)}</div>
      <div class="ba" style="margin-top:10px"><button class="btn o ${inCmp(m.id)?'on':''}" data-cmp="${m.id}" onclick="toggleCmp(${m.id})">${inCmp(m.id)?'✓ Compare':'＋ Compare'}</button>${isEditor()?`<button class="btn" onclick="editMovie(${m.id})">✎ Edit this movie</button>`:''}</div></div></div>
      ${TOKEN?`<div class="act"><b>Your activity:</b> <input id="myr" class="sel" type="number" min="1" max="10" step="0.5" placeholder="1-10"><button class="btn o" onclick="act(${m.id},'rating')">Rate</button><button class="btn o" onclick="act(${m.id},'like')">👍 Like</button><button class="btn o" onclick="act(${m.id},'dislike')">👎 Dislike</button><button class="btn o" onclick="act(${m.id},'watchlist_add')">＋ Watchlist</button><button class="btn o" onclick="act(${m.id},'watchlist_remove')">− Watchlist</button></div>`:'<p class="muted" style="font-size:12px">Log in to rate, like or add to your watchlist.</p>'}
      ${m.overview?`<p>${esc(m.overview)}</p>`:''}<table class="facts">${rows.map(r=>`<tr><td>${r[0]}</td><td>${esc(r[1])}</td></tr>`).join('')}</table>`;
  }catch(e){$('#mbody').innerHTML='<div class="err">Could not load details: '+esc(e.message)+'</div>'}
}
async function act(id,type){
  const body={movie_id:id,interaction_type:type};
  if(type==='rating'){const v=parseFloat($('#myr').value);if(!(v>=1&&v<=10)){$('#dnote').innerHTML='<div class="note bad">Enter a rating between 1 and 10.</div>';return}body.rating=v}
  try{await sendJSON('POST','interactions',body);$('#dnote').innerHTML='<div class="note ok">Saved to the shared database ('+type.replace('_',' ')+').</div>'}
  catch(e){if(e.status===401){logout();loginForm('Session expired. Please sign in again.')}else $('#dnote').innerHTML='<div class="note bad">'+esc(e.message)+'</div>'}
}

// ---- login / register / export / edit ----
function renderAuth(){
  $('#auth').innerHTML=(TOKEN?`<small>${esc(USER)} · ${esc(ROLE)}</small>${isEditor()?'<button class="btn o" onclick="exportCsv(\'movies\')">Export CSV</button>':''}<button class="btn o" onclick="logout()">Logout</button>`:'<button class="btn o" onclick="loginForm()">Log in / Register</button>')
   +'<button class="btn o" onclick="route()" title="Re-fetch everything from the shared database">⟳ Refresh</button>';
}
function logout(){TOKEN=USER=ROLE=null;sessionStorage.clear();renderAuth();route()}
function loginForm(msg=''){
  $('#mbody').innerHTML=`<h3 style="margin-top:0">Log in</h3>${msg?`<div class="note bad">${esc(msg)}</div>`:''}<div class="fm"><label>Username<input id="lu" autocomplete="username"></label><label>Password<input id="lp" type="password" autocomplete="current-password"></label>
   <button class="btn" id="lgo">Sign in</button> <button class="btn o" id="lreg">Create user account</button><p class="muted" style="font-size:12px">Editors can edit the catalogue. Normal users can rate, like and keep a watchlist.</p></div>`;
  $('#modal').classList.add('on');$('#lu').focus();
  const fin=r=>{TOKEN=r.token;USER=r.username;ROLE=r.role;sessionStorage.setItem('tok',TOKEN);sessionStorage.setItem('usr',USER);sessionStorage.setItem('role',ROLE);renderAuth();closeModal();route()};
  const cred=()=>({username:$('#lu').value.trim(),password:$('#lp').value});
  const go=async()=>{try{fin(await sendJSON('POST','auth/login',cred()))}catch(e){loginForm(e.message)}};
  $('#lgo').onclick=go;$('#lp').onkeydown=e=>{if(e.key==='Enter')go()};
  $('#lreg').onclick=async()=>{try{await sendJSON('POST','users/register',cred());await go()}catch(e){loginForm(e.message)}};
}
async function exportCsv(kind){
  try{busy(1);const r=await fetch(`/api/export/${kind}.csv`,{headers:authH()});if(!r.ok)throw await apiError(r);
    const a=document.createElement('a');a.href=URL.createObjectURL(await r.blob());a.download=kind+'_export.csv';a.click();URL.revokeObjectURL(a.href)}
  catch(e){showErr(e)}finally{busy(-1)}
}
async function editMovie(id){
  if(!isEditor()){loginForm('Editor login required to edit movies.');return}
  $('#mbody').innerHTML='<div class="empty">Loading…</div>';$('#modal').classList.add('on');
  let m;try{m=await api('movies/'+id)}catch(e){$('#mbody').innerHTML='<div class="err">'+esc(e.message)+'</div>';return}
  const F=[['title','Title','text',m.title,1],['overview','Overview','area',m.overview],['genres','Genres (comma separated)','text',m.genres||[],1],
    ['release_date','Release date','date',m.release_date],['vote_average','Rating (0–10)','number',m.rating],['popularity','Popularity','number',m.popularity,1],
    ['budget','Budget (USD)','number',m.budget],['revenue','Revenue (USD)','number',m.revenue],['runtime','Runtime (min)','number',m.runtime],['original_language','Language code (e.g. en)','text',m.language,1]];
  const inp=([k,l,t,v])=>t==='area'?`<label>${l}<textarea id="f_${k}" rows="4">${esc(v)}</textarea></label>`
    :`<label>${l}<input id="f_${k}" type="${t}" ${t==='number'?'step="any"':''} value="${esc(Array.isArray(v)?v.join(', '):v)}"></label>`;
  $('#mbody').innerHTML=`<h3 style="margin-top:0">Edit: ${esc(m.title)}${yr(m)} <small class="muted">(TMDB id ${m.id})</small></h3><div id="em"></div>
   <div class="fm">${inp(F[0])}${inp(F[1])}${inp(F[2])}<div class="two">${F.slice(3).map(inp).join('')}</div>
   <p class="muted" style="font-size:12px">Empty optional fields are stored as unknown. Id, vote count, director, cast and poster are read-only. Saved straight to the shared database.</p>
   <button class="btn" id="sv">Save</button> <button class="btn o" onclick="details(${m.id})">Cancel</button></div>`;
  $('#sv').onclick=async()=>{
    const body={},bad=[];
    for(const [k,l,t,orig,req] of F){
      const raw=$('#f_'+k).value.trim();let v;
      if(k==='genres')v=raw?raw.split(',').map(x=>x.trim()).filter(Boolean):[];
      else if(t==='number'){v=raw===''?null:Number(raw);if(Number.isNaN(v))bad.push(l+' must be a number')}
      else v=raw===''?null:raw;
      if(req&&v===null)bad.push(l+' cannot be empty');
      if(k==='vote_average'&&v!==null&&(v<0||v>10))bad.push('Rating must be between 0 and 10');
      if(['budget','revenue','popularity','runtime'].includes(k)&&v!==null&&v<0)bad.push(l+' cannot be negative');
      if(k==='original_language'&&v&&!/^[a-z]{2,3}$/.test(v))bad.push('Language must be a 2-3 letter lowercase code');
      if(JSON.stringify(v)!==JSON.stringify(orig??(k==='genres'?[]:null)))body[k]=v;
    }
    if(bad.length){$('#em').innerHTML='<div class="note bad">'+bad.map(esc).join('<br>')+'</div>';return}
    if(!Object.keys(body).length){$('#em').innerHTML='<div class="note bad">No changes to save.</div>';return}
    try{await sendJSON('PATCH','movies/'+m.id,body);
      await details(m.id,'Saved to the shared database.');   // re-fetch the saved record from the API
      route()}                                                // refresh KPIs, tables and charts behind the modal
    catch(e){if(e.status===401){logout();loginForm('Session expired. Please sign in again.')}else $('#em').innerHTML='<div class="note bad">'+esc(e.message)+'</div>'}
  };
}

// ---- start ----
renderAuth();renderTray();
(async()=>{try{Object.assign(META,await api('analytics/summary'))}catch(e){/* shown by route() */}
  if(!location.hash)location.hash='overview';else route()})();
"""


def render_page() -> str:
    return ("<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>Movie Intelligence Platform</title><style>" + CSS + "</style></head><body>" + BODY +
            "<script src='https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js'></script>"
            "<script>" + JS + "</script></body></html>")
