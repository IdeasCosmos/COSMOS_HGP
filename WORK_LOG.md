# COSMOS-HGP 통합 작업 기록

## 📅 작업 일시
- 시작: 2025-10-04
- 담당: Claude Code AI

---

## 🎯 작업 목표
React 프론트엔드 대시보드를 실행하고 백엔드와 연결하여 COSMOS-HGP 시스템 완성

---

## 📋 작업 단계별 기록

### 1단계: 프로젝트 구조 분석 ✅
**시간**: 초기
**작업 내용**:
- 프로젝트 파일 구조 스캔
- 3개의 주요 파일 발견:
  - `import React, { useEffect, useMemo, useR.js` (이상한 파일명)
  - `대시보드.ini` (요구사항 명세)
  - `Dashboard.jsx` (기존 대시보드)

**발견 사항**:
- 파일명이 잘못됨 (JavaScript 코드가 파일명에 포함됨)
- `대시보드.ini`에 당구식 물리 엔진 요구사항 명시됨
- 고무줄 느낌 제거 필요

---

### 2단계: 물리 엔진 수정 ✅
**파일**: `web/src/BeadFlowMessenger.jsx` (이름 변경 후)

**수정 전** (270-290번째 줄):
```javascript
// 스프링 기반 물리
const ax = (tgt.x - b.p.x) * 0.010 * b.jitter;
const ay = (tgt.y - b.p.y) * 0.010 * b.jitter + (b.phase===2? 0.15 : 0.06);
b.v.x = (b.v.x + ax) * 0.965;
b.v.y = (b.v.y + ay) * 0.965;
```

**수정 후** (270-346번째 줄):
```javascript
// 당구식 직선 이동 물리 엔진
const DT = 1/60, FRICTION = 0.985, VMAX = 420;
const ACC = [140, 160, 220]; // [inlet→bin, bin→router, router→outlet] px/s²
const GRAVITY = [120, 120, 260]; // phase별 중력

// 직선 방향 벡터 계산
const dx = tgt.x - b.p.x, dy = tgt.y - b.p.y;
const len = Math.hypot(dx, dy) || 1;
const ux = dx/len, uy = dy/len;

// 가속도 적용
const acc = ACC[b.phase];
const grav = GRAVITY[b.phase];
b.v.x += ux * acc * DT;
b.v.y += (uy * acc + grav) * DT;

// 마찰 적용
b.v.x *= FRICTION; b.v.y *= FRICTION;

// 최대 속도 제한
const speed = Math.hypot(b.v.x, b.v.y);
if(speed > VMAX){ b.v.x *= VMAX/speed; b.v.y *= VMAX/speed; }

// 충돌 (반발계수 0.35)
const e=0.35;
const vrel_n = (b.v.x-o.v.x)*nx + (b.v.y-o.v.y)*ny;
if(vrel_n < 0){
  const impulse = -(1+e)*vrel_n/2;
  b.v.x += impulse*nx; b.v.y += impulse*ny;
  o.v.x -= impulse*nx; o.v.y -= impulse*ny;
}
```

**변경 사항**:
- ❌ 제거: 스프링 기반 탄성, 고무줄 느낌, 지터
- ✅ 추가: 60fps 고정, 직선 가속도, 반발 충돌, 속도 제한

---

### 3단계: 파일 구조 정리 ✅
**작업**:
```bash
# 이상한 파일명 변경
mv "import React, { useEffect, useMemo, useR.js" "web/src/BeadFlowMessenger.jsx"
```

**main.jsx 수정**:
```javascript
// Before
import Dashboard from './Dashboard.jsx'

// After
import BeadFlowMessengerFull from './BeadFlowMessenger.jsx'
```

---

### 4단계: 백엔드 서버 구축 ✅
**문제**: Flask가 설치되지 않음 (외부 관리 환경)

**해결책**: Flask 없이 작동하는 간단한 HTTP 서버 작성

**파일**: `simple_backend.py`
```python
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import time

class CosmosHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # CORS 헤더
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if self.path == '/health':
            response = {'status': 'ok', 'service': 'COSMOS-HGP Backend'}
        elif self.path == '/api/demo':
            response = {'beads': self.generate_demo_beads(20)}

        self.wfile.write(json.dumps(response).encode())
```

**실행**:
```bash
python3 simple_backend.py  # 포트 5001
```

---

### 5단계: 프론트엔드 실행 ✅
```bash
cd web
npm run dev  # 포트 5173
```

**결과**:
- ✅ Vite 서버 정상 실행
- ✅ 포트 5173, 5001 모두 리스닝 중

---

### 6단계: WSL 포트 포워딩 설정 ✅
**문제**: Windows 브라우저에서 WSL 서버 접속 불가

**해결책 파일들**:

#### 1. `add-firewall-rule.bat` (방화벽 설정)
```batch
@echo off
netsh advfirewall firewall add rule name="COSMOS_Frontend_Vite" dir=in action=allow protocol=TCP localport=5173
netsh advfirewall firewall add rule name="COSMOS_Backend_API" dir=in action=allow protocol=TCP localport=5001
```

#### 2. `setup-wsl-port-forward.ps1` (포트 포워딩)
```powershell
$wslIp = (wsl hostname -I).Trim().Split()[0]
netsh interface portproxy add v4tov4 listenport=5173 listenaddress=0.0.0.0 connectport=5173 connectaddress=$wslIp
netsh interface portproxy add v4tov4 listenport=5001 listenaddress=0.0.0.0 connectport=5001 connectaddress=$wslIp
```

#### 3. `start-cosmos.bat` (자동 실행 스크립트)
```batch
@echo off
start "COSMOS Backend" wsl -d Ubuntu -- bash -c "cd %WSL_PATH% && python3 simple_backend.py"
start "COSMOS Frontend" wsl -d Ubuntu -- bash -c "cd %WSL_PATH%/web && npm run dev"
start http://localhost:5173
```

---

### 7단계: 디버깅 - 흰 화면 문제 🔧

#### 문제 1: React 작동 확인
**테스트 파일 생성**: `SimpleTest.jsx`
```javascript
export default function SimpleTest() {
  return <h1>✅ React가 정상적으로 작동합니다!</h1>
}
```

**결과**: ✅ React는 정상 작동

---

#### 문제 2: BeadFlowMessenger 에러
**에러**: `ReferenceError: clamp01 is not defined`

**원인**: 228번째 줄에서 사용되는 `clamp01` 함수가 정의되지 않음
```javascript
const thEff = clamp01(threshold + 0);  // ❌ 함수 없음
```

**해결**: 407번째 줄에 함수 추가
```javascript
/* ---------------- Utility functions ---------------- */
function clamp01(x){ return Math.max(0, Math.min(1, x)); }
```

---

#### 문제 3: 에러 바운더리 추가
**파일**: `main.jsx`
```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('React Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{padding: '50px'}}>
          <h1>⚠️ 에러 발생</h1>
          <pre>{this.state.error?.toString()}</pre>
          <button onClick={() => window.location.reload()}>새로고침</button>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BeadFlowMessengerFull />
    </ErrorBoundary>
  </React.StrictMode>,
)
```

**효과**: 에러 발생 시 정확한 에러 메시지 표시

---

## 📊 최종 시스템 구성

### 실행 중인 서버
1. **프론트엔드**: `http://localhost:5173`
   - Vite 개발 서버
   - React 18 + BeadFlow 시각화

2. **백엔드**: `http://localhost:5001`
   - Python HTTP 서버
   - CORS 지원
   - API 엔드포인트: `/health`, `/api/demo`, `/api/execute`

### 포트 정보
- `5173`: Vite 프론트엔드
- `5001`: Python 백엔드
- WSL IP: `172.31.71.146`

---

## ✅ 정상 작동하는 기능

### 물리 엔진
- ✅ 당구식 직선 이동
- ✅ 60fps 고정
- ✅ 반발계수 0.35
- ✅ 최대 속도 420 px/s
- ✅ 직선 가속도 (140→160→220)

### 시각화
- ✅ 골드&화이트 테마
- ✅ 7계층 bins (1-7)
- ✅ 64개 코돈 크기 스케일링
- ✅ 임계값 기반 색상 전환 (금색→갈색→검정)
- ✅ 메신저형 사이드바

### 기능
- ✅ Threshold 슬라이더 (0.00-1.00)
- ✅ Bins 조정 (1-8)
- ✅ Darkening 모드 (carry/resetLayer/resetAlways)
- ✅ MetaBall 집계 (on/off, factor 2-32)
- ✅ 사운드 시스템 (충돌, 통과, bin 유입)
- ✅ High-Contrast 모드
- ✅ PNG Export
- ✅ WebM Recording
- ✅ JSON Export/Import
- ✅ 툴팁 (마우스 오버)
- ✅ 실시간 메트릭 (total, meta, avg, blocked, near, var)

### 백엔드 API
- ✅ Health check: `GET /health`
- ✅ Demo data: `GET /api/demo`
- ✅ Execute: `POST /api/execute`

---

## ⚠️ 현재 작동하지 않는 기능

### WebSocket 실시간 스트리밍
- ❌ HTTP 서버만 구현되어 있음
- ❌ WebSocket 미지원
- 📝 향후 작업: `python-socketio` 또는 `websockets` 라이브러리 추가 필요

### 인증 시스템
- ❌ 백엔드에 미구현
- 📝 `auth_system.py` 파일은 있으나 통합 안 됨

### 고급 COSMOS 기능
- ❌ 7계층 전파 시뮬레이션
- ❌ 모드 전환 (Stability/Innovation/Adaptive)
- ❌ 실제 데이터 처리 (현재 데모 데이터만)

---

## 🐛 발생했던 버그 및 해결

### Bug #1: 파일명 오류
- **증상**: `import React, { useEffect, useMemo, useR.js` 파일을 찾을 수 없음
- **원인**: JavaScript 코드가 파일명에 포함됨
- **해결**: `mv` 명령어로 `BeadFlowMessenger.jsx`로 변경

### Bug #2: 고무줄 느낌 물리
- **증상**: 구슬이 스프링처럼 흔들림
- **원인**: 스프링 기반 물리 엔진 사용
- **해결**: 당구식 직선 이동 물리로 전면 교체

### Bug #3: Flask ImportError
- **증상**: `ModuleNotFoundError: No module named 'flask'`
- **원인**: 외부 관리 Python 환경
- **해결**: Flask 없이 작동하는 `http.server` 기반 백엔드 작성

### Bug #4: 흰 화면
- **증상**: 브라우저에서 흰 화면만 표시
- **원인**: `clamp01` 함수 미정의
- **해결**: Utility 함수 섹션에 추가
```javascript
function clamp01(x){ return Math.max(0, Math.min(1, x)); }
```

### Bug #5: WSL 접속 불가
- **증상**: Windows 브라우저에서 localhost 접속 안 됨
- **원인**: WSL-Windows 포트 포워딩 미설정
- **해결**: PowerShell 스크립트로 포트 포워딩 자동화

---

## 📁 생성된 파일 목록

### 백엔드
- `simple_backend.py` - Python HTTP 서버 (Flask 불필요)

### 프론트엔드
- `web/src/BeadFlowMessenger.jsx` - 메인 대시보드 컴포넌트 (수정됨)
- `web/src/SimpleTest.jsx` - React 테스트 컴포넌트
- `web/test.html` - 연결 테스트 페이지

### 자동화 스크립트
- `add-firewall-rule.bat` - Windows 방화벽 규칙 추가
- `setup-wsl-port-forward.ps1` - WSL 포트 포워딩 설정
- `start-cosmos.bat` - 통합 시스템 자동 실행

### 문서
- `WORK_LOG.md` - 이 파일

---

## 🔧 디버깅 가이드

### 문제: 흰 화면이 나올 때
1. 브라우저 개발자 도구 열기 (F12)
2. Console 탭에서 에러 확인
3. 일반적인 에러:
   - `ReferenceError: XXX is not defined` → 함수 누락
   - `Cannot read property of undefined` → 데이터 구조 문제
   - `Module not found` → import 경로 오류

### 문제: 서버 접속 불가
1. WSL에서 포트 확인:
   ```bash
   ss -tuln | grep -E "5173|5001"
   ```
2. Windows에서 포트 포워딩 확인:
   ```powershell
   netsh interface portproxy show v4tov4
   ```
3. 방화벽 규칙 확인:
   ```powershell
   netsh advfirewall firewall show rule name=all | findstr COSMOS
   ```

### 문제: 백엔드 에러
1. 백엔드 로그 확인:
   ```bash
   # 백그라운드 프로세스 ID 확인
   ps aux | grep python
   # 로그 출력 확인
   ```

### 문제: 프론트엔드 빌드 에러
1. Vite 로그 확인:
   ```bash
   cd web
   npm run dev
   # 에러 메시지 확인
   ```
2. 의존성 재설치:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

---

## 🚀 실행 방법

### 방법 1: 수동 실행 (WSL)
```bash
# 1. 백엔드 시작
python3 simple_backend.py &

# 2. 프론트엔드 시작
cd web
npm run dev &

# 3. 브라우저 접속
# http://localhost:5173
```

### 방법 2: 자동 실행 (Windows)
```batch
# 1. 방화벽 설정 (최초 1회만)
# add-firewall-rule.bat을 관리자 권한으로 실행

# 2. COSMOS 실행
# start-cosmos.bat을 더블클릭
```

---

## 📈 성능 지표

### 목표
- 60fps 유지
- 400개 구슬 동시 처리
- 지연 시간 < 16ms

### 실제 측정 (예정)
- FPS: [측정 필요]
- 메모리: [측정 필요]
- CPU: [측정 필요]

---

## 🔄 향후 작업 계획

### 우선순위 1: WebSocket 통합
- [ ] `websockets` 라이브러리 설치
- [ ] WebSocket 서버 구현
- [ ] 프론트엔드 WebSocket 클라이언트 연결
- [ ] 실시간 데이터 스트리밍 테스트

### 우선순위 2: 인증 시스템
- [ ] `auth_system.py` 통합
- [ ] JWT 토큰 발급
- [ ] 로그인 UI 추가

### 우선순위 3: 고급 기능
- [ ] 7계층 전파 알고리즘 구현
- [ ] 3가지 모드 전환 기능
- [ ] 실제 데이터 소스 연결

### 우선순위 4: 최적화
- [ ] Canvas 렌더링 최적화
- [ ] 충돌 감지 공간 분할
- [ ] Web Worker로 물리 계산 분리

---

## 📞 지원

### 문제 보고
- GitHub Issues: [링크]
- 이메일: [이메일]

### 문서
- API 문서: `/API공식문서.md`
- 사용 가이드: `/공식가이드.md`

---

## 📝 변경 이력

### 2025-10-04
- ✅ 초기 프로젝트 분석
- ✅ 물리 엔진 당구식으로 변경
- ✅ 파일 구조 정리
- ✅ 백엔드 서버 구축 (simple_backend.py)
- ✅ 프론트엔드 실행
- ✅ WSL 포트 포워딩 설정
- ✅ 버그 수정 (clamp01 함수 추가)
- ✅ 에러 바운더리 추가
- ✅ 프로파일링 시스템 통합
- ✅ 문서 작성 (이 파일)

---

## 🔬 프로파일링 시스템

### 추가된 기능 (최종 업데이트)

#### DebugProfiler 컴포넌트
**파일**: `web/src/DebugProfiler.jsx`

**측정 항목**:
1. **FPS (Frames Per Second)**
   - 실시간 FPS 측정
   - 60fps 목표 대비 성능 등급 (A/B/C/D)
   - 1초 간격으로 업데이트

2. **Frame Time**
   - 프레임당 렌더링 시간 (ms)
   - 16.67ms 이하 유지 목표

3. **Memory Usage**
   - JavaScript Heap 사용량 (MB)
   - Chrome 전용 (performance.memory API)

4. **FPS History Graph**
   - 최근 30초간 FPS 히스토리
   - 시각적 그래프 (녹색/노랑/빨강)

5. **Error Tracking**
   - 런타임 에러 캡처
   - 최근 3개 에러 표시
   - 스택 트레이스 포함

**사용 방법**:
```javascript
// BeadFlowMessenger에서 토글
const [showProfiler, setShowProfiler] = useState(false);

// UI 버튼
<button onClick={()=>setShowProfiler(v=>!v)}>🔬</button>

// 컴포넌트
<DebugProfiler enabled={showProfiler} position="top-right" />
```

**성능 등급**:
- **A등급**: FPS ≥ 55
- **B등급**: FPS ≥ 45
- **C등급**: FPS ≥ 30
- **D등급**: FPS < 30

**위치 옵션**:
- `top-right` (기본값)
- `top-left`
- `bottom-right`
- `bottom-left`

#### Performance Logger
**클래스**: `PerformanceLogger`

**기능**:
```javascript
import { perfLogger } from './DebugProfiler.jsx';

// 성능 측정 시작
perfLogger.mark('physics-start');

// ... 물리 계산 ...

// 성능 측정 종료
perfLogger.mark('physics-end');

// 측정값 기록
perfLogger.measure('physics-calculation', 'physics-start', 'physics-end');

// 리포트 출력
perfLogger.log();  // 콘솔에 테이블 형식 출력
```

**출력 예시**:
```
📊 Performance Report
┌─────────────────────────┬──────────┬─────────────┐
│ name                    │ duration │ timestamp   │
├─────────────────────────┼──────────┼─────────────┤
│ physics-calculation     │ 2.34 ms  │ 1234567890  │
│ render-frame            │ 8.12 ms  │ 1234567891  │
│ collision-detection     │ 1.05 ms  │ 1234567892  │
└─────────────────────────┴──────────┴─────────────┘
```

#### usePerformance Hook
**사용 예시**:
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

### 디버깅 워크플로우

#### 1단계: 성능 문제 감지
```
1. 프로파일러 활성화 (🔬 버튼 클릭)
2. FPS가 30 이하로 떨어지는지 확인
3. FPS 그래프에서 드롭 패턴 분석
```

#### 2단계: 병목 지점 찾기
```javascript
// step 함수 프로파일링
perfLogger.mark('step-start');
step(beads, layout, threshold, audio);
perfLogger.mark('step-end');
perfLogger.measure('step-duration', 'step-start', 'step-end');

// drawOnce 함수 프로파일링
perfLogger.mark('draw-start');
drawOnce(canvasRef.current, beads, layout, threshold, theme);
perfLogger.mark('draw-end');
perfLogger.measure('draw-duration', 'draw-start', 'draw-end');

perfLogger.log();
```

#### 3단계: 최적화 적용
```
- step 시간 > 10ms → 물리 계산 최적화
- drawOnce 시간 > 8ms → 렌더링 최적화
- Memory 증가 → 메모리 누수 확인
```

#### 4단계: 검증
```
1. 프로파일러로 FPS 재측정
2. 목표 60fps 달성 확인
3. 메모리 안정성 확인
```

### 알려진 이슈 및 해결

#### 이슈 #1: FPS 드롭 (30fps 이하)
**원인**:
- 구슬 개수 과다 (> 400개)
- 충돌 감지 O(n²) 복잡도

**해결**:
```javascript
// 공간 분할 알고리즘 적용 (향후)
// Quadtree 또는 Grid-based collision detection
```

#### 이슈 #2: 메모리 증가
**원인**:
- 이벤트 리스너 미제거
- Canvas 재생성

**해결**:
```javascript
// useEffect cleanup 확인
useEffect(() => {
  return () => {
    // cleanup 코드
  };
}, [dependencies]);
```

#### 이슈 #3: Chrome 전용 메모리 측정
**원인**:
- `performance.memory`는 Chrome API

**해결**:
- 다른 브라우저에서는 메모리 측정 비활성화
- 조건부 렌더링으로 대응

### 성능 최적화 체크리스트

- [ ] FPS >= 55 (A등급)
- [ ] Frame Time <= 16.67ms
- [ ] Memory < 100MB (경량 유지)
- [ ] 에러 0개
- [ ] 400개 구슬 동시 처리
- [ ] 1분 이상 안정적 실행

---

**작성자**: Claude Code AI
**최종 수정**: 2025-10-04 (프로파일링 시스템 추가)
**버전**: 1.1
