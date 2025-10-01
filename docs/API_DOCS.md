# COSMOS-HGP API 문서

## 인증

모든 PRO 엔드포인트는 Bearer 토큰이 필요합니다:

```
Authorization: Bearer test_key_12345
```

---

## 엔드포인트

### 1. GET /

**헬스체크**

인증 불필요

**응답:**
```json
{
  "status": "COSMOS-HGP PRO API",
  "version": "1.0"
}
```

---

### 2. GET /health

**서버 상태 확인**

인증 불필요

**응답:**
```json
{
  "healthy": true
}
```

---

### 3. POST /codon/analyze

**Python 코드를 DNA 코돈으로 분석**

인증 필요

**요청:**
```json
{
  "code": "def hello():\n    x = 1\n    for i in range(10):\n        print(i)"
}
```

**응답:**
```json
{
  "codons": ["AAA", "TAA", "GAA"],
  "layer_mapping": {
    "L1_QUANTUM": 0.12,
    "L2_ATOMIC": 0.20,
    "L3_MOLECULAR": 0.25
  }
}
```

**에러:**
```json
{
  "detail": "Invalid Python code syntax"
}
```

---

### 4. POST /velocity/calculate

**계층별 탈출 속도 계산**

인증 필요

**요청:**
```json
{
  "layer": 1,
  "impact": 0.25
}
```

**응답:**
```json
{
  "threshold": 0.12,
  "blocked": true,
  "recommendation": "block"
}
```

**에러:**
```json
{
  "detail": "Invalid layer provided: 8"
}
```

---

## 에러 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 400 | Bad Request | 잘못된 요청 형식 또는 파라미터 |
| 401 | Unauthorized | 인증 실패 (API 키 없음/잘못됨) |
| 500 | Internal Server Error | 서버 내부 오류 |

---

## 속도 제한

- **PRO**: 10,000 calls/월
- **Rate Limit**: 초당 10 requests

---

## Python 클라이언트

### 설치
```bash
pip install cosmos-hgp
```

### 사용법
```python
from cosmos import CosmosAPI

# API 클라이언트 초기화
api = CosmosAPI(api_key="test_key_12345")

# Codon 분석
result = api.analyze_codon("""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
""")
print(result)

# Velocity 계산
velocity = api.calculate_velocity(layer=3, impact=0.26)
print(velocity)
```

---

## cURL 예제

### Codon 분석
```bash
curl -X POST "http://localhost:7860/codon/analyze" \
  -H "Authorization: Bearer test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello():\n    x = 1"}'
```

### Velocity 계산
```bash
curl -X POST "http://localhost:7860/velocity/calculate" \
  -H "Authorization: Bearer test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"layer": 1, "impact": 0.25}'
```

---

## 지원

- **문서**: [https://cosmos-hgp.dev](https://cosmos-hgp.dev)
- **이슈**: [GitHub Issues](https://github.com/IdeasCosmos/COSMOS_HGP/issues)
- **이메일**: sjpupro@gmail.com

