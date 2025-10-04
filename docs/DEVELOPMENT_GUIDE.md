# 🚀 COSMOS 개발 및 확장 가이드

## 목차
- [프로젝트 구조](#프로젝트-구조)
- [개발 환경 설정](#개발-환경-설정)
- [컴포넌트 확장](#컴포넌트-확장)
- [물리 엔진 커스터마이징](#물리-엔진-커스터마이징)
- [백엔드 API 확장](#백엔드-api-확장)
- [디버깅 및 프로파일링](#디버깅-및-프로파일링)

---

## 프로젝트 구조

```
COSMOS_V1/
├── web/                          # 프론트엔드 (React + Vite)
│   ├── src/
│   │   ├── BeadFlowMessenger.jsx # 메인 대시보드 컴포넌트
│   │   ├── DebugProfiler.jsx     # 성능 프로파일러
│   │   ├── main.jsx              # 엔트리 포인트
│   │   └── index.css             # 글로벌 스타일
│   ├── package.json              # 프론트엔드 의존성
│   ├── vite.config.js            # Vite 설정
│   ├── start-dev.bat             # Windows 개발 서버 시작
│   ├── start-dev.sh              # Linux 개발 서버 시작
│   ├── setup-ports.ps1           # 포트 설정 (수동)
│   ├── setup-ports-auto.ps1      # 포트 설정 (자동)
│   └── README-SETUP.md           # 포트 설정 가이드
│
├── cosmos_integration_system.py  # 통합 시스템 (Python)
├── auth_system.py                # 인증 시스템
├── simple_backend.py             # 간단한 HTTP 서버
├── test.py                       # 테스트 스크립트
│
├── docs/                         # 문서
│   ├── SERVER_TROUBLESHOOTING.md # 서버 문제 해결
│   ├── DEVELOPMENT_GUIDE.md      # 개발 가이드 (이 파일)
│   └── API_DOCS.md               # API 문서
│
├── start-cosmos.bat              # Windows 통합 시작 스크립트
├── add-firewall-rule.bat         # 방화벽 규칙 자동 추가
├── requirements.txt              # Python 의존성
├── README.md                     # 프로젝트 README
└── WORK_LOG.md                   # 작업 로그
```

---

## 개발 환경 설정

### 1. Python 환경

```bash
# 가상 환경 생성
python -m venv venv

# 활성화 (Linux/WSL)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. Node.js 환경

```bash
cd web
npm install
```

### 3. 개발 서버 실행

#### 옵션 1: 통합 실행 (권장)
```bash
# Windows
start-cosmos.bat

# Linux/WSL
./start-cosmos.sh
```

#### 옵션 2: 개별 실행
```bash
# 백엔드 (터미널 1)
python simple_backend.py

# 프론트엔드 (터미널 2)
cd web
npm run dev
```

### 4. 코드 품질 도구

```bash
# Python
pip install black flake8 pytest

# 코드 포맷팅
black *.py

# 린팅
flake8 *.py

# 테스트
pytest test.py
```

---

## 컴포넌트 확장

### BeadFlowMessenger 컴포넌트 구조

```javascript
// web/src/BeadFlowMessenger.jsx

export default function BeadFlowMessengerFull() {
  // 1. State 관리
  const [beads, setBeads] = useState([]);
  const [threshold, setThreshold] = useState(0.5);
  const [binCount, setBinCount] = useState(4);
  // ...

  // 2. 물리 엔진 (step 함수)
  function step(beads, layout, threshold, audio) {
    // 당구식 직선 이동 물리
    // 회전, 충돌, 중력 처리
  }

  // 3. 렌더링 (drawOnce 함수)
  function drawOnce(canvas, beads, layout, threshold, theme) {
    // Canvas 2D 렌더링
  }

  // 4. Layout 계산
  function layoutCompute(W, H, PAD, binCount) {
    // bins, router, outlet, inlets 위치 계산
  }

  // 5. Beads 생성
  function buildBeads(series, layout, threshold, carryMode, rand) {
    // 데이터 → 구슬 변환
  }

  return (
    <div>
      {/* UI 컨트롤 */}
      {/* Canvas */}
      {/* 프로파일러 */}
    </div>
  );
}
```

### 새로운 시각화 요소 추가

#### 예시: 트레일 효과 추가

```javascript
// 1. State 추가
const [trails, setTrails] = useState([]);

// 2. step 함수에서 트레일 기록
function step(beads, layout, threshold, audio) {
  // 기존 물리 엔진 코드...

  // 트레일 기록
  beads.forEach(b => {
    if (!b.trail) b.trail = [];
    b.trail.push({ x: b.p.x, y: b.p.y });
    if (b.trail.length > 30) b.trail.shift(); // 최대 30개
  });
}

// 3. drawOnce 함수에서 트레일 렌더링
function drawOnce(canvas, beads, layout, threshold, theme) {
  const ctx = canvas.getContext('2d');

  // 트레일 그리기
  for (const b of beads) {
    if (!b.trail || b.trail.length < 2) continue;

    ctx.save();
    ctx.strokeStyle = b.color;
    ctx.lineWidth = 1;
    ctx.globalAlpha = 0.3;
    ctx.beginPath();
    ctx.moveTo(b.trail[0].x, b.trail[0].y);
    for (let i = 1; i < b.trail.length; i++) {
      ctx.lineTo(b.trail[i].x, b.trail[i].y);
    }
    ctx.stroke();
    ctx.restore();
  }

  // 기존 구슬 렌더링 코드...
}
```

### 새로운 UI 컨트롤 추가

```javascript
// 1. State 추가
const [showTrails, setShowTrails] = useState(false);

// 2. UI 추가
<label className="flex items-center gap-2 text-sm">
  Show Trails
  <input
    type="checkbox"
    checked={showTrails}
    onChange={e => setShowTrails(e.target.checked)}
  />
</label>

// 3. drawOnce에서 조건부 렌더링
function drawOnce(canvas, beads, layout, threshold, theme) {
  // ...
  if (showTrails) {
    // 트레일 렌더링
  }
  // ...
}
```

---

## 물리 엔진 커스터마이징

### 현재 물리 엔진 파라미터

```javascript
// web/src/BeadFlowMessenger.jsx:277

const DT = 1/60;           // 프레임 시간 (고정 60fps)
const FRICTION = 0.985;    // 마찰 계수
const VMAX = 420;          // 최대 속도 (px/s)

// phase별 가속도
const ACC = b.phase===2 ? 220 : (b.phase===1 ? 160 : 140);

// phase별 중력
const GRAVITY = b.phase===2 ? 260 : 120;

// 충돌 반발계수
const e = 0.35;

// 도달 판정 거리
const arrivalDist = Math.max(8, b.r * 0.6);
```

### 물리 엔진 수정 예시

#### 예시 1: 속도 증가

```javascript
function step(beads, layout, threshold, audio) {
  const DT = 1/60;
  const FRICTION = 0.99;  // 마찰 감소 (빠르게)
  const VMAX = 600;       // 최대 속도 증가

  // phase별 가속도 증가
  const ACC = b.phase===2 ? 300 : (b.phase===1 ? 220 : 180);

  // ...
}
```

#### 예시 2: 부드러운 움직임

```javascript
function step(beads, layout, threshold, audio) {
  const DT = 1/60;
  const FRICTION = 0.95;  // 마찰 증가 (부드럽게)
  const VMAX = 300;       // 최대 속도 감소

  // 더 부드러운 가속
  const ACC = b.phase===2 ? 150 : (b.phase===1 ? 100 : 80);

  // ...
}
```

#### 예시 3: 튕기는 효과 강화

```javascript
function step(beads, layout, threshold, audio) {
  // ...

  // 충돌 처리
  for (const o of beads) {
    if (o === b || o.phase !== b.phase) continue;

    const cdx = b.p.x - o.p.x, cdy = b.p.y - o.p.y;
    const cd = Math.hypot(cdx, cdy);
    const minDist = b.r + o.r;

    if (cd < minDist && cd > 0) {
      // ...

      // 반발계수 증가 (더 튕김)
      const e = 0.8;  // 기본 0.35 → 0.8

      // ...
    }
  }
}
```

### 회전 속도 조절

```javascript
// web/src/BeadFlowMessenger.jsx:317

// 현재 코드
const angularVelocity = speed / (b.r * 10);

// 빠른 회전
const angularVelocity = speed / (b.r * 5);

// 느린 회전
const angularVelocity = speed / (b.r * 20);
```

---

## 백엔드 API 확장

### simple_backend.py 구조

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class CosmosHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            # ...
        elif self.path == '/api/demo':
            # 데모 데이터 반환
            # ...

    def do_POST(self):
        if self.path == '/api/execute':
            # POST 데이터 처리
            # ...
```

### 새로운 엔드포인트 추가

#### 예시: /api/stats 엔드포인트

```python
def do_GET(self):
    if self.path == '/health':
        # ...

    elif self.path == '/api/stats':
        # 통계 데이터 생성
        stats = {
            'total_beads': 100,
            'blocked': 15,
            'avg_impact': 0.45,
            'timestamp': time.time()
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode())
```

#### 프론트엔드에서 사용

```javascript
// web/src/BeadFlowMessenger.jsx

useEffect(() => {
  const fetchStats = async () => {
    try {
      const res = await fetch('http://localhost:5001/api/stats');
      const data = await res.json();
      console.log('Stats:', data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  fetchStats();
  const interval = setInterval(fetchStats, 5000); // 5초마다
  return () => clearInterval(interval);
}, []);
```

### 데이터 스키마 수정

```python
# simple_backend.py

def generate_demo_data(count=100):
    """데모 데이터 생성"""
    data = []
    for i in range(count):
        item = {
            'id': f's{i}',
            'impact': round(random.uniform(0.1, 0.9), 3),
            'blocked': random.random() < 0.15,
            'cat': i % 4,
            'layer': (i % 7) + 1,
            'codon': generate_codon(i),

            # 새로운 필드 추가
            'priority': random.choice(['high', 'medium', 'low']),
            'timestamp': time.time() + i,
        }
        data.append(item)
    return data
```

---

## 디버깅 및 프로파일링

### DebugProfiler 사용법

```javascript
// web/src/main.jsx 또는 BeadFlowMessenger.jsx

import DebugProfiler from './DebugProfiler.jsx';

function App() {
  const [showProfiler, setShowProfiler] = useState(true);

  return (
    <div>
      {/* 앱 컨텐츠 */}

      {/* 프로파일러 */}
      <DebugProfiler
        enabled={showProfiler}
        position="top-right"  // top-left, bottom-right, bottom-left
      />
    </div>
  );
}
```

### usePerformance 훅 사용

```javascript
import { usePerformance } from './DebugProfiler.jsx';

function MyComponent() {
  const { fps, frameTime, memory } = usePerformance();

  return (
    <div>
      <p>FPS: {fps}</p>
      <p>Frame Time: {frameTime.toFixed(2)}ms</p>
      <p>Memory: {memory.toFixed(2)}MB</p>
    </div>
  );
}
```

### Performance Logger 사용

```javascript
import { perfLogger } from './DebugProfiler.jsx';

function expensiveOperation() {
  perfLogger.mark('operation-start');

  // 시간이 걸리는 작업...

  perfLogger.mark('operation-end');
  perfLogger.measure('operation-duration', 'operation-start', 'operation-end');

  // 콘솔에 리포트 출력
  perfLogger.log();
}
```

### Canvas 렌더링 최적화

#### 오프스크린 캔버스 사용

```javascript
const offscreenCanvas = document.createElement('canvas');
const offscreenCtx = offscreenCanvas.getContext('2d');

offscreenCanvas.width = W;
offscreenCanvas.height = H;

// 오프스크린에 렌더링
drawOnce(offscreenCanvas, beads, layout, threshold, theme);

// 메인 캔버스에 복사
const mainCtx = canvas.getContext('2d');
mainCtx.drawImage(offscreenCanvas, 0, 0);
```

#### 불필요한 렌더링 스킵

```javascript
const lastRenderTimeRef = useRef(0);

useEffect(() => {
  if (!running) return;

  const draw = (timestamp) => {
    // 60fps 제한 (16.67ms)
    if (timestamp - lastRenderTimeRef.current < 16.67) {
      rafIdRef.current = requestAnimationFrame(draw);
      return;
    }

    lastRenderTimeRef.current = timestamp;

    step(beads, layout, threshold, audio);
    drawOnce(canvas, beads, layout, threshold, theme);

    rafIdRef.current = requestAnimationFrame(draw);
  };

  rafIdRef.current = requestAnimationFrame(draw);
  return () => cancelAnimationFrame(rafIdRef.current);
}, [running, beads, layout, threshold]);
```

---

## 테스트

### 프론트엔드 테스트

```bash
cd web
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom
```

```javascript
// web/src/BeadFlowMessenger.test.jsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import BeadFlowMessengerFull from './BeadFlowMessenger.jsx';

describe('BeadFlowMessenger', () => {
  it('renders without crashing', () => {
    render(<BeadFlowMessengerFull />);
    expect(screen.getByText(/BeadFlow/i)).toBeInTheDocument();
  });

  it('updates threshold value', () => {
    const { container } = render(<BeadFlowMessengerFull />);
    const slider = container.querySelector('input[type="range"]');

    fireEvent.change(slider, { target: { value: '0.75' } });
    expect(slider.value).toBe('0.75');
  });
});
```

### 백엔드 테스트

```python
# test_backend.py
import unittest
import requests

class TestBackend(unittest.TestCase):
    BASE_URL = 'http://localhost:5001'

    def test_health(self):
        response = requests.get(f'{self.BASE_URL}/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')

    def test_demo_data(self):
        response = requests.get(f'{self.BASE_URL}/api/demo')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

if __name__ == '__main__':
    unittest.main()
```

---

## 배포

### Docker 컨테이너화

```dockerfile
# Dockerfile
FROM node:18-alpine AS frontend-build

WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ ./
RUN npm run build

FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=frontend-build /app/web/dist ./web/dist
COPY *.py ./

EXPOSE 5001 5173

CMD ["python", "simple_backend.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  cosmos:
    build: .
    ports:
      - "5001:5001"
      - "5173:5173"
    environment:
      - NODE_ENV=production
    volumes:
      - ./data:/app/data
```

---

**마지막 업데이트**: 2025-10-04
**작성자**: Claude Code
