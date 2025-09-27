#!/usr/bin/env python3
"""
COSMOS-HGP V2-min+ 배포 버전
핵심 3요소: 계층 실행, 국소 차단, 누적 캡
가시성 2요소: 타임라인, 결정적 재실행
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

app = Flask(__name__)
CORS(app)

# ===============================
# 1. 핵심 데이터 구조
# ===============================

@dataclass
class Rule:
    """개별 실행 규칙"""
    name: str
    layer: int  # 1-7
    function: str  # "multiply", "normalize", "tanh", "sum"
    
    def run(self, input_data: Any) -> Any:
        """규칙 실행"""
        if self.function == "multiply":
            return np.array(input_data) * 1.1
        elif self.function == "normalize":
            arr = np.array(input_data)
            norm = np.linalg.norm(arr)
            return arr / (norm + 1e-12) if norm > 0 else arr
        elif self.function == "tanh":
            return np.tanh(np.array(input_data))
        elif self.function == "sum":
            return np.sum(np.array(input_data))
        else:
            return input_data

@dataclass
class GroupDef:
    """그룹 정의"""
    name: str
    type: str  # "rule" or "group"
    threshold: Optional[float] = None
    children: Optional[List['GroupDef']] = None

@dataclass
class ExecutionResult:
    """실행 결과"""
    output: Any
    impact: float
    path: str
    blocked: bool
    meta: Dict[str, Any]

# ===============================
# 2. 핵심 엔진
# ===============================

class CosmosEngine:
    """COSMOS-HGP V2-min+ 엔진"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules = {}
        self.log_events = []
        self.cumulative_velocity = 0.0
        self.execution_path = []
        
    def add_rule(self, rule: Rule):
        """규칙 추가"""
        self.rules[rule.name] = rule
    
    def calculate_impact(self, before: Any, after: Any) -> float:
        """임팩트 계산"""
        try:
            before_arr = np.array(before, dtype=float)
            after_arr = np.array(after, dtype=float)
            
            before_norm = np.linalg.norm(before_arr)
            after_norm = np.linalg.norm(after_arr)
            
            if before_norm < 1e-12:
                return 0.5 if after_norm > 1e-12 else 0.0
            
            change = np.linalg.norm(after_arr - before_arr) / before_norm
            scale = abs(np.tanh(after_norm / before_norm) - 1.0)
            
            impact = 0.5 * change + 0.5 * scale
            return max(0.0, min(1.0, impact))
        except:
            return 0.1
    
    def update_cumulative(self, impact: float):
        """누적 속도 업데이트"""
        self.cumulative_velocity = 1.0 - (1.0 - self.cumulative_velocity) * (1.0 - impact)
    
    def execute_group(self, group_def: GroupDef, input_data: Any, path: str = "") -> ExecutionResult:
        """그룹 실행"""
        start_time = time.time()
        current_path = f"{path}/{group_def.name}" if path else group_def.name
        
        # 로그 이벤트 기록
        self.log_events.append({
            "ts": datetime.now().isoformat(),
            "path": current_path,
            "node": group_def.name,
            "type": group_def.type,
            "event": "enter",
            "impact": 0.0,
            "threshold": group_def.threshold or self.config.get("global_threshold", 0.30),
            "cum": self.cumulative_velocity,
            "duration_ms": 0.0,
            "note": "group_start"
        })
        
        if group_def.type == "rule":
            # 규칙 실행
            rule = self.rules.get(group_def.name)
            if not rule:
                return ExecutionResult(
                    output=input_data,
                    impact=0.0,
                    path=current_path,
                    blocked=True,
                    meta={"error": "rule_not_found"}
                )
            
            try:
                output = rule.run(input_data)
                impact = self.calculate_impact(input_data, output)
                
                # 임계값 체크
                threshold = group_def.threshold or self.config.get("global_threshold", 0.30)
                blocked = impact >= threshold
                
                if not blocked:
                    self.update_cumulative(impact)
                
                # 누적 캡 체크
                if self.cumulative_velocity >= self.config.get("cumulative_cap", 0.50):
                    blocked = True
                
                duration_ms = (time.time() - start_time) * 1000
                
                # 로그 이벤트 기록
                self.log_events.append({
                    "ts": datetime.now().isoformat(),
                    "path": current_path,
                    "node": group_def.name,
                    "type": "rule",
                    "event": "block" if blocked else "exit",
                    "impact": impact,
                    "threshold": threshold,
                    "cum": self.cumulative_velocity,
                    "duration_ms": duration_ms,
                    "note": f"blocked={blocked}, cap_hit={self.cumulative_velocity >= self.config.get('cumulative_cap', 0.50)}"
                })
                
                return ExecutionResult(
                    output=output if not blocked else input_data,
                    impact=impact,
                    path=current_path,
                    blocked=blocked,
                    meta={
                        "duration_ms": duration_ms,
                        "threshold": threshold,
                        "cumulative": self.cumulative_velocity
                    }
                )
                
            except Exception as e:
                # 에러 시 차단
                self.log_events.append({
                    "ts": datetime.now().isoformat(),
                    "path": current_path,
                    "node": group_def.name,
                    "type": "rule",
                    "event": "error",
                    "impact": 0.0,
                    "threshold": 0.0,
                    "cum": self.cumulative_velocity,
                    "duration_ms": (time.time() - start_time) * 1000,
                    "note": f"error: {str(e)}"
                })
                
                return ExecutionResult(
                    output=input_data,
                    impact=0.0,
                    path=current_path,
                    blocked=True,
                    meta={"error": str(e)}
                )
        
        else:
            # 그룹 실행 (자식들 순차 처리)
            current_data = input_data
            group_blocked = False
            
            if group_def.children:
                for child in group_def.children:
                    result = self.execute_group(child, current_data, current_path)
                    
                    if result.blocked:
                        group_blocked = True
                        break
                    
                    current_data = result.output
            
            duration_ms = (time.time() - start_time) * 1000
            
            # 그룹 종료 로그
            self.log_events.append({
                "ts": datetime.now().isoformat(),
                "path": current_path,
                "node": group_def.name,
                "type": "group",
                "event": "block" if group_blocked else "exit",
                "impact": 0.0,
                "threshold": 0.0,
                "cum": self.cumulative_velocity,
                "duration_ms": duration_ms,
                "note": f"group_blocked={group_blocked}"
            })
            
            return ExecutionResult(
                output=current_data,
                impact=0.0,
                path=current_path,
                blocked=group_blocked,
                meta={"duration_ms": duration_ms}
            )
    
    def generate_timeline(self) -> str:
        """타임라인 생성"""
        timeline_parts = []
        current_path = ""
        
        for event in self.log_events:
            if event["type"] == "rule" and event["event"] == "exit":
                node = event["node"]
                if event["blocked"]:
                    timeline_parts.append(f"[{node} blocked: impact={event['impact']:.2f}≥{event['threshold']:.2f}]")
                else:
                    timeline_parts.append(node)
            elif event["type"] == "rule" and event["event"] == "block":
                node = event["node"]
                timeline_parts.append(f"[{node} blocked: impact={event['impact']:.2f}≥{event['threshold']:.2f}]")
            elif "cap_hit=true" in event.get("note", ""):
                timeline_parts.append("(subtree stop by cap)")
        
        return " → ".join(timeline_parts) if timeline_parts else "no_execution"
    
    def get_summary(self) -> Dict[str, Any]:
        """실행 요약"""
        rules_executed = len([e for e in self.log_events if e["type"] == "rule" and e["event"] == "exit"])
        blocks = len([e for e in self.log_events if "blocked=true" in e.get("note", "")])
        cap_hits = len([e for e in self.log_events if "cap_hit=true" in e.get("note", "")])
        max_depth = max(len(e["path"].split("/")) for e in self.log_events) if self.log_events else 0
        total_duration = sum(e["duration_ms"] for e in self.log_events)
        
        return {
            "rules_executed": rules_executed,
            "blocks": blocks,
            "cap_hits": cap_hits,
            "max_depth": max_depth,
            "duration_ms": total_duration,
            "cumulative_velocity": self.cumulative_velocity
        }

# ===============================
# 3. 전역 엔진 인스턴스
# ===============================

engine = CosmosEngine({
    "global_threshold": 0.30,
    "cumulative_cap": 0.50,
    "epsilon": 1e-12,
    "max_depth": 64
})

# 기본 규칙들 추가
engine.add_rule(Rule("A_Init", 1, "multiply"))
engine.add_rule(Rule("B_Scale", 2, "multiply"))
engine.add_rule(Rule("C_Normalize", 3, "normalize"))
engine.add_rule(Rule("D_Transform", 4, "tanh"))
engine.add_rule(Rule("E_Finalize", 5, "sum"))

# ===============================
# 4. API 엔드포인트
# ===============================

@app.route('/')
def index():
    """메인 페이지"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>COSMOS-HGP V2-min+</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #0e1117; color: #fafafa; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .demo-section { background: #262730; padding: 20px; margin: 20px 0; border-radius: 8px; }
            .input-group { margin: 10px 0; }
            label { display: block; margin-bottom: 5px; color: #00d4ff; }
            input, textarea, select { width: 100%; padding: 8px; border: 1px solid #444; background: #1a1a1a; color: #fafafa; border-radius: 4px; }
            button { background: #00d4ff; color: #0e1117; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #00a0cc; }
            .result { background: #1a1a1a; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #00d4ff; }
            .timeline { font-family: monospace; background: #000; padding: 10px; border-radius: 4px; }
            .metric { display: inline-block; margin: 10px; padding: 10px; background: #333; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌌 COSMOS-HGP V2-min+</h1>
                <p>국소 실패를 상위로 번지지 않게 차단하는 '계층형 실행 엔진'</p>
            </div>
            
            <div class="demo-section">
                <h3>🚀 데모 실행</h3>
                <div class="input-group">
                    <label>입력 데이터 (JSON 배열):</label>
                    <textarea id="inputData" rows="3">[1, 2, 3, 4, 5]</textarea>
                </div>
                <div class="input-group">
                    <label>임계값:</label>
                    <select id="threshold">
                        <option value="0.30">0.30 (표준)</option>
                        <option value="0.70">0.70 (높음)</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>누적 캡:</label>
                    <select id="cumulativeCap">
                        <option value="0.50">0.50 (표준)</option>
                        <option value="0.30">0.30 (보수적)</option>
                    </select>
                </div>
                <button onclick="runDemo()">실행</button>
            </div>
            
            <div id="results" style="display: none;">
                <div class="demo-section">
                    <h3>📊 실행 결과</h3>
                    <div id="output"></div>
                </div>
                
                <div class="demo-section">
                    <h3>⏱️ 타임라인</h3>
                    <div id="timeline" class="timeline"></div>
                </div>
                
                <div class="demo-section">
                    <h3>📈 메트릭</h3>
                    <div id="metrics"></div>
                </div>
            </div>
        </div>
        
        <script>
            async function runDemo() {
                const inputData = JSON.parse(document.getElementById('inputData').value);
                const threshold = parseFloat(document.getElementById('threshold').value);
                const cumulativeCap = parseFloat(document.getElementById('cumulativeCap').value);
                
                try {
                    const response = await fetch('/run', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            data: inputData,
                            group_def: {
                                "name": "main",
                                "type": "group",
                                "children": [
                                    {"name": "A_Init", "type": "rule"},
                                    {"name": "B_Scale", "type": "rule"},
                                    {"name": "C_Normalize", "type": "rule"},
                                    {"name": "D_Transform", "type": "rule"},
                                    {"name": "E_Finalize", "type": "rule"}
                                ]
                            },
                            threshold: threshold,
                            cumulative_cap: cumulativeCap
                        })
                    });
                    
                    const result = await response.json();
                    
                    document.getElementById('output').innerHTML = `
                        <div class="result">
                            <strong>최종 출력:</strong> ${JSON.stringify(result.output)}<br>
                            <strong>차단됨:</strong> ${result.blocked}<br>
                            <strong>경로:</strong> ${result.path}
                        </div>
                    `;
                    
                    document.getElementById('timeline').textContent = result.timeline;
                    
                    document.getElementById('metrics').innerHTML = `
                        <div class="metric">규칙 실행: ${result.summary.rules_executed}</div>
                        <div class="metric">차단 수: ${result.summary.blocks}</div>
                        <div class="metric">캡 히트: ${result.summary.cap_hits}</div>
                        <div class="metric">누적 속도: ${result.summary.cumulative_velocity.toFixed(3)}</div>
                        <div class="metric">실행 시간: ${result.summary.duration_ms.toFixed(1)}ms</div>
                    `;
                    
                    document.getElementById('results').style.display = 'block';
                } catch (error) {
                    alert('실행 중 오류가 발생했습니다: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """
    return html

@app.route('/run', methods=['POST'])
def run_cosmos():
    """COSMOS 실행 API"""
    try:
        data = request.get_json()
        
        # 입력 데이터
        input_data = data.get('data', [1, 2, 3, 4, 5])
        group_def = data.get('group_def', {})
        threshold = data.get('threshold', 0.30)
        cumulative_cap = data.get('cumulative_cap', 0.50)
        
        # 엔진 설정 업데이트
        engine.config['global_threshold'] = threshold
        engine.config['cumulative_cap'] = cumulative_cap
        
        # 로그 초기화
        engine.log_events = []
        engine.cumulative_velocity = 0.0
        
        # 그룹 정의 파싱
        if isinstance(group_def, dict):
            group = GroupDef(
                name=group_def.get('name', 'main'),
                type=group_def.get('type', 'group'),
                threshold=group_def.get('threshold'),
                children=[GroupDef(**child) for child in group_def.get('children', [])] if group_def.get('children') else None
            )
        else:
            # 기본 그룹
            group = GroupDef(
                name="main",
                type="group",
                children=[
                    GroupDef(name="A_Init", type="rule"),
                    GroupDef(name="B_Scale", type="rule"),
                    GroupDef(name="C_Normalize", type="rule"),
                    GroupDef(name="D_Transform", type="rule"),
                    GroupDef(name="E_Finalize", type="rule")
                ]
            )
        
        # 실행
        result = engine.execute_group(group, input_data)
        
        # 타임라인 생성
        timeline = engine.generate_timeline()
        
        # 요약 생성
        summary = engine.get_summary()
        
        # 로그 저장
        log_file = "/app/log/annotations.jsonl"
        with open(log_file, "a") as f:
            for event in engine.log_events:
                f.write(json.dumps(event) + "\n")
        
        return jsonify({
            "output": result.output.tolist() if hasattr(result.output, 'tolist') else result.output,
            "blocked": result.blocked,
            "path": result.path,
            "timeline": timeline,
            "summary": summary,
            "events": engine.log_events
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """헬스 체크"""
    return jsonify({"status": "healthy", "version": "v2-min+"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
