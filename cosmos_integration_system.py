#!/usr/bin/env python3
"""
COSMOS-HGP Complete Integration System
=====================================

완전한 COSMOS-HGP 시스템을 다른 프로젝트에서 재사용할 수 있도록 정리한 통합 모듈입니다.

주요 기능:
- 7계층 계층구조 (Quantum → Atomic → Molecular → Compound → Organic → Ecosystem → Cosmos)
- 3가지 운영 모드 (Stability, Innovation, Adaptive)
- DNA 코돈 기반 인코딩 (64개 코돈)
- MetaBall 집계 시스템
- 실시간 WebSocket 스트리밍
- BeadFlow 물리 시뮬레이션
- React 대시보드 통합

사용법:
    from cosmos_integration_system import CosmosIntegrationSystem
    
    # 시스템 초기화
    cosmos = CosmosIntegrationSystem()
    
    # 백엔드 시작
    cosmos.start_backend(port=5000)
    
    # 프론트엔드 빌드 및 서빙
    cosmos.build_frontend()
    cosmos.serve_frontend(port=3000)

필요한 패키지:
    pip install flask flask-socketio fastapi uvicorn websockets
    pip install numpy pandas matplotlib plotly
    pip install nodejs npm (시스템에 설치)
"""

import json
import time
import asyncio
import threading
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from functools import wraps

# Flask 및 WebSocket 관련
try:
    from flask import Flask, jsonify, request
    from flask_socketio import SocketIO, emit
    from flask_cors import CORS
except ImportError:
    print("Flask 관련 패키지가 필요합니다: pip install flask flask-socketio flask-cors")
    raise

# 데이터 처리 관련
try:
    import numpy as np
    import pandas as pd
except ImportError:
    print("데이터 처리 패키지가 필요합니다: pip install numpy pandas")
    raise

# 인증 시스템
try:
    from auth_system import get_auth, UserTier
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    print("⚠️  Warning: auth_system.py not available")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CosmosIntegrationSystem:
    """
    COSMOS-HGP 완전 통합 시스템
    
    이 클래스는 전체 COSMOS-HGP 시스템을 관리하며,
    백엔드 API, WebSocket 서버, 프론트엔드 빌드를 모두 포함합니다.
    """
    
    def __init__(self, project_name: str = "cosmos-hgp"):
        """
        COSMOS 통합 시스템 초기화
        
        Args:
            project_name: 프로젝트 이름
        """
        self.project_name = project_name
        self.backend_port = 5000
        self.frontend_port = 3000
        
        # Flask 앱 초기화
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'cosmos-secret-key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        CORS(self.app)
        
        # 인증 시스템 초기화
        self.auth = get_auth() if AUTH_AVAILABLE else None
        
        # 시스템 상태
        self.is_running = False
        self.connected_clients = set()
        self.execution_history = []
        self.current_mode = 'stability'
        self.threshold = 0.33
        
        # 7계층 정의
        self.layers = {
            1: 'Quantum',
            2: 'Atomic', 
            3: 'Molecular',
            4: 'Compound',
            5: 'Organic',
            6: 'Ecosystem',
            7: 'Cosmos'
        }
        
        # DNA 코돈 매핑
        self.codon_map = self._generate_codon_map()
        
        # 인증 데코레이터 설정
        self._setup_auth_decorators()
        
        # 라우트 설정
        self._setup_routes()
        self._setup_socketio_events()
    
    def _setup_auth_decorators(self):
        """인증 데코레이터 설정"""
        if not AUTH_AVAILABLE:
            return
        
        # 데코레이터: API 키 검증
        def require_auth(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                api_key = request.headers.get('X-API-Key')
                
                if not api_key:
                    return jsonify({'error': 'API key required', 'code': 'AUTH_REQUIRED'}), 401
                
                if not self.auth.verify_api_key(api_key):
                    return jsonify({'error': 'Invalid API key', 'code': 'AUTH_INVALID'}), 401
                
                # 사용량 체크
                allowed, message = self.auth.check_usage_limit(api_key)
                if not allowed:
                    return jsonify({
                        'error': message, 
                        'code': 'QUOTA_EXCEEDED',
                        'upgrade_url': '/pricing'
                    }), 429
                
                # request에 사용자 정보 첨부
                request.cosmos_user = self.auth.get_user(api_key)
                request.api_key = api_key
                return f(*args, **kwargs)
            
            return decorated_function
        
        # 데코레이터: 기능별 권한 검증
        def require_feature(feature_name: str):
            def decorator(f):
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    api_key = request.headers.get('X-API-Key')
                    
                    if not self.auth.check_feature_access(api_key, feature_name):
                        user = self.auth.get_user(api_key)
                        return jsonify({
                            'error': f'Feature "{feature_name}" not available in {user.tier.value} tier',
                            'code': 'FEATURE_LOCKED',
                            'upgrade_url': '/pricing'
                        }), 403
                    
                    return f(*args, **kwargs)
                return decorated_function
            return decorator
        
        # 데코레이터들을 인스턴스에 저장
        self.require_auth = require_auth
        self.require_feature = require_feature
    
    def _generate_codon_map(self) -> Dict[str, str]:
        """64개 DNA 코돈 매핑 생성"""
        bases = ['A', 'C', 'G', 'T']
        codons = {}
        
        for i, base1 in enumerate(bases):
            for j, base2 in enumerate(bases):
                for k, base3 in enumerate(bases):
                    codon = f"{base1}{base2}{base3}"
                    # 간단한 해시 기반 매핑
                    codon_id = i * 16 + j * 4 + k
                    codons[codon] = {
                        'id': codon_id,
                        'type': ['processing', 'filtering', 'routing', 'aggregation'][codon_id % 4],
                        'complexity': (codon_id % 10) / 10.0
                    }
        
        return codons
    
    def _setup_routes(self):
        """Flask 라우트 설정"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """시스템 상태 확인"""
            return jsonify({
                'healthy': True,
                'system': 'COSMOS-HGP',
                'version': '2.0.0',
                'mode': self.current_mode,
                'threshold': self.threshold,
                'connected_clients': len(self.connected_clients),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/cosmos/execute', methods=['POST'])
        def execute_cosmos():
            """COSMOS 실행 엔드포인트"""
            try:
                data = request.get_json()
                group = data.get('group', 'standard_pipeline')
                input_data = data.get('input', [])
                profile = data.get('profile', self.current_mode)
                options = data.get('options', {})
                
                # 인증이 활성화된 경우 인증 체크
                if AUTH_AVAILABLE and hasattr(self, 'require_auth'):
                    # API 키 검증
                    api_key = request.headers.get('X-API-Key')
                    if not api_key:
                        return jsonify({'error': 'API key required', 'code': 'AUTH_REQUIRED'}), 401
                    
                    if not self.auth.verify_api_key(api_key):
                        return jsonify({'error': 'Invalid API key', 'code': 'AUTH_INVALID'}), 401
                    
                    # 사용량 체크
                    allowed, message = self.auth.check_usage_limit(api_key)
                    if not allowed:
                        return jsonify({
                            'error': message, 
                            'code': 'QUOTA_EXCEEDED',
                            'upgrade_url': '/pricing'
                        }), 429
                    
                    # 입력 크기 제한 체크
                    user = self.auth.get_user(api_key)
                    limits = self.auth.get_tier_limits(user.tier)
                    input_size = len(str(input_data))
                    if input_size > limits.max_input_size:
                        return jsonify({
                            'error': f'Input size ({input_size} bytes) exceeds limit ({limits.max_input_size} bytes)',
                            'code': 'INPUT_TOO_LARGE'
                        }), 413
                
                # 실행 결과 생성
                result = self._execute_cosmos_logic(group, input_data, profile, options)
                
                # 인증이 활성화된 경우 사용량 증가
                if AUTH_AVAILABLE and api_key:
                    self.auth.increment_usage(api_key)
                    result['usage'] = self.auth.get_usage_stats(api_key)
                
                # WebSocket으로 결과 브로드캐스트
                self._broadcast_execution_result(result)
                
                return jsonify(result), 200
                
            except Exception as e:
                logger.error(f"Execution error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/cosmos/config', methods=['GET', 'POST'])
        def config_cosmos():
            """시스템 설정 관리"""
            if request.method == 'GET':
                return jsonify({
                    'mode': self.current_mode,
                    'threshold': self.threshold,
                    'layers': self.layers,
                    'codon_count': len(self.codon_map)
                })
            
            elif request.method == 'POST':
                data = request.get_json()
                if 'mode' in data:
                    self.current_mode = data['mode']
                if 'threshold' in data:
                    self.threshold = max(0.0, min(1.0, float(data['threshold'])))
                
                # 설정 변경을 모든 클라이언트에 알림
                self.socketio.emit('config_updated', {
                    'mode': self.current_mode,
                    'threshold': self.threshold
                })
                
                return jsonify({'status': 'updated'}), 200
        
        @self.app.route('/api/cosmos/stats', methods=['GET'])
        def get_stats():
            """실행 통계 조회"""
            return jsonify({
                'total_executions': len(self.execution_history),
                'mode': self.current_mode,
                'threshold': self.threshold,
                'recent_executions': self.execution_history[-10:],
                'connected_clients': len(self.connected_clients)
            })
        
        # 인증 관련 엔드포인트들
        @self.app.route('/api/auth/usage', methods=['GET'])
        def get_usage():
            """사용량 통계 조회"""
            if not AUTH_AVAILABLE:
                return jsonify({'error': 'Authentication not available'}), 503
            
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
            
            stats = self.auth.get_usage_stats(api_key)
            if not stats:
                return jsonify({'error': 'Invalid API key'}), 401
            
            return jsonify(stats), 200
        
        @self.app.route('/api/auth/features', methods=['GET'])
        def get_features():
            """사용 가능한 기능 목록 조회"""
            if not AUTH_AVAILABLE:
                return jsonify({'error': 'Authentication not available'}), 503
            
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
            
            user = self.auth.get_user(api_key)
            if not user:
                return jsonify({'error': 'Invalid API key'}), 401
            
            limits = self.auth.get_tier_limits(user.tier)
            
            return jsonify({
                'tier': user.tier.value,
                'features': limits.features,
                'limits': {
                    'monthly_executions': limits.monthly_executions,
                    'max_input_size': limits.max_input_size,
                    'max_concurrent': limits.max_concurrent,
                    'cascade_prediction': limits.cascade_prediction,
                    'annotation_access': limits.annotation_access
                }
            }), 200
        
        @self.app.route('/api/auth/demo-keys', methods=['GET'])
        def get_demo_keys():
            """데모 API 키 목록 조회 (개발용)"""
            if not AUTH_AVAILABLE:
                return jsonify({'error': 'Authentication not available'}), 503
            
            demo_keys = [
                {
                    'api_key': 'demo_free_key_123',
                    'tier': 'free',
                    'description': 'Free tier - 50 executions/month'
                },
                {
                    'api_key': 'demo_pro_key_456', 
                    'tier': 'pro',
                    'description': 'Pro tier - 5000 executions/month'
                },
                {
                    'api_key': 'demo_enterprise_key_789',
                    'tier': 'enterprise', 
                    'description': 'Enterprise tier - Unlimited executions'
                }
            ]
            
            return jsonify({'demo_keys': demo_keys}), 200
    
    def _setup_socketio_events(self):
        """WebSocket 이벤트 설정"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """클라이언트 연결 처리"""
            self.connected_clients.add(request.sid)
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {
                'message': 'COSMOS stream ready',
                'client_id': request.sid,
                'system_status': 'online'
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """클라이언트 연결 해제 처리"""
            self.connected_clients.discard(request.sid)
            logger.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('request_execution')
        def handle_execution_request(data):
            """실시간 실행 요청 처리"""
            try:
                group = data.get('group', 'standard_pipeline')
                input_data = data.get('input', [])
                
                result = self._execute_cosmos_logic(group, input_data, self.current_mode, {})
                emit('execution_result', result)
                
            except Exception as e:
                emit('execution_error', {'error': str(e)})
    
    def _execute_cosmos_logic(self, group: str, input_data: List[Any], 
                            profile: str, options: Dict) -> Dict:
        """
        COSMOS 실행 로직 (시뮬레이션)
        
        실제 COSMOS 엔진과 연결되면 이 부분을 교체합니다.
        """
        execution_path = []
        total_impact = 0.0
        
        # 입력 데이터를 7계층으로 처리
        for i, item in enumerate(input_data):
            layer_num = (i % 7) + 1
            layer_name = self.layers[layer_num]
            
            # 임팩트 계산 (시뮬레이션)
            impact = min(1.0, abs(item) / 10.0 if isinstance(item, (int, float)) else 0.5)
            total_impact += impact
            
            # 임계값 체크
            is_blocked = impact >= self.threshold
            status = 'BLOCKED' if is_blocked else 'PASSED'
            
            # 코돈 생성
            codon = self._generate_codon_for_item(item, layer_num)
            
            step = {
                'step': i + 1,
                'layer': layer_name,
                'layer_number': layer_num,
                'impact': impact,
                'threshold': self.threshold,
                'status': status,
                'blocked': is_blocked,
                'codon': codon,
                'rule': f"rule_{group}_{layer_name.lower()}",
                'timestamp': datetime.now().isoformat()
            }
            
            execution_path.append(step)
        
        # 메트릭스 계산
        metrics = {
            'total_impact': total_impact,
            'average_impact': total_impact / len(input_data) if input_data else 0,
            'blocked_count': sum(1 for step in execution_path if step['blocked']),
            'cascade_depth': self._calculate_cascade_depth(execution_path),
            'execution_path': execution_path
        }
        
        result = {
            'execution_id': f"exec_{int(time.time() * 1000)}",
            'group': group,
            'profile': profile,
            'input': input_data,
            'metrics': metrics,
            'mode': self.current_mode,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        # 실행 히스토리에 추가
        self.execution_history.append(result)
        if len(self.execution_history) > 100:  # 최대 100개 유지
            self.execution_history.pop(0)
        
        return result
    
    def _generate_codon_for_item(self, item: Any, layer_num: int) -> str:
        """아이템과 계층에 기반한 코돈 생성"""
        # 간단한 해시 기반 코돈 생성
        item_str = str(item)
        hash_val = hash(item_str + str(layer_num)) % 64
        
        bases = ['A', 'C', 'G', 'T']
        a = bases[hash_val % 4]
        b = bases[(hash_val // 4) % 4]
        c = bases[(hash_val // 16) % 4]
        
        return f"{a}{b}{c}"
    
    def _calculate_cascade_depth(self, execution_path: List[Dict]) -> int:
        """캐스케이드 깊이 계산"""
        depth = 0
        current_depth = 0
        
        for step in execution_path:
            if step['blocked']:
                current_depth += 1
                depth = max(depth, current_depth)
            else:
                current_depth = 0
        
        return depth
    
    def _broadcast_execution_result(self, result: Dict):
        """실행 결과를 모든 클라이언트에 브로드캐스트"""
        self.socketio.emit('execution_result', result)
        logger.info(f"Broadcasted execution result to {len(self.connected_clients)} clients")
    
    def create_frontend_files(self, output_dir: str = "cosmos_frontend"):
        """React 프론트엔드 파일 생성"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # package.json 생성
        package_json = {
            "name": f"{self.project_name}-dashboard",
            "version": "2.0.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
                "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "framer-motion": "^10.16.4",
                "recharts": "^2.8.0",
                "lucide-react": "^0.294.0",
                "d3": "^7.8.5",
                "socket.io-client": "^4.7.2"
            },
            "devDependencies": {
                "@types/react": "^18.2.37",
                "@types/react-dom": "^18.2.15",
                "@vitejs/plugin-react": "^4.1.0",
                "vite": "^5.0.0",
                "eslint": "^8.53.0",
                "eslint-plugin-react": "^7.33.2",
                "eslint-plugin-react-hooks": "^4.6.0",
                "eslint-plugin-react-refresh": "^0.4.4",
                "tailwindcss": "^3.3.0",
                "autoprefixer": "^10.4.16",
                "postcss": "^8.4.31"
            }
        }
        
        with open(output_path / "package.json", 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # vite.config.js 생성
        vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        ws: true
      }
    }
  }
})"""
        
        with open(output_path / "vite.config.js", 'w') as f:
            f.write(vite_config)
        
        # tailwind.config.js 생성
        tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cosmos: {
          gold: '#FFD700',
          'gold-dark': '#FFA500',
          'gold-soft': '#FFF7D6'
        }
      }
    },
  },
  plugins: [],
}"""
        
        with open(output_path / "tailwind.config.js", 'w') as f:
            f.write(tailwind_config)
        
        # src 디렉토리 생성
        src_path = output_path / "src"
        src_path.mkdir(exist_ok=True)
        
        # index.html 생성
        index_html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>COSMOS-HGP Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>"""
        
        with open(output_path / "index.html", 'w') as f:
            f.write(index_html)
        
        # main.jsx 생성
        main_jsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)"""
        
        with open(src_path / "main.jsx", 'w') as f:
            f.write(main_jsx)
        
        # App.jsx 생성
        app_jsx = """import CosmosBeadFlowDashboard from './CosmosBeadFlowDashboard'

function App() {
  return <CosmosBeadFlowDashboard />
}

export default App"""
        
        with open(src_path / "App.jsx", 'w') as f:
            f.write(app_jsx)
        
        # index.css 생성
        index_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}"""
        
        with open(src_path / "index.css", 'w') as f:
            f.write(index_css)
        
        # CosmosBeadFlowDashboard.jsx 생성 (간소화된 버전)
        dashboard_jsx = self._generate_dashboard_component()
        
        with open(src_path / "CosmosBeadFlowDashboard.jsx", 'w') as f:
            f.write(dashboard_jsx)
        
        logger.info(f"Frontend files created in {output_path}")
        return output_path
    
    def _generate_dashboard_component(self) -> str:
        """대시보드 React 컴포넌트 생성"""
        return '''import React, { useEffect, useState, useRef, useMemo } from 'react';
import { io } from 'socket.io-client';

export default function CosmosBeadFlowDashboard() {
  const [series, setSeries] = useState([]);
  const [engineStatus, setEngineStatus] = useState('disconnected');
  const [stats, setStats] = useState({
    executions: 0,
    cascades: 0,
    mode: 'stability',
    avgImpact: 0
  });
  
  const [threshold, setThreshold] = useState(0.33);
  const [mode, setMode] = useState('stability');
  const [running, setRunning] = useState(true);
  
  const canvasRef = useRef(null);
  const socketRef = useRef(null);
  const animationRef = useRef(null);
  
  const W = 1400, H = 700;
  
  // WebSocket 연결
  useEffect(() => {
    socketRef.current = io('http://localhost:5000');
    
    socketRef.current.on('connect', () => {
      console.log('✓ COSMOS Engine connected');
      setEngineStatus('connected');
    });
    
    socketRef.current.on('disconnect', () => {
      console.log('COSMOS Engine disconnected');
      setEngineStatus('disconnected');
    });
    
    socketRef.current.on('execution_result', (data) => {
      const beads = transformExecution(data);
      setSeries(prev => [...prev, ...beads].slice(-200));
      setStats(prev => ({
        ...prev,
        executions: prev.executions + beads.length,
        cascades: prev.cascades + beads.filter(b => b.blocked).length
      }));
    });
    
    return () => {
      socketRef.current?.disconnect();
    };
  }, []);
  
  // 실행 결과를 비드 형식으로 변환
  const transformExecution = (execution) => {
    const { metrics = {} } = execution;
    const executionPath = metrics.execution_path || [];
    
    return executionPath.map((step, i) => ({
      id: `exec_${Date.now()}_${i}`,
      impact: Math.max(0, Math.min(1, step.impact || 0.1)),
      blocked: step.status === 'BLOCKED',
      cat: (step.layer_number - 1) % 7,
      layer: step.layer_number,
      codon: step.codon || 'AAA',
      ruleName: step.rule,
      threshold: step.threshold,
      mode: execution.mode,
      status: step.status,
      timestamp: Date.now()
    }));
  };
  
  // 원격 실행
  const executeRemote = async () => {
    try {
      const input = Array.from({ length: 10 }, () => Math.random() * 10);
      await fetch('http://localhost:5000/api/cosmos/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          group: 'standard_pipeline',
          input,
          profile: mode
        })
      });
    } catch (e) {
      console.error('Execution failed:', e);
    }
  };
  
  // 설정 업데이트
  const updateConfig = async (key, value) => {
    try {
      await fetch('http://localhost:5000/api/cosmos/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [key]: value })
      });
    } catch (e) {
      console.error('Config update failed:', e);
    }
  };
  
  // 애니메이션 루프
  useEffect(() => {
    if (!running) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const animation = () => {
      // 캔버스 클리어
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, W, H);
      
      // 그리드 그리기
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
      
      // 7개 레이어 빈 그리기
      for (let i = 0; i < 7; i++) {
        const x = W / 3 + i * 120;
        const y = H / 2 + (i % 2 ? 48 : -48);
        
        // 빈
        ctx.fillStyle = '#FFF7D6';
        ctx.strokeStyle = '#E0E0E0';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(x - 30, y - 28, 60, 56, 10);
        ctx.fill();
        ctx.stroke();
        
        // 레이어 라벨
        ctx.fillStyle = '#444';
        ctx.font = '12px ui-sans-serif';
        ctx.fillText(`L${i + 1}`, x - 8, y + 4);
      }
      
      // 라우터
      const routerX = W / 2 + 180;
      const routerY = H / 2;
      ctx.fillStyle = '#FFF2B0';
      ctx.beginPath();
      ctx.roundRect(routerX - 48, routerY - 26, 96, 52, 12);
      ctx.fill();
      ctx.stroke();
      ctx.fillText('Router', routerX - 22, routerY + 4);
      
      // 아웃렛
      const outletX = W - 120;
      const outletY = H / 2;
      ctx.fillStyle = '#FFF3C6';
      ctx.beginPath();
      ctx.moveTo(outletX - 30, outletY - 30);
      ctx.arc(outletX - 30, outletY, 30, -Math.PI / 2, Math.PI / 2);
      ctx.lineTo(outletX + 12, outletY);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      
      // 비드 그리기
      series.forEach((bead, i) => {
        const beadX = 100 + (i % 10) * 30;
        const beadY = 100 + Math.floor(i / 10) * 30;
        const beadRadius = 4 + bead.impact * 8;
        
        const color = bead.blocked ? '#000000' : 
                     bead.impact / threshold >= 0.75 ? '#1E1E1E' :
                     bead.impact / threshold >= 0.5 ? '#6A4A00' : '#E8B500';
        
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(beadX, beadY, beadRadius, 0, Math.PI * 2);
        ctx.fill();
      });
      
      animationRef.current = requestAnimationFrame(animation);
    };
    
    animationRef.current = requestAnimationFrame(animation);
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [running, series, threshold]);
  
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
            onChange={(e) => {
              setMode(e.target.value);
              updateConfig('mode', e.target.value);
            }}
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
            onChange={(e) => {
              const value = parseFloat(e.target.value);
              setThreshold(value);
              updateConfig('threshold', value);
            }}
            className="w-32"
          />
          <span>{threshold.toFixed(2)}</span>
        </label>
        
        <div className="ml-auto flex items-center gap-4 text-xs text-gray-600">
          <span>Beads: <strong>{series.length}</strong></span>
          <span>Executions: <strong>{stats.executions}</strong></span>
          <span>Cascades: <strong>{stats.cascades}</strong></span>
        </div>
      </div>
      
      {/* Canvas */}
      <div className="relative flex-1">
        <canvas 
          ref={canvasRef} 
          width={W} 
          height={H} 
          className="h-full w-full"
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
}'''
    
    def start_backend(self, port: int = 5000, debug: bool = False):
        """백엔드 서버 시작"""
        self.backend_port = port
        
        logger.info(f"Starting COSMOS-HGP backend on port {port}")
        logger.info("Available endpoints:")
        logger.info(f"  - Health: http://localhost:{port}/health")
        logger.info(f"  - Execute: http://localhost:{port}/api/cosmos/execute")
        logger.info(f"  - Config: http://localhost:{port}/api/cosmos/config")
        logger.info(f"  - Stats: http://localhost:{port}/api/cosmos/stats")
        logger.info(f"  - WebSocket: ws://localhost:{port}")
        
        self.is_running = True
        
        try:
            self.socketio.run(
                self.app,
                host='0.0.0.0',
                port=port,
                debug=debug,
                allow_unsafe_werkzeug=True
            )
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.is_running = False
    
    def build_frontend(self, frontend_dir: str = "cosmos_frontend") -> bool:
        """프론트엔드 빌드"""
        frontend_path = Path(frontend_dir)
        
        if not frontend_path.exists():
            logger.info("Creating frontend files...")
            self.create_frontend_files(frontend_dir)
        
        logger.info("Installing frontend dependencies...")
        try:
            subprocess.run(['npm', 'install'], cwd=frontend_path, check=True)
            logger.info("Frontend dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install frontend dependencies: {e}")
            return False
        except FileNotFoundError:
            logger.error("Node.js/npm not found. Please install Node.js first.")
            return False
    
    def serve_frontend(self, frontend_dir: str = "cosmos_frontend", port: int = 3000):
        """프론트엔드 개발 서버 시작"""
        frontend_path = Path(frontend_dir)
        
        if not frontend_path.exists():
            logger.error("Frontend directory not found. Run build_frontend() first.")
            return
        
        self.frontend_port = port
        
        logger.info(f"Starting frontend development server on port {port}")
        
        try:
            subprocess.run(['npm', 'run', 'dev'], cwd=frontend_path)
        except KeyboardInterrupt:
            logger.info("Frontend server stopped by user")
        except subprocess.CalledProcessError as e:
            logger.error(f"Frontend server error: {e}")
    
    def run_full_system(self, backend_port: int = 5000, frontend_port: int = 3000):
        """전체 시스템 실행 (백엔드 + 프론트엔드)"""
        logger.info("Starting COSMOS-HGP Full System...")
        
        # 프론트엔드 빌드
        if not self.build_frontend():
            logger.error("Failed to build frontend")
            return
        
        # 백엔드를 별도 스레드에서 실행
        backend_thread = threading.Thread(
            target=self.start_backend,
            args=(backend_port, False),
            daemon=True
        )
        backend_thread.start()
        
        # 백엔드 시작 대기
        time.sleep(3)
        
        # 프론트엔드 서버 시작
        frontend_thread = threading.Thread(
            target=self.serve_frontend,
            args=("cosmos_frontend", frontend_port),
            daemon=True
        )
        frontend_thread.start()
        
        # 브라우저 열기
        time.sleep(5)
        webbrowser.open(f"http://localhost:{frontend_port}")
        
        logger.info("COSMOS-HGP system is running!")
        logger.info(f"Backend: http://localhost:{backend_port}")
        logger.info(f"Frontend: http://localhost:{frontend_port}")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping COSMOS-HGP system...")
    
    def get_system_info(self) -> Dict:
        """시스템 정보 반환"""
        return {
            'project_name': self.project_name,
            'version': '2.0.0',
            'backend_port': self.backend_port,
            'frontend_port': self.frontend_port,
            'is_running': self.is_running,
            'connected_clients': len(self.connected_clients),
            'current_mode': self.current_mode,
            'threshold': self.threshold,
            'layers': self.layers,
            'codon_count': len(self.codon_map),
            'execution_count': len(self.execution_history)
        }


# 사용 예시 및 테스트 함수
def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='COSMOS-HGP Integration System')
    parser.add_argument('--mode', choices=['backend', 'frontend', 'full'], 
                       default='full', help='실행 모드')
    parser.add_argument('--backend-port', type=int, default=5000, 
                       help='백엔드 포트')
    parser.add_argument('--frontend-port', type=int, default=3000, 
                       help='프론트엔드 포트')
    parser.add_argument('--debug', action='store_true', 
                       help='디버그 모드')
    
    args = parser.parse_args()
    
    # COSMOS 시스템 초기화
    cosmos = CosmosIntegrationSystem("cosmos-hgp-demo")
    
    if args.mode == 'backend':
        cosmos.start_backend(args.backend_port, args.debug)
    elif args.mode == 'frontend':
        cosmos.serve_frontend("cosmos_frontend", args.frontend_port)
    elif args.mode == 'full':
        cosmos.run_full_system(args.backend_port, args.frontend_port)


if __name__ == "__main__":
    main()
