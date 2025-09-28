#!/usr/bin/env bash
set -e

echo "=== COSMOS Flask 시각화 데모 시작 ==="

# 필요한 디렉토리 생성
mkdir -p ../log ../viz_out

# Python 경로 설정
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."

# Flask 의존성 확인
echo "Flask 의존성 확인 중..."
if ! python -c "import flask" 2>/dev/null; then
    echo "Flask가 설치되지 않았습니다. 설치하시겠습니까? (y/n)"
    read -r choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        echo "Flask 설치 중..."
        pip install -r ../requirements_flask.txt
    fi
fi

# Flask 서버 시작
echo "Flask 서버 시작 중..."
echo "브라우저에서 다음 URL을 확인하세요:"
echo "  - http://localhost:5000 (대시보드)"
echo "  - http://localhost:5000/metrics (실시간 지표)"
echo "  - http://localhost:5000/events (이벤트 목록)"
echo "  - http://localhost:5000/viz (시각화 목록)"
echo ""
echo "서버를 중지하려면 Ctrl+C를 누르세요."

cd ..
python simple_server.py
