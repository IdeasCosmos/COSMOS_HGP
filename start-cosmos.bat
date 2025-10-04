@echo off
chcp 65001 >nul
REM COSMOS-HGP 통합 시스템 시작 스크립트
REM WSL에서 프론트엔드와 백엔드를 동시에 실행

echo ════════════════════════════════════════════
echo   🌌 COSMOS-HGP 통합 시스템 시작
echo ════════════════════════════════════════════
echo.

REM 포트 설정 확인
echo [0/3] 포트 설정 확인 중...
choice /C YN /N /M "포트 포워딩 및 방화벽을 자동으로 설정하시겠습니까? (Y/N): "
if errorlevel 2 goto skip_firewall
if errorlevel 1 goto setup_firewall

:setup_firewall
echo.
echo 🔐 관리자 권한으로 포트 설정 중...
call "%~dp0add-firewall-rule.bat"
goto continue

:skip_firewall
echo.
echo ⏭️  포트 설정 건너뛰기 (수동 설정 필요)

:continue
echo.

REM WSL 경로 설정
set WSL_PATH=/home/sjpu/SJPU/integrated_system_v1/커서전용/커서/COSMOS/COSMOS_V1

echo [1/3] 백엔드 서버 시작 중...
start "COSMOS Backend" wsl -d Ubuntu -- bash -c "cd %WSL_PATH% && python3 simple_backend.py"
timeout /t 3 /nobreak > nul
echo ✓ 백엔드 서버 시작됨 (포트 5001)
echo.

echo [2/3] 프론트엔드 서버 시작 중...
start "COSMOS Frontend" wsl -d Ubuntu -- bash -c "cd %WSL_PATH%/web && npm run dev"
timeout /t 5 /nobreak > nul
echo ✓ 프론트엔드 서버 시작됨 (포트 5173)
echo.

echo [3/3] 브라우저 열기...
timeout /t 2 /nobreak > nul
start http://localhost:5173
echo.

echo ════════════════════════════════════════════
echo   ✅ COSMOS-HGP 시스템 실행 중!
echo ════════════════════════════════════════════
echo.
echo 📍 접속 주소:
echo   • 프론트엔드: http://localhost:5173
echo   • 프론트엔드: http://localhost:5174
echo   • 백엔드 API: http://localhost:5001/health
echo.
echo 💡 팁:
echo   - 서비스 종료: 터미널 창 닫기
echo   - 포트 변경 시: add-firewall-rule.bat 재실행
echo.
echo ════════════════════════════════════════════
pause
