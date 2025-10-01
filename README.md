# ⚜️ COSMOS HGP
**Gold & White Edition**

> *"모든 코드는 생명의 언어로 번역될 수 있다."*

╭━⚜️━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━⚜️━╮

## ✨ 공식 가이드

**COSMOS-HGP (Cosmic Hierarchical Genetic Processing)** - 차세대 AI 시스템 통합 플랫폼

7계층 구조와 64개 DNA 코돈을 기반으로 한 혁신적인 AI 처리 시스템입니다. FREE와 PRO 두 가지 버전으로 제공되며, 다양한 도메인(AIOps, Finance, Healthcare)에 특화된 컨설팅 기능을 제공합니다.

## 🚀 1) 시작하기 (Getting Started)

### 설치 (Installation)
```bash
# 방법 A (권장)
pip install cosmos-hgp

# 방법 B (소스에서 직접 설치)
git clone https://github.com/IdeasCosmos/COSMOS_HGP.git
cd COSMOS_HGP
pip install -e .
```

### 5분 튜토리얼 (First Run)
라이브러리의 기본 엔진을 경험해 보세요.

**모듈 가져오기 (Import)**
```python
from cosmos import BasicEngine
```

**엔진 생성 (Initialize Engine)**
```python
engine = BasicEngine()
```

**규칙 정의 (Define Rules)**
```python
rules = [
    {"name": "double", "func": lambda x: x * 2},
    {"name": "add_one", "func": lambda x: x + 1}
]
```

**실행 (Execute)**
```python
result = engine.execute([1, 2, 3], rules)
print(result)
```

--- ✧ ---

## ⚙️ 2) 고급 사용법 (Advanced Usage)

### 중첩 규칙 (Nested Rules)
규칙 내부에 하위 규칙을 정의하여 복잡한 로직을 구성합니다.

```python
rules = [
    {"name": "outer", "func": ...},
    [
        {"name": "inner1", "func": ...},
        {"name": "inner2", "func": ...}
    ]
]
```

### 임계값 조정 (Threshold Adjustment)
엔진의 민감도를 제어하여 실행을 최적화합니다.

```python
result = engine.execute(
    data,
    rules,
    threshold=0.5,      # 높을수록 엄격
    cumulative_cap=0.7  # 누적 한계
)
```

--- ✧ ---

## 💎 3) PRO 기능: Quantum Codon Analysis API

Python 코드를 양자적 DNA 코돈으로 변환하고, 다차원적 계층으로 분석하는 PRO API입니다.

### API 키 발급
1. `cosmos-hgp.com/pricing` 방문
2. PRO 플랜 구독 후 이메일로 API 키 수신

### 코드에서 사용 예시
```python
from cosmos import CosmosAPI

# 발급받은 API 키를 입력하세요
api = CosmosAPI(api_key="sk_live_...") 

# 분석하고 싶은 Python 코드를 문자열로 전달합니다
codons = api.analyze_codon("your python code here")
print(codons)
```

### 🆓 FREE 기능
- **기본 엔진**: 계층형 실행, Impact 계산, 국소 차단
- **DNA 코돈**: 월 50회 분석 (제한)
- **대시보드**: 전체 기능 UI 미리보기

### 💎 PRO 기능 ($5/월)
- **무제한 사용**: DNA 코돈 무제한, API 호출 무제한
- **7계층 속도 제어**: 읽기/쓰기 가능한 임계값 조정
- **이중성 모드**: Stability/Innovation/Adaptive 전환
- **양방향 처리**: Top-Down/Bottom-Up 실행
- **예측 차단**: ML 기반 cascade 예측
- **자가 치유**: 자동 복구 시스템
- **병렬 처리**: GPU 가속 배치 처리
- **실시간 텔레메트리**: 모니터링 및 분석
- **자가 디버깅**: 6가지 자동 테스트
- **CSV 분석**: 모든 유형 자동 감지
- **웹로그 분석**: 공격 패턴 탐지
- **도메인 컨설팅**: AIOps/Finance/Healthcare 전문 분석

## 🏗️ 아키텍처

```
COSMOS_V1/
├── cosmos/              # FREE 패키지 (공개)
│   ├── engine.py        # 기본 엔진
│   ├── api_client.py    # PRO API 호출
│   └── exceptions.py    # 예외 처리
├── web/                 # 웹 대시보드 (공개)
│   ├── src/
│   │   └── Dashboard.jsx
│   ├── index.html
│   └── package.json
├── tests/               # 테스트 (공개)
│   ├── test_basic.py
│   └── test_integration.py
├── docs/                # 문서 (공개)
│   ├── API_DOCS.md
│   ├── USAGE_GUIDE.md
│   └── ARCHITECTURE.md
├── main.py              # 통합 실행기
├── start.bat            # Windows 실행기
├── start.sh             # Linux/macOS 실행기
└── README.md            # 이 파일
```

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/yourusername/COSMOS-HGP.git
cd COSMOS-HGP
```

### 2. 종속성 설치
```bash
# Python 종속성
pip install fastapi uvicorn pydantic numpy pandas python-multipart

# Node.js 종속성
cd web
npm install
cd ..
```

### 3. 실행
```bash
# Windows
start.bat

# Linux/macOS
./start.sh

# 또는 직접
python main.py
```

### 4. 접속
- **대시보드**: http://localhost:3000
- **API 문서**: http://localhost:7860/docs

## 🔧 개발 환경 설정

### Python 환경
```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 또는 venv\Scripts\activate  # Windows

# 종속성 설치
pip install -r requirements.txt
```

### Node.js 환경
```bash
cd web
npm install
npm run dev
```

## 📚 API 문서

### 기본 엔드포인트
- `GET /` - 루트
- `GET /health` - 헬스 체크
- `GET /pro/features` - 기능 목록

### FREE 기능
- `POST /codon/analyze` - DNA 코돈 분석 (월 50회 제한)

### PRO 기능 (인증 필요)
- `POST /velocity/calculate` - 7계층 속도 계산
- `POST /pro/process` - 예측+양방향+자가치유
- `POST /pro/batch` - 병렬 처리
- `POST /pro/duality/switch` - 이중성 모드 전환
- `POST /pro/threshold/adjust` - 임계값 조정
- `GET /pro/telemetry` - 실시간 텔레메트리
- `GET /pro/stats` - 통계 정보
- `POST /selftest` - 자가 디버깅
- `POST /analyze/csv` - CSV 분석
- `POST /analyze/weblog` - 웹로그 분석
- `POST /consult/{domain}` - 도메인 컨설팅

## 🔐 인증

PRO 기능 사용을 위해서는 API 키가 필요합니다.

```bash
# 헤더에 API 키 포함
Authorization: Bearer YOUR_API_KEY
```

## 🧪 테스트

```bash
# Python 테스트
python -m pytest tests/

# API 테스트
curl http://localhost:7860/health
curl http://localhost:7860/pro/features
```

## 📊 성능

- **처리 속도**: 평균 50ms (단일 요청)
- **동시 처리**: 최대 1000 요청/초
- **메모리 사용량**: 기본 200MB, 최대 2GB
- **응답 시간**: 99% 요청이 100ms 이내

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 Apache 2.0 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

- **GitHub**: [IdeasCosmos/COSMOS_HGP](https://github.com/IdeasCosmos/COSMOS_HGP)
- **개발자**: 장재혁 (IdeasCosmos)
- **이메일**: sjpupro@gmail.com
- **이슈**: [GitHub Issues](https://github.com/IdeasCosmos/COSMOS_HGP/issues)
- **토론**: [GitHub Discussions](https://github.com/IdeasCosmos/COSMOS_HGP/discussions)

## 🗺️ 로드맵

- [ ] v2.0: GPU 가속 지원
- [ ] v2.1: 실시간 스트리밍
- [ ] v2.2: 다국어 지원
- [ ] v3.0: 클라우드 네이티브 아키텍처

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트들의 도움을 받았습니다:
- FastAPI
- React
- Vite
- Tailwind CSS
- Framer Motion

---

╰━⚜️━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━⚜️━╯

**COSMOS-HGP** - 우주적 규모의 운영 시스템으로 여러분의 비즈니스를 혁신하세요! 🚀

**⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!**