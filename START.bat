@echo off
echo ========================================
echo 🚀 COSMOS-HGP Windows 실행기
echo ========================================
echo.

REM Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다
    echo 💡 Python 3.8+ 설치 후 다시 시도하세요
    pause
    exit /b 1
)

REM Node.js 확인
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js가 설치되지 않았습니다
    echo 💡 Node.js 16+ 설치 후 다시 시도하세요
    pause
    exit /b 1
)

echo ✅ Python과 Node.js 확인됨
echo.

REM 메인 실행
echo 🚀 COSMOS-HGP 시작 중...
python main.py

pause