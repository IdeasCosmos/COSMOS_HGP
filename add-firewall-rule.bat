@echo off
chcp 65001 >nul
REM COSMOS-HGP 방화벽 규칙 추가
REM 관리자 권한 자동 요청

echo ========================================
echo COSMOS-HGP 방화벽 규칙 추가
echo ========================================
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔐 관리자 권한이 필요합니다. 권한 상승 중...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ✓ 관리자 권한으로 실행 중
echo.

REM 포트 목록
set PORTS=5173 5174 5001

REM 기존 규칙 제거
echo [1/4] 기존 방화벽 규칙 제거 중...
for %%p in (%PORTS%) do (
    netsh advfirewall firewall delete rule name="COSMOS-Port-%%p" >nul 2>&1
    netsh advfirewall firewall delete rule name="COSMOS-Port-%%p-Out" >nul 2>&1
)
echo ✓ 기존 규칙 제거 완료
echo.

REM 인바운드 규칙 추가
echo [2/4] 인바운드 방화벽 규칙 추가 중...
for %%p in (%PORTS%) do (
    netsh advfirewall firewall add rule name="COSMOS-Port-%%p" dir=in action=allow protocol=TCP localport=%%p >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 포트 %%p 인바운드 규칙 추가 성공
    ) else (
        echo   ✗ 포트 %%p 인바운드 규칙 추가 실패
    )
)
echo.

REM 아웃바운드 규칙 추가
echo [3/4] 아웃바운드 방화벽 규칙 추가 중...
for %%p in (%PORTS%) do (
    netsh advfirewall firewall add rule name="COSMOS-Port-%%p-Out" dir=out action=allow protocol=TCP localport=%%p >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 포트 %%p 아웃바운드 규칙 추가 성공
    ) else (
        echo   ✗ 포트 %%p 아웃바운드 규칙 추가 실패
    )
)
echo.

REM WSL 포트 포워딩 설정
echo [4/4] WSL 포트 포워딩 설정 중...
for /f "tokens=*" %%i in ('wsl hostname -I') do set WSL_IP=%%i
for /f "tokens=1" %%a in ("%WSL_IP%") do set WSL_IP=%%a

if not "%WSL_IP%"=="" (
    echo   WSL IP: %WSL_IP%
    for %%p in (%PORTS%) do (
        netsh interface portproxy delete v4tov4 listenport=%%p listenaddress=0.0.0.0 >nul 2>&1
        netsh interface portproxy add v4tov4 listenport=%%p listenaddress=0.0.0.0 connectport=%%p connectaddress=%WSL_IP% >nul 2>&1
        echo   ✓ 포트 %%p 포워딩 설정: 0.0.0.0:%%p -^> %WSL_IP%:%%p
    )
) else (
    echo   ✗ WSL IP를 찾을 수 없습니다
)

echo.
echo ════════════════════════════════════════════
echo ✅ 모든 설정이 완료되었습니다!
echo ════════════════════════════════════════════
echo.
echo 📍 접속 주소:
echo   • http://localhost:5173
echo   • http://localhost:5174
echo   • http://localhost:5001/health
echo.
echo 💡 이제 start-cosmos.bat을 실행하세요!
echo.
pause
