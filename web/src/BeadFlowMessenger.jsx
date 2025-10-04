import React, { useEffect, useMemo, useRef, useState } from "react";
import DebugProfiler, { perfLogger } from "./DebugProfiler.jsx";

/**
 * COSMOS-HGP • BeadFlow Messenger • Full Edition
 * Gold & White • Messenger shell • Canvas renderer • MetaBall aggregation
 * Codon-sized beads (64 codons) + 7-layer scaling • Progressive darkening
 * Black on block • Router/Bins/Outlet • Metrics panel • Tooltips
 * Export PNG/WebM/JSON • Import JSON • Sound toggle • High-contrast toggle
 * No security layer here.
 */
export default function BeadFlowMessengerFull({
  initialSeries = makeDemoSeries(24), // demo
  threshold: thresholdProp = 0.33,
  binCount: binCountProp = 4,
}) {
  /* ---------- UI state ---------- */
  const [binCount, setBinCount] = useState(binCountProp);
  const [threshold, setThreshold] = useState(thresholdProp);
  const [carryMode, setCarryMode] = useState("carry"); // carry | resetLayer | resetAlways
  const [soundOn, setSoundOn] = useState(false);
  const [running, setRunning] = useState(true);
  const [aggregate, setAggregate] = useState(true);
  const [metaFactor, setMetaFactor] = useState(10);
  const [hiContrast, setHiContrast] = useState(false);
  const [recording, setRecording] = useState(false);
  const [showProfiler, setShowProfiler] = useState(false);

  /* ---------- Layout ---------- */
  const W = 1200, H = 640, PAD = 18;
  const layout = useMemo(() => layoutCompute(W, H, PAD, binCount), [W, H, PAD, binCount]);
  const theme = hiContrast ? HC_THEME : GW_THEME;

  /* ---------- Audio ---------- */
  const audio = useAudio();
  useEffect(() => { soundOn ? audio.enable() : audio.disable(); }, [soundOn]);

  /* ---------- Canvas & loop ---------- */
  const canvasRef = useRef(null);
  const rafRef = useRef(0);
  const beadsRef = useRef([]);
  const seedRef = useRef(42);

  const [hoverInfo, setHoverInfo] = useState(null);
  const [metrics, setMetrics] = useState({ total:0, meta:0, avg:0, sum:0, var:0, blocked:0, near:0 });

  const recorderRef = useRef(null); const chunksRef = useRef([]);

  useEffect(() => {
    const src = aggregate ? toMeta(initialSeries, binCount, metaFactor) : initialSeries;
    beadsRef.current = buildBeads(src, threshold, binCount, carryMode, layout, seedRef.current);
    drawOnce(canvasRef.current, beadsRef.current, layout, threshold, theme);
    setMetrics(calcMetrics(src, threshold));
  }, [initialSeries, threshold, binCount, carryMode, layout, aggregate, metaFactor, theme]);

  useEffect(() => {
    cancelAnimationFrame(rafRef.current);
    if (!running) return;
    const loop = () => {
      step(beadsRef.current, layout, threshold, audio);
      drawOnce(canvasRef.current, beadsRef.current, layout, threshold, theme);
      rafRef.current = requestAnimationFrame(loop);
    };
    rafRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(rafRef.current);
  }, [running, layout, threshold, audio, theme]);

  useEffect(() => {
    const cvs = canvasRef.current; if(!cvs) return;
    const onMove = (e) => {
      const rect = cvs.getBoundingClientRect();
      const x = (e.clientX - rect.left) * (cvs.width/rect.width);
      const y = (e.clientY - rect.top) * (cvs.height/rect.height);
      const b = pickBead(beadsRef.current, x, y);
      if (b) {
        const label = tooltipLabel(b, threshold);
        setHoverInfo({ x: e.clientX, y: e.clientY, label });
      } else setHoverInfo(null);
    };
    const onLeave = ()=> setHoverInfo(null);
    cvs.addEventListener('mousemove', onMove); cvs.addEventListener('mouseleave', onLeave);
    return () => { cvs.removeEventListener('mousemove', onMove); cvs.removeEventListener('mouseleave', onLeave); };
  }, [threshold]);

  const download = (url, name) => { const a=document.createElement('a'); a.href=url; a.download=name; a.click(); };
  const exportPNG = () => { if(!canvasRef.current) return; const url = canvasRef.current.toDataURL('image/png'); download(url, `beadflow_${Date.now()}.png`); };
  const startRec = () => {
    if(!canvasRef.current) return;
    const stream = canvasRef.current.captureStream(30);
    const mime = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')? 'video/webm;codecs=vp9':'video/webm;codecs=vp8';
    const rec = new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:6_000_000});
    chunksRef.current = [];
    rec.ondataavailable = e=> e.data.size && chunksRef.current.push(e.data);
    rec.onstop = ()=>{ const blob=new Blob(chunksRef.current,{type:'video/webm'}); download(URL.createObjectURL(blob), `beadflow_${Date.now()}.webm`); chunksRef.current=[]; recorderRef.current=null; setRecording(false); };
    rec.start(); recorderRef.current = rec; setRecording(true);
  };
  const stopRec = () => { if(recorderRef.current){ recorderRef.current.stop(); } };
  const exportJSON = () => {
    const raw = beadsRef.current.flatMap(b=> b.children ?? [{impact:b.impact, cat:b.cat, blocked:b.blocked, codon:b.codon, layer:b.layer}]);
    const spec = { seed: seedRef.current, threshold, binCount, aggregate, metaFactor, series: raw };
    const blob = new Blob([JSON.stringify(spec,null,2)],{type:'application/json'});
    download(URL.createObjectURL(blob), `beadflow_${Date.now()}.json`);
  };
  const importJSON = async (file) => {
    const text = await file.text(); const spec = JSON.parse(text);
    seedRef.current = spec.seed || 42;
    const agg = !!(spec.aggregate ?? aggregate);
    const bcount = spec.binCount ?? binCount;
    const mf = spec.metaFactor ?? metaFactor;
    setThreshold(spec.threshold ?? threshold);
    setBinCount(bcount);
    setAggregate(agg);
    setMetaFactor(mf);
    const base = spec.series || [];
    const src = agg ? toMeta(base, bcount, mf) : base;
    beadsRef.current = buildBeads(src, spec.threshold ?? threshold, bcount, carryMode, layout, seedRef.current);
    drawOnce(canvasRef.current, beadsRef.current, layout, spec.threshold ?? threshold, theme);
    setMetrics(calcMetrics(src, spec.threshold ?? threshold));
  };

  return (
    <div className="flex h-screen w-full" style={{background:theme.bg}}>
      <aside className="hidden md:flex w-64 flex-col border-r" style={{borderColor:theme.border, background:theme.side}}>
        <div className="px-4 py-3 text-sm font-semibold">⚜️ COSMOS • Channels</div>
        <div className="flex-1 overflow-auto">
          {['Ops','R&D','Compliance','SRE','Exec'].map((n,i)=> (
            <div key={i} className="flex items-center gap-3 px-4 py-3 hover:bg-white/70 cursor-pointer">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full" style={{background:theme.chipGrad,color:'#111'}}>{n[0]}</span>
              <div className="text-sm">
                <div className="font-medium">{n}</div>
                <div className="text-xs" style={{color:theme.muted}}>KPI & Flow</div>
              </div>
            </div>
          ))}
        </div>
        <div className="p-3 text-xs" style={{color:theme.muted}}>Gold & White • Secure-ready</div>
      </aside>

      <section className="flex-1 flex flex-col">
        <header className="flex items-center justify-between border-b px-4 py-3" style={{borderColor:theme.border, background:theme.header}}>
          <div className="flex items-center gap-3">
            <span className="text-lg font-semibold" style={{color:theme.text}}>BeadFlow • Executive Cosmic View</span>
            <span className="rounded-full border px-3 py-1 text-xs" style={{borderColor:theme.border, background:theme.surface}}>Stability / Innovation / Adaptive</span>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={()=>setShowProfiler(v=>!v)} className="rounded-full border px-3 py-1 text-xs" style={{borderColor:theme.border, background:showProfiler? theme.goldSoft:theme.surface}} title="Performance Profiler">🔬</button>
            <button onClick={()=>setHiContrast(v=>!v)} className="rounded-full border px-3 py-1 text-xs" style={{borderColor:theme.border, background:theme.surface}}>{hiContrast? 'HC':'GW'}</button>
            <button onClick={()=>setSoundOn(v=>!v)} className="rounded-full border px-3 py-1 text-xs" style={{borderColor:theme.border, background:soundOn? theme.goldSoft:theme.surface}}>{soundOn? '🔊':'🔇'}</button>
            <button onClick={exportPNG} className="rounded-full border px-4 py-1 text-sm" style={{borderColor:theme.border}}>PNG</button>
            {recording
              ? <button onClick={stopRec} className="rounded-full border px-4 py-1 text-sm" style={{borderColor:theme.border}}>Stop</button>
              : <button onClick={startRec} className="rounded-full border px-4 py-1 text-sm" style={{borderColor:theme.border}}>Rec</button>}
            <button onClick={exportJSON} className="rounded-full border px-4 py-1 text-sm" style={{borderColor:theme.border}}>JSON</button>
            <label className="rounded-full border px-3 py-1 text-sm cursor-pointer" style={{borderColor:theme.border}}>
              Import<input type="file" accept="application/json" className="hidden" onChange={e=>e.target.files[0]&&importJSON(e.target.files[0])}/>
            </label>
            {running ? (
              <button onClick={()=>setRunning(false)} className="rounded-full border px-4 py-1 text-sm" style={{borderColor:theme.border}}>Pause</button>
            ) : (
              <button onClick={()=>setRunning(true)} className="rounded-full border px-4 py-1 text-sm" style={{borderColor:theme.border}}>Start</button>
            )}
          </div>
        </header>

        <div className="flex flex-wrap items-center gap-4 border-b px-4 py-3" style={{borderColor:theme.border, background:theme.toolbar}}>
          <label className="flex items-center gap-2 text-sm">Bins
            <input type="range" min={1} max={8} value={binCount} onChange={e=>setBinCount(parseInt(e.target.value||'1',10))} className="w-40"/>
            <span>{binCount}</span>
          </label>
          <label className="flex items-center gap-2 text-sm">Threshold
            <input type="range" min={0} max={1} step={0.01} value={threshold} onChange={e=>setThreshold(parseFloat(e.target.value))} className="w-44"/>
            <span>{threshold.toFixed(2)}</span>
          </label>
          <label className="flex items-center gap-2 text-sm">Darkening
            <select value={carryMode} onChange={e=>setCarryMode(e.target.value)} className="rounded-md border px-2 py-1" style={{borderColor:theme.border, background:theme.surface}}>
              <option value="carry">carry</option>
              <option value="resetLayer">resetLayer</option>
              <option value="resetAlways">resetAlways</option>
            </select>
          </label>
          <label className="flex items-center gap-2 text-sm">MetaBall
            <input type="checkbox" checked={aggregate} onChange={e=>setAggregate(e.target.checked)}/>
            <span>factor</span>
            <input type="number" min={2} max={32} value={metaFactor} onChange={e=>setMetaFactor(Math.max(2,Math.min(32,parseInt(e.target.value||'10',10))))} className="w-16 rounded-md border px-2 py-1" style={{borderColor:theme.border, background:theme.surface}}/>
          </label>
          <div className="ml-auto flex items-center gap-4 text-xs" style={{color:theme.muted}}>
            <span>total {metrics.total}</span>
            <span>meta {metrics.meta}</span>
            <span>avg {metrics.avg.toFixed(3)}</span>
            <span>blocked {metrics.blocked}</span>
            <span>near {metrics.near}</span>
            <span>var {metrics.var.toFixed(4)}</span>
          </div>
        </div>

        <div className="relative flex-1" style={{background:theme.canvas}}>
          <canvas ref={canvasRef} width={W} height={H} className="h-full w-full"/>
          {hoverInfo && (
            <div style={{position:'fixed', left:hoverInfo.x+12, top:hoverInfo.y+12, background:'#fff', border:`1px solid ${theme.border}`, borderRadius:8, padding:'8px 10px', fontSize:12, color:'#333', boxShadow:'0 6px 18px rgba(0,0,0,0.08)'}}>
              <pre style={{margin:0}}>{hoverInfo.label}</pre>
            </div>
          )}
          <div className="pointer-events-none absolute inset-x-0 bottom-0 h-20" style={{background:theme.fade}}/>
        </div>
      </section>

      {/* 프로파일러 */}
      <DebugProfiler enabled={showProfiler} position="top-right" />
    </div>
  );
}

/* ---------------- Themes ---------------- */
const GW_THEME = {
  bg:'#FFFFFF', text:'#333', muted:'#666', border:'#E0E0E0', surface:'#F9F9F9', header:'#FFFFFF', toolbar:'#FFFDF2', side:'#FFF7D6', canvas:'#FFFFFF',
  chipGrad:'linear-gradient(#FFD700,#FFA500)', gold:'#FFD700', orange:'#FFA500', goldSoft:'#FFF4C2', fade:'linear-gradient(to top,#FFFFFF,transparent)'
};
const HC_THEME = {
  ...GW_THEME,
  canvas:'#FFFFFF',
  border:'#CFCFCF',
  muted:'#444',
};

/* ---------------- Physics + Drawing ---------------- */
function buildBeads(series, threshold, binCount, carryMode, layout, seed){
  const rand = mulberry32(1000 + (seed||0));
  const bins = layout.bins; const inlets = layout.inlets(series.length);
  const router = layout.router; const outlet = layout.outlet;

  const entities = series.map((s,i)=>{
    const cat = Number.isFinite(s.cat)? s.cat : (i % binCount);
    const layer = Number.isFinite(s.layer)? s.layer : (cat % 7)+1;
    const thEff = clamp01(threshold + 0);
    const r = thEff>0 ? (s.impact/thEff) : 0;
    const blocked = !!s.blocked || r>=1.0;
    const stage = blocked ? "black" : r>=0.75? "near" : r>=0.5? "darkening":"gold";
    const codon = s.codon || demoCodon(i);
    const base = 4.0;
    const size = base * codonScale(codon) * layerScale(layer) * (0.9 + s.impact*0.6);

    return {
      id: s.id || `b${i}`,
      cat, layer, thEff,
      stage, blocked, impact: s.impact, codon,
      color: toneColor(stage),
      r: size,
      children: s.children,
      p:{ x: inlets[i]?.x ?? (layout.PAD+46), y: inlets[i]?.y ?? (layout.PAD+46) },
      v:{ x: 0, y: 0 },
      tgt1:{ x: bins[cat % bins.length].x, y: bins[cat % bins.length].y },
      tgt2:{ x: router.x, y: router.y },
      tgt3:{ x: outlet.x, y: outlet.y },
      phase:0,
      tattoo: blocked? `-${i+1}`: null,
      darkness: stageDarkness(stage),
      carryMode,
      jitter: 0.5 + rand()*0.75,
      rotation: 0, // 회전 각도
    };
  });

  entities.forEach(e=>{
    if(!e.children) return;
    const sumArea = e.children.reduce((acc,ch)=>{
      const cr = 4.0 * codonScale(ch.codon||'AAA') * layerScale(e.layer) * (0.9 + ch.impact*0.6);
      return acc + cr*cr; }, 0);
    const metaR = Math.sqrt(Math.max(1,sumArea));
    e.r = metaR * 0.65;
    const thEff = e.thEff; const anyBlocked = e.children.some(c=> c.blocked || (thEff>0 && c.impact/thEff>=1));
    e.blocked = e.blocked || anyBlocked; e.stage = e.blocked? 'black': e.stage; e.tattoo = e.blocked? e.tattoo: null;
  });

  return entities;
}

function step(beads, layout, threshold, audio){
  // 당구식 직선 이동 물리 엔진 (대시보드.ini 사양 준수)
  const DT = 1/60, FRICTION = 0.985, VMAX = 420;
  const crowded = new Map();
  beads.forEach(b=>{ const key=b.cat; crowded.set(key, 1+(crowded.get(key)||0)); });

  for(const b of beads){
    if(b.phase>=3) continue;

    const tgt = b.phase===0? b.tgt1 : b.phase===1? b.tgt2 : b.tgt3;

    // 목표 지점으로 직선 이동
    const dx = tgt.x - b.p.x;
    const dy = tgt.y - b.p.y;
    const dist = Math.hypot(dx, dy);
    const len = dist || 1;
    const ux = dx / len;
    const uy = dy / len;

    // 가속도 (phase별)
    const ACC = b.phase===2 ? 220 : (b.phase===1 ? 160 : 140);
    b.v.x += ux * ACC * DT;
    b.v.y += (uy * ACC + (b.phase===2 ? 260 : 120)) * DT;

    // 마찰
    b.v.x *= FRICTION;
    b.v.y *= FRICTION;

    // 최대 속도 제한
    const speed = Math.hypot(b.v.x, b.v.y);
    if(speed > VMAX){
      b.v.x *= VMAX / speed;
      b.v.y *= VMAX / speed;
    }

    // 위치 업데이트
    b.p.x += b.v.x * DT;
    b.p.y += b.v.y * DT;

    // 회전 (속도에 비례)
    const angularVelocity = speed / (b.r * 10);
    b.rotation = (b.rotation || 0) + angularVelocity * DT;

    // 충돌 (반발계수 e=0.35)
    for(const o of beads){
      if(o===b || o.phase!==b.phase) continue;
      const cdx=b.p.x-o.p.x, cdy=b.p.y-o.p.y;
      const cd = Math.hypot(cdx, cdy);
      const minDist = b.r + o.r;

      if(cd < minDist && cd > 0){
        // 침투 보정 (factor 0.4)
        const overlap = minDist - cd;
        const nx = cdx / cd;
        const ny = cdy / cd;
        b.p.x += nx * overlap * 0.4;
        b.p.y += ny * overlap * 0.4;
        o.p.x -= nx * overlap * 0.4;
        o.p.y -= ny * overlap * 0.4;

        // 반발계수 0.35
        const e = 0.35;
        const relVx = b.v.x - o.v.x;
        const relVy = b.v.y - o.v.y;
        const relV = relVx * nx + relVy * ny;
        if(relV < 0){
          const impulse = -(1 + e) * relV / 2;
          b.v.x += impulse * nx;
          b.v.y += impulse * ny;
          o.v.x -= impulse * nx;
          o.v.y -= impulse * ny;

          // 임계 이상 충돌시 사운드
          if(Math.abs(relV) > 50) audio.click();
        }
      }
    }

    // Phase 전환 (도달判定: |target − p| < max(8, r*0.6))
    const arrivalDist = Math.max(8, b.r * 0.6);
    if(dist < arrivalDist){
      if(b.phase===0){
        if(b.blocked){
          b.phase=3;
          b.v.x=b.v.y=0;
          audio.thunk();
        } else {
          b.phase=1;
          audio.pour(crowded.get(b.cat)||2);
        }
      }
      else if(b.phase===1){ b.phase=2; }
      else if(b.phase===2){ b.phase=3; b.v.x=b.v.y=0; audio.thunk(); }
    }

    // 색상 업데이트 (임계값 기반)
    if(!b.blocked){
      const ratio = b.impact / Math.max(0.01, threshold);
      if(ratio >= 1.0) {
        b.color = '#000000'; // 검정 (차단)
        b.blocked = true;
      } else if(ratio >= 0.75) {
        b.color = '#1E1E1E'; // 거의 검정 (위험)
      } else if(ratio >= 0.5) {
        b.color = '#6A4A00'; // 어두운 갈색 (주의)
      } else {
        b.color = '#E8B500'; // 금색 (정상)
      }
    } else {
      b.color = '#000000'; // 차단된 구슬은 검정
    }
  }
}

function drawOnce(canvas, beads, layout, threshold, theme){
  if(!canvas) return; const ctx = canvas.getContext('2d'); const {W,H} = layout;
  ctx.clearRect(0,0,W,H); ctx.fillStyle=theme.canvas; ctx.fillRect(0,0,W,H);
  ctx.strokeStyle = theme.grid||'#F0F0F0'; ctx.lineWidth=1; for(let x=100;x<W;x+=100){ ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); } for(let y=100;y<H;y+=100){ ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }

  layout.inlets(Math.max(beads.length,1)).forEach((p,i)=>{ drawCircle(ctx,p.x,p.y,6,'#111'); drawText(ctx, `${i+1}`, p.x-18,p.y+4,'10','#666'); });
  layout.bins.forEach((b,i)=>{ drawRoundRect(ctx,b.x-28,b.y-26,56,52,8, theme.goldSoft, theme.border); drawText(ctx, `bin ${i+1}`, b.x-14,b.y+34,'10',theme.muted); });
  drawRoundRect(ctx,layout.router.x-44,layout.router.y-24,88,48,10, '#FFF2B0', theme.border); drawText(ctx,'Router', layout.router.x-18, layout.router.y+4,'11','#444');
  ctx.fillStyle = '#FFF3C6'; ctx.strokeStyle = theme.border; ctx.beginPath(); ctx.moveTo(layout.outlet.x-28, layout.outlet.y-28); ctx.arc(layout.outlet.x-28, layout.outlet.y,28,-Math.PI/2, Math.PI/2); ctx.lineTo(layout.outlet.x+10, layout.outlet.y); ctx.closePath(); ctx.fill(); ctx.stroke();

  for(const b of beads){
    const inletArr = layout.inlets(beads.length);
    const inlet = inletArr[beads.indexOf(b)] || inletArr[0];
    const midX = (inlet.x + b.tgt1.x)/2; const midY = (inlet.y + b.tgt1.y)/2 - 18;
    if(b.blocked){ ctx.setLineDash([6,6]); ctx.strokeStyle = '#ef4444'; ctx.lineWidth=2; } else { ctx.setLineDash([]); ctx.strokeStyle = '#F3C94B'; ctx.lineWidth=1.5; }
    ctx.beginPath(); ctx.moveTo(inlet.x, inlet.y); ctx.quadraticCurveTo(midX, midY, b.tgt1.x, b.tgt1.y); ctx.stroke();
    if(!b.blocked){ ctx.beginPath(); ctx.moveTo(b.tgt1.x+8, b.tgt1.y); ctx.lineTo(layout.router.x-10, layout.router.y); ctx.stroke(); ctx.beginPath(); ctx.moveTo(layout.router.x+10, layout.router.y); ctx.lineTo(layout.outlet.x-12, layout.outlet.y); ctx.stroke(); }
    if(b.blocked){ drawCircle(ctx, b.tgt1.x-12, b.tgt1.y-8, 6, '#000'); drawText(ctx, b.tattoo||'-', b.tgt1.x-15, b.tgt1.y-5,'9','#fff'); }
  }
  for(const b of beads){ drawCircle(ctx, b.p.x, b.p.y, b.r, b.blocked? '#000000' : b.color, 1.0, b.rotation || 0); }
  for(const b of beads){ if(!b.children || b.phase!==3) continue; const n=Math.min(b.children.length, 48); for(let k=0;k<n;k++){ const a=(2*Math.PI*k)/n, rr=b.r*0.55; const cx=b.p.x+Math.cos(a)*rr*0.7, cy=b.p.y+Math.sin(a)*rr*0.7; const ch=b.children[k]; const r = 2; const col = ch.blocked? '#000' : ( (ch.impact/Math.max(1e-4,b.thEff))>=0.5 ? '#6A4A00' : '#E8B500'); drawCircle(ctx, cx, cy, r, col, 0.9); } }
  drawBadge(ctx, 14, 14, `Threshold ${threshold.toFixed(2)}`);
}

/* ---------------- Picking + Metrics + Tooltip ---------------- */
function pickBead(beads,x,y){
  for(let i=beads.length-1;i>=0;i--){ const b=beads[i]; const dx=x-b.p.x, dy=y-b.p.y; if(dx*dx+dy*dy <= (b.r+4)*(b.r+4)) return b; }
  return null;
}
function calcMetrics(series, threshold){
  const total = series.length; const impacts = series.map(s=>s.impact||0); const sum = impacts.reduce((a,b)=>a+b,0); const avg = total? sum/total : 0; const mean = avg; const v = total? impacts.reduce((a,b)=>a+(b-mean)*(b-mean),0)/total : 0; const near = series.filter(s=>!s.blocked && (s.impact/Math.max(1e-6,threshold))>=0.5).length; const blocked = series.filter(s=> s.blocked || (s.impact/Math.max(1e-6,threshold))>=1).length; const meta = series.filter(s=>Array.isArray(s.children) && s.children.length>0).length; return { total, meta, sum, avg, var:v, blocked, near };
}
function tooltipLabel(b, threshold){
  const r = (b.impact/Math.max(1e-6,b.thEff)); const lines = [
    `id: ${b.id}`,
    `cat: ${b.cat}  layer: L${b.layer}`,
    `codon: ${b.codon}  weight: ${codonScale(b.codon).toFixed(2)}`,
    `impact: ${b.impact.toFixed(3)}  thEff: ${b.thEff.toFixed(2)}  rel: ${r.toFixed(2)}`,
    `state: ${b.blocked? 'BLOCKED':'OK'}  phase: ${b.phase}`,
    b.children? `children: ${b.children.length}`: null,
  ].filter(Boolean);
  return lines.join('\n');
}

/* ---------------- Layout helpers ---------------- */
function layoutCompute(W,H,PAD,binCount){
  // 세로 배치: 위에서 아래로 떨어지는 구조
  // Inlet(상단) → Bins → Router → Outlet(하단)

  const centerX = W / 2;
  const binSpacing = Math.min(120, (W - PAD * 4) / Math.max(1, binCount));
  const binStartX = centerX - (binCount * binSpacing) / 2 + binSpacing / 2;

  const inletY = PAD + 80;      // 상단
  const binsY = H * 0.35;       // 위에서 35% 위치
  const routerY = H * 0.6;      // 중간 60% 위치
  const outletY = H * 0.85;     // 하단 85% 위치

  // Bins: 가로로 정렬
  const bins = Array.from({length:binCount}).map((_,i)=>({
    x: binStartX + i * binSpacing,
    y: binsY
  }));

  // Router: 중간
  const router = { x: centerX, y: routerY };

  // Outlet: 하단
  const outlet = { x: centerX, y: outletY };

  // Inlets: 상단 (가로로 분산)
  const inlets = (n)=> Array.from({length:n}).map((_,i)=>({
    x: binStartX + (i % binCount) * binSpacing,
    y: inletY
  }));

  return { W,H,PAD, bins, router, outlet, inlets };
}

/* ---------------- Draw prims ---------------- */
function drawCircle(ctx,x,y,r,fill,alpha=1,rotation=0){
  ctx.save();
  ctx.globalAlpha=alpha;
  ctx.translate(x,y);
  if(rotation) ctx.rotate(rotation);

  // Gradient for 3D ball effect
  const grad = ctx.createRadialGradient(-r*0.3, -r*0.3, 0, 0, 0, r);
  grad.addColorStop(0, lightenColor(fill, 0.4));
  grad.addColorStop(0.7, fill);
  grad.addColorStop(1, darkenColor(fill, 0.3));
  ctx.fillStyle = grad;

  ctx.beginPath();
  ctx.arc(0,0,r,0,Math.PI*2);
  ctx.fill();

  // Rotation indicator (small dot)
  if(rotation){
    ctx.fillStyle = 'rgba(255,255,255,0.6)';
    ctx.beginPath();
    ctx.arc(r*0.6, 0, r*0.15, 0, Math.PI*2);
    ctx.fill();
  }

  ctx.restore();
}

function lightenColor(hex, factor){
  const num = parseInt(hex.slice(1), 16);
  const r = Math.min(255, ((num >> 16) & 255) + 255 * factor);
  const g = Math.min(255, ((num >> 8) & 255) + 255 * factor);
  const b = Math.min(255, (num & 255) + 255 * factor);
  return `rgb(${r},${g},${b})`;
}

function darkenColor(hex, factor){
  const num = parseInt(hex.slice(1), 16);
  const r = Math.max(0, ((num >> 16) & 255) * (1-factor));
  const g = Math.max(0, ((num >> 8) & 255) * (1-factor));
  const b = Math.max(0, (num & 255) * (1-factor));
  return `rgb(${r},${g},${b})`;
}
function drawText(ctx,txt,x,y,size,color){ ctx.save(); ctx.fillStyle=color; ctx.font=`${size}px ui-sans-serif`; ctx.fillText(txt,x,y); ctx.restore(); }
function drawRoundRect(ctx,x,y,w,h,r,fill,stroke){ ctx.save(); ctx.fillStyle=fill; ctx.strokeStyle=stroke; ctx.lineWidth=1; ctx.beginPath(); ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+h,r); ctx.arcTo(x+w,y+h,x,y+h,r); ctx.arcTo(x,y+h,x,y,r); ctx.arcTo(x,y,x+w,y,r); ctx.closePath(); ctx.fill(); ctx.stroke(); ctx.restore(); }
function drawBadge(ctx,x,y,label){ const pad=8; ctx.save(); ctx.font='12px ui-sans-serif'; const m=ctx.measureText(label); const w=m.width+pad*2; const h=22; drawRoundRect(ctx,x,y,w,h,10,'#FFF4C2','#E0E0E0'); ctx.fillStyle='#333'; ctx.fillText(label,x+pad,y+15); ctx.restore(); }

/* ---------------- Utility functions ---------------- */
function clamp01(x){ return Math.max(0, Math.min(1, x)); }

/* ---------------- Codon + Layer scaling ---------------- */
function codonIndex(c){
  if(!c||c.length<3) return 0; const s=c.toUpperCase(); const m={A:0,C:1,G:2,T:3}; const a=m[s[0]]??0, b=m[s[1]]??0, d=m[s[2]]??0; return a*16 + b*4 + d;
}
function codonScale(c){ const idx=codonIndex(c); return 1.0 + (idx/63)*0.6; }
function layerScale(L){ const k=[0,1.00,1.04,1.08,1.12,1.16,1.20,1.25]; return k[L]||1.0; }
function stageDarkness(s){ return s==='black'?1: s==='near'?0.9: s==='darkening'?0.66: 0; }
function toneColor(stage){ if(stage==='black') return '#000000'; if(stage==='near') return '#1E1E1E'; if(stage==='darkening') return '#6A4A00'; return '#E8B500'; }
function lerpColor(a,b,t){ t=Math.max(0,Math.min(1,t)); const pa=parseInt(a.slice(1),16), pb=parseInt(b.slice(1),16); const ar=(pa>>16)&255, ag=(pa>>8)&255, ab=pa&255; const br=(pb>>16)&255, bg=(pb>>8)&255, bb=pb&255; const rr=Math.round(ar+(br-ar)*t), gg=Math.round(ag+(bg-ag)*t), bb2=Math.round(ab+(bb-ab)*t); return `rgb(${rr},${gg},${bb2})`; }

/* ---------------- RNG ---------------- */
function mulberry32(a){ return function(){ var t=a+=0x6D2B79F5; t=Math.imul(t^t>>>15, t|1); t^=t+Math.imul(t^t>>>7, t|61); return ((t^t>>>14)>>>0)/4294967296; }; }

/* ---------------- Audio ---------------- */
function useAudio(){
  const ref = useRef({ ctx:null, enabled:false });
  const enable = ()=>{ if(ref.current.ctx){ ref.current.enabled=true; return; } try{ ref.current.ctx = new (window.AudioContext||window.webkitAudioContext)(); ref.current.enabled=true; }catch(e){ ref.current.enabled=false; } };
  const disable = ()=>{ ref.current.enabled=false; };
  const click = ()=>{ if(!ref.current.enabled||!ref.current.ctx) return; const ctx=ref.current.ctx; const o=ctx.createOscillator(); const g=ctx.createGain(); o.type='triangle'; o.frequency.value=880; g.gain.value=0.0001; o.connect(g); g.connect(ctx.destination); const t=ctx.currentTime; g.gain.exponentialRampToValueAtTime(0.05, t+0.01); g.gain.exponentialRampToValueAtTime(0.0001, t+0.08); o.start(t); o.stop(t+0.09); };
  const thunk = ()=>{ if(!ref.current.enabled||!ref.current.ctx) return; const ctx=ref.current.ctx; const o=ctx.createOscillator(); const g=ctx.createGain(); o.type='sine'; o.frequency.setValueAtTime(220, ctx.currentTime); g.gain.value=0.0001; o.connect(g); g.connect(ctx.destination); const t=ctx.currentTime; g.gain.exponentialRampToValueAtTime(0.12, t+0.02); g.gain.exponentialRampToValueAtTime(0.0001, t+0.25); o.frequency.exponentialRampToValueAtTime(140, t+0.25); o.start(t); o.stop(t+0.26); };
  const pour = (intensity=3)=>{ if(!ref.current.enabled||!ref.current.ctx) return; const ctx=ref.current.ctx; const buf=ctx.createBuffer(1, ctx.sampleRate*0.4, ctx.sampleRate); const data=buf.getChannelData(0); for(let i=0;i<data.length;i++){ data[i]=(Math.random()*2-1)*Math.exp(-i/(data.length/(2+intensity))); } const src=ctx.createBufferSource(); src.buffer=buf; const biquad=ctx.createBiquadFilter(); biquad.type='bandpass'; biquad.frequency.value=1000; const g=ctx.createGain(); g.gain.value=0.05; src.connect(biquad); biquad.connect(g); g.connect(ctx.destination); src.start(); };
  return { enable, disable, click, thunk, pour };
}

/* ---------------- Demo data ---------------- */
function demoCodon(i){ const bases=['A','C','G','T']; const a=bases[i%4], b=bases[(i>>2)%4], c=bases[(i>>4)%4]; return `${a}${b}${c}`; }
function makeDemoSeries(n){
  return Array.from({length:n}).map((_,i)=>({
    id:`s${i}`,
    impact: +(0.12 + Math.random()*0.55).toFixed(3),
    blocked: Math.random()<0.12,
    cat: i%4,
    layer: (i%7)+1,
    codon: demoCodon(i)
  }));
}

/* ---------------- Aggregation ---------------- */
function toMeta(series, binCount, factor){
  const byCat = new Map();
  series.forEach(s=>{ const c=Number.isFinite(s.cat)?s.cat:0; if(!byCat.has(c)) byCat.set(c,[]); byCat.get(c).push(s); });
  const metas=[]; for(const [cat, arr] of byCat){ for(let i=0;i<arr.length;i+=factor){ const chunk=arr.slice(i,i+factor); const impacts=chunk.map(x=>x.impact||0); const blocked=chunk.some(x=>x.blocked); const m = impacts.reduce((a,b)=>a+b,0)/Math.max(1,impacts.length); metas.push({ id:`m-${cat}-${i}`, cat, impact:m, blocked, children:chunk, layer:(cat%7)+1, codon: 'AAA' }); } }
  return metas;
}
