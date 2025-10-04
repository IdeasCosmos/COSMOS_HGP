import React, { useEffect, useRef, useState } from 'react';

/**
 * COSMOS 디버깅 & 프로파일링 시스템
 *
 * 기능:
 * - FPS 측정
 * - 렌더링 시간 측정
 * - 메모리 사용량
 * - 에러 로그
 * - 성능 히스토리
 */

export default function DebugProfiler({ enabled = true, position = 'top-right' }) {
  const [stats, setStats] = useState({
    fps: 0,
    frameTime: 0,
    memory: 0,
    errors: [],
    warnings: [],
    renders: 0,
    lastUpdate: Date.now()
  });

  const [history, setHistory] = useState({
    fps: [],
    frameTime: [],
    memory: []
  });

  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(performance.now());
  const rafIdRef = useRef(null);

  // FPS 측정
  useEffect(() => {
    if (!enabled) return;

    const measureFPS = () => {
      const now = performance.now();
      const delta = now - lastTimeRef.current;

      frameCountRef.current++;

      // 매 초마다 FPS 계산
      if (delta >= 1000) {
        const fps = Math.round((frameCountRef.current * 1000) / delta);
        const frameTime = delta / frameCountRef.current;

        setStats(prev => ({
          ...prev,
          fps,
          frameTime: frameTime.toFixed(2),
          renders: prev.renders + 1,
          lastUpdate: Date.now()
        }));

        setHistory(prev => ({
          fps: [...prev.fps.slice(-59), fps],
          frameTime: [...prev.frameTime.slice(-59), frameTime],
          memory: prev.memory
        }));

        frameCountRef.current = 0;
        lastTimeRef.current = now;
      }

      rafIdRef.current = requestAnimationFrame(measureFPS);
    };

    rafIdRef.current = requestAnimationFrame(measureFPS);

    return () => {
      if (rafIdRef.current) {
        cancelAnimationFrame(rafIdRef.current);
      }
    };
  }, [enabled]);

  // 메모리 측정 (Chrome only)
  useEffect(() => {
    if (!enabled) return;

    const measureMemory = () => {
      if (performance.memory) {
        const usedMB = (performance.memory.usedJSHeapSize / 1048576).toFixed(2);
        setStats(prev => ({ ...prev, memory: usedMB }));
        setHistory(prev => ({
          ...prev,
          memory: [...prev.memory.slice(-59), parseFloat(usedMB)]
        }));
      }
    };

    const interval = setInterval(measureMemory, 1000);
    return () => clearInterval(interval);
  }, [enabled]);

  // 에러 캡처
  useEffect(() => {
    if (!enabled) return;

    const handleError = (event) => {
      setStats(prev => ({
        ...prev,
        errors: [...prev.errors.slice(-9), {
          message: event.message,
          stack: event.error?.stack,
          timestamp: Date.now()
        }]
      }));
    };

    const handleWarning = (event) => {
      setStats(prev => ({
        ...prev,
        warnings: [...prev.warnings.slice(-9), {
          message: event.message,
          timestamp: Date.now()
        }]
      }));
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleWarning);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleWarning);
    };
  }, [enabled]);

  if (!enabled) return null;

  const positionStyles = {
    'top-right': { top: 10, right: 10 },
    'top-left': { top: 10, left: 10 },
    'bottom-right': { bottom: 10, right: 10 },
    'bottom-left': { bottom: 10, left: 10 }
  };

  const fpsColor = stats.fps >= 55 ? '#22c55e' : stats.fps >= 30 ? '#f59e0b' : '#ef4444';

  return (
    <div style={{
      position: 'fixed',
      ...positionStyles[position],
      background: 'rgba(0, 0, 0, 0.85)',
      color: '#fff',
      padding: '12px',
      borderRadius: '8px',
      fontFamily: 'monospace',
      fontSize: '11px',
      zIndex: 9999,
      minWidth: '200px',
      maxWidth: '300px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
    }}>
      <div style={{ marginBottom: '8px', fontSize: '12px', fontWeight: 'bold', borderBottom: '1px solid #444', paddingBottom: '4px' }}>
        🔬 COSMOS Profiler
      </div>

      {/* FPS */}
      <div style={{ marginBottom: '4px' }}>
        <span style={{ color: '#888' }}>FPS:</span>
        <span style={{ color: fpsColor, fontWeight: 'bold', marginLeft: '8px' }}>
          {stats.fps}
        </span>
        <span style={{ color: '#666', marginLeft: '8px' }}>
          ({stats.frameTime}ms)
        </span>
      </div>

      {/* Memory */}
      {stats.memory > 0 && (
        <div style={{ marginBottom: '4px' }}>
          <span style={{ color: '#888' }}>Memory:</span>
          <span style={{ color: '#60a5fa', marginLeft: '8px' }}>
            {stats.memory} MB
          </span>
        </div>
      )}

      {/* Renders */}
      <div style={{ marginBottom: '4px' }}>
        <span style={{ color: '#888' }}>Renders:</span>
        <span style={{ color: '#a78bfa', marginLeft: '8px' }}>
          {stats.renders}
        </span>
      </div>

      {/* FPS Graph */}
      {history.fps.length > 0 && (
        <div style={{ marginTop: '8px', marginBottom: '4px' }}>
          <div style={{ color: '#888', fontSize: '10px', marginBottom: '2px' }}>FPS History</div>
          <div style={{
            display: 'flex',
            alignItems: 'flex-end',
            height: '40px',
            gap: '1px',
            background: '#222',
            padding: '2px',
            borderRadius: '4px'
          }}>
            {history.fps.slice(-30).map((fps, i) => {
              const height = Math.min((fps / 60) * 100, 100);
              const color = fps >= 55 ? '#22c55e' : fps >= 30 ? '#f59e0b' : '#ef4444';
              return (
                <div
                  key={i}
                  style={{
                    flex: 1,
                    height: `${height}%`,
                    background: color,
                    minWidth: '2px'
                  }}
                />
              );
            })}
          </div>
        </div>
      )}

      {/* Errors */}
      {stats.errors.length > 0 && (
        <div style={{ marginTop: '8px', borderTop: '1px solid #444', paddingTop: '8px' }}>
          <div style={{ color: '#ef4444', fontSize: '11px', fontWeight: 'bold', marginBottom: '4px' }}>
            ⚠️ Errors ({stats.errors.length})
          </div>
          {stats.errors.slice(-3).map((error, i) => (
            <div key={i} style={{
              background: '#2d1212',
              padding: '4px',
              borderRadius: '4px',
              marginBottom: '2px',
              fontSize: '10px',
              color: '#fca5a5'
            }}>
              {error.message}
            </div>
          ))}
        </div>
      )}

      {/* Performance Grade */}
      <div style={{ marginTop: '8px', borderTop: '1px solid #444', paddingTop: '8px', textAlign: 'center' }}>
        <div style={{ fontSize: '10px', color: '#888', marginBottom: '2px' }}>Performance</div>
        <div style={{ fontSize: '16px', fontWeight: 'bold', color: fpsColor }}>
          {stats.fps >= 55 ? 'A' : stats.fps >= 45 ? 'B' : stats.fps >= 30 ? 'C' : 'D'}
        </div>
      </div>
    </div>
  );
}

/**
 * Performance Hook - 커스텀 훅으로 사용 가능
 */
export function usePerformance() {
  const [perf, setPerf] = useState({
    fps: 0,
    frameTime: 0,
    memory: 0
  });

  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(performance.now());

  useEffect(() => {
    let rafId;

    const measure = () => {
      const now = performance.now();
      const delta = now - lastTimeRef.current;

      frameCountRef.current++;

      if (delta >= 1000) {
        const fps = Math.round((frameCountRef.current * 1000) / delta);
        const frameTime = delta / frameCountRef.current;
        const memory = performance.memory ? (performance.memory.usedJSHeapSize / 1048576) : 0;

        setPerf({ fps, frameTime, memory });

        frameCountRef.current = 0;
        lastTimeRef.current = now;
      }

      rafId = requestAnimationFrame(measure);
    };

    rafId = requestAnimationFrame(measure);
    return () => cancelAnimationFrame(rafId);
  }, []);

  return perf;
}

/**
 * Performance Logger - 콘솔 로그용
 */
export class PerformanceLogger {
  constructor() {
    this.marks = new Map();
    this.measures = [];
  }

  mark(name) {
    performance.mark(name);
    this.marks.set(name, performance.now());
  }

  measure(name, startMark, endMark) {
    try {
      performance.measure(name, startMark, endMark);
      const entries = performance.getEntriesByName(name);
      if (entries.length > 0) {
        const duration = entries[entries.length - 1].duration;
        this.measures.push({ name, duration, timestamp: Date.now() });
        return duration;
      }
    } catch (e) {
      console.warn('Performance measure failed:', e);
    }
    return 0;
  }

  getReport() {
    return {
      marks: Array.from(this.marks.entries()),
      measures: this.measures
    };
  }

  clear() {
    this.marks.clear();
    this.measures = [];
    performance.clearMarks();
    performance.clearMeasures();
  }

  log() {
    console.group('📊 Performance Report');
    console.table(this.measures);
    console.groupEnd();
  }
}

export const perfLogger = new PerformanceLogger();
