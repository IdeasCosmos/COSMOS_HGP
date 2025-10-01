/* eslint-disable react-hooks/exhaustive-deps */
import React,{useMemo,useRef,useState}from"react";
import{AnimatePresence,motion}from"framer-motion";
import{Area,AreaChart,CartesianGrid,ResponsiveContainer,Tooltip,XAxis,YAxis}from"recharts";
import{LayoutDashboard,BookOpen,Key,CreditCard,Settings}from"lucide-react";

/* Design System */
const DS={primary:"#FFD700",secondary:"#FFA500",bg:"#FFFFFF",surface:"#F9F9F9",text:"#333",border:"#E0E0E0"};
const cx=(...c)=>c.filter(Boolean).join(" ");
const API_URL=window.location.hostname==="localhost"?"http://localhost:7860":`http://${window.location.hostname}:7860`;

/* Ripple */
const RippleButton=({className,children,onClick,...p})=>{
  const ref=useRef(null);const[r,setR]=useState([]);
  return(<button ref={ref} onClick={e=>{const b=ref.current.getBoundingClientRect();const s=Math.max(b.width,b.height);const x=e.clientX-b.left-s/2;const y=e.clientY-b.top-s/2;const id=crypto.randomUUID();setR(v=>[...v,{id,x,y,s}]);onClick&&onClick(e);setTimeout(()=>setR(v=>v.filter(t=>t.id!==id)),600)}} className={cx("relative overflow-hidden rounded-full px-4 py-2 font-medium shadow transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",className)} {...p}>
      <span className="relative z-10">{children}</span>
    {r.map(t=>(<span key={t.id} style={{left:t.x,top:t.y,width:t.s,height:t.s}} className="pointer-events-none absolute rounded-full bg-white/40 animate-[ripple_0.6s_ease-out]"/>))}
      <style>{`@keyframes ripple{from{transform:scale(0);opacity:.6}to{transform:scale(2.5);opacity:0}}`}</style>
  </button>);
};

/* Header */
const Header=({apiKey,setApiKey})=>(
  <header className="sticky top-0 z-20 backdrop-blur border-b" style={{borderColor:DS.border}}>
    <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
      <div className="flex items-center gap-2"><span className="text-2xl">⚜️</span><span className="text-lg font-semibold" style={{color:DS.text}}>COSMOS-HGP Premium</span></div>
      <div className="flex items-center gap-2">
        <input aria-label="api-key" type="password" placeholder="API Key" value={apiKey} onChange={e=>setApiKey(e.target.value)} className="ml-3 w-48 rounded-md border px-2 py-1 text-sm" style={{borderColor:DS.border,background:DS.surface}}/>
        <RippleButton className="ml-2 bg-gradient-to-b from-[#FFD700] to-[#FFA500] text-[#111]" onClick={()=>window.location.href="../pricing.html"}>Get PRO</RippleButton>
      </div>
    </div>
  </header>
);

/* Sidebar */
const Sidebar=()=>(
  <aside className="hidden lg:block w-64 border-r h-[calc(100vh-56px)] sticky top-14" style={{borderColor:DS.border,background:DS.bg}}>
    <nav className="p-4 space-y-1 text-sm">
      <SideItem icon={<LayoutDashboard size={18}/>} label="Dashboard" active/>
      <SideItem icon={<BookOpen size={18}/>} label="Documentation"/>
      <SideItem icon={<Key size={18}/>} label="API Keys"/>
      <SideItem icon={<CreditCard size={18}/>} label="Billing"/>
      <SideItem icon={<Settings size={18}/>} label="Settings"/>
    </nav>
  </aside>
);
const SideItem=({icon,label,active,href})=>(<a href={href||"#"} className={cx("flex items-center gap-2 rounded-md px-3 py-2",active?"bg-[#FFF7D6] text-[#111] font-medium":"hover:bg-[#FFF7D6]/60")}>{icon}<span>{label}</span></a>);

/* Small UI */
const Spinner=()=>(<span className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-[#FFA500] border-r-transparent"/>);
const Badge=({children})=>(<span className="rounded-full border px-3 py-1 text-xs" style={{borderColor:DS.border,background:DS.surface}}>{children}</span>);

/* Previews */
const DualityModePreview=()=>(<motion.div className="h-24 w-full rounded-lg" style={{background:"linear-gradient(90deg,#FFF7D6,#FFFFFF)"}} animate={{backgroundPositionX:["0%","100%"]}} transition={{repeat:Infinity,duration:2,ease:"easeInOut"}}/>);
const DNACodonPreview=()=>(<motion.div className="grid h-24 w-full grid-cols-8 gap-1">{Array.from({length:32}).map((_,i)=>(<motion.div key={i} className="rounded-sm" style={{background:i%3?"#FFE794":"#FFF4C2"}} animate={{scale:[1,1.08,1]}} transition={{repeat:Infinity,duration:1.8,delay:i*.03}}/>))}</motion.div>);
const PlaceholderPreview=()=>(<motion.div className="h-24 w-full rounded-lg border" style={{borderColor:DS.border,background:DS.surface}} animate={{opacity:[.8,1,.8]}} transition={{repeat:Infinity,duration:2}}/>);

/* Feature Card */
const FeatureCard=({item,onOpen})=>(
  <motion.div whileHover={{y:-6}} className="group relative rounded-2xl border p-4 shadow-sm" style={{borderColor:DS.border,background:"#fff"}}>
    <div className="absolute right-3 top-3">{item.locked&&(<span className="rounded-full bg-neutral-900/80 px-2 py-0.5 text-xs text-white">🔒 PRO</span>)}</div>
    <div className="mb-2 flex items-center gap-2"><span className="text-xl">{item.icon}</span><h3 className="text-base font-semibold">{item.title}</h3></div>
    <p className="mb-3 line-clamp-3 text-sm text-neutral-600">{item.desc}</p>
    <div className="mb-3">{item.preview?<item.preview/>:<PlaceholderPreview/>}</div>
    <div className="flex justify-end">
      <RippleButton onClick={()=>onOpen(item)} className="opacity-0 group-hover:opacity-100 transition bg-gradient-to-b from-[#FFD700] to-[#FFA500] text-[#111]">자세히 보기</RippleButton>
    </div>
  </motion.div>
);

/* Generic Modal */
const Modal=({open,onClose,children})=>(
  <AnimatePresence>
    {open&&(
      <motion.div className="fixed inset-0 z-40 grid place-items-center bg-black/40 p-4" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}>
        <motion.div className="w-full max-w-3xl rounded-2xl border bg-white p-5" style={{borderColor:DS.border}} initial={{y:30,opacity:0}} animate={{y:0,opacity:1}} exit={{y:20,opacity:0}}>
          {children}
          <div className="mt-4 text-right">
            <RippleButton onClick={onClose} className="bg-neutral-100">닫기</RippleButton>
          </div>
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
);

/* Hero */
const Hero=({apiKey,health,featuresCount})=>(
  <section className="mb-4 rounded-2xl border p-5" style={{borderColor:DS.border,background:"#fff"}}>
    <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 className="text-xl font-semibold">COSMOS-HGP Premium Dashboard</h1>
        <p className="text-sm text-neutral-600">Server: {health} • PRO Features: {featuresCount}</p>
      </div>
      <div className="flex items-center gap-2"><Badge>React 18</Badge><Badge>Tailwind</Badge><Badge>Framer</Badge><Badge>Recharts</Badge></div>
    </div>
  </section>
);

/* FREE Engine */
const FreeEngineSection=({onLocalRun,onApiRun,series,loading,avgImpact,input,threshold,setInput,setThreshold,sendPath})=>(
  <section className="rounded-2xl border p-5 bg-white" style={{borderColor:DS.border}}>
      <h2 className="mb-3 text-lg font-semibold">FREE • Basic Engine</h2>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-3">
        <label className="block text-sm">데이터</label>
        <input className="w-full rounded-lg border px-3 py-2" style={{borderColor:DS.border,background:DS.surface}} value={input} onChange={e=>setInput(e.target.value)} placeholder="1,2,3,4,5"/>
        <div><label className="block text-sm">Threshold: {threshold.toFixed(2)}</label><input type="range" min={0} max={1} step={.01} value={threshold} onChange={e=>setThreshold(+e.target.value)} className="w-full accent-[#FFA500]"/></div>
        <div className="flex items-center gap-2 flex-wrap">
          <RippleButton onClick={onLocalRun} className="bg-gradient-to-b from-[#FFD700] to-[#FFA500] text-[#111]">로컬</RippleButton>
          <RippleButton onClick={onApiRun} className="bg-neutral-100">API</RippleButton>
          <RippleButton onClick={sendPath} className="bg-neutral-100">경로</RippleButton>
          {loading&&<Spinner/>}<span className="text-sm text-neutral-600">평균: {avgImpact}</span>
          </div>
          </div>
      <div className="h-64 rounded-xl border p-2" style={{borderColor:DS.border,background:DS.surface}}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={series}>
            <defs><linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={DS.primary} stopOpacity={.9}/><stop offset="100%" stopColor={DS.secondary} stopOpacity={.2}/></linearGradient></defs>
            <CartesianGrid stroke="#eee"/><XAxis dataKey="idx"/><YAxis/><Tooltip contentStyle={{borderRadius:12,borderColor:DS.border,background:"#fff"}}/>
            <Area type="monotone" dataKey="value" stroke={DS.secondary} fill="url(#gold)"/>
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );

/* Codon */
const CodonSection=({code,setCode,onAnalyze,codonUsage,result,loading})=>(
  <section className="rounded-2xl border p-5 bg-white" style={{borderColor:DS.border}}>
    <h2 className="mb-3 text-lg font-semibold">DNA 코돈</h2>
    <div className="grid gap-4 md:grid-cols-2">
      <div className="space-y-2">
        <label className="text-sm">Code</label>
        <textarea value={code} onChange={e=>setCode(e.target.value)} rows={8} className="w-full rounded-lg border px-3 py-2 font-mono text-xs" style={{borderColor:DS.border,background:DS.surface}}/>
        <div className="flex items-center gap-2">
          <RippleButton onClick={onAnalyze} className="bg-gradient-to-b from-[#FFD700] to-[#FFA500] text-[#111]">{loading?<><Spinner/> 분석중</>:"분석"}</RippleButton>
          <small className="text-xs text-neutral-600">{codonUsage}/50</small>
        </div>
      </div>
      <div>
        <div className="text-xs mb-1 text-neutral-600">결과</div>
        <pre className="h-44 overflow-auto rounded-lg border p-3 text-xs" style={{borderColor:DS.border,background:"#fff"}}>{result?JSON.stringify(result,null,2):"결과"}</pre>
      </div>
    </div>
  </section>
);

/* Velocity */
const VelocitySection=({layer,setLayer,impact,setImpact,onCalc,result,loading})=>(
  <section className="rounded-2xl border p-5 bg-white" style={{borderColor:DS.border}}>
    <h2 className="mb-3 text-lg font-semibold">7계층 속도</h2>
    <div className="grid gap-4 md:grid-cols-2">
      <div className="grid grid-cols-2 gap-3">
        <div><label className="text-sm">Layer</label><input type="number" min={1} max={7} value={layer} onChange={e=>setLayer(+e.target.value)} className="w-full rounded-lg border px-3 py-2" style={{borderColor:DS.border,background:DS.surface}}/></div>
        <div><label className="text-sm">Impact</label><input type="number" step="0.01" min={0} max={1} value={impact} onChange={e=>setImpact(+e.target.value)} className="w-full rounded-lg border px-3 py-2" style={{borderColor:DS.border,background:DS.surface}}/></div>
        <div className="col-span-2"><RippleButton onClick={onCalc} className="bg-gradient-to-b from-[#FFD700] to-[#FFA500] text-[#111]">{loading?<><Spinner/> 계산중</>:"계산"}</RippleButton></div>
      </div>
      <div>
        <div className="text-xs mb-1 text-neutral-600">결과</div>
        <pre className="h-32 overflow-auto rounded-lg border p-3 text-xs" style={{borderColor:DS.border,background:"#fff"}}>{result?JSON.stringify(result,null,2):"결과"}</pre>
      </div>
    </div>
  </section>
);

/* Duality */
const DualitySection=({mode,setMode,onSwitch,result,loading})=>(
  <section className="rounded-2xl border p-5 bg-white" style={{borderColor:DS.border}}>
    <h2 className="mb-3 text-lg font-semibold">이중성 모드</h2>
    <div className="grid gap-4 md:grid-cols-2">
      <div className="flex items-center gap-3">
        <label className="text-sm">Mode</label>
        <select value={mode} onChange={e=>setMode(e.target.value)} className="rounded-lg border px-3 py-2" style={{borderColor:DS.border,background:DS.surface}}>
          <option value="stability">Stability</option>
          <option value="innovation">Innovation</option>
          <option value="adaptive">Adaptive</option>
        </select>
        <RippleButton onClick={onSwitch} className="bg-gradient-to-b from-[#FFD700] to-[#FFA500] text-[#111]">{loading?<><Spinner/> 전환</>:"전환"}</RippleButton>
      </div>
      <div>
        <div className="text-xs mb-1 text-neutral-600">결과</div>
        <pre className="h-24 overflow-auto rounded-lg border p-3 text-xs" style={{borderColor:DS.border,background:"#fff"}}>{result?JSON.stringify(result,null,2):"결과"}</pre>
      </div>
    </div>
  </section>
);

/* Path Visualizer */
const PathViz=({paths})=>{
  const w=900,h=220,pad=12;
  return(<section className="rounded-2xl border p-5 bg-white" style={{borderColor:DS.border}}>
    <h2 className="mb-3 text-lg font-semibold">경로 시각화</h2>
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full rounded-lg border" style={{borderColor:DS.border,background:"#fff"}}>
      <defs><linearGradient id="pw" x1="0" x2="1"><stop offset="0%" stopColor="#FFD700"/><stop offset="100%" stopColor="#FFA500"/></linearGradient></defs>
      {paths.map((seg,i)=>{
        const d=seg.points.map((p,j)=>`${j?"L":"M"}${pad+p.x*(w-2*pad)} ${h-pad-p.y*(h-2*pad)}`).join(" ");
        const sw=1+Math.max(.5,seg.impact*6);
        const col=seg.blocked?"#ef4444":"url(#pw)";
        return(<path key={i} d={d} fill="none" stroke={col} strokeWidth={sw} strokeOpacity={seg.blocked?.8:.95} strokeLinecap="round"/>);
      })}
    </svg>
    <p className="mt-2 text-xs text-neutral-600">골드=정상, 빨강=차단, 굵기=impact</p>
  </section>);
};

/* Pro Features (8개) */
const FEAT={
  codon:{ep:"/codon/analyze",method:"POST",preview:DNACodonPreview,desc:"64개 코돈 분석",icon:"🧬"},
  velocity:{ep:"/velocity/calculate",method:"POST",preview:PlaceholderPreview,desc:"7계층 임계값",icon:"🚀"},
  process:{ep:"/pro/process",method:"POST",preview:PlaceholderPreview,desc:"예측+양방향+자가치유",icon:"⚙️"},
  batch:{ep:"/pro/batch",method:"POST",preview:PlaceholderPreview,desc:"병렬 처리",icon:"📦"},
  dualitySwitch:{ep:"/pro/duality/switch",method:"POST",preview:DualityModePreview,desc:"모드 전환",icon:"🎭"},
  thresholdAdj:{ep:"/pro/threshold/adjust",method:"POST",preview:PlaceholderPreview,desc:"임계값 조정",icon:"🎚️"},
  telemetry:{ep:"/pro/telemetry",method:"GET",preview:PlaceholderPreview,desc:"텔레메트리",icon:"📡"},
  stats:{ep:"/pro/stats",method:"GET",preview:PlaceholderPreview,desc:"통계",icon:"📊"},
};

const ProFeaturesGrid=({onOpen})=>{
  const items=Object.entries(FEAT).map(([slug,v])=>({slug,title:labelize(slug),icon:v.icon,locked:true,preview:v.preview,desc:v.desc}));
  return(<section className="mt-6"><h2 className="mb-3 text-lg font-semibold">PRO Features (8개)</h2><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{items.map(it=>(<FeatureCard key={it.slug} item={it} onOpen={onOpen}/>))}</div></section>);
};

const labelize=s=>({codon:"DNA 코돈",velocity:"7계층 속도",process:"프로세스",batch:"배치",dualitySwitch:"이중성",thresholdAdj:"임계값",telemetry:"텔레메트리",stats:"통계"}[s]||s);

/* PRO Modal */
const ProModal=({open,featureName,onClose})=>(
  <Modal open={open} onClose={onClose}>
    <h2 className="text-lg font-semibold">🔒 PRO 전용</h2>
    <h3 className="mt-1">{featureName}</h3>
    <p className="mt-2 text-sm text-neutral-700">PRO 구독이 필요합니다.</p>
    <div className="mt-3"><span className="text-2xl font-bold">$5/월</span></div>
    <a href="../pricing.html"><button className="mt-3 rounded-full px-4 py-2 bg-gradient-to-b from-[#FFD700] to-[#FFA500] text-[#111]">구독</button></a>
  </Modal>
);

/* Root */
export default function Dashboard(){
  const[apiKey,setApiKey]=useState("");
  const[health,setHealth]=useState("…");const[featuresCount,setFeaturesCount]=useState("…");

  const fetchPublic=async()=>{
    try{
      const r1=await fetch(`${API_URL}/health`).then(r=>r.json()).catch(()=>null);
      const r2=await fetch(`${API_URL}/pro/features`).then(r=>r.json()).catch(()=>null);
      setHealth(r1?.healthy?"✅":"❌");setFeaturesCount(r2?.features?.length||"—");
    }catch{setHealth("offline")}
  };

  const[proOpen,setProOpen]=useState(false);const[proFeat,setProFeat]=useState("");
  const showProModal=name=>{setProFeat(name);setProOpen(true);};

  const callAPI=async(endpoint,data=null,method="POST")=>{
    const opt={method,headers:{"Content-Type":"application/json"}};
    if(endpoint.includes("/pro/")||endpoint==="/velocity/calculate"||endpoint==="/codon/analyze"){
      if(!apiKey){showProModal(endpoint);throw new Error("API key required");}
      opt.headers["Authorization"]=`Bearer ${apiKey}`;
    }
    if(data&&method!=="GET") opt.body=JSON.stringify(data);
    const res=await fetch(`${API_URL}${endpoint}`,opt);
    if(!res.ok)throw new Error(`HTTP ${res.status}`);
    return res.json();
  };

  const[input,setInput]=useState("1,2,3,4,5");const[threshold,setThreshold]=useState(.5);
  const[series,setSeries]=useState([]);const[fLoading,setFLoading]=useState(false);
  const avgImpact=useMemo(()=>series.length?(series.reduce((a,b)=>a+b.impact,0)/series.length).toFixed(3):"0.000",[series]);

  const runLocalFree=async()=>{
    setFLoading(true);await new Promise(r=>setTimeout(r,120));
    const nums=input.split(/[,\s]+/).map(Number).filter(Number.isFinite);
    const data=nums.map((v,i)=>{const imp=Math.tanh(v/(i+1)*.6);const blocked=imp>=threshold;const value=blocked?v:v*(1+(threshold-imp)*.3);return{idx:i+1,value:+value.toFixed(3),impact:+imp.toFixed(3),blocked};});
    setSeries(data);setFLoading(false);
  };

  const runApiFree=async()=>{
    setFLoading(true);
    try{
      const nums=input.split(/[,\s]+/).map(Number).filter(Number.isFinite);
      const payload=nums.map((v,i)=>({layer:Math.min(7,i+1),impact:Math.min(.99,Math.abs(v)/(i+2))}));
      const outs=await Promise.all(payload.map(p=>callAPI("/velocity/calculate",p).catch(e=>({error:String(e)}))));
      const data=outs.map((o,i)=>({idx:i+1,value:o.blocked?nums[i]:nums[i]*(o.threshold?1+(o.threshold-.1)*.2:1),impact:+payload[i].impact.toFixed(3),blocked:!!o.blocked}));
      setSeries(data);
    }catch(e){console.error(e)}
    setFLoading(false);
  };

  const[paths,setPaths]=useState([]);
  const sendPath=()=>{if(!series.length)return;
    const maxV=Math.max(...series.map(s=>s.value||0))||1;
    const pts=series.map((s,i)=>({x:i/(series.length-1||1),y:Math.min(1,(s.value||0)/maxV)}));
    const blocked=series.some(s=>s.blocked);const impact=series.reduce((a,b)=>a+b.impact,0)/(series.length||1);
    setPaths(p=>[...p.slice(-3),{points:pts,impact,blocked}]);
  };

  const[codonUsage,setCodonUsage]=useState(0);
  const[code,setCode]=useState(`def process(data):\n    return [x*2 for x in data]`);
  const[codonRes,setCodonRes]=useState(null);const[codonLoading,setCodonLoading]=useState(false);
  const analyzeCodon=async()=>{
    if(!apiKey&&codonUsage>=50){alert("FREE 한도 초과!");showProModal("DNA 코돈");return;}
    setCodonLoading(true);
    try{const r=await callAPI("/codon/analyze",{code});setCodonUsage(x=>x+1);setCodonRes(r);}catch(e){setCodonRes({error:String(e)})}
    setCodonLoading(false);
  };

  const[layer,setLayer]=useState(1);const[impact,setImpact]=useState(.25);
  const[velRes,setVelRes]=useState(null);const[velLoading,setVelLoading]=useState(false);
  const calcVelocity=async()=>{setVelLoading(true);try{const r=await callAPI("/velocity/calculate",{layer,impact});setVelRes(r);}catch(e){setVelRes({error:String(e)})}setVelLoading(false);};

  const[mode,setMode]=useState("stability");const[dualRes,setDualRes]=useState(null);const[dualLoading,setDualLoading]=useState(false);
  const switchDuality=async()=>{setDualLoading(true);try{const r=await callAPI("/pro/duality/switch",{mode});setDualRes(r);}catch(e){setDualRes({error:String(e)})}setDualLoading(false);};

  const[open,setOpen]=useState(false);const[active,setActive]=useState(null);
  const[loading,setLoading]=useState(false);const[apiResult,setApiResult]=useState(null);const[apiError,setApiError]=useState(null);

  const openFeature=it=>{setActive(it);setOpen(true);setApiResult(null);setApiError(null);};
  const runFeature=async()=>{
    if(!active)return;
    const def=FEAT[active.slug];if(!def)return;
    if(!apiKey){showProModal(active.title);return;}
    setLoading(true);setApiError(null);setApiResult(null);
    try{
      const sample={codon:{code:"def f():\n  return 1"},velocity:{layer:1,impact:.25},process:{data:[1,2,3]},batch:{data_list:[[1,2],[3,4]]},dualitySwitch:{mode:"stability"},thresholdAdj:{layer:1,value:.15},telemetry:null,stats:null}[active.slug];
      const res=await callAPI(def.ep,sample,def.method||"POST");
      setApiResult(res);
    }catch(e){setApiError(e.message||String(e))}
    setLoading(false);
  };

  React.useEffect(()=>{fetchPublic();},[]);

  return(
    <div className="min-h-screen" style={{background:`linear-gradient(180deg,#FFFFFF,#FFFFFF 60%,#FFF7D6)`,color:DS.text}}>
      <Header apiKey={apiKey} setApiKey={setApiKey}/>
      <div className="mx-auto flex max-w-7xl">
        <Sidebar/>
        <div className="flex-1">
          <main className="mx-auto w-full max-w-7xl p-4">
            <Hero apiKey={apiKey} health={health} featuresCount={featuresCount}/>
            <FreeEngineSection onLocalRun={runLocalFree} onApiRun={runApiFree} series={series} loading={fLoading} avgImpact={avgImpact} input={input} threshold={threshold} setInput={setInput} setThreshold={setThreshold} sendPath={sendPath}/>
            <CodonSection code={code} setCode={setCode} onAnalyze={analyzeCodon} codonUsage={codonUsage} result={codonRes} loading={codonLoading}/>
            <VelocitySection layer={layer} setLayer={setLayer} impact={impact} setImpact={setImpact} onCalc={calcVelocity} result={velRes} loading={velLoading}/>
            <DualitySection mode={mode} setMode={setMode} onSwitch={switchDuality} result={dualRes} loading={dualLoading}/>
            <PathViz paths={paths}/>
            <ProFeaturesGrid onOpen={openFeature}/>
          </main>
    </div>
    </div>

  <AnimatePresence>
        {open&&(
          <motion.div className="fixed inset-0 z-40 grid place-items-center bg-black/40 p-4" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}>
            <motion.div className="w-full max-w-3xl rounded-2xl border bg-white p-5" style={{borderColor:DS.border}} initial={{y:30,opacity:0}} animate={{y:0,opacity:1}} exit={{y:20,opacity:0}}>
          <div className="flex items-start justify-between gap-4">
                <h3 className="text-lg font-semibold">{active?.icon} {active?.title}</h3>
                <RippleButton onClick={()=>setOpen(false)} className="bg-neutral-100">닫기</RippleButton>
          </div>
              <p className="mt-2 text-sm text-neutral-700">{active?.desc}</p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div>
                  <div className="mb-2 text-xs font-medium text-neutral-600">데모</div>
                  <div className="mb-3">{active?.preview?<active.preview/>:<PlaceholderPreview/>}</div>
                  <RippleButton onClick={runFeature} className="bg-gradient-to-b from-[#FFD700] to-[#FFA500] text-[#111]">{loading?<><Spinner/> 호출중</>:"API 호출"}</RippleButton>
            </div>
            <div>
                  <div className="mb-2 text-xs font-medium text-neutral-600">응답</div>
                  <pre className="h-48 overflow-auto rounded-lg border p-3 text-xs" style={{borderColor:DS.border,background:"#fff"}}>
{apiError?String(apiError):apiResult?JSON.stringify(apiResult,null,2):"응답"}
                  </pre>
            </div>
          </div>
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>

      <ProModal open={proOpen} featureName={proFeat} onClose={()=>setProOpen(false)}/>
    </div>
  );
}
