# COSMOS 시각화 데모

이 디렉토리는 COSMOS 시스템의 시각화 기능을 데모하는 스크립트들을 포함합니다.

## 실행 방법

### Windows 환경
```cmd
demo\run_viz.bat
```

### Linux/Mac 환경
```bash
chmod +x demo/run_viz.sh
./demo/run_viz.sh
```

## 기능

1. **시각화 생성**: `viz/log_to_map.py`를 실행하여 정적 시각화 파일들을 생성합니다.
2. **API 서버 시작**: FastAPI 서버를 포트 8000에서 시작합니다.

## 접근 가능한 엔드포인트

- **API 문서**: http://localhost:8000
- **히트맵**: http://localhost:8000/viz/heatmap.png
- **타임라인**: http://localhost:8000/viz/timeline.png
- **코돈 막대그래프**: http://localhost:8000/viz/codon_bar.png
- **요약 통계**: http://localhost:8000/viz/summary_stats.json
- **실시간 지표**: http://localhost:8000/metrics/live
- **이벤트 목록**: http://localhost:8000/events
- **이벤트 통계**: http://localhost:8000/events/stats
- **시각화 파일 목록**: http://localhost:8000/viz

## 요구사항

- Python 3.7+
- 필요한 패키지들 (requirements.txt 참조)
- 로그 파일: `./log/annotations.jsonl` (없으면 샘플 데이터 자동 생성)

## 문제 해결

1. **포트 충돌**: 포트 8000이 사용 중인 경우, `run_viz.bat` 또는 `run_viz.sh`에서 포트를 변경하세요.
2. **의존성 오류**: `pip install -r requirements.txt`를 실행하여 필요한 패키지를 설치하세요.
3. **권한 오류**: Linux/Mac에서 실행 권한이 없는 경우 `chmod +x demo/run_viz.sh`를 실행하세요.
