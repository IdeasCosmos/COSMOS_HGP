# COSMOS-HGP V2-min+ 배포 가이드

## 🚀 GitHub 푸시 방법

### 방법 1: 수정된 배치 파일 사용 (권장)
1. `fix_and_deploy.cmd` 파일을 **더블클릭**하여 실행
2. 관리자 권한이 필요할 수 있음

### 방법 2: 수동 명령어 실행
**명령 프롬프트(cmd)**를 관리자 권한으로 실행하고:

```cmd
cd /d "C:\path\to\cosmos-v2-deploy"
git init
git remote add origin https://github.com/IdeasCosmos/COSMOS_HGP.git
git add .
git commit -m "feat: COSMOS-HGP V2-min+ deployment package"
git branch -M main
git push -u origin main
```

### 방법 3: GitHub Desktop 사용
1. GitHub Desktop 설치
2. "Clone a repository from the Internet" 선택
3. URL: `https://github.com/IdeasCosmos/COSMOS_HGP.git`
4. 파일들을 복사하고 커밋/푸시

### 방법 4: GitHub 웹에서 직접 업로드
1. https://github.com/IdeasCosmos/COSMOS_HGP 접속
2. "Add file" → "Upload files" 클릭
3. `cosmos-v2-deploy` 폴더의 모든 파일들을 드래그 앤 드롭

## 🔧 문제 해결

### 권한 문제
- 관리자 권한으로 명령 프롬프트 실행
- 또는 다른 디렉토리에서 실행

### Git 인증 문제
- Personal Access Token 사용
- 또는 SSH 키 설정

### 한글 인코딩 문제
- `chcp 65001` 명령어로 UTF-8 설정
- 또는 영문으로만 작업

## 📁 배포할 파일들

```
cosmos-v2-deploy/
├── src/main.py              # 메인 애플리케이션
├── scripts/deploy.sh        # 자동 배포 스크립트
├── scripts/test_deployment.py # 배포 테스트
├── docs/                    # 배포 가이드
│   ├── README.md
│   ├── MANUS_AI_DEPLOYMENT.md
│   └── GENSPARK_AI_DEPLOYMENT.md
├── Dockerfile              # Docker 설정
├── docker-compose.yml      # 컨테이너 오케스트레이션
├── requirements.txt        # 의존성
├── .gitignore             # Git 무시 파일
└── README.md              # 프로젝트 가이드
```

## 🎯 배포 완료 후

배포가 완료되면 다음을 확인할 수 있습니다:
- ✅ GitHub 리포지토리에 모든 파일 업로드
- ✅ README.md 자동 표시
- ✅ Docker 설정 파일들
- ✅ 배포 가이드 문서들
