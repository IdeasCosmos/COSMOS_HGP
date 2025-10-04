import React, { useEffect, useState, useRef, useMemo } from 'react';

/**
 * COSMOS-HGP Complete Integration Dashboard
 * 7계층 구조 + DNA 코돈 + MetaBall + 실시간 WebSocket
 */

// ============================================================================
// COSMOS Bridge - Python 백엔드 연결
// ============================================================================

class CosmosBridge {
  constructor() {
    this.listeners = new Set();
    this.ws = null;
    this.connectionAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect(wsUrl = 'ws://localhost:5001') {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    try {
      // HTTP 연결 테스트 먼저
      fetch('http://localhost:5001/health')
        .then(response => response.json())
        .then(data => {
          console.log('Backend health check:', data);
          // 백엔드가 정상이면 WebSocket 연결 시도
          this.ws = new WebSocket(wsUrl);
          this.setupWebSocketEvents();
        })
        .catch(error => {
          console.error('Backend not available:', error);
          this.notify({ type: 'connection', status: 'error' });
        });
    } catch (e) {
      console.error('Connection failed:', e);
      this.notify({ type: 'connection', status: 'error' });
    }
  }

  setupWebSocketEvents() {
    if (!this.ws) return;
    
    this.ws.onopen = () => {
      console.log('✓ COSMOS Engine connected');
      this.connectionAttempts = 0;
      this.notify({ type: 'connection', status: 'connected' });
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.execution_result) {
          const beads = this.transformExecution(data.execution_result);
          this.notify({ type: 'execution', beads });
        }
      } catch (e) {
        console.error('Parse error:', e);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.notify({ type: 'connection', status: 'error' });
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.notify({ type: 'connection', status: 'disconnected' });
      this.attemptReconnect('ws://localhost:5001');
    };
  }

  attemptReconnect(wsUrl) {
    if (this.connectionAttempts >= this.maxReconnectAttempts) return;
    
    this.connectionAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.connectionAttempts), 30000);
    
    console.log(`Reconnecting in ${delay/1000}s (attempt ${this.connectionAttempts})`);
    setTimeout(() => this.connect(wsUrl), delay);
  }

  transformExecution(execution) {
    const { execution_path = [], metrics = {}, mode = 'stability' } = execution;
    
    return execution_path.map((step, i) => ({
      id: `exec_${Date.now()}_${i}`,
      impact: Math.max(0, Math.min(1, step.impact || 0.1)),
      blocked: step.status === 'BLOCKED',
      cat: (step.layer_number - 1) % 7,
      layer: step.layer_number,
      codon: step.codon || 'AAA',
      ruleName: step.rule,
      threshold: step.threshold || 0.33,
      mode,
      status: step.status,
      timestamp: Date.now()
    }));
  }

  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  notify(data) {
    this.listeners.forEach(cb => cb(data));
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  async executeRemote(group, input, mode = 'stability') {
    try {
      const response = await fetch('http://localhost:5000/api/cosmos/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ group, input, profile: mode })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (e) {
      console.error('Remote execution failed:', e);
      throw e;
    }
  }
}

// ============================================================================
// BeadFlow Physics Engine
// ============================================================================

class BeadFlowPhysics {
  constructor(layout, threshold) {
    this.layout = layout;
    this.threshold = threshold;
    this.beads = [];
  }

  initBeads(series) {
    this.beads = series.map((s, i) => this.createBead(s, i, series.length));
    return this.beads;
  }

  createBead(item, index, total) {
    const cat = item.cat ?? (index % 7);
    const layer = item.layer ?? ((cat % 7) + 1);
    const impact = Math.max(0, Math.min(1, item.impact ?? 0.1));
    const blocked = item.blocked || (impact / Math.max(0.01, this.threshold)) >= 1;
    
    const baseRadius = 4.0;
    const impactScale = 0.9 + impact * 0.6;
    const radius = baseRadius * impactScale;

    const inlets = this.layout.inlets(total);
    const startPos = inlets[index] || inlets[0];

    return {
      id: item.id || `b${index}`,
      cat, layer, impact, blocked,
      stage: blocked ? 'black' : impact / this.threshold >= 0.75 ? 'near' : 'gold',
      threshold: this.threshold,
      r: radius,
      p: { x: startPos.x, y: startPos.y },
      v: { x: 0, y: 0 },
      phase: 0,
      jitter: 0.5 + Math.random() * 0.75,
      ruleName: item.ruleName,
      status: item.status,
      mode: item.mode
    };
  }

  step() {
    const { bins, router, outlet } = this.layout;
    
    for (const bead of this.beads) {
      if (bead.phase >= 3) continue;

      const target = bead.phase === 0 ? bins[bead.cat] :
                     bead.phase === 1 ? router : outlet;

      const dx = target.x - bead.p.x;
      const dy = target.y - bead.p.y;
      const ax = dx * 0.010 * bead.jitter;
      const ay = dy * 0.010 * bead.jitter + (bead.phase === 2 ? 0.15 : 0.06);

      bead.v.x = (bead.v.x + ax) * 0.965;
      bead.v.y = (bead.v.y + ay) * 0.965;
      bead.p.x += bead.v.x;
      bead.p.y += bead.v.y;

      // Phase transitions
      const distance = Math.hypot(target.x - bead.p.x, target.y - bead.p.y);
      if (distance < Math.max(8, bead.r * 0.6)) {
        if (bead.phase === 0) {
          if (bead.blocked) {
            bead.phase = 3;
            bead.v.x = bead.v.y = 0;
          } else {
            bead.phase = 1;
          }
        } else if (bead.phase === 1) {
          bead.phase = 2;
        } else if (bead.phase === 2) {
          bead.phase = 3;
        }
      }
    }
  }
}

// ============================================================================
// Main Dashboard Component
// ============================================================================

export default function CosmosBeadFlowDashboard() {
  // State management
  const [series, setSeries] = useState(makeDemoSeries(32));
  const [engineStatus, setEngineStatus] = useState('disconnected');
  const [stats, setStats] = useState({
    executions: 0,
    cascades: 0,
    mode: 'stability',
    avgImpact: 0
  });
  
  // Configuration
  const [threshold, setThreshold] = useState(0.33);
  const [binCount, setBinCount] = useState(7);
  const [running, setRunning] = useState(true);
  const [mode, setMode] = useState('stability');

  // Refs
  const canvasRef = useRef(null);
  const bridgeRef = useRef(null);
  const physicsRef = useRef(null);
  const rafRef = useRef(0);

  // Layout computation - 반응형으로 변경
  const canvasRef2 = useRef(null);
  const [dimensions, setDimensions] = useState({ W: 1400, H: 700 });
  const PAD = 20;
  const layout = useMemo(() => computeLayout(dimensions.W, dimensions.H, PAD, binCount), [dimensions.W, dimensions.H, PAD, binCount]);

  // 캔버스 크기 조정
  useEffect(() => {
    const resizeCanvas = () => {
      if (canvasRef.current) {
        const rect = canvasRef.current.getBoundingClientRect();
        const newW = Math.max(800, rect.width);
        const newH = Math.max(400, rect.height);
        setDimensions({ W: newW, H: newH });
        
        canvasRef.current.width = newW;
        canvasRef.current.height = newH;
      }
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    return () => window.removeEventListener('resize', resizeCanvas);
  }, []);

  // Initialize bridge
  useEffect(() => {
    bridgeRef.current = new CosmosBridge();
    
    const unsubscribe = bridgeRef.current.subscribe((message) => {
      if (message.type === 'connection') {
        setEngineStatus(message.status);
      } else if (message.type === 'execution') {
        setSeries(prev => [...prev, ...message.beads].slice(-200));
        setStats(prev => ({
          ...prev,
          executions: prev.executions + message.beads.length,
          cascades: prev.cascades + message.beads.filter(b => b.blocked).length
        }));
      }
    });

    bridgeRef.current.connect();

    return () => {
      unsubscribe();
      bridgeRef.current.disconnect();
    };
  }, []);

  // Initialize physics
  useEffect(() => {
    physicsRef.current = new BeadFlowPhysics(layout, threshold);
    physicsRef.current.initBeads(series);
    drawFrame(canvasRef.current, physicsRef.current.beads, layout, threshold);
  }, [series, threshold, layout]);

  // Animation loop
  useEffect(() => {
    if (!running) return;
    
    const loop = () => {
      if (physicsRef.current) {
        physicsRef.current.step();
        drawFrame(canvasRef.current, physicsRef.current.beads, layout, threshold);
      }
      rafRef.current = requestAnimationFrame(loop);
    };
    
    rafRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(rafRef.current);
  }, [running, layout, threshold]);

  // Remote execution
  const executeRemote = async () => {
    try {
      const input = Array.from({ length: 10 }, () => Math.random() * 10);
      
      // 백엔드가 연결되어 있으면 원격 실행
      if (bridgeRef.current && engineStatus === 'connected') {
        await bridgeRef.current.executeRemote('standard_pipeline', input, mode);
      } else {
        // 백엔드 연결이 없으면 로컬 데모 실행
        console.log('Backend not connected, running demo execution');
        const newBeads = makeDemoSeries(8).map(bead => ({
          ...bead,
          mode,
          timestamp: Date.now()
        }));
        setSeries(prev => [...prev, ...newBeads].slice(-200));
        setStats(prev => ({
          ...prev,
          executions: prev.executions + newBeads.length,
          cascades: prev.cascades + newBeads.filter(b => b.blocked).length
        }));
      }
    } catch (e) {
      console.error('Execution failed:', e);
      // 오류 시에도 데모 데이터로 대체
      const newBeads = makeDemoSeries(8);
      setSeries(prev => [...prev, ...newBeads].slice(-200));
    }
  };

  return (
    <div className="flex h-screen w-full flex-col bg-white">
      {/* Header */}
      <header className="flex items-center justify-between border-b px-6 py-4">
        <div className="flex items-center gap-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-yellow-400 to-orange-500">
            <span className="text-lg font-bold text-black">⚛</span>
          </div>
          <div>
            <h1 className="text-xl font-bold">COSMOS-HGP Executive Dashboard</h1>
            <p className="text-xs text-gray-600">Hierarchical Gradient Propagation • Duality Architecture</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <span className={`rounded-full px-3 py-1 text-xs font-medium ${
            engineStatus === 'connected' ? 'bg-green-100 text-green-800' :
            engineStatus === 'error' ? 'bg-red-100 text-red-800' :
            'bg-gray-100 text-gray-600'
          }`}>
            {engineStatus === 'connected' ? '● Connected' :
             engineStatus === 'error' ? '● Error' :
             '○ Offline'}
          </span>
          
          <span className="rounded-full border px-3 py-1 text-xs bg-gray-50">
            {mode.charAt(0).toUpperCase() + mode.slice(1)} Mode
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={executeRemote}
            className="rounded-lg px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600"
          >
            Execute
          </button>
      </div>
      </header>
      
      {/* Control Panel */}
      <div className="flex items-center gap-4 border-b px-6 py-3 bg-yellow-50">
        <label className="flex items-center gap-2 text-sm">
          <span>Mode</span>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            className="rounded-md border px-2 py-1"
          >
          <option value="stability">Stability</option>
          <option value="innovation">Innovation</option>
          <option value="adaptive">Adaptive</option>
        </select>
        </label>
        
        <label className="flex items-center gap-2 text-sm">
          <span>Threshold</span>
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-32"
          />
          <span>{threshold.toFixed(2)}</span>
        </label>
        
        <label className="flex items-center gap-2 text-sm">
          <span>Layers</span>
          <input
            type="range"
            min={1}
            max={7}
            value={binCount}
            onChange={(e) => setBinCount(parseInt(e.target.value))}
            className="w-24"
          />
          <span>{binCount}</span>
        </label>
        
        <div className="ml-auto flex items-center gap-4 text-xs text-gray-600">
          <span>Beads: <strong>{series.length}</strong></span>
          <span>Executions: <strong>{stats.executions}</strong></span>
          <span>Cascades: <strong>{stats.cascades}</strong></span>
        </div>
      </div>
      
      {/* Canvas */}
      <div className="relative flex-1 bg-gray-50">
        <canvas 
          ref={canvasRef} 
          width={dimensions.W} 
          height={dimensions.H} 
          className="h-full w-full block mx-auto"
          style={{ 
            maxWidth: '100%', 
            maxHeight: '100%',
            objectFit: 'contain'
          }}
        />
        
        {!running && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-20">
            <button
              onClick={() => setRunning(true)}
              className="rounded-full bg-white px-8 py-4 text-lg font-medium shadow-lg"
            >
              ▶ Resume
            </button>
          </div>
        )}
      </div>
      
      {/* Footer */}
      <footer className="flex items-center justify-between border-t px-6 py-3">
        <div className="flex items-center gap-4 text-xs text-gray-600">
          <span>v2.0.0</span>
          <span>•</span>
          <span>7 Layers • 64 Codons • 3 Modes</span>
          <span>•</span>
          <span>Last update: {new Date().toLocaleTimeString()}</span>
        </div>
        
        <button
          onClick={() => setRunning(v => !v)}
          className="rounded-md border px-3 py-1 text-xs"
        >
          {running ? 'Pause' : 'Play'}
        </button>
      </footer>
    </div>
  );
}

// ============================================================================
// Drawing Functions
// ============================================================================

function drawFrame(canvas, beads, layout, threshold) {
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const { W, H } = layout;
  
  // Clear
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = '#FFFFFF';
  ctx.fillRect(0, 0, W, H);
  
  // Grid
  ctx.strokeStyle = '#F5F5F5';
  ctx.lineWidth = 1;
  for (let x = 100; x < W; x += 100) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, H);
    ctx.stroke();
  }
  for (let y = 100; y < H; y += 100) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(W, y);
    ctx.stroke();
  }
  
  // Infrastructure
  drawInfrastructure(ctx, layout);
  
  // Paths
  drawPaths(ctx, beads, layout);
  
  // Beads
  for (const bead of beads) {
    const color = bead.blocked ? '#000000' : getBeadColor(bead, threshold);
    drawCircle(ctx, bead.p.x, bead.p.y, bead.r, color, 0.96);
  }
  
  // Badge
  drawBadge(ctx, 16, 16, `Threshold ${threshold.toFixed(2)}`);
}

function drawInfrastructure(ctx, layout) {
  // 7개 레이어 빈
  layout.bins.forEach((bin, i) => {
    drawRoundRect(ctx, bin.x - 30, bin.y - 28, 60, 56, 10, '#FFF7D6', '#E0E0E0');
    drawText(ctx, `L${i + 1}`, bin.x - 8, bin.y + 4, '12px', '#444');
  });
  
  // 라우터
  const r = layout.router;
  drawRoundRect(ctx, r.x - 48, r.y - 26, 96, 52, 12, '#FFF2B0', '#E0E0E0');
  drawText(ctx, 'Router', r.x - 22, r.y + 4, '12px', '#444');
  
  // 아웃렛
  const o = layout.outlet;
  ctx.fillStyle = '#FFF3C6';
  ctx.strokeStyle = '#E0E0E0';
  ctx.beginPath();
  ctx.moveTo(o.x - 30, o.y - 30);
  ctx.arc(o.x - 30, o.y, 30, -Math.PI / 2, Math.PI / 2);
  ctx.lineTo(o.x + 12, o.y);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
}

function drawPaths(ctx, beads, layout) {
  for (const bead of beads) {
    const bin = layout.bins[bead.cat];
    const router = layout.router;
    const outlet = layout.outlet;
    
    if (bead.blocked) {
      ctx.setLineDash([6, 6]);
      ctx.strokeStyle = '#ef4444';
    } else {
      ctx.setLineDash([]);
      ctx.strokeStyle = '#F3C94B';
    }
    
    ctx.lineWidth = 1.5;
    ctx.globalAlpha = 0.3;
    
    ctx.beginPath();
    ctx.moveTo(bin.x, bin.y);
    ctx.lineTo(router.x - 10, router.y);
    ctx.stroke();
    
    if (!bead.blocked) {
      ctx.beginPath();
      ctx.moveTo(router.x + 10, router.y);
      ctx.lineTo(outlet.x - 12, outlet.y);
      ctx.stroke();
    }
    
    ctx.globalAlpha = 1.0;
    ctx.setLineDash([]);
  }
}

function getBeadColor(bead, threshold) {
  const ratio = bead.impact / Math.max(0.01, threshold);
  if (ratio >= 0.75) return '#1E1E1E';
  if (ratio >= 0.5) return '#6A4A00';
  return '#E8B500';
}

// ============================================================================
// Utility Functions
// ============================================================================

function computeLayout(W, H, PAD, binCount) {
  const bins = Array.from({ length: binCount }).map((_, i) => ({
    x: Math.floor(W / 3) + i * Math.min(120, (W - 360) / Math.max(1, binCount - 1)),
    y: Math.floor(H / 2) + (i % 2 ? 48 : -48)
  }));
  
  const router = { x: Math.floor(W / 2) + 180, y: Math.floor(H / 2) };
  const outlet = { x: W - 120, y: Math.floor(H / 2) };
  const inlets = (n) => Array.from({ length: n }).map((_, i) => ({
    x: PAD + 60,
    y: PAD + 60 + i * 28
  }));
  
  return { W, H, PAD, bins, router, outlet, inlets };
}

function drawCircle(ctx, x, y, r, fill, alpha = 1) {
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.fillStyle = fill;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawText(ctx, text, x, y, font, color) {
  ctx.save();
  ctx.font = font + ' ui-sans-serif';
  ctx.fillStyle = color;
  ctx.fillText(text, x, y);
  ctx.restore();
}

function drawRoundRect(ctx, x, y, w, h, r, fill, stroke) {
  ctx.save();
  ctx.fillStyle = fill;
  ctx.strokeStyle = stroke;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  ctx.restore();
}

function drawBadge(ctx, x, y, label) {
  ctx.save();
  ctx.font = '11px ui-sans-serif';
  const m = ctx.measureText(label);
  const w = m.width + 16;
  drawRoundRect(ctx, x, y, w, 20, 10, '#FFF4C2', '#E0E0E0');
  ctx.fillStyle = '#333';
  ctx.fillText(label, x + 8, y + 14);
  ctx.restore();
}

function makeDemoSeries(n) {
  return Array.from({ length: n }).map((_, i) => ({
    id: `demo_${i}`,
    impact: +(0.08 + Math.random() * 0.6).toFixed(3),
    blocked: Math.random() < 0.15,
    cat: i % 7,
    layer: (i % 7) + 1,
    codon: generateCodon(i)
  }));
}

function generateCodon(i) {
  const bases = ['A', 'C', 'G', 'T'];
  return bases[i % 4] + bases[(i >> 2) % 4] + bases[(i >> 4) % 4];
}