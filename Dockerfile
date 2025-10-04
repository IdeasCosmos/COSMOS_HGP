# Stage 1: Frontend 빌드
FROM node:18-alpine AS frontend-build

WORKDIR /app/web

# 의존성 설치
COPY web/package*.json ./
RUN npm ci --only=production

# 소스 코드 복사 및 빌드
COPY web/ ./
RUN npm run build

# Stage 2: Python 백엔드
FROM python:3.12-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 백엔드 코드 복사
COPY *.py ./
COPY data/ ./data/

# 프론트엔드 빌드 복사
COPY --from=frontend-build /app/web/dist ./web/dist

# 환경 변수
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# 포트 노출
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/health')"

# 서버 시작
CMD ["python", "simple_backend.py"]
