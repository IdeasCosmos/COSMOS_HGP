# 🌌 COSMOS-HGP MVP

**COSMOS (Cosmic Operations System with Multi-layered Orchestration and Self-healing)** - Hierarchical Gradient Propagation 시스템

**개발자**: 장재혁 (IdeasCosmos)  
**이메일**: sjpupro@gmail.com  
**라이선스**: MIT (OSS) + Commercial (Pro)

## 📸 스크린샷

![메인 대시보드](./images/dashboard_main.png)
![분석 결과](./images/analysis_results.png)
![시스템 테스트](./images/test_system.png)

## 📊 아키텍처

![시스템 아키텍처](./images/architecture_diagram.png)
![7계층 구조](./images/layer_structure.png)

## 📈 성능 지표

![성능 벤치마크](./images/performance_benchmark.png)
![메모리 사용량](./images/memory_usage.png)

## 📁 MVP 프로젝트 구조

```
COSMOS_MVP1001/
├── 📁 main/                # 메인 실행 파일들
├── 📁 core/                # 핵심 시스템 모듈 (엔진, 속도, 치유, 주석)
├── 📁 api/                 # API 서버 모듈 (인증, 서버, WebSocket)
├── 📁 utils/               # 유틸리티 (프로파일러)
├── 📁 scripts/             # 스크립트 (데이터 다운로드)
├── 📁 tests/               # 테스트 모듈 (단위, 통합, 성능)
├── 📁 templates/           # 웹 템플릿 (대시보드, 결과, 테스트)
├── 📁 images/              # 이미지 저장소 (스크린샷, 다이어그램)
├── 🚀 app.py               # Flask 대시보드 앱
├── 🚀 mvp_main.py          # MVP 메인 실행기
├── 🚀 main_test.py         # 통합 테스트 실행기
├── 📊 universal_csv_analyzer.py # 범용 CSV 분석기
├── 📊 unified_cosmos.py    # 통합 COSMOS 시스템
├── 📖 requirements.txt     # Python 의존성
└── 📖 README.md           # 프로젝트 문서
```

> **상세 구조**: [ARCHITECTURE_MVP.md](./ARCHITECTURE_MVP.md) 참조

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt
```

### 2. 메인 실행
```bash
# 대시보드 실행
python mvp_main.py dashboard

# CSV 파일 분석
python mvp_main.py analyze --file data.csv

# 자가 테스트 실행
python mvp_main.py test

# 프로파일러 실행
python mvp_main.py profiler

# 데이터 다운로드
python mvp_main.py download
```

### 3. 테스트 실행
```bash
# 전체 테스트
python main_test.py

# 빠른 테스트만
python main_test.py --test quick

# 특정 테스트
python main_test.py --test basic
python main_test.py --test integration
python main_test.py --test performance
python main_test.py --test profiler
python main_test.py --test api
python main_test.py --test self
```

## 🌟 주요 기능

### 🔧 핵심 시스템
- **7계층 우주속도 시스템**: L1_QUANTUM ~ L7_COSMOS
- **양방향 처리**: Top-Down (제어) + Down-Up (분석)
- **자가치유 시스템**: 오류 진단 및 자동 복구
- **국소적 실패 격리**: 연쇄 실패 방지

### 🔐 보안 및 인증
- **JWT 토큰 시스템**: 역할 기반 접근 제어
- **API 인증**: 사용자/관리자/시스템 역할
- **실시간 통신**: WebSocket 지원

### 📊 모니터링 및 프로파일링
- **자가 프로파일러**: 시스템 성능 실시간 모니터링
- **건강도 보고서**: 시스템 상태 및 권장사항
- **성능 메트릭**: CPU, 메모리, 처리량, 지연시간

### 🌐 웹 대시보드
- **Flask 기반**: 간단하고 빠른 웹 인터페이스
- **실시간 모니터링**: 시스템 상태 시각화
- **결과 분석**: CSV 데이터 분석 결과 표시
- **API 엔드포인트**: RESTful API 제공

## 🎯 도메인 지원

### 🤖 AIOps (IT 운영)
- 로그 분석 및 이상 탐지
- 경보 소음 억제
- 3WHY 문제 설명

### 💰 금융
- 위험도 계산
- 시장 분석
- 거래 모니터링

### 🏥 헬스케어
- 생체 신호 분석
- 환자 데이터 처리
- 의료 영상 분석

## 📈 성능 특징

- **높은 처리량**: 초당 50+ 작업 처리
- **낮은 지연시간**: 평균 < 50ms
- **메모리 효율성**: < 100MB 메모리 사용
- **확장성**: 최대 8개 워커 지원
- **안정성**: 99%+ 성공률

## 🔄 라이센스 전략

### 무료 기능 (MIT 라이센스)
- 기본 대시보드 (Flask/Streamlit)
- 제한된 안정/혁신 모드 사용
- 결과 출력 및 3WHY 설명

### 유료 기능 (상업 라이센스)
- 고급 대시보드 및 동적 시각화
- 무제한 사용 및 사전 차단
- 상세 문제 분석 + 컨설팅

## 🛠️ 개발 및 배포

### 개발 환경
```bash
# 개발 모드로 대시보드 실행
python app.py
```

### 프로덕션 배포
```bash
# 프로덕션 모드로 실행
python mvp_main.py dashboard
```

## 📞 지원

- **GitHub**: [IdeasCosmos/COSMOS_HGP](https://github.com/IdeasCosmos/COSMOS_HGP)
- **개발자**: 장재혁 (IdeasCosmos)
- **이메일**: sjpupro@gmail.com
- **문서**: 프로젝트 내 README 파일들
- **이슈**: GitHub Issues를 통한 버그 리포트

## 🚀 Pro 기능 (Commercial License)

- **병렬 실행**: 성능 최적화
- **분산 처리**: 클러스터 지원  
- **고급 대시보드**: 실시간 시각화
- **ML 예측**: 사전 위험 평가
- **엔터프라이즈 지원**: 우선 지원, 컨설팅

**Pro 라이선스 문의**: sjpupro@gmail.com

---

**COSMOS-HGP** - 우주적 규모의 운영 시스템으로 여러분의 비즈니스를 혁신하세요! 🚀
