@echo off
setlocal enabledelayedexpansion

REM UTF-8 인코딩 설정
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo COSMOS-HGP V2-min+ GitHub Setup
echo ========================================
echo.

REM 현재 디렉토리 확인
echo 현재 디렉토리: %CD%
echo.

REM Git 초기화
echo [1/6] Git 리포지토리 초기화...
git init
if %ERRORLEVEL% neq 0 (
    echo ❌ Git 초기화 실패
    pause
    exit /b 1
)
echo ✅ Git 초기화 완료
echo.

REM 리모트 추가
echo [2/6] 리모트 리포지토리 추가...
git remote add origin https://github.com/IdeasCosmos/COSMOS_HGP.git
if %ERRORLEVEL% neq 0 (
    echo ⚠️ 리모트가 이미 존재할 수 있습니다
    git remote -v
)
echo ✅ 리모트 설정 완료
echo.

REM 파일 추가
echo [3/6] 파일 추가...
git add .
if %ERRORLEVEL% neq 0 (
    echo ❌ 파일 추가 실패
    pause
    exit /b 1
)
echo ✅ 파일 추가 완료
echo.

REM 커밋
echo [4/6] 커밋 생성...
git commit -m "feat: COSMOS-HGP V2-min+ 배포 패키지 - 계층적 실행 엔진"
if %ERRORLEVEL% neq 0 (
    echo ❌ 커밋 실패
    pause
    exit /b 1
)
echo ✅ 커밋 완료
echo.

REM 브랜치 설정
echo [5/6] 메인 브랜치 설정...
git branch -M main
echo ✅ 브랜치 설정 완료
echo.

REM 푸시
echo [6/6] GitHub에 푸시...
git push -u origin main
if %ERRORLEVEL% neq 0 (
    echo ❌ 푸시 실패 - 인증이 필요할 수 있습니다
    echo.
    echo 해결 방법:
    echo 1. GitHub Personal Access Token 설정
    echo 2. 또는 SSH 키 설정
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎉 성공적으로 푸시되었습니다!
echo ========================================
echo.
echo 📋 리포지토리: https://github.com/IdeasCosmos/COSMOS_HGP
echo.
echo 📦 포함된 파일들:
echo   ✅ src/main.py - 메인 애플리케이션
echo   ✅ scripts/deploy.sh - 배포 스크립트
echo   ✅ scripts/test_deployment.py - 테스트 스크립트
echo   ✅ docs/ - 배포 가이드
echo   ✅ Dockerfile - 컨테이너 설정
echo   ✅ requirements.txt - 의존성
echo.

pause
