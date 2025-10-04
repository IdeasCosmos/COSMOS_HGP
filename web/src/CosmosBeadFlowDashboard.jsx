import React, { useEffect, useState, useRef, useMemo, useCallback } from 'react';

/**
 * COSMOS-HGP Complete Integration
 * Philosophy: Unifying Order (threshold control) and Chaos (butterfly effects)
 * - 7-Layer Hierarchy: Quantum → Atomic → Molecular → Compound → Organic → Ecosystem → Cosmos
 * - 3 Operational Modes: Stability (order preservation), Innovation (chaos exploration), Adaptive (dynamic balance)
 * - Codon-based DNA encoding: 64 codons mapping to different operation types
 * - MetaBall aggregation: Hierarchical grouping showing macro from micro
 * - Real-time WebSocket streaming from Python COSMOS engine
 * - Executive dashboard with full control and monitoring
 */

// ============================================================================
// COSMOS Bridge - Connects Python backend to React frontend
// ============================================================================

class CosmosBridge {
  constructor() {
    this.listeners = new Set();
    this.ws = null;
    this.reconnectInterval = null;
    this.connectionAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect(wsUrl = 'ws://localhost:5000/socket.io/?EIO=4&transport=websocket') {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    try {
      this.ws = new WebSocket(wsUrl);
      
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
        this.attemptReconnect(wsUrl);
      };
    } catch (e) {
      console.error('Connection failed:', e);
      this.notify({ type: 'connection', status: 'error' });
    }
  }

  attemptReconnect(wsUrl) {
    if (this.connectionAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached');
      return;
    }

    this.connectionAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.connectionAttempts), 30000);
    
    console.log(`Reconnecting in ${delay/1000}s (attempt ${this.connectionAttempts})`);
    
    setTimeout(() => this.connect(wsUrl), delay);
  }

  transformExecution(execution) {
    const { execution_path = [], metrics = {}, mode = 'stability' } = execution;
    
    return execution_path.map((step, i) => {
      const layerNum = this.layerNameToNumber(step.layer);
      const impact = typeof step.impact === 'number' ? step.impact : 0.1;
      const blocked = step.status === 'BLOCKED' || step.status === 'CASCADE_BLOCKED';
      
      return {
        id: `exec_${Date.now()}_${i}`,
        impact: Math.max(0, Math.min(1, impact)),
        blocked,
        cat: (layerNum - 1) % 7,
        layer: layerNum,
        codon: this.ruleToCodon(step.rule || 'unknown'),
        ruleName: step.rule,
        threshold: step.threshold || 0.33,
        mode,
        status: step.status,
        timestamp: Date.now()
      };
    });
  }

  layerNameToNumber(name) {
    const map = {
      'Quantum': 1, 'Atomic': 2, 'Molecular': 3, 'Compound': 4,
      'Organic': 5, 'Ecosystem': 6, 'Cosmos': 7
    };
    return map[name] || 1;
  }

  ruleToCodon(ruleName) {
    let hash = 0;
    for (let i = 0; i < ruleName.length; i++) {
      hash = ((hash << 5) - hash) + ruleName.charCodeAt(i);
      hash = hash & hash;
    }
    const bases = ['A', 'C', 'G', 'T'];
    const a = bases[Math.abs(hash) % 4];
    const b = bases[Math.abs(hash >> 2) % 4];
    const c = bases[Math.abs(hash >> 4) % 4];
    return `${a}${b}${c}`;
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
    if (this.reconnectInterval) {
      clearInterval(this.reconnectInterval);
    }
  }

  async executeRemote(group, input, mode = 'stability') {
    try {
      const response = await fetch('http://localhost:5000/api/cosmos/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer demo-token'
        },
        body: JSON.stringify({
          group,
          input: Array.isArray(input) ? input : [input],
          profile: mode,
          options: {
            predict_risk: true,
            return_annotations: true,
            return_telemetry: true
          }
        })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const result = await response.json();
      return result;
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

  initBeads(series, aggregate, metaFactor) {
    const data = aggregate ? this.aggregateToMeta(series, metaFactor) : series;
    this.beads = data.map((s, i) => this.createBead(s, i, data.length));
    return this.beads;
  }

  createBead(item, index, total) {
    const cat = item.cat ?? (index % 7);
    const layer = item.layer ?? ((cat % 7) + 1);
    const impact = Math.max(0, Math.min(1, item.impact ?? 0.1));
    const blocked = item.blocked || (impact / Math.max(0.01, this.threshold)) >= 1;
    
    const baseRadius = 4.0;
    const codonScale = this.getCodonScale(item.codon);
    const layerScale = this.getLayerScale(layer);
    const impactScale = 0.9 + impact * 0.6;
    const radius = baseRadius * codonScale * layerScale * impactScale;

    const inlets = this.layout.inlets(total);
    const startPos = inlets[index] || inlets[0];

    const ratio = impact / Math.max(0.01, this.threshold);
    const stage = blocked ? 'black' : ratio >= 0.75 ? 'near' : ratio >= 0.5 ? 'darkening' : 'gold';

    return {
      id: item.id || `b${index}`,
      cat, layer, impact, blocked, codon: item.codon || 'AAA',
      stage, threshold: this.threshold,
      r: radius,
      children: item.children,
      p: { x: startPos.x, y: startPos.y },
      v: { x: 0, y: 0 },
      phase: 0,
      jitter: 0.5 + Math.random() * 0.75,
      tattoo: blocked ? `-${index + 1}` : null,
      ruleName: item.ruleName,
      status: item.status,
      mode: item.mode
    };
  }

  getCodonScale(codon) {
    if (!codon || codon.length < 3) return 1.0;
    const bases = { A: 0, C: 1, G: 2, T: 3 };
    const a = bases[codon[0]] ?? 0;
    const b = bases[codon[1]] ?? 0;
    const c = bases[codon[2]] ?? 0;
    const index = a * 16 + b * 4 + c;
    return 1.0 + (index / 63) * 0.6;
  }

  getLayerScale(layer) {
    const scales = [0, 1.00, 1.04, 1.08, 1.12, 1.16, 1.20, 1.25];
    return scales[layer] || 1.0;
  }

  aggregateToMeta(series, factor) {
    const byCat = new Map();
    series.forEach(s => {
      const cat = s.cat ?? 0;
      if (!byCat.has(cat)) byCat.set(cat, []);
      byCat.get(cat).push(s);
    });

    const metas = [];
    for (const [cat, items] of byCat) {
      for (let i = 0; i < items.length; i += factor) {
        const chunk = items.slice(i, i + factor);
        const impacts = chunk.map(x => x.impact ?? 0);
        const avgImpact = impacts.reduce((a, b) => a + b, 0) / Math.max(1, impacts.length);
        const anyBlocked = chunk.some(x => x.blocked);
        
        metas.push({
          id: `meta_${cat}_${i}`,
          cat,
          layer: (cat % 7) + 1,
          impact: avgImpact,
          blocked: anyBlocked,
          codon: 'AAA',
          children: chunk
        });
      }
    }
    
    return metas;
  }

  step(audio) {
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

      // Collision detection
      for (const other of this.beads) {
        if (other === bead || other.phase !== bead.phase) continue;
        
        const dx = bead.p.x - other.p.x;
        const dy = bead.p.y - other.p.y;
        const dist2 = dx * dx + dy * dy;
        const minDist = bead.r + other.r + 2;
        
        if (dist2 > 0 && dist2 < minDist * minDist) {
          const dist = Math.sqrt(dist2);
          const nx = dx / dist;
          const ny = dy / dist;
          const push = (minDist - dist) * 0.35;
          
          bead.p.x += nx * push;
          bead.p.y += ny * push;
          other.p.x -= nx * push;
          other.p.y -= ny * push;
          
          if (audio.enabled && Math.random() < 0.02) audio.click();
        }
      }

      // Phase transitions
      const distance = Math.hypot(target.x - bead.p.x, target.y - bead.p.y);
      if (distance < Math.max(8, bead.r * 0.6)) {
        if (bead.phase === 0) {
          if (bead.blocked) {
            bead.phase = 3;
            bead.v.x = bead.v.y = 0;
            if (audio.enabled) audio.thunk();
          } else {
            bead.phase = 1;
            if (audio.enabled) audio.pour(2);
          }
        } else if (bead.phase === 1) {
          bead.phase = 2;
        } else if (bead.phase === 2) {
          bead.phase = 3;
          if (audio.enabled) audio.thunk();
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
    avgImpact: 0,
    totalImpact: 0
  });
  
  // Configuration
  const [threshold, setThreshold] = useState(0.33);
  const [binCount, setBinCount] = useState(7);
  const [aggregate, setAggregate] = useState(true);
  const [metaFactor, setMetaFactor] = useState(10);
  const [soundOn, setSoundOn] = useState(false);
  const [running, setRunning] = useState(true);
  const [mode, setMode] = useState('stability');
  
  // UI state
  const [hoverInfo, setHoverInfo] = useState(null);
  const [selectedBead, setSelectedBead] = useState(null);
  const [showControls, setShowControls] = useState(true);

  // Refs
  const canvasRef = useRef(null);
  const bridgeRef = useRef(null);
  const physicsRef = useRef(null);
  const audioRef = useRef(null);
  const rafRef = useRef(0);

  // Layout computation
  const W = 1400, H = 700, PAD = 20;
  const layout = useMemo(() => computeLayout(W, H, PAD, binCount), [W, H, PAD, binCount]);
  const theme = GOLD_WHITE_THEME;

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

    // Try to connect (will gracefully fail if backend not running)
    bridgeRef.current.connect();

    return () => {
      unsubscribe();
      bridgeRef.current.disconnect();
    };
  }, []);

  // Initialize audio
  useEffect(() => {
    audioRef.current = createAudio();
    if (soundOn) audioRef.current.enable();
    else audioRef.current.disable();
  }, [soundOn]);

  // Initialize physics
  useEffect(() => {
    if (!physicsRef.current || physicsRef.current.threshold !== threshold) {
      physicsRef.current = new BeadFlowPhysics(layout, threshold);
    }
    
    physicsRef.current.initBeads(series, aggregate, metaFactor);
    drawFrame(canvasRef.current, physicsRef.current.beads, layout, threshold, theme);
    
    // Update stats
    const impacts = series.map(s => s.impact ?? 0);
    const sum = impacts.reduce((a, b) => a + b, 0);
    setStats(prev => ({
      ...prev,
      avgImpact: impacts.length ? sum / impacts.length : 0,
      totalImpact: sum
    }));
  }, [series, threshold, layout, aggregate, metaFactor, theme]);

  // Animation loop
  useEffect(() => {
    if (!running) return;
    
    const loop = () => {
      if (physicsRef.current && audioRef.current) {
        physicsRef.current.step(audioRef.current);
        drawFrame(canvasRef.current, physicsRef.current.beads, layout, threshold, theme);
      }
      rafRef.current = requestAnimationFrame(loop);
    };
    
    rafRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(rafRef.current);
  }, [running, layout, threshold, theme]);

  // Mouse interaction
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const handleMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = (e.clientX - rect.left) * (canvas.width / rect.width);
      const y = (e.clientY - rect.top) * (canvas.height / rect.height);
      
      const bead = findBeadAt(physicsRef.current?.beads || [], x, y);
      if (bead) {
        setHoverInfo({
          x: e.clientX,
          y: e.clientY,
          bead
        });
      } else {
        setHoverInfo(null);
      }
    };

    const handleClick = (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = (e.clientX - rect.left) * (canvas.width / rect.width);
      const y = (e.clientY - rect.top) * (canvas.height / rect.height);
      
      const bead = findBeadAt(physicsRef.current?.beads || [], x, y);
      setSelectedBead(bead);
    };

    canvas.addEventListener('mousemove', handleMove);
    canvas.addEventListener('click', handleClick);
    canvas.addEventListener('mouseleave', () => setHoverInfo(null));

    return () => {
      canvas.removeEventListener('mousemove', handleMove);
      canvas.removeEventListener('click', handleClick);
      canvas.removeEventListener('mouseleave', () => setHoverInfo(null));
    };
  }, []);

  // Remote execution
  const executeRemote = async () => {
    if (!bridgeRef.current) return;
    
    try {
      const input = Array.from({ length: 10 }, () => Math.random() * 10);
      await bridgeRef.current.executeRemote('standard_pipeline', input, mode);
    } catch (e) {
      console.error('Execution failed:', e);
      // Fall back to demo data
      const newBeads = makeDemoSeries(8);
      setSeries(prev => [...prev, ...newBeads].slice(-200));
    }
  };

  // Export functions
  const exportPNG = () => {
    const url = canvasRef.current.toDataURL('image/png');
    downloadFile(url, `cosmos_${Date.now()}.png`);
  };

  const exportJSON = () => {
    const data = {
      series,
      config: { threshold, binCount, aggregate, metaFactor, mode },
      stats,
      timestamp: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    downloadFile(URL.createObjectURL(blob), `cosmos_${Date.now()}.json`);
  };

  const clearData = () => {
    setSeries([]);
    setStats({
      executions: 0,
      cascades: 0,
      mode,
      avgImpact: 0,
      totalImpact: 0
    });
  };

  return (
    <div className="flex h-screen w-full flex-col" style={{ background: theme.bg }}>
      {/* Header */}
      <header className="flex items-center justify-between border-b px-6 py-4" 
              style={{ borderColor: theme.border, background: theme.header }}>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full" 
                 style={{ background: theme.goldGrad }}>
              <span className="text-lg font-bold" style={{ color: '#1a1a1a' }}>⚛</span>
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: theme.text }}>
                COSMOS-HGP Executive Dashboard
              </h1>
              <p className="text-xs" style={{ color: theme.muted }}>
                Hierarchical Gradient Propagation • Duality Architecture
              </p>
            </div>
          </div>
          
          <div className="ml-4 flex items-center gap-2">
            <span className={`rounded-full px-3 py-1 text-xs font-medium ${
              engineStatus === 'connected' ? 'bg-green-100 text-green-800' :
              engineStatus === 'error' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-600'
            }`}>
              {engineStatus === 'connected' ? '● Connected' :
               engineStatus === 'error' ? '● Error' :
               '○ Offline'}
            </span>
            
            <span className="rounded-full border px-3 py-1 text-xs"
                  style={{ borderColor: theme.border, background: theme.surface }}>
              {mode.charAt(0).toUpperCase() + mode.slice(1)} Mode
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setSoundOn(v => !v)}
            className="rounded-lg border px-3 py-2 text-sm hover:bg-gray-50"
            style={{ borderColor: theme.border }}
          >
            {soundOn ? '🔊' : '🔇'}
          </button>
          
          <button
            onClick={executeRemote}
            className="rounded-lg px-4 py-2 text-sm font-medium text-white"
            style={{ background: 'linear-gradient(135deg, #FFD700, #FFA500)' }}
          >
            Execute
          </button>
          
          <button
            onClick={exportPNG}
            className="rounded-lg border px-4 py-2 text-sm hover:bg-gray-50"
            style={{ borderColor: theme.border }}
          >
            PNG
          </button>
          
          <button
            onClick={exportJSON}
            className="rounded-lg border px-4 py-2 text-sm hover:bg-gray-50"
            style={{ borderColor: theme.border }}
          >
            JSON
          </button>
          
          <button
            onClick={clearData}
            className="rounded-lg border px-4 py-2 text-sm hover:bg-gray-50"
            style={{ borderColor: theme.border, color: '#ef4444' }}
          >
            Clear
          </button>
        </div>
      </header>

      {/* Control Panel */}
      {showControls && (
        <div className="flex flex-wrap items-center gap-4 border-b px-6 py-3"
             style={{ borderColor: theme.border, background: theme.toolbar }}>
          <label className="flex items-center gap-2 text-sm">
            <span style={{ color: theme.text }}>Mode</span>
            <select
              value={mode}
              onChange={e => setMode(e.target.value)}
              className="rounded-md border px-2 py-1"
              style={{ borderColor: theme.border, background: theme.surface }}
            >
              <option value="stability">Stability</option>
              <option value="innovation">Innovation</option>
              <option value="adaptive">Adaptive</option>
            </select>
          </label>

          <label className="flex items-center gap-2 text-sm">
            <span style={{ color: theme.text }}>Threshold</span>
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={threshold}
              onChange={e => setThreshold(parseFloat(e.target.value))}
              className="w-32"
            />
            <span style={{ color: theme.text }}>{threshold.toFixed(2)}</span>
          </label>

          <label className="flex items-center gap-2 text-sm">
            <span style={{ color: theme.text }}>Layers</span>
            <input
              type="range"
              min={1}
              max={7}
              value={binCount}
              onChange={e => setBinCount(parseInt(e.target.value))}
              className="w-24"
            />
            <span style={{ color: theme.text }}>{binCount}</span>
          </label>

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={aggregate}
              onChange={e => setAggregate(e.target.checked)}
            />
            <span style={{ color: theme.text }}>MetaBall</span>
          </label>

          {aggregate && (
            <label className="flex items-center gap-2 text-sm">
              <span style={{ color: theme.text }}>Factor</span>
              <input
                type="number"
                min={2}
                max={32}
                value={metaFactor}
                onChange={e => setMetaFactor(parseInt(e.target.value) || 10)}
                className="w-16 rounded-md border px-2 py-1"
                style={{ borderColor: theme.border, background: theme.surface }}
              />
            </label>
          )}

          <div className="ml-auto flex items-center gap-4 text-xs" style={{ color: theme.muted }}>
            <span>Beads: <strong>{series.length}</strong></span>
            <span>Executions: <strong>{stats.executions}</strong></span>
            <span>Cascades: <strong>{stats.cascades}</strong></span>
            <span>Avg Impact: <strong>{stats.avgImpact.toFixed(3)}</strong></span>
          </div>

          <button
            onClick={() => setShowControls(false)}
            className="text-xs" style={{ color: theme.muted }}
          >
            Hide ▲
          </button>
        </div>
      )}

      {!showControls && (
        <div className="border-b px-6 py-2" style={{ borderColor: theme.border, background: theme.toolbar }}>
          <button
            onClick={() => setShowControls(true)}
            className="text-xs" style={{ color: theme.muted }}
          >
            Show Controls ▼
          </button>
        </div>
      )}

      {/* Canvas */}
      <div className="relative flex-1" style={{ background: theme.canvas }}>
        <canvas ref={canvasRef} width={W} height={H} className="h-full w-full" />
        
        {/* Tooltip */}
        {hoverInfo && (
          <div
            style={{
              position: 'fixed',
              left: hoverInfo.x + 12,
              top: hoverInfo.y + 12,
              background: 'white',
              border: `1px solid ${theme.border}`,
              borderRadius: 8,
              padding: 10,
              fontSize: 11,
              lineHeight: 1.5,
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
              maxWidth: 280,
              zIndex: 1000
            }}
          >
            <div style={{ fontWeight: 600, marginBottom: 4 }}>{hoverInfo.bead.id}</div>
            <div style={{ color: '#666' }}>
              <div>Layer L{hoverInfo.bead.layer} • Cat {hoverInfo.bead.cat}</div>
              <div>Codon: {hoverInfo.bead.codon}</div>
              <div>Impact: {hoverInfo.bead.impact.toFixed(3)} / {hoverInfo.bead.threshold.toFixed(2)}</div>
              <div>Status: {hoverInfo.bead.blocked ? '🔴 Blocked' : '🟢 OK'}</div>
              {hoverInfo.bead.ruleName && <div>Rule: {hoverInfo.bead.ruleName}</div>}
              {hoverInfo.bead.children && <div>Children: {hoverInfo.bead.children.length}</div>}
            </div>
          </div>
        )}

        {/* Play/Pause overlay */}
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

        {/* Bottom gradient */}
        <div
          className="pointer-events-none absolute inset-x-0 bottom-0 h-24"
          style={{ background: 'linear-gradient(to top, rgba(255,255,255,0.9), transparent)' }}
        />
      </div>

      {/* Footer */}
      <footer className="flex items-center justify-between border-t px-6 py-3"
              style={{ borderColor: theme.border, background: theme.header }}>
        <div className="flex items-center gap-4 text-xs" style={{ color: theme.muted }}>
          <span>v2.0.0</span>
          <span>•</span>
          <span>7 Layers • 64 Codons • 3 Modes</span>
          <span>•</span>
          <span>Last update: {new Date().toLocaleTimeString()}</span>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setRunning(v => !v)}
            className="rounded-md border px-3 py-1 text-xs"
            style={{ borderColor: theme.border }}
          >
            {running ? 'Pause' : 'Play'}
          </button>
        </div>
      </footer>
    </div>
  );
}

// ============================================================================
// Drawing Functions
// ============================================================================

function drawFrame(canvas, beads, layout, threshold, theme) {
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const { W, H } = layout;
  
  // Clear
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = theme.canvas;
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
  drawInfrastructure(ctx, layout, theme);
  
  // Paths
  drawPaths(ctx, beads, layout, theme);
  
  // Beads
  for (const bead of beads) {
    const color = bead.blocked ? '#000000' : getBeadColor(bead, threshold);
    drawCircle(ctx, bead.p.x, bead.p.y, bead.r, color, 0.96);
  }
  
  // Meta children preview
  for (const bead of beads) {
    if (bead.children && bead.phase === 3) {
      const n = Math.min(bead.children.length, 48);
      for (let i = 0; i < n; i++) {
        const angle = (2 * Math.PI * i) / n;
        const dist = bead.r * 0.6;
        const x = bead.p.x + Math.cos(angle) * dist;
        const y = bead.p.y + Math.sin(angle) * dist;
        const child = bead.children[i];
        const childColor = child.blocked ? '#000' : '#E8B500';
        drawCircle(ctx, x, y, 2, childColor, 0.85);
      }
    }
  }
  
  // Badge
  drawBadge(ctx, 16, 16, `Threshold ${threshold.toFixed(2)}`);
}

function drawInfrastructure(ctx, layout, theme) {
  // Inlets
  const inlets = layout.inlets(50);
  for (let i = 0; i < 10; i++) {
    const inlet = inlets[i * 5] || inlets[0];
    drawCircle(ctx, inlet.x, inlet.y, 6, '#666', 0.6);
  }
  
  // Bins
  layout.bins.forEach((bin, i) => {
    drawRoundRect(ctx, bin.x - 30, bin.y - 28, 60, 56, 10, theme.goldSoft, theme.border);
    drawText(ctx, `L${i + 1}`, bin.x - 8, bin.y + 4, '12px', '#444');
  });
  
  // Router
  const r = layout.router;
  drawRoundRect(ctx, r.x - 48, r.y - 26, 96, 52, 12, '#FFF2B0', theme.border);
  drawText(ctx, 'Router', r.x - 22, r.y + 4, '12px', '#444');
  
  // Outlet
  const o = layout.outlet;
  ctx.fillStyle = '#FFF3C6';
  ctx.strokeStyle = theme.border;
  ctx.beginPath();
  ctx.moveTo(o.x - 30, o.y - 30);
  ctx.arc(o.x - 30, o.y, 30, -Math.PI / 2, Math.PI / 2);
  ctx.lineTo(o.x + 12, o.y);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
}

function drawPaths(ctx, beads, layout, theme) {
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

function findBeadAt(beads, x, y) {
  for (let i = beads.length - 1; i >= 0; i--) {
    const bead = beads[i];
    const dx = x - bead.p.x;
    const dy = y - bead.p.y;
    if (dx * dx + dy * dy <= (bead.r + 4) * (bead.r + 4)) {
      return bead;
    }
  }
  return null;
}

function downloadFile(url, name) {
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.click();
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

// ============================================================================
// Audio System
// ============================================================================

function createAudio() {
  let ctx = null;
  let enabled = false;
  
  const enable = () => {
    if (!ctx) {
      try {
        ctx = new (window.AudioContext || window.webkitAudioContext)();
      } catch (e) {
        console.warn('Audio not supported');
        return;
      }
    }
    enabled = true;
  };
  
  const disable = () => {
    enabled = false;
  };
  
  const click = () => {
    if (!enabled || !ctx) return;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'triangle';
    o.frequency.value = 880;
    g.gain.value = 0.0001;
    o.connect(g);
    g.connect(ctx.destination);
    const t = ctx.currentTime;
    g.gain.exponentialRampToValueAtTime(0.05, t + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.08);
    o.start(t);
    o.stop(t + 0.09);
  };
  
  const thunk = () => {
    if (!enabled || !ctx) return;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'sine';
    o.frequency.value = 220;
    g.gain.value = 0.0001;
    o.connect(g);
    g.connect(ctx.destination);
    const t = ctx.currentTime;
    g.gain.exponentialRampToValueAtTime(0.12, t + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.25);
    o.frequency.exponentialRampToValueAtTime(140, t + 0.25);
    o.start(t);
    o.stop(t + 0.26);
  };
  
  const pour = (intensity = 3) => {
    if (!enabled || !ctx) return;
    const buf = ctx.createBuffer(1, ctx.sampleRate * 0.4, ctx.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < data.length; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (data.length / (2 + intensity)));
    }
    const src = ctx.createBufferSource();
    src.buffer = buf;
    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = 1000;
    const g = ctx.createGain();
    g.gain.value = 0.05;
    src.connect(filter);
    filter.connect(g);
    g.connect(ctx.destination);
    src.start();
  };
  
  return { enabled, enable, disable, click, thunk, pour };
}

// ============================================================================
// Theme
// ============================================================================

const GOLD_WHITE_THEME = {
  bg: '#FFFFFF',
  text: '#1a1a1a',
  muted: '#666666',
  border: '#E0E0E0',
  surface: '#F9F9F9',
  header: '#FFFFFF',
  toolbar: '#FFFDF2',
  canvas: '#FFFFFF',
  goldGrad: 'linear-gradient(135deg, #FFD700, #FFA500)',
  goldSoft: '#FFF7D6'
};
