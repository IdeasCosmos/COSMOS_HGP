@echo off
setlocal enabledelayedexpansion

REM UTF-8 인코딩 설정
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo COSMOS-HGP V2-min+ GitHub Setup (Fixed)
echo ========================================
echo.

REM 배치 파일이 있는 디렉토리로 이동
cd /d "%~dp0"
echo 현재 디렉토리: %CD%
echo.

REM Git이 설치되어 있는지 확인
git --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Git이 설치되지 않았습니다
    echo https://git-scm.com/download/win 에서 Git을 설치해주세요
    pause
    exit /b 1
)
echo ✅ Git 확인 완료
echo.

REM 기존 .git 폴더가 있다면 제거
if exist .git (
    echo 기존 Git 리포지토리 제거 중...
    rmdir /s /q .git
)
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

REM Git 사용자 설정 (필요한 경우)
echo [2.5/6] Git 사용자 설정...
git config user.name "COSMOS-HGP" >nul 2>&1
git config user.email "cosmos@example.com" >nul 2>&1
echo ✅ Git 설정 완료
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
git commit -m "feat: COSMOS-HGP V2-min+ deployment package"
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
echo ⚠️ GitHub 인증이 필요할 수 있습니다
git push -u origin main
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ 푸시 실패
    echo.
    echo 해결 방법:
    echo 1. GitHub Personal Access Token 사용:
    echo    - GitHub ^> Settings ^> Developer settings ^> Personal access tokens
    echo    - 토큰 생성 후 비밀번호 대신 사용
    echo.
    echo 2. 또는 GitHub Desktop 사용
    echo.
    echo 3. 또는 GitHub 웹에서 직접 업로드
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
