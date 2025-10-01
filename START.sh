#!/bin/bash

echo "========================================"
echo "🚀 COSMOS-HGP Linux/macOS 실행기"
echo "========================================"
echo

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3이 설치되지 않았습니다"
    echo "💡 Python 3.8+ 설치 후 다시 시도하세요"
    exit 1
fi

# Node.js 확인
if ! command -v node &> /dev/null; then
    echo "❌ Node.js가 설치되지 않았습니다"
    echo "💡 Node.js 16+ 설치 후 다시 시도하세요"
    exit 1
fi

echo "✅ Python과 Node.js 확인됨"
echo

# 실행 권한 부여
chmod +x main.py

# 메인 실행
echo "🚀 COSMOS-HGP 시작 중..."
python3 main.py