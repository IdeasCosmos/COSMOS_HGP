@echo off
chcp 65001 >nul
echo 🚀 COSMOS-HGP V2-min+ 배포판 GitHub 푸시
echo ================================================

echo.
echo 1. Git 리포지토리 초기화...
git init

echo.
echo 2. 리모트 리포지토리 추가...
git remote add origin https://github.com/IdeasCosmos/COSMOS_HGP.git

echo.
echo 3. 파일 추가...
git add .

echo.
echo 4. 배포판 커밋...
git commit -m "feat: COSMOS-HGP V2-min+ 배포 패키지"

echo.
echo 5. 메인 브랜치 설정...
git branch -M main

echo.
echo 6. 리포지토리에 푸시...
git push -u origin main

echo.
echo 🎉 COSMOS-HGP V2-min+ 배포판 푸시 완료!
echo 📋 리포지토리 URL: https://github.com/IdeasCosmos/COSMOS_HGP

pause
