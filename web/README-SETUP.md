# 🌌 COSMOS 포트 설정 가이드

## 🚀 빠른 시작 (권장)

Windows에서 `start-cosmos-full.bat`을 실행하세요.

```bash
# Windows 탐색기에서:
web\start-cosmos-full.bat 더블클릭
```

### 실행 과정:
1. **포트 설정 방법 선택**
   - `1`: 자동 설정 (추천) - 백그라운드에서 자동으로 처리
   - `2`: 수동 설정 - 설정 과정을 확인
   - `3`: 건너뛰기 - 이미 설정된 경우

2. **백엔드 시작 여부**
   - `Y`: 백엔드 시작 (포트 5001)
   - `N`: 백엔드 건너뛰기

3. **프론트엔드 자동 시작**
   - 자동으로 Vite 개발 서버 시작 (포트 5173 또는 5174)

4. **브라우저 자동 열기**
   - `Y`: 자동으로 브라우저 열기
   - `N`: 수동으로 접속

---

## 📋 개별 스크립트 사용

### 1. 포트 설정만 하기

#### 자동 모드 (백그라운드):
```powershell
# Windows PowerShell에서:
.\setup-ports-auto.ps1
```

#### 수동 모드 (과정 확인):
```powershell
# Windows PowerShell에서:
.\setup-ports.ps1
```

### 2. 서비스만 시작하기

```bash
# WSL에서:
cd web
npm run dev
```

---

## 🔧 수동 설정 (문제 발생 시)

### WSL IP 확인
```bash
wsl hostname -I
```

### 포트 포워딩 추가
```powershell
# Windows PowerShell (관리자 권한):
$wslIP = "YOUR_WSL_IP"
netsh interface portproxy add v4tov4 listenport=5173 listenaddress=0.0.0.0 connectport=5173 connectaddress=$wslIP
netsh interface portproxy add v4tov4 listenport=5174 listenaddress=0.0.0.0 connectport=5174 connectaddress=$wslIP
```

### 방화벽 규칙 추가
```powershell
# Windows PowerShell (관리자 권한):
New-NetFirewallRule -DisplayName "COSMOS-WSL-Port-5173" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "COSMOS-WSL-Port-5174" -Direction Inbound -LocalPort 5174 -Protocol TCP -Action Allow
```

### 포트 포워딩 확인
```powershell
netsh interface portproxy show v4tov4
```

---

## ❓ 문제 해결

### 1. "관리자 권한이 필요합니다" 오류
- PowerShell을 관리자 권한으로 실행하세요
- 또는 스크립트를 우클릭 → "관리자 권한으로 실행"

### 2. "포트가 이미 사용 중입니다" 오류
- Vite가 자동으로 다른 포트(5174)를 사용합니다
- `netstat -ano | findstr :5173`으로 사용 중인 프로세스 확인

### 3. WSL IP가 변경됨
- WSL을 재시작하면 IP가 변경될 수 있습니다
- `setup-ports.ps1`을 다시 실행하여 포트 포워딩을 업데이트하세요

### 4. 방화벽 경고
- Windows Defender가 차단할 수 있습니다
- "액세스 허용"을 클릭하거나 방화벽 규칙을 수동으로 추가하세요

---

## 📊 포트 사용 현황

| 포트 | 서비스 | 용도 |
|------|--------|------|
| 5173 | Vite (Frontend) | React 개발 서버 (기본) |
| 5174 | Vite (Frontend) | React 개발 서버 (대체) |
| 5001 | Python Backend | Flask/HTTP 서버 |

---

## 🎯 다음 단계

1. ✅ 포트 설정 완료
2. ✅ 서비스 시작
3. 📍 브라우저에서 http://localhost:5173 접속
4. 🎨 대시보드 확인

---

## 💡 팁

- **자동 시작**: `start-cosmos-full.bat`을 바탕화면 바로가기로 만들어두세요
- **포트 변경**: `web/vite.config.js`에서 기본 포트 변경 가능
- **로그 확인**: 터미널 창에서 실시간 로그 확인 가능
- **개발 중단**: 터미널 창을 닫거나 `Ctrl+C`로 중단

---

생성일: 2025-10-04
작성자: Claude Code
