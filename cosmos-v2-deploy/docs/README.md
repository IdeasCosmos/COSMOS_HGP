# COSMOS-HGP V2-min+

**국소 실패를 상위로 번지지 않게 차단하는 '계층형 실행 엔진'**

## 🚀 핵심 기능

### 핵심 3요소
1. **계층 실행**: 중첩 그룹을 순차 처리
2. **국소 차단**: `impact >= threshold`면 해당 노드/서브트리만 차단
3. **누적 캡**: `V = 1 - Π(1 - v)`가 cap 도달 시 해당 서브트리 정지

### 가시성 2요소
4. **결과 타임라인**: ASCII 텍스트 타임라인 출력
5. **결정적 재실행**: 동일 입력·설정일 때 동일 경로 재현

## 📦 배포

### Docker로 실행
```bash
# 빌드
docker build -t cosmos-hgp:v2-min+ .

# 실행
docker run -p 5000:5000 cosmos-hgp:v2-min+

# 또는 docker-compose 사용
docker-compose up -d
```

### 접속
- 웹 인터페이스: http://localhost:5000
- API 엔드포인트: http://localhost:5000/run
- 헬스 체크: http://localhost:5000/health

## 🎯 데모 시나리오

### 시나리오 A: 정상 흐름
- 입력: `[1, 2, 3, 4, 5]`
- 임계값: `0.30`
- 기대: 모든 노드 통과

### 시나리오 B: 국소 차단
- 동일 입력 + 임계값: `0.70`
- 기대: 중간 레벨 노드 차단, 하위 서브트리 스킵

### 시나리오 C: 누적캡 차단
- 동일 입력 + 누적캡: `0.30`
- 기대: 누적 V≥0.30 지점에서 서브트리 정지

## 📊 성능 목표

- 입력 10^4 실수 벡터, 깊이 ≤ 12, 노드 ≤ 64
- **P95 < 60ms**, P99 < 120ms
- 메모리 피크 **< 256MB**

## 🔧 API 사용법

### POST /run
```json
{
  "data": [1, 2, 3, 4, 5],
  "group_def": {
    "name": "main",
    "type": "group",
    "children": [
      {"name": "A_Init", "type": "rule"},
      {"name": "B_Scale", "type": "rule"},
      {"name": "C_Normalize", "type": "rule"}
    ]
  },
  "threshold": 0.30,
  "cumulative_cap": 0.50
}
```

### 응답
```json
{
  "output": [결과값],
  "blocked": false,
  "path": "main/A_Init/B_Scale/C_Normalize",
  "timeline": "A_Init → B_Scale → C_Normalize",
  "summary": {
    "rules_executed": 3,
    "blocks": 0,
    "cap_hits": 0,
    "cumulative_velocity": 0.15,
    "duration_ms": 2.1
  }
}
```

## 📝 로그

실행 로그는 `/app/log/annotations.jsonl`에 JSONL 형식으로 저장됩니다.

## 🏗️ 아키텍처

- **엔진**: `CosmosEngine` - 핵심 실행 로직
- **규칙**: `Rule` - 개별 처리 단위
- **그룹**: `GroupDef` - 계층적 그룹 정의
- **결과**: `ExecutionResult` - 실행 결과 및 메타데이터

## 🔍 모니터링

- 실시간 타임라인 표시
- 실행 메트릭 (규칙 실행 수, 차단 수, 누적 속도)
- 성능 지표 (실행 시간, 깊이, 캡 히트)
