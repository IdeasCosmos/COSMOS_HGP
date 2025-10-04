1) API_DOCS_ko.md
# ⚜️ COSMOS-HGP API 문서 (KO)

## 인증
모든 **PRO** 엔드포인트는 Bearer 토큰 필요:


Authorization: Bearer sk_live_your_key


---

## 엔드포인트

### 1. GET `/`
헬스체크

**응답**
```json
{
  "status": "COSMOS-HGP PRO API",
  "version": "1.0"
}

2. POST /codon/analyze

Python 코드를 DNA 코돈으로 분석

요청

{
  "code": "def hello():\n    x = 1"
}


응답

{
  "codons": ["AAA", "TAA"],
  "layer_mapping": {
    "L1_QUANTUM": 0.12,
    "L2_ATOMIC": 0.20
  }
}

3. POST /velocity/calculate

계층별 탈출 속도 계산

요청

{
  "layer": 1,
  "impact": 0.25
}


응답

{
  "threshold": 0.12,
  "blocked": false,
  "recommendation": "pass"
}

에러 코드

400 잘못된 요청

401 인증 실패

500 서버 에러

속도 제한

PRO: 월 10,000 calls

초당 10 requests

Python 클라이언트 예시
from cosmos import CosmosAPI

api = CosmosAPI(api_key="sk_live_...")
result = api.analyze_codon("def hi(): return 1")
print(result)


---

### 📄 2) API_DOCS_en.md
```markdown
# ⚜️ COSMOS-HGP API Documentation (EN)

## Authentication
All **PRO** endpoints require a Bearer token:


Authorization: Bearer sk_live_your_key


---

## Endpoints

### 1. GET `/`
Health check

**Response**
```json
{
  "status": "COSMOS-HGP PRO API",
  "version": "1.0"
}

2. POST /codon/analyze

Analyze Python code into DNA codons

Request

{
  "code": "def hello():\n    x = 1"
}


Response

{
  "codons": ["AAA", "TAA"],
  "layer_mapping": {
    "L1_QUANTUM": 0.12,
    "L2_ATOMIC": 0.20
  }
}

3. POST /velocity/calculate

Calculate escape velocity per layer

Request

{
  "layer": 1,
  "impact": 0.25
}


Response

{
  "threshold": 0.12,
  "blocked": false,
  "recommendation": "pass"
}

Error Codes

400 Bad Request

401 Unauthorized

500 Server Error

Rate Limits

PRO: 10,000 calls/month

10 requests/second

Python Client Example
from cosmos import CosmosAPI

api = CosmosAPI(api_key="sk_live_...")
result = api.analyze_codon("def hi(): return 1")
print(result)


---

### 📄 3) README HTML 다국어 지원

`README_ko.html` / `README_en.html` 에 상단에 언어 전환 버튼 추가:

```html
<div style="text-align:right; margin-bottom:12px;">
  <a href="README_ko.html" class="btn">한국어</a>
  <a href="README_en.html" class="btn gold">English</a>
</div>