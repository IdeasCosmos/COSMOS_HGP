#!/bin/bash

# COSMOS-HGP V2-min+ 배포 스크립트

echo "🌌 COSMOS-HGP V2-min+ 배포 시작"

# 1. Docker 이미지 빌드
echo "📦 Docker 이미지 빌드 중..."
docker build -t cosmos-hgp:v2-min+ .

if [ $? -eq 0 ]; then
    echo "✅ Docker 이미지 빌드 성공"
else
    echo "❌ Docker 이미지 빌드 실패"
    exit 1
fi

# 2. 로그 디렉토리 생성
echo "📁 로그 디렉토리 생성 중..."
mkdir -p logs

# 3. 컨테이너 실행
echo "🚀 컨테이너 실행 중..."
docker run -d \
    --name cosmos-hgp \
    -p 5000:5000 \
    -v $(pwd)/logs:/app/log \
    cosmos-hgp:v2-min+

if [ $? -eq 0 ]; then
    echo "✅ 컨테이너 실행 성공"
    echo "🌐 웹 인터페이스: http://localhost:5000"
    echo "🔍 API 엔드포인트: http://localhost:5000/run"
    echo "❤️ 헬스 체크: http://localhost:5000/health"
else
    echo "❌ 컨테이너 실행 실패"
    exit 1
fi

# 4. 헬스 체크
echo "🔍 헬스 체크 중..."
sleep 5

for i in {1..10}; do
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "✅ 서비스 정상 동작 확인"
        break
    else
        echo "⏳ 서비스 시작 대기 중... ($i/10)"
        sleep 2
    fi
done

echo "🎉 COSMOS-HGP V2-min+ 배포 완료!"
echo ""
echo "📋 사용 가능한 명령어:"
echo "  - 컨테이너 중지: docker stop cosmos-hgp"
echo "  - 컨테이너 제거: docker rm cosmos-hgp"
echo "  - 로그 확인: docker logs cosmos-hgp"
echo "  - 컨테이너 재시작: docker restart cosmos-hgp"
