@echo off
cd /d "%~dp0"
echo Starting COSMOS D3 Dashboard...
echo.
echo Installing dependencies if needed...
call npm install
echo.
echo Starting development server...
call npm run dev
pause
