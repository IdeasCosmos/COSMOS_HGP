#!/usr/bin/env python3
"""
간단한 Flask 서버로 COSMOS 시각화 시스템 실행
"""

import os
import sys
import json
import time
import webbrowser
from pathlib import Path
from flask import Flask, jsonify, send_file, render_template_string
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

app = Flask(__name__)
if CORS_AVAILABLE:
    CORS(app)

LOG = Path("./log/annotations.jsonl")
VIZ = Path("./viz_out")

# 대시보드 HTML 템플릿
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COSMOS 시각화 대시보드</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            padding: 30px;
        }
        .card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        .card h3 {
            margin: 0 0 15px 0;
            color: #2c3e50;
            font-size: 1.3em;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .image-container {
            text-align: center;
            margin: 15px 0;
        }
        .image-container img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #3498db;
        }
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }
        .stat-label {
            font-size: 0.9em;
            color: #7f8c8d;
            margin-top: 5px;
        }
        .refresh-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px 5px;
        }
        .refresh-btn:hover {
            background: #2980b9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌌 COSMOS 시각화 대시보드</h1>
            <p>실시간 시스템 모니터링 및 시각화</p>
            <button class="refresh-btn" onclick="location.reload()">🔄 새로고침</button>
            <button class="refresh-btn" onclick="window.open('/en', '_blank')">🌍 English Dashboard</button>
        </div>

        <div class="grid">
            <!-- 실시간 지표 -->
            <div class="card">
                <h3>📊 실시간 지표</h3>
                <div id="metrics">
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-value">{{ metrics.p95_ms or 0 }}</div>
                            <div class="stat-label">P95 지연시간 (ms)</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{{ metrics.blocks or 0 }}</div>
                            <div class="stat-label">블록 이벤트</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{{ metrics.caps or 0 }}</div>
                            <div class="stat-label">캡 이벤트</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{{ metrics.running_groups or 0 }}</div>
                            <div class="stat-label">실행 중인 그룹</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{{ metrics.total_events or 0 }}</div>
                            <div class="stat-label">총 이벤트 수</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 히트맵 -->
            <div class="card">
                <h3>🔥 레이어 히트맵</h3>
                <div class="image-container">
                    <img src="/viz/heatmap.png" alt="히트맵" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div style="display:none; color:#e74c3c;">이미지를 불러올 수 없습니다</div>
                </div>
            </div>

            <!-- 타임라인 -->
            <div class="card">
                <h3>⏱️ 이벤트 타임라인</h3>
                <div class="image-container">
                    <img src="/viz/timeline.png" alt="타임라인" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div style="display:none; color:#e74c3c;">이미지를 불러올 수 없습니다</div>
                </div>
            </div>

            <!-- 코돈 분석 -->
            <div class="card">
                <h3>🧬 코돈 패턴 분석</h3>
                <div class="image-container">
                    <img src="/viz/codon_bar.png" alt="코돈 분석" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div style="display:none; color:#e74c3c;">이미지를 불러올 수 없습니다</div>
                </div>
            </div>

            <!-- 이벤트 통계 -->
            <div class="card">
                <h3>📈 이벤트 통계</h3>
                <div class="stats">
                    {% for kind, count in event_stats.by_kind.items() %}
                    <div class="stat-item">
                        <div class="stat-value">{{ count }}</div>
                        <div class="stat-label">{{ kind }} 이벤트</div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- API 링크 -->
            <div class="card">
                <h3>🔗 API 엔드포인트</h3>
                <div style="background: #ecf0f1; padding: 20px; border-radius: 10px;">
                    <h4>빠른 접근</h4>
                    <a href="/metrics" style="display: inline-block; background: #3498db; color: white; text-decoration: none; padding: 8px 16px; border-radius: 20px; margin: 5px;">📊 실시간 지표</a>
                    <a href="/events" style="display: inline-block; background: #3498db; color: white; text-decoration: none; padding: 8px 16px; border-radius: 20px; margin: 5px;">📋 이벤트 목록</a>
                    <a href="/viz" style="display: inline-block; background: #3498db; color: white; text-decoration: none; padding: 8px 16px; border-radius: 20px; margin: 5px;">🖼️ 시각화 목록</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

def load_events():
    """이벤트 로드"""
    if not LOG.exists():
        return []
    
    events = []
    try:
        with LOG.open(encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except:
                    continue
    except:
        pass
    
    return events

def get_metrics():
    """실시간 지표 계산"""
    now = time.time()
    events = load_events()
    
    blocks = caps = 0
    durations = []
    running = set()
    total_events = len(events)
    
    for e in events:
        ts = e.get("ts", 0) / 1000  # 밀리초를 초로 변환
        if now - ts > 60:  # 최근 1분
            continue
            
        k = e.get("kind", "")
        if k == "block":
            blocks += 1
        if k == "cap":
            caps += 1
        if k in ("enter", "exit"):
            durations.append(e.get("dur_ms", 0.0))
        if k == "enter":
            running.add(e.get("path", ""))
    
    p95 = sorted(durations)[int(0.95 * len(durations))] if durations else 0.0
    
    return {
        "p95_ms": round(p95, 2),
        "blocks": blocks,
        "caps": caps,
        "running_groups": len(running),
        "total_events": total_events,
        "recent_events": len(durations)
    }

def get_event_stats():
    """이벤트 통계"""
    events = load_events()
    
    stats = {
        "by_kind": {},
        "by_layer": {}
    }
    
    for e in events:
        kind = e.get("kind", "unknown")
        stats["by_kind"][kind] = stats["by_kind"].get(kind, 0) + 1
        
        layer = e.get("layer", 0)
        if layer > 0:
            stats["by_layer"][layer] = stats["by_layer"].get(layer, 0) + 1
    
    return stats

@app.route('/')
def dashboard():
    """한국어 대시보드"""
    metrics = get_metrics()
    event_stats = get_event_stats()
    return render_template_string(DASHBOARD_HTML, metrics=metrics, event_stats=event_stats)

@app.route('/en')
def dashboard_en():
    """영문 대시보드"""
    dashboard_path = Path("./dashboard_en.html")
    if dashboard_path.exists():
        return send_file(str(dashboard_path), mimetype="text/html")
    else:
        return "English dashboard not found", 404

@app.route('/metrics')
def metrics():
    """실시간 지표 API"""
    return jsonify(get_metrics())

@app.route('/events')
def events():
    """이벤트 목록 API"""
    events = load_events()
    return jsonify({"events": events[-50:], "total": len(events)})  # 최근 50개

@app.route('/viz/<filename>')
def viz_file(filename):
    """시각화 파일 서빙"""
    file_path = VIZ / filename
    if file_path.exists():
        return send_file(str(file_path))
    else:
        return "파일을 찾을 수 없습니다", 404

@app.route('/viz')
def viz_list():
    """시각화 파일 목록"""
    if not VIZ.exists():
        return jsonify({"files": []})
    
    files = []
    for file_path in VIZ.iterdir():
        if file_path.is_file():
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
    
    return jsonify({"files": sorted(files, key=lambda x: x["modified"], reverse=True)})

def main():
    """메인 실행 함수"""
    print("=== COSMOS 시각화 시스템 시작 ===")
    
    # 시각화 생성
    try:
        from viz.log_to_map import main as generate_viz
        generate_viz()
        print("[OK] 시각화 생성 완료!")
    except Exception as e:
        print(f"[WARNING] 시각화 생성 오류: {e}")
    
    # 서버 시작
    print("[INFO] Flask 서버 시작 중...")
    print("[INFO] 브라우저에서 http://localhost:5000 을 열어보세요!")
    
    # 자동으로 브라우저 열기
    try:
        webbrowser.open('http://localhost:5000')
    except:
        pass
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
