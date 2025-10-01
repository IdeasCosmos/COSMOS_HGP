# ⚜️ COSMOS HGP
**Cosmic Hierarchical Genetic Processing**

> *"모든 코드는 생명의 언어로 번역될 수 있다."*

╭━⚜️━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━⚜️━╮

## ✨ 소개

**COSMOS-HGP (Cosmic Hierarchical Genetic Processing)** - 차세대 AI 시스템 통합 플랫폼

7계층 구조와 64개 DNA 코돈을 기반으로 한 혁신적인 AI 처리 시스템입니다. FREE와 PRO 두 가지 버전으로 제공되며, 다양한 도메인(AIOps, Finance, Healthcare)에 특화된 컨설팅 기능을 제공합니다.

---

## 🚀 빠른 시작 (Quick Start)

### 1️⃣ 저장소 클론
```bash
git clone https://github.com/IdeasCosmos/COSMOS_HGP.git
cd COSMOS_HGP
```

### 2️⃣ 종속성 설치
```bash
# Python 패키지 설치
pip install -r requirements.txt
```

### 3️⃣ 실행
```bash
# Windows
START.bat

# Linux/macOS
chmod +x START.sh
./START.sh

# 또는 Python으로 직접 실행
python main.py
```

---

## 📦 기본 사용법 (Basic Usage)

### 무료 기능 사용하기
```python
from cosmos import Engine

# 엔진 초기화
engine = Engine()

# 기본 처리 실행
result = engine.process(data)
print(result)
```

### PRO 기능 사용하기 (API)
```python
from cosmos import CosmosAPI

# Hugging Face API를 통해 PRO 기능 호출
api = CosmosAPI(
    api_key="your_api_key",
    base_url="https://huggingface.co/spaces/janjaess/COSMOS-_HGP"
)

# DNA 코돈 분석 (PRO)
result = api.analyze_codon("your python code")
print(result)

# 7계층 속도 계산 (PRO)
velocity = api.calculate_velocity(data)
print(velocity)
```

---

## 🆓 무료 기능 (FREE Features)

GitHub에서 다운로드 가능한 무료 오픈소스 버전:

- ✅ **기본 엔진**: 계층형 실행 및 Impact 계산
- ✅ **로컬 실행**: 자체 환경에서 실행 가능
- ✅ **커스터마이징**: 소스 코드 수정 가능
- ✅ **웹 인터페이스**: 기본 대시보드 포함
- ✅ **테스트 코드**: 전체 테스트 스위트 포함
- ✅ **문서**: 전체 API 문서 제공

---

## 💎 PRO 기능 (PRO Features - $5/월)

Hugging Face Spaces에서 제공되는 프리미엄 기능:

🔗 **PRO 버전 접속**: https://huggingface.co/spaces/janjaess/COSMOS-_HGP

### 고급 분석 기능
- 🧬 **DNA 코돈 분석**: Python 코드를 64개 DNA 코돈으로 변환
- ⚡ **7계층 속도 제어**: 읽기/쓰기 가능한 임계값 실시간 조정
- 🔄 **이중성 모드**: Stability/Innovation/Adaptive 전환
- 🔀 **양방향 처리**: Top-Down/Bottom-Up 동시 실행
- 🎯 **예측 차단**: ML 기반 cascade 예측 및 사전 차단

### AI 기반 기능
- 🔮 **자가 치유**: 자동 복구 및 최적화 시스템
- 🚀 **병렬 처리**: GPU 가속 배치 처리
- 📊 **실시간 텔레메트리**: 상세한 모니터링 및 분석
- 🐛 **자가 디버깅**: 6가지 자동 테스트 및 검증
- 📈 **CSV 분석**: 모든 데이터 형식 자동 감지
- 🔐 **웹로그 분석**: 보안 위협 및 공격 패턴 탐지

### 도메인 전문 컨설팅
- 🖥️ **AIOps**: IT 운영 자동화 및 장애 예측
- 💰 **Finance**: 금융 데이터 분석 및 리스크 관리
- 🏥 **Healthcare**: 의료 데이터 처리 및 패턴 분석

### PRO API 엔드포인트
```python
# DNA 코돈 분석
POST /codon/analyze

# 7계층 속도 계산
POST /velocity/calculate

# 통합 처리 (예측+양방향+자가치유)
POST /pro/process

# 병렬 배치 처리
POST /pro/batch

# 이중성 모드 전환
POST /pro/duality/switch

# 임계값 조정
POST /pro/threshold/adjust

# 실시간 텔레메트리
GET /pro/telemetry

# 통계 정보
GET /pro/stats

# 자가 디버깅
POST /selftest

# CSV 분석
POST /analyze/csv

# 웹로그 분석
POST /analyze/weblog

# 도메인 컨설팅
POST /consult/{domain}
```

---

## 🏗️ 프로젝트 구조

```
COSMOS_V1/
├── cosmos/              # FREE 패키지 (공개)
│   ├── engine.py        # 기본 엔진
│   ├── api_client.py    # PRO API 호출 클라이언트
│   └── exceptions.py    # 예외 처리
│
├── web/                 # 웹 대시보드 (공개)
│   ├── src/
│   │   └── Dashboard.jsx
│   ├── index.html
│   └── pricing.html
│
├── tests/               # 테스트 (공개)
│   ├── test_basic.py
│   └── test_engine.py
│
├── docs/                # 문서 (공개)
│   ├── API_DOCS.md
│   ├── CHANGELOG.md
│   └── 공식가이드.md
│
├── main.py              # 통합 실행기
├── START.bat            # Windows 실행 스크립트
├── START.sh             # Linux/macOS 실행 스크립트
├── requirements.txt     # Python 의존성
├── setup.py             # 설치 스크립트
├── LICENSE              # Apache 2.0 라이선스
└── README.md            # 이 파일

# PRO 기능은 별도 서버에서 제공
# (core_modules/, pro/ - 비공개)
```

---

## 🔧 개발 환경 설정

### Python 환경
```bash
# Python 3.9+ 권장
python --version

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 또는 venv\Scripts\activate  # Windows

# 종속성 설치
pip install -r requirements.txt
```

### 시스템 요구사항
- **Python**: 3.9 이상
- **메모리**: 최소 2GB RAM
- **디스크**: 최소 500MB 여유 공간
- **OS**: Windows, Linux, macOS

---

## 📚 상세 문서

- 📖 [API 문서](docs/API_DOCS.md)
- 📝 [변경 로그](docs/CHANGELOG.md)
- 🇰🇷 [한국어 가이드](docs/공식가이드.md)
- 🇬🇧 [English API Docs](docs/API_DOCS_en.html)

---

## 💰 가격 정책

| 기능 | 무료 (FREE) | PRO |
|------|------------|-----|
| **기본 엔진** | ✅ 무제한 | ✅ 무제한 |
| **DNA 코돈 분석** | ❌ | ✅ 무제한 |
| **7계층 속도 제어** | ❌ | ✅ |
| **AI 예측 차단** | ❌ | ✅ |
| **자가 치유** | ❌ | ✅ |
| **병렬 처리** | ❌ | ✅ |
| **도메인 컨설팅** | ❌ | ✅ |
| **가격** | **무료** | **$5/월** |

👉 **PRO 구독**: https://huggingface.co/spaces/janjaess/COSMOS-_HGP

---

## 🧪 테스트

```bash
# 기본 테스트 실행
python -m pytest tests/

# 특정 테스트 실행
python tests/test_basic.py
```

---

## 📊 성능 지표

- **처리 속도**: 평균 50ms (단일 요청)
- **메모리 사용량**: 기본 200MB
- **확장성**: 수평 확장 가능

---

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

이 프로젝트는 **Apache 2.0 라이선스** 하에 배포됩니다.

자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 📞 연락처 및 지원

- **GitHub**: [IdeasCosmos/COSMOS_HGP](https://github.com/IdeasCosmos/COSMOS_HGP)
- **Hugging Face**: [janjaess/COSMOS-_HGP](https://huggingface.co/spaces/janjaess/COSMOS-_HGP)
- **개발자**: Ideas_of_Cosmos
- **이메일**: jbb1956@nate.com
- **이슈**: [GitHub Issues](https://github.com/IdeasCosmos/COSMOS_HGP/issues)
- **토론**: [GitHub Discussions](https://github.com/IdeasCosmos/COSMOS_HGP/discussions)

---

## 🗺️ 로드맵

- [x] v1.0: 무료 버전 공개 (2025 Q1)
- [ ] v1.5: PRO API 정식 출시 (2025 Q2)
- [ ] v2.0: GPU 가속 지원 (2025 Q3)
- [ ] v2.5: 실시간 스트리밍 (2025 Q4)
- [ ] v3.0: 클라우드 네이티브 아키텍처 (2026)

---

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트들의 도움을 받았습니다:
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

---

╰━⚜️━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━⚜️━╯

**COSMOS-HGP** - 우주적 규모의 운영 시스템으로 여러분의 비즈니스를 혁신하세요! 🚀

**⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!**
