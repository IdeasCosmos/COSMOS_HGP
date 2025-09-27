# 🌌 COSMOS-HGP V2-min+

**국소 실패를 상위로 번지지 않게 차단하는 '계층형 실행 엔진'**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI/CD](https://github.com/IdeasCosmos/COSMOS_HGP/workflows/CI/badge.svg)](https://github.com/IdeasCosmos/COSMOS_HGP/actions)
[![Docker](https://img.shields.io/docker/v/cosmos-hgp/v2-min-plus?label=docker)](https://hub.docker.com/r/cosmos-hgp/v2-min-plus)

## 🚀 핵심 기능

### OSS (Open Source) - Apache 2.0
- ✅ **계층 실행**: 중첩 그룹을 순차 처리
- ✅ **국소 차단**: `impact >= threshold`면 해당 노드/서브트리만 차단
- ✅ **누적 캡**: `V = 1 - Π(1 - v)`가 cap 도달 시 해당 서브트리 정지
- ✅ **결과 타임라인**: ASCII 텍스트 타임라인 출력
- ✅ **결정적 재실행**: 동일 입력·설정일 때 동일 경로 재현
- ✅ **REST API**: 완전한 웹 API
- ✅ **웹 대시보드**: 실시간 모니터링 UI

### Pro (Commercial) - 별도 라이선스
- 🔒 **병렬 실행**: 멀티스레드/멀티프로세스 동시 처리
- 🔒 **분산 처리**: 클러스터링, 노드 장애 감지, 재분배
- 🔒 **고급 대시보드**: WebSocket 실시간 스트리밍, 차트, 알림
- 🔒 **ML 예측**: 임팩트 사전 예측, 이상 탐지, 적응형 임계값
- 🔒 **고급 규칙 관리**: GUI 편집기, 버전 관리, 감사 로그
- 🔒 **SLA 모니터링**: Slack/Email 연동, 성능 추적
- 🔒 **보안/RBAC**: 인증, 역할 기반 접근 제어
- 🔒 **엔터프라이즈 지원**: 우선 지원, 설치 가이드, 컨설팅

## 📦 빠른 시작

### Docker로 실행 (권장)

```bash
# 1. 저장소 클론
git clone https://github.com/IdeasCosmos/COSMOS_HGP.git
cd COSMOS_HGP

# 2. Docker 컨테이너 실행
docker-compose up -d

# 3. 웹 대시보드 접속
open http://localhost:5000
```

### 수동 설치

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 애플리케이션 실행
python main.py

# 3. API 테스트
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -d '{"data": [1,2,3,4,5], "threshold": 0.30, "cumulative_cap": 0.50}'
```

## 🧪 데모 시나리오

### 시나리오 A: 정상 흐름
```json
{
  "data": [1, 2, 3, 4, 5],
  "threshold": 0.30,
  "cumulative_cap": 0.50
}
```
**결과**: 모든 노드 통과, 타임라인에 무차단 경로 표시

### 시나리오 B: 국소 차단
```json
{
  "data": [1, 2, 3, 4, 5],
  "threshold": 0.70,
  "cumulative_cap": 0.50
}
```
**결과**: 중간 레벨 노드 blocked, 하위 서브트리 skip, 상위는 계속

### 시나리오 C: 누적캡 차단
```json
{
  "data": [10, 20, 30, 40, 50],
  "threshold": 0.30,
  "cumulative_cap": 0.50
}
```
**결과**: 누적 `V≥0.50` 지점에서 서브트리 stop

### 시나리오 D: 극단값 처리
```json
{
  "data": [1e6, 1e-6, NaN, Infinity, -Infinity],
  "threshold": 0.30,
  "cumulative_cap": 0.50
}
```
**결과**: 정규화 후 일부 차단, 전체는 살아있음

## 📊 성능 목표

- **입력**: 10^4 실수 벡터, 깊이 ≤ 12, 노드 ≤ 64
- **P95 지연**: < 60ms
- **P99 지연**: < 120ms
- **메모리 피크**: < 256MB

## 🔧 API 레퍼런스

### POST /run
메인 실행 엔드포인트

**요청:**
```json
{
  "data": [1, 2, 3, 4, 5],
  "threshold": 0.30,
  "cumulative_cap": 0.50,
  "seed": 42
}
```

**응답:**
```json
{
  "output": [1.1, 2.2, 3.3, 4.4, 5.5],
  "timeline": "multiply → normalize → tanh → sum",
  "summary": {
    "rules_executed": 4,
    "blocks": 0,
    "cap_hits": 0,
    "duration_ms": 15.2,
    "cumulative_velocity": 0.234
  },
  "execution_id": "a1b2c3d4",
  "timestamp": 1640995200.0
}
```

### GET /health
헬스 체크

### GET /metrics
시스템 메트릭

## 🏗️ 아키텍처

```
src/
├── engine/
│   ├── core/           # OSS 핵심 엔진
│   │   ├── hier_exec.py    # 계층 실행기
│   │   ├── impact.py       # 임팩트 계산
│   │   ├── cap.py          # 누적 캡
│   │   └── filters.py      # 불평등 필터
│   └── pro/            # Pro 상업 기능
│       ├── parallel_exec.py    # 병렬 실행
│       ├── distributed.py      # 분산 처리
│       ├── advanced_dashboard.py # 고급 대시보드
│       └── ml_predictor.py     # ML 예측
├── api/                # REST API
├── dashboard/          # 웹 UI
└── utils/              # 유틸리티
```

## 📈 로그 형식

실행 로그는 JSONL 형식으로 `/log/annotations.jsonl`에 저장:

```json
{"ts": 1640995200.0, "path": "root/multiply", "node": "multiply", "type": "rule", "event": "exit", "impact": 0.15, "blocked": false, "cumulative": 0.15}
{"ts": 1640995200.1, "path": "root/normalize", "node": "normalize", "type": "rule", "event": "block", "impact": 0.72, "blocked": true, "cumulative": 0.15}
```

## 🔄 결정적 재실행

동일한 입력과 설정으로 실행하면 항상 동일한 경로를 재현:

```bash
# 시드 42로 실행
curl -X POST http://localhost:5000/run \
  -d '{"data": [1,2,3], "seed": 42}'

# 다시 시드 42로 실행 → 동일한 결과
curl -X POST http://localhost:5000/run \
  -d '{"data": [1,2,3], "seed": 42}'
```

## 🚀 Pro 라이선스

엔터프라이즈 기능이 필요하신가요?

- **병렬 실행**: 성능 최적화
- **분산 처리**: 클러스터 지원
- **고급 대시보드**: 실시간 시각화
- **ML 예측**: 사전 위험 평가
- **엔터프라이즈 지원**: 우선 지원, 컨설팅

**연락처**: contact@cosmos-hgp.com

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 [Apache License 2.0](LICENSE) 하에 배포됩니다.

## 📞 지원

- **이슈**: [GitHub Issues](https://github.com/IdeasCosmos/COSMOS_HGP/issues)
- **토론**: [GitHub Discussions](https://github.com/IdeasCosmos/COSMOS_HGP/discussions)
- **상업 라이선스**: contact@cosmos-hgp.com

---

**COSMOS-HGP**: 계층형 실행으로 안정성을 보장하는 차세대 데이터 처리 엔진