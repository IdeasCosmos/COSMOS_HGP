#!/usr/bin/env python3
"""
COSMOS-HGP V2-min+ 배포판 GitHub 푸시 스크립트
"""

import subprocess
import os
import sys

def run_command(command, description):
    """명령어 실행"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print(f"✅ {description} 완료")
            if result.stdout.strip():
                print(f"   출력: {result.stdout.strip()}")
        else:
            print(f"❌ {description} 실패: {result.stderr.strip()}")
            return False
        return True
    except Exception as e:
        print(f"❌ {description} 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 COSMOS-HGP V2-min+ 배포판 GitHub 푸시")
    print("=" * 60)
    
    # 1. Git 초기화
    if not os.path.exists('.git'):
        if not run_command('git init', 'Git 리포지토리 초기화'):
            return
    else:
        print("✅ Git 리포지토리 이미 존재")
    
    # 2. 리모트 확인/추가
    result = subprocess.run('git remote -v', shell=True, capture_output=True, text=True)
    if 'origin' not in result.stdout:
        if not run_command('git remote add origin https://github.com/IdeasCosmos/COSMOS_HGP.git', '리모트 리포지토리 추가'):
            return
    else:
        print("✅ 리모트 리포지토리 이미 설정됨")
    
    # 3. 파일 추가
    if not run_command('git add .', '파일 스테이징'):
        return
    
    # 4. 커밋
    commit_message = """feat: COSMOS-HGP V2-min+ 배포 패키지

🌌 계층적 실행 엔진 - 국소 실패를 상위로 번지지 않게 차단

✨ 핵심 기능:
- 계층 실행: 중첩 그룹 순차 처리
- 국소 차단: impact >= threshold 시 노드 차단
- 누적 캡: V = 1 - Π(1 - v) 공식 적용
- 타임라인: ASCII 텍스트 실행 경로 표시
- 결정적 재실행: 동일 입력 시 동일 결과 보장

🚀 배포 지원:
- Docker 기반 컨테이너화
- MANUS AI, GENSPARK AI 배포 가이드
- Flask 웹 API
- 자동 테스트 스위트

📊 성능 목표:
- P95 < 60ms, P99 < 120ms
- 메모리 피크 < 256MB
- 입력 10^4 실수 벡터 지원"""
    
    if not run_command(f'git commit -m "{commit_message}"', '배포판 커밋'):
        return
    
    # 5. 브랜치 설정
    run_command('git branch -M main', '메인 브랜치 설정')
    
    # 6. 푸시
    if not run_command('git push -u origin main', '리포지토리에 푸시'):
        print("⚠️ 푸시 실패 - 인증이 필요할 수 있습니다.")
        print("GitHub에서 Personal Access Token을 사용하거나 SSH 키를 설정해주세요.")
        return
    
    print("\n🎉 COSMOS-HGP V2-min+ 배포판이 성공적으로 푸시되었습니다!")
    print("📋 리포지토리 URL: https://github.com/IdeasCosmos/COSMOS_HGP")
    print("\n📦 포함된 파일들:")
    print("  ✅ src/main.py - 메인 애플리케이션")
    print("  ✅ scripts/deploy.sh - 자동 배포 스크립트")
    print("  ✅ scripts/test_deployment.py - 배포 테스트")
    print("  ✅ docs/ - MANUS AI, GENSPARK AI 배포 가이드")
    print("  ✅ Dockerfile, docker-compose.yml - 컨테이너 설정")
    print("  ✅ requirements.txt - 의존성 목록")

if __name__ == "__main__":
    main()
