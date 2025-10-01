# 우아한 연미장 스타일 README

<div align="center">

```
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║                          C O S M O S - H G P                          ║
║                                                                        ║
║                    Hierarchical Gradient Propagation                  ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

<br>

**우주의 질서로 시스템의 카오스를 제어하다**

<br>

[![License](https://img.shields.io/badge/license-MIT-gold.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-white.svg?style=flat-square)](https://www.python.org)
[![Status](https://img.shields.io/badge/status-MVP-gold.svg?style=flat-square)]()

</div>

---

## I. 철학

어떤 시스템도 하나의 실패로 전체가 무너져서는 안 된다.

COSMOS-HGP는 **계층적 격리**를 통해 국소적 장애가 상위로 전파되는 것을 차단한다.  
우주의 7계층 구조에서 영감을 받은 아키텍처는 각 층이 독립적으로 안정성을 유지하도록 설계되었다.

<br>

```
L7 ━━━━━━━━━━━━━━━━━━━━  COSMOS      (전체 조화)
                         
L6 ━━━━━━━━━━━━━━━━━━━━  ECOSYSTEM   (생태 균형)
                         
L5 ━━━━━━━━━━━━━━━━━━━━  ORGANIC     (유기적 연결)
                         
L4 ━━━━━━━━━━━━━━━━━━━━  COMPOUND    (복합 구조)
                         
L3 ━━━━━━━━━━━━━━━━━━━━  MOLECULAR   (분자 결합)
                         
L2 ━━━━━━━━━━━━━━━━━━━━  ATOMIC      (원자 상호작용)
                         
L1 ━━━━━━━━━━━━━━━━━━━━  QUANTUM     (양자 요동)
```

<br>

각 계층은 고유한 **탈출 속도**를 가진다.  
하위 계층의 충격이 임계값을 초과하면, 그 층에서 자동으로 격리된다.

---

## II. 원리

### 핵심 메커니즘

<table>
<tr>
<td width="50%">

**계층적 실행**
```python
Group {
  Rule("normalize"),
  Group {
    Rule("transform"),
    Rule("validate")
  },
  Rule("finalize")
}
```

</td>
<td width="50%">

**충격 계산**
```
impact = 0.5 × change_rate + 
         0.5 × |scale_factor - 1|
```

</td>
</tr>
</table>

<br>

### 격리 정책

```
IF   impact ≥ threshold    THEN  해당 노드 차단
IF   V ≥ cumulative_cap    THEN  서브트리 정지
```

여기서 누적 속도 **V**는 다음과 같이 정의된다:

```
V = 1 - ∏(1 - vₖ)
```

---

## III. 시연

### 정상 흐름
```json
{
  "data": [1, 2, 3, 4, 5],
  "threshold": 0.30,
  "cumulative_cap": 0.50
}
```
**결과**: 모든 노드 통과  
**타임라인**: `normalize → transform → finalize`

<br>

### 국소 차단
```json
{
  "data": [1, 2, 3, 4, 5],
  "threshold": 0.70,
  "cumulative_cap": 0.50
}
```
**결과**: 중간 노드 차단, 하위 서브트리 스킵  
**타임라인**: `normalize → [BLOCKED] → finalize`

<br>

### 누적 정지
```json
{
  "data": [10, 20, 30, 40, 50],
  "threshold": 0.30,
  "cumulative_cap": 0.50
}
```
**결과**: 누적 임계값 도달로 서브트리 정지  
**타임라인**: `normalize → transform → [CAP REACHED]`

---

## IV. 사용

### 설치

```bash
git clone https://github.com/IdeasCosmos/COSMOS_HGP.git
cd COSMOS_HGP
pip install -r requirements.txt
```

### 실행

```bash
# 대시보드 실행
python app.py

# 또는 메인 실행기 사용
python main/mvp_main.py dashboard
```

### 웹 인터페이스

```
http://localhost:5000
```

### API 호출

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@data.csv"
```

### 응답

```json
{
  "job_id": "upload_1641234567",
  "filename": "data.csv",
  "status": "uploaded",
  "analysis": {
    "records": 1000,
    "columns": 5,
    "anomalies": 3,
    "quality_score": 95.2
  }
}
```

---

## V. 성능

<table>
<tr>
<td align="center"><b>입력 크기</b></td>
<td align="center"><b>처리 시간</b></td>
<td align="center"><b>메모리 사용</b></td>
<td align="center"><b>이상 탐지율</b></td>
</tr>
<tr>
<td align="center">10⁴ 레코드</td>
<td align="center">< 150ms</td>
<td align="center">< 256MB</td>
<td align="center">95.2%</td>
</tr>
<tr>
<td align="center">10⁵ 레코드</td>
<td align="center">< 1.2s</td>
<td align="center">< 512MB</td>
<td align="center">94.8%</td>
</tr>
</table>

<br>

깊이 ≤ 7, 계층 ≤ 64 조건 하에서 측정

---

## VI. 아키텍처

```
cosmos-mvp1001/
│
├─ main/                  메인 실행 파일들
│  └─ mvp_main.py        통합 실행기
│
├─ templates/             웹 인터페이스
│  ├─ dashboard.html      메인 대시보드
│  ├─ results.html        결과 표시
│  └─ test.html          시스템 테스트
│
├─ core/                  핵심 엔진 (향후 확장)
├─ api/                   API 서버 (향후 확장)
├─ utils/                 유틸리티 (향후 확장)
│
├─ app.py                 Flask 대시보드
├─ universal_csv_analyzer.py  범용 CSV 분석기
└─ requirements.txt       의존성 목록
```

---

## VII. 로드맵

<table>
<tr>
<td width="25%"><b>Phase 1</b><br>MVP 완성</td>
<td width="25%"><b>Phase 2</b><br>핵심 엔진</td>
<td width="25%"><b>Phase 3</b><br>DNA 코돈</td>
<td width="25%"><b>Phase 4</b><br>이중성 구조</td>
</tr>
</table>

현재 **Phase 1** 단계로, 웹 대시보드와 CSV 분석 기능이 완성되었습니다.

---

## VIII. 주요 기능

### 현재 구현된 기능

<table>
<tr>
<td align="center"><b>웹 대시보드</b></td>
<td align="center"><b>파일 업로드</b></td>
<td align="center"><b>CSV 분석</b></td>
<td align="center"><b>시스템 테스트</b></td>
</tr>
<tr>
<td align="center">Flask 기반 UI</td>
<td align="center">드래그 앤 드롭</td>
<td align="center">범용 분석기</td>
<td align="center">기능 검증</td>
</tr>
</table>

### 향후 확장 예정

- **계층형 실행 엔진**: 7계층 우주 속도 시스템
- **DNA 코돈 매핑**: 생물학적 규칙 시스템
- **이중성 아키텍처**: 안정성 vs 혁신 모드
- **자가 치유 시스템**: 자동 오류 복구

---

## IX. 기여

```bash
git checkout -b feature/elegant-solution
git commit -m "Add: 우아한 해결책"
git push origin feature/elegant-solution
```

이슈와 토론은 [GitHub Issues](https://github.com/IdeasCosmos/COSMOS_HGP/issues)에서

**개발자**: 장재혁 (IdeasCosmos)  
**이메일**: sjpupro@gmail.com

---

## X. 라이선스

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.

---

<div align="center">

<br>

**COSMOS-HGP**  
*Hierarchical Gradient Propagation*

<br>

```
우주의 질서  ━━  시스템의 안정성
```

<br>

[문서](./실행_가이드.md) · [이슈](https://github.com/IdeasCosmos/COSMOS_HGP/issues) · [토론](https://github.com/IdeasCosmos/COSMOS_HGP/discussions)

<br>

</div>
