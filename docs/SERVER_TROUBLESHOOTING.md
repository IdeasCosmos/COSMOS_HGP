# 🔧 COSMOS 서버 문제 해결 가이드

## 목차
- [WSL 포트 접근 문제](#wsl-포트-접근-문제)
- [방화벽 차단 문제](#방화벽-차단-문제)
- [포트 충돌 문제](#포트-충돌-문제)
- [자동화 스크립트 사용](#자동화-스크립트-사용)

---

## WSL 포트 접근 문제

### 증상
- Windows 브라우저에서 `http://localhost:5173` 접근 시 "연결할 수 없음" 오류
- WSL 내부에서는 정상 작동하지만 Windows에서 접근 불가

### 원인
WSL2는 독립적인 가상 네트워크를 사용하므로 Windows에서 WSL 포트에 직접 접근 불가능

### 해결 방법

#### 방법 1: 자동화 스크립트 사용 (권장)
```bash
# Windows에서 실행
start-cosmos.bat
→ Y 입력 (포트 자동 설정)
→ UAC 창에서 "예" 클릭
```

#### 방법 2: 수동 설정
```powershell
# Windows PowerShell (관리자 권한)

# 1. WSL IP 확인
wsl hostname -I

# 2. 포트 포워딩 추가 (WSL_IP를 실제 IP로 대체)
$wslIP = "172.x.x.x"
netsh interface portproxy add v4tov4 listenport=5173 listenaddress=0.0.0.0 connectport=5173 connectaddress=$wslIP
netsh interface portproxy add v4tov4 listenport=5174 listenaddress=0.0.0.0 connectport=5174 connectaddress=$wslIP
netsh interface portproxy add v4tov4 listenport=5001 listenaddress=0.0.0.0 connectport=5001 connectaddress=$wslIP

# 3. 포트 포워딩 확인
netsh interface portproxy show v4tov4
```

#### 방법 3: .wslconfig 설정 (영구적)
```ini
# Windows: C:\Users\<사용자명>\.wslconfig
[wsl2]
localhostForwarding=true
```

**WSL 재시작 필요**:
```powershell
wsl --shutdown
wsl
```

---

## 방화벽 차단 문제

### 증상
- 포트 포워딩은 설정했지만 여전히 "연결할 수 없음" 오류
- Windows Defender 또는 다른 방화벽이 포트를 차단

### 해결 방법

#### 방법 1: 자동화 스크립트 (권장)
```bash
# Windows에서 실행
add-firewall-rule.bat
→ UAC 창에서 "예" 클릭
```

#### 방법 2: 수동 방화벽 규칙 추가
```powershell
# Windows PowerShell (관리자 권한)

# 인바운드 규칙
New-NetFirewallRule -DisplayName "COSMOS-Port-5173" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "COSMOS-Port-5174" -Direction Inbound -LocalPort 5174 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "COSMOS-Port-5001" -Direction Inbound -LocalPort 5001 -Protocol TCP -Action Allow

# 아웃바운드 규칙
New-NetFirewallRule -DisplayName "COSMOS-Port-5173-Out" -Direction Outbound -LocalPort 5173 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "COSMOS-Port-5174-Out" -Direction Outbound -LocalPort 5174 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "COSMOS-Port-5001-Out" -Direction Outbound -LocalPort 5001 -Protocol TCP -Action Allow
```

#### 방법 3: Windows Defender GUI
1. Windows 검색 → "Windows Defender 방화벽"
2. "고급 설정" 클릭
3. "인바운드 규칙" → "새 규칙"
4. "포트" 선택 → "다음"
5. "TCP" 선택, "특정 로컬 포트": `5173, 5174, 5001` 입력
6. "연결 허용" 선택
7. 모든 프로필 체크
8. 이름: "COSMOS Ports"

---

## 포트 충돌 문제

### 증상
- `Port 5173 is in use, trying another one...`
- Vite가 5174 포트로 자동 변경됨

### 원인
- 다른 애플리케이션이 이미 포트 5173을 사용 중

### 해결 방법

#### 방법 1: 포트 사용 프로세스 찾기
```powershell
# Windows
netstat -ano | findstr :5173

# 프로세스 종료 (PID 확인 후)
taskkill /PID <PID> /F
```

```bash
# WSL
lsof -i :5173

# 프로세스 종료
kill -9 <PID>
```

#### 방법 2: Vite 기본 포트 변경
```javascript
// web/vite.config.js
export default {
  server: {
    port: 3000,  // 원하는 포트로 변경
    host: true
  }
}
```

#### 방법 3: 5174 포트 사용
Vite가 자동으로 5174로 변경하면 그대로 사용:
```
http://localhost:5174
```

---

## 자동화 스크립트 사용

### start-cosmos.bat (통합 시작 스크립트)

**기능**:
- 포트 포워딩 자동 설정
- 방화벽 규칙 자동 추가
- 백엔드/프론트엔드 자동 시작
- 브라우저 자동 열기

**사용법**:
```bash
# Windows 탐색기에서 더블클릭
start-cosmos.bat

# 또는 PowerShell에서
.\start-cosmos.bat
```

**실행 과정**:
```
[0/3] 포트 포워딩 및 방화벽을 자동으로 설정하시겠습니까? (Y/N): Y
→ UAC 창 표시 → "예" 클릭
→ 포트 포워딩 + 방화벽 자동 설정

[1/3] 백엔드 서버 시작 중...
→ Python 백엔드 시작 (포트 5001)

[2/3] 프론트엔드 서버 시작 중...
→ Vite 개발 서버 시작 (포트 5173 또는 5174)

[3/3] 브라우저 열기...
→ http://localhost:5173 자동 열기
```

### add-firewall-rule.bat (포트 설정 전용)

**기능**:
- WSL IP 자동 감지
- 포트 포워딩 자동 설정
- 방화벽 규칙 자동 추가 (인바운드/아웃바운드)

**사용법**:
```bash
# Windows 탐색기에서 더블클릭
add-firewall-rule.bat

# 또는 PowerShell에서
.\add-firewall-rule.bat
```

**자동 처리 항목**:
1. 관리자 권한 자동 요청
2. WSL IP 자동 감지
3. 기존 포트 포워딩 제거
4. 새 포트 포워딩 추가 (5173, 5174, 5001)
5. 방화벽 규칙 추가 (인바운드 + 아웃바운드)
6. 현재 상태 표시

### setup-ports.ps1 (PowerShell - 수동 확인용)

**기능**:
- 설정 과정을 터미널에 상세히 출력
- 각 단계별 성공/실패 확인 가능

**사용법**:
```powershell
# PowerShell (관리자 권한)
.\setup-ports.ps1
```

### setup-ports-auto.ps1 (PowerShell - 자동 백그라운드)

**기능**:
- 사용자 입력 없이 백그라운드에서 자동 실행
- 빠른 설정 완료

**사용법**:
```powershell
# PowerShell (관리자 권한)
.\setup-ports-auto.ps1
```

---

## 문제 해결 체크리스트

### 1단계: WSL IP 확인
```powershell
wsl hostname -I
```
**예상 출력**: `172.x.x.x` 형식의 IP 주소

### 2단계: 포트 포워딩 확인
```powershell
netsh interface portproxy show v4tov4
```
**예상 출력**:
```
Listen on ipv4:             Connect to ipv4:
Address         Port        Address         Port
--------------- ----------  --------------- ----------
0.0.0.0         5173        172.x.x.x       5173
0.0.0.0         5174        172.x.x.x       5174
0.0.0.0         5001        172.x.x.x       5001
```

### 3단계: 방화벽 규칙 확인
```powershell
Get-NetFirewallRule -DisplayName "*COSMOS*"
```
**예상 출력**: 6개의 규칙 (3개 인바운드 + 3개 아웃바운드)

### 4단계: 포트 사용 확인
```bash
# WSL에서
netstat -tuln | grep 5173
```
**예상 출력**: `0.0.0.0:5173` 또는 `:::5173`

### 5단계: 접속 테스트
```bash
# Windows PowerShell
curl http://localhost:5173
curl http://localhost:5001/health
```

---

## 일반적인 오류 메시지

### "요청한 작업을 수행하려면 권한 상승이 필요합니다"
**해결**:
- 스크립트를 관리자 권한으로 실행
- 또는 자동화 스크립트 사용 (자동으로 UAC 요청)

### "Port 5173 is in use"
**해결**:
- 포트 사용 프로세스 종료
- 또는 5174 포트 사용

### "WSL IP를 찾을 수 없습니다"
**해결**:
```bash
wsl --shutdown
wsl
```

### "ERR_CONNECTION_REFUSED"
**해결 순서**:
1. WSL에서 서버가 실행 중인지 확인
2. 포트 포워딩 확인
3. 방화벽 규칙 확인
4. WSL IP 변경 여부 확인 (재시작 후)

---

## 고급 문제 해결

### WSL IP가 계속 변경되는 경우

**해결책 1**: 고정 IP 설정
```ini
# Windows: C:\Users\<사용자명>\.wslconfig
[wsl2]
localhostForwarding=true
```

**해결책 2**: 시작 스크립트에 포트 설정 통합
- `start-cosmos.bat` 사용 시 자동으로 현재 WSL IP 감지 및 설정

### 포트 포워딩이 재부팅 후 사라지는 경우

**해결**: 시작 작업 등록
```powershell
# 작업 스케줄러에 add-firewall-rule.bat 등록
# 트리거: 시스템 시작 시
# 작업: add-firewall-rule.bat 실행
```

### 다중 WSL 배포판 사용 시

**해결**: 특정 배포판 지정
```powershell
wsl -d Ubuntu hostname -I
```

---

## 참고 자료

- [WSL 네트워크 설정 공식 문서](https://docs.microsoft.com/windows/wsl/networking)
- [Windows Defender 방화벽 가이드](https://docs.microsoft.com/windows/security/threat-protection/windows-firewall)
- [Vite 서버 설정](https://vitejs.dev/config/server-options.html)

---

**마지막 업데이트**: 2025-10-04
**작성자**: Claude Code
