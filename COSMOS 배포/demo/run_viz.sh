#!/usr/bin/env bash
set -e

echo "=== COSMOS 시각화 데모 시작 ==="

# 필요한 디렉토리 생성
mkdir -p ../log ../viz_out

# Python 경로 설정
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."

# 시각화 생성
echo "시각화 생성 중..."
cd ..
python -m viz.log_to_map

# FastAPI 서버 시작
echo "FastAPI 서버 시작 중..."
echo "브라우저에서 다음 URL들을 확인하세요:"
echo "  - http://localhost:8000 (API 문서)"
echo "  - http://localhost:8000/viz/heatmap.png (히트맵)"
echo "  - http://localhost:8000/viz/timeline.png (타임라인)"
echo "  - http://localhost:8000/metrics/live (실시간 지표)"
echo "  - http://localhost:8000/events (이벤트 목록)"
echo ""
echo "서버를 중지하려면 Ctrl+C를 누르세요."

uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
