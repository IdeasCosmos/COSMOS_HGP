@echo off
echo === COSMOS Flask 시각화 데모 시작 ===

REM UNC 경로 문제 해결 - 로컬 드라이브로 복사
set TEMP_DIR=%TEMP%\cosmos_temp
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM 필요한 디렉토리 생성
if not exist "log" mkdir "log"
if not exist "viz_out" mkdir "viz_out"

REM Flask 의존성 확인
echo Flask 의존성 확인 중...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask가 설치되지 않았습니다. 설치하시겠습니까? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        echo Flask 설치 중...
        pip install flask
    )
)

REM Flask 서버 시작
echo Flask 서버 시작 중...
echo 브라우저에서 다음 URL을 확인하세요:
echo   - http://localhost:5000 (대시보드)
echo   - http://localhost:5000/metrics (실시간 지표)
echo   - http://localhost:5000/events (이벤트 목록)
echo   - http://localhost:5000/viz (시각화 목록)
echo.
echo 서버를 중지하려면 Ctrl+C를 누르세요.

python simple_server.py
