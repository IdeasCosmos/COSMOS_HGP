#!/usr/bin/env python3
"""
COSMOS-HGP V2-min+ 배포 버전 (Open Source)
핵심 3요소: 계층 실행, 국소 차단, 누적 캡
가시성 2요소: 타임라인, 결정적 재실행

License: Apache 2.0
Pro Features: Available with commercial license
Contact: contact@cosmos-hgp.com
"""
import json
import time
import hashlib
import numpy as np
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import os
import random
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import yaml

# Import core engine
from src.engine.core import HierarchicalExecutor, Rule, GroupDef, ExecutionResult

app = Flask(__name__)
CORS(app)

# ===============================
# 1. 핵심 데이터 구조
# ===============================

@dataclass
class ExecutionRequest:
    """실행 요청 데이터"""
    data: List[float]
    group_def: Dict[str, Any]
    threshold: float = 0.30
    cumulative_cap: float = 0.50
    seed: Optional[int] = None

@dataclass
class ExecutionResponse:
    """실행 응답 데이터"""
    output: Any
    timeline: str
    summary: Dict[str, Any]
    logs: List[Dict[str, Any]]
    execution_id: str
    timestamp: float

# ===============================
# 2. 기본 규칙 함수들
# ===============================

def multiply_rule(input_data: Any) -> Any:
    """1.1배 곱하기 규칙"""
    return np.array(input_data) * 1.1

def normalize_rule(input_data: Any) -> Any:
    """정규화 규칙"""
    arr = np.array(input_data)
    norm = np.linalg.norm(arr)
    return arr / (norm + 1e-12) if norm > 0 else arr

def tanh_rule(input_data: Any) -> Any:
    """tanh 활성화 규칙"""
    return np.tanh(np.array(input_data))

def sum_rule(input_data: Any) -> Any:
    """합계 규칙"""
    return np.sum(np.array(input_data))

# ===============================
# 3. 코스모스 엔진 초기화
# ===============================

# 전역 엔진 인스턴스
engine = HierarchicalExecutor({
    "global_threshold": 0.30,
    "cumulative_cap": 0.50,
    "max_depth": 64,
    "epsilon": 1e-12
})

# 기본 규칙들 등록
engine.add_rule(Rule("multiply", multiply_rule, layer=1, threshold=0.30))
engine.add_rule(Rule("normalize", normalize_rule, layer=2, threshold=0.25))
engine.add_rule(Rule("tanh", tanh_rule, layer=3, threshold=0.35))
engine.add_rule(Rule("sum", sum_rule, layer=4, threshold=0.20))

# ===============================
# 4. Flask 라우트
# ===============================

@app.route('/')
def index():
    """메인 대시보드 페이지"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COSMOS-HGP V2-min+</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .result { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 15px; font-family: monospace; white-space: pre-wrap; }
        .timeline { background: #e3f2fd; padding: 15px; border-radius: 4px; margin: 10px 0; font-family: monospace; }
        .pro-banner { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .status-card { background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .status-value { font-size: 24px; font-weight: bold; color: #007bff; }
        .status-label { color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌌 COSMOS-HGP V2-min+</h1>
            <p><strong>국소 실패를 상위로 번지지 않게 차단하는 '계층형 실행 엔진'</strong></p>
            <p>License: Apache 2.0 | <a href="https://github.com/IdeasCosmos/COSMOS_HGP" style="color: #007bff;">GitHub</a></p>
        </div>

        <div class="pro-banner">
            <h3>🚀 COSMOS-HGP Pro Available</h3>
            <p>병렬 실행, 분산 처리, 고급 대시보드, ML 예측 등 엔터프라이즈 기능</p>
            <p>Contact: contact@cosmos-hgp.com</p>
        </div>

        <div class="status-grid">
            <div class="status-card">
                <div class="status-value" id="executions">0</div>
                <div class="status-label">총 실행</div>
            </div>
            <div class="status-card">
                <div class="status-value" id="blocks">0</div>
                <div class="status-label">차단 수</div>
            </div>
            <div class="status-card">
                <div class="status-value" id="avg-impact">0.00</div>
                <div class="status-label">평균 임팩트</div>
            </div>
            <div class="status-card">
                <div class="status-value" id="p95-latency">0ms</div>
                <div class="status-label">P95 지연</div>
            </div>
        </div>

        <div class="card">
            <h3>🧪 데모 시나리오</h3>
            <button class="btn" onclick="runScenario('A')">시나리오 A: 정상 흐름</button>
            <button class="btn" onclick="runScenario('B')">시나리오 B: 국소 차단</button>
            <button class="btn" onclick="runScenario('C')">시나리오 C: 누적캡 차단</button>
            <button class="btn" onclick="runScenario('D')">시나리오 D: 극단값 처리</button>
        </div>

        <div class="card">
            <h3>⚙️ 커스텀 실행</h3>
            <div>
                <label>입력 데이터 (JSON 배열):</label><br>
                <textarea id="inputData" rows="3" style="width: 100%; padding: 8px;">[1, 2, 3, 4, 5]</textarea>
            </div>
            <div style="margin: 10px 0;">
                <label>임계값: <input type="number" id="threshold" value="0.30" step="0.01" min="0" max="1"></label>
                <label>누적 캡: <input type="number" id="cap" value="0.50" step="0.01" min="0" max="1"></label>
            </div>
            <button class="btn" onclick="runCustom()">실행</button>
        </div>

        <div class="card">
            <h3>📊 실행 결과</h3>
            <div id="results"></div>
        </div>

        <div class="card">
            <h3>📈 실시간 타임라인</h3>
            <div id="timeline" class="timeline">실행 결과가 여기에 표시됩니다...</div>
        </div>
    </div>

    <script>
        let executionCount = 0;
        let blockCount = 0;
        let totalImpact = 0;
        let latencies = [];

        const scenarios = {
            'A': { data: [1, 2, 3, 4, 5], threshold: 0.30, cap: 0.50 },
            'B': { data: [1, 2, 3, 4, 5], threshold: 0.70, cap: 0.50 },
            'C': { data: [10, 20, 30, 40, 50], threshold: 0.30, cap: 0.50 },
            'D': { data: [1e6, 1e-6, NaN, Infinity, -Infinity], threshold: 0.30, cap: 0.50 }
        };

        async function runScenario(scenario) {
            const config = scenarios[scenario];
            await execute(config.data, config.threshold, config.cap, `시나리오 ${scenario}`);
        }

        async function runCustom() {
            const data = JSON.parse(document.getElementById('inputData').value);
            const threshold = parseFloat(document.getElementById('threshold').value);
            const cap = parseFloat(document.getElementById('cap').value);
            await execute(data, threshold, cap, '커스텀 실행');
        }

        async function execute(data, threshold, cap, label) {
            const startTime = performance.now();
            
            try {
                const response = await fetch('/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        data: data,
                        threshold: threshold,
                        cumulative_cap: cap,
                        seed: 42
                    })
                });

                const result = await response.json();
                const endTime = performance.now();
                const latency = endTime - startTime;

                // 통계 업데이트
                executionCount++;
                if (result.summary.blocks > 0) blockCount++;
                totalImpact += result.summary.cumulative_velocity || 0;
                latencies.push(latency);

                updateStats();
                displayResults(result, label, latency);
                
            } catch (error) {
                document.getElementById('results').innerHTML = 
                    '<div class="result" style="color: red;">오류: ' + error.message + '</div>';
            }
        }

        function updateStats() {
            document.getElementById('executions').textContent = executionCount;
            document.getElementById('blocks').textContent = blockCount;
            document.getElementById('avg-impact').textContent = 
                (totalImpact / executionCount).toFixed(3);
            
            if (latencies.length > 0) {
                const sorted = latencies.slice().sort((a, b) => a - b);
                const p95Index = Math.ceil(sorted.length * 0.95) - 1;
                document.getElementById('p95-latency').textContent = 
                    Math.round(sorted[p95Index]) + 'ms';
            }
        }

        function displayResults(result, label, latency) {
            const html = `
                <div class="result">
<strong>${label}</strong> (${Math.round(latency)}ms)
실행 ID: ${result.execution_id}
출력: ${JSON.stringify(result.output)}
요약: 실행=${result.summary.rules_executed}, 차단=${result.summary.blocks}, 캡=${result.summary.cap_hits}
누적 속도: ${result.summary.cumulative_velocity?.toFixed(3) || 'N/A'}
지속시간: ${result.summary.duration_ms?.toFixed(1)}ms
                </div>
            `;
            
            document.getElementById('results').innerHTML = html;
            document.getElementById('timeline').textContent = result.timeline;
        }

        // 페이지 로드 시 초기 상태 업데이트
        updateStats();
    </script>
</body>
</html>
    ''')

@app.route('/health')
def health():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "license": "Apache 2.0",
        "timestamp": time.time(),
        "features": {
            "hierarchical_execution": True,
            "local_blocking": True,
            "cumulative_capping": True,
            "timeline_generation": True,
            "deterministic_replay": True
        },
        "pro_features": {
            "parallel_execution": False,
            "distributed_processing": False,
            "advanced_dashboard": False,
            "ml_prediction": False,
            "enterprise_support": False
        }
    })

@app.route('/run', methods=['POST'])
def run_execution():
    """메인 실행 엔드포인트"""
    try:
        # 요청 데이터 파싱
        req_data = request.get_json()
        if not req_data:
            return jsonify({"error": "JSON 데이터가 필요합니다"}), 400
        
        # 시드 설정 (결정적 재실행)
        seed = req_data.get('seed', 42)
        random.seed(seed)
        np.random.seed(seed)
        
        # 실행 ID 생성
        execution_id = hashlib.md5(f"{req_data}_{time.time()}".encode()).hexdigest()[:8]
        
        # 기본 그룹 정의 (시나리오별로 다르게 설정 가능)
        group_def = GroupDef(
            name="root",
            type="group",
            children=[
                GroupDef(name="multiply", type="rule"),
                GroupDef(name="normalize", type="rule"),
                GroupDef(name="tanh", type="rule"),
                GroupDef(name="sum", type="rule")
            ]
        )
        
        # 임계값과 캡 설정
        threshold = req_data.get('threshold', 0.30)
        cumulative_cap = req_data.get('cumulative_cap', 0.50)
        
        engine.config['global_threshold'] = threshold
        engine.config['cumulative_cap'] = cumulative_cap
        
        # 엔진 초기화
        engine.log_events = []
        engine.cumulative_velocity = 0.0
        
        # 실행 시작
        start_time = time.time()
        result = engine.execute_group(group_def, req_data['data'])
        end_time = time.time()
        
        # 타임라인 생성
        timeline = engine.generate_timeline()
        
        # 요약 생성
        summary = engine.get_summary()
        summary['execution_id'] = execution_id
        summary['total_duration_ms'] = (end_time - start_time) * 1000
        
        # 응답 생성
        response = ExecutionResponse(
            output=result.output.tolist() if hasattr(result.output, 'tolist') else result.output,
            timeline=timeline,
            summary=summary,
            logs=engine.log_events,
            execution_id=execution_id,
            timestamp=time.time()
        )
        
        return jsonify(asdict(response))
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/metrics')
def get_metrics():
    """메트릭 엔드포인트"""
    return jsonify({
        "timestamp": time.time(),
        "engine_status": "running",
        "config": engine.config,
        "registered_rules": list(engine.rules.keys()),
        "license": "Apache 2.0"
    })

if __name__ == '__main__':
    # 로그 디렉토리 생성
    os.makedirs('/app/log', exist_ok=True)
    
    # 개발 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=False)
