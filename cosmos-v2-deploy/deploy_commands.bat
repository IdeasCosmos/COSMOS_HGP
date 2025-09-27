@echo off
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
git commit -m "feat: COSMOS-HGP V2-min+ 배포 패키지

🌌 계층적 실행 엔진 - 국소 실패를 상위로 번지지 않게 차단

✨ 핵심 기능:
- 계층 실행: 중첩 그룹 순차 처리
- 국소 차단: impact >= threshold 시 노드 차단  
- 누적 캡: V = 1 - Π(1 - v) 공식 적용
- 타임라인: ASCII 텍스트 실행 경로 표시
- 결정적 재실행: 동일 입력 시 동일 결과 보장

🚀 배포 지원:
- Docker 기반 컨테이너화
- MANUS AI, GENSPARK AI 배포 가이드
- Flask 웹 API
- 자동 테스트 스위트

📊 성능 목표:
- P95 ^< 60ms, P99 ^< 120ms
- 메모리 피크 ^< 256MB
- 입력 10^4 실수 벡터 지원"

echo.
echo 5. 메인 브랜치 설정...
git branch -M main

echo.
echo 6. 리포지토리에 푸시...
git push -u origin main

echo.
echo 🎉 COSMOS-HGP V2-min+ 배포판 푸시 완료!
echo 📋 리포지토리 URL: https://github.com/IdeasCosmos/COSMOS_HGP
echo.
echo 📦 포함된 파일들:
echo   ✅ src/main.py - 메인 애플리케이션
echo   ✅ scripts/deploy.sh - 자동 배포 스크립트  
echo   ✅ scripts/test_deployment.py - 배포 테스트
echo   ✅ docs/ - MANUS AI, GENSPARK AI 배포 가이드
echo   ✅ Dockerfile, docker-compose.yml - 컨테이너 설정
echo   ✅ requirements.txt - 의존성 목록

pause
