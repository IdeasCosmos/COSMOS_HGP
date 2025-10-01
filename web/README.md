# 🌟 COSMOS-HGP Premium Dashboard

React 18 + Tailwind CSS + Framer Motion으로 제작된 프리미엄 대시보드입니다.

## 🚀 빠른 시작

### 설치

```bash
cd web/
npm install
```

### 개발 서버 실행

```bash
npm run dev
```

브라우저에서 `http://localhost:5173` 접속

### 프로덕션 빌드

```bash
npm run build
```

빌드된 파일은 `dist/` 폴더에 생성됩니다.

## 📦 기술 스택

- **React 18** - UI 라이브러리
- **Tailwind CSS** - 유틸리티 CSS 프레임워크
- **Framer Motion** - 애니메이션
- **Recharts** - 차트 라이브러리
- **Lucide React** - 아이콘
- **Vite** - 빌드 도구

## 🎨 주요 기능

### ✨ 인터랙티브 UI
- 리플 버튼 효과
- 부드러운 애니메이션
- 반응형 디자인

### 📊 FREE 엔진 데모
- 실시간 데이터 처리
- 동적 차트 시각화
- Threshold 조절

### 🔒 PRO 기능 소개
- 6가지 PRO 기능 카드
- 애니메이션 프리뷰
- 상세 모달

## 🛠️ 개발

### 디렉토리 구조

```
web/
├── src/
│   ├── Dashboard.jsx  # 메인 컴포넌트
│   ├── main.jsx       # 진입점
│   └── index.css      # 전역 스타일
├── public/            # 정적 파일
├── index.html         # HTML 템플릿
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

### 스크립트

```bash
npm run dev      # 개발 서버
npm run build    # 프로덕션 빌드
npm run preview  # 빌드 미리보기
npm run lint     # ESLint 실행
```

## 🎯 배포

### Vercel

```bash
npm i -g vercel
vercel
```

### Netlify

```bash
npm run build
# dist/ 폴더를 Netlify에 드래그 앤 드롭
```

### GitHub Pages

```bash
npm run build
npm install -g gh-pages
gh-pages -d dist
```

## 🌐 환경 변수

`.env` 파일 생성:

```env
VITE_API_URL=https://your-api-domain.com
VITE_API_KEY=your_api_key_here
```

## 📱 브라우저 지원

- Chrome (최신)
- Firefox (최신)
- Safari (최신)
- Edge (최신)

## 🤝 기여

이슈와 PR은 언제나 환영합니다!

## 📄 라이선스

Apache License 2.0

---

**Made with ⚜️ by COSMOS-HGP Team**

