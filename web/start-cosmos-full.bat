@echo off
chcp 65001 >nul
title COSMOS 통합 시작 스크립트

echo ════════════════════════════════════════════
echo   🌌 COSMOS 통합 시작 스크립트
echo ════════════════════════════════════════════
echo.

:: 포트 설정 선택
echo [포트 설정 방법 선택]
echo.
echo 1. 자동 설정 (추천) - 백그라운드에서 자동 설정
echo 2. 수동 설정 - 설정 과정을 확인하며 진행
echo 3. 건너뛰기 - 이미 설정되어 있음
echo.
choice /C 123 /N /M "선택하세요 (1/2/3): "

if errorlevel 3 goto skip_port_setup
if errorlevel 2 goto manual_setup
if errorlevel 1 goto auto_setup

:auto_setup
echo.
echo [자동 설정 모드]
echo 백그라운드에서 포트를 설정하는 중...
powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0setup-ports-auto.ps1"
timeout /t 2 /nobreak >nul
echo ✅ 포트 설정 완료
goto start_services

:manual_setup
echo.
echo [수동 설정 모드]
echo PowerShell 창이 열립니다. 설정 과정을 확인하세요.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-ports.ps1"
goto start_services

:skip_port_setup
echo.
echo [포트 설정 건너뛰기]
echo 기존 설정을 사용합니다.

:start_services
echo.
echo ════════════════════════════════════════════
echo   🚀 서비스 시작 중
echo ════════════════════════════════════════════
echo.

:: 백엔드 시작 확인
echo [백엔드 시작 여부]
echo.
choice /C YN /N /M "백엔드를 시작하시겠습니까? (Y/N): "

if errorlevel 2 goto skip_backend
if errorlevel 1 goto start_backend

:start_backend
echo.
echo [1/2] 백엔드 시작 중...
start "COSMOS Backend" wsl -d Ubuntu -e bash -c "cd /home/sjpu/SJPU/integrated_system_v1/커서전용/커서/COSMOS/COSMOS_V1 && python3 simple_backend.py"
timeout /t 2 /nobreak >nul
echo ✅ 백엔드 시작됨 (포트 5001)
goto start_frontend

:skip_backend
echo.
echo [백엔드 건너뛰기]

:start_frontend
echo.
echo [2/2] 프론트엔드 시작 중...
start "COSMOS Frontend" wsl -d Ubuntu -e bash -c "cd /home/sjpu/SJPU/integrated_system_v1/커서전용/커서/COSMOS/COSMOS_V1/web && npm run dev"
timeout /t 3 /nobreak >nul
echo ✅ 프론트엔드 시작됨

echo.
echo ════════════════════════════════════════════
echo   ✅ 모든 서비스가 시작되었습니다!
echo ════════════════════════════════════════════
echo.
echo 📍 접속 주소:
echo   • Frontend: http://localhost:5173
echo   • Frontend: http://localhost:5174
echo   • Backend:  http://localhost:5001
echo.
echo 💡 팁:
echo   - 브라우저가 자동으로 열리지 않으면 위 주소를 직접 입력하세요
echo   - 포트가 사용 중이면 자동으로 다른 포트로 변경됩니다
echo   - 서비스를 종료하려면 새로 열린 터미널 창을 닫으세요
echo.

:: 브라우저 자동 열기
echo [브라우저 자동 열기]
choice /C YN /N /M "브라우저를 자동으로 여시겠습니까? (Y/N): "

if errorlevel 2 goto end
if errorlevel 1 goto open_browser

:open_browser
timeout /t 3 /nobreak >nul
start http://localhost:5173
goto end

:end
echo.
pause
