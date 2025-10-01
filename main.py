#!/usr/bin/env python3
"""
COSMOS-HGP 통합 실행기
하나의 명령어로 API 서버 + 웹 대시보드 자동 실행

사용법:
    python main.py

기능:
- API 서버 자동 시작 (포트 7860)
- 웹 대시보드 자동 빌드 및 서빙 (포트 3000)
- 브라우저 자동 열기
- 통합 로그 관리
"""

import os
import sys
import time
import webbrowser
import subprocess
import threading
import signal
from pathlib import Path
from datetime import datetime

class CosmosLauncher:
    def __init__(self):
        self.api_process = None
        self.web_process = None
        self.running = True
        
    def print_banner(self):
        """시작 배너 출력"""
        print("\n" + "="*60)
        print("🚀 COSMOS-HGP 통합 실행기")
        print("="*60)
        print("📡 API 서버: http://localhost:7860")
        print("🌐 웹 대시보드: http://localhost:3000")
        print("📖 API 문서: http://localhost:7860/docs")
        print("🔑 테스트 키: test_key_12345")
        print("="*60)
        print("⏹️  종료하려면 Ctrl+C를 누르세요")
        print("="*60 + "\n")
    
    def check_dependencies(self):
        """종속성 확인"""
        print("🔍 종속성 확인 중...")
        
        # Python 패키지 확인
        try:
            import fastapi
            import uvicorn
            import pandas
            import numpy
            print("✅ Python 종속성 확인됨")
        except ImportError as e:
            print(f"❌ Python 종속성 누락: {e}")
            print("💡 해결방법: pip install fastapi uvicorn pandas numpy")
            return False
        
        # Node.js 확인
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Node.js 확인됨")
            else:
                print("❌ Node.js가 설치되지 않음")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Node.js가 설치되지 않음")
            return False
        
        return True
    
    def start_api_server(self):
        """API 서버 시작"""
        print("🚀 API 서버 시작 중...")
        
        try:
            # pro 폴더로 이동
            pro_dir = Path("pro")
            if not pro_dir.exists():
                print("❌ pro/ 폴더를 찾을 수 없습니다")
                return False
            
            # API 서버 실행
            self.api_process = subprocess.Popen(
                [sys.executable, "app.py"],
                cwd=pro_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 서버 시작 대기
            time.sleep(3)
            
            if self.api_process.poll() is None:
                print("✅ API 서버 시작됨 (포트 7860)")
                return True
            else:
                print("❌ API 서버 시작 실패")
                return False
                
        except Exception as e:
            print(f"❌ API 서버 오류: {e}")
            return False
    
    def build_web_dashboard(self):
        """웹 대시보드 빌드"""
        print("🔨 웹 대시보드 빌드 중...")
        
        try:
            web_dir = Path("web")
            if not web_dir.exists():
                print("❌ web/ 폴더를 찾을 수 없습니다")
                return False
            
            # package.json 확인
            package_json = web_dir / "package.json"
            if not package_json.exists():
                print("❌ web/package.json을 찾을 수 없습니다")
                return False
            
            # npm install
            print("📦 종속성 설치 중...")
            install_result = subprocess.run(
                ['npm', 'install'],
                cwd=web_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if install_result.returncode != 0:
                print(f"❌ npm install 실패: {install_result.stderr}")
                return False
            
            print("✅ 웹 종속성 설치 완료")
            
            # npm run build
            print("🏗️  웹 대시보드 빌드 중...")
            build_result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=web_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if build_result.returncode != 0:
                print(f"❌ 빌드 실패: {build_result.stderr}")
                return False
            
            print("✅ 웹 대시보드 빌드 완료")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ 빌드 시간 초과")
            return False
        except Exception as e:
            print(f"❌ 빌드 오류: {e}")
            return False
    
    def start_web_server(self):
        """웹 서버 시작 (빌드된 파일 서빙)"""
        print("🌐 웹 서버 시작 중...")
        
        try:
            # 간단한 HTTP 서버로 빌드된 파일 서빙
            web_dir = Path("web/dist")
            if not web_dir.exists():
                print("❌ web/dist 폴더를 찾을 수 없습니다")
                return False
            
            # Python 내장 HTTP 서버 사용
            self.web_process = subprocess.Popen(
                [sys.executable, "-m", "http.server", "3000"],
                cwd=web_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            time.sleep(2)
            
            if self.web_process.poll() is None:
                print("✅ 웹 서버 시작됨 (포트 3000)")
                return True
            else:
                print("❌ 웹 서버 시작 실패")
                return False
                
        except Exception as e:
            print(f"❌ 웹 서버 오류: {e}")
            return False
    
    def open_browser(self):
        """브라우저 자동 열기"""
        print("🌐 브라우저 열기 중...")
        
        try:
            # 3초 대기 후 브라우저 열기
            time.sleep(3)
            webbrowser.open("http://localhost:3000")
            print("✅ 브라우저가 열렸습니다")
        except Exception as e:
            print(f"⚠️  브라우저 자동 열기 실패: {e}")
            print("💡 수동으로 http://localhost:3000 에 접속하세요")
    
    def monitor_processes(self):
        """프로세스 모니터링"""
        print("\n📊 서버 상태 모니터링 시작...")
        print("⏹️  종료하려면 Ctrl+C를 누르세요\n")
        
        try:
            while self.running:
                # API 서버 상태 확인
                if self.api_process and self.api_process.poll() is not None:
                    print("❌ API 서버가 중지되었습니다")
                    break
                
                # 웹 서버 상태 확인
                if self.web_process and self.web_process.poll() is not None:
                    print("❌ 웹 서버가 중지되었습니다")
                    break
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n🛑 사용자가 중지 요청")
            self.shutdown()
    
    def shutdown(self):
        """서버 종료"""
        print("\n🛑 서버 종료 중...")
        self.running = False
        
        if self.api_process:
            self.api_process.terminate()
            print("✅ API 서버 종료됨")
        
        if self.web_process:
            self.web_process.terminate()
            print("✅ 웹 서버 종료됨")
        
        print("👋 COSMOS-HGP가 종료되었습니다")
    
    def run(self):
        """메인 실행 함수"""
        self.print_banner()
        
        # 1. 종속성 확인
        if not self.check_dependencies():
            print("\n❌ 종속성 확인 실패. 설치 후 다시 시도하세요.")
            return False
        
        # 2. API 서버 시작
        if not self.start_api_server():
            print("\n❌ API 서버 시작 실패")
            return False
        
        # 3. 웹 대시보드 빌드
        if not self.build_web_dashboard():
            print("\n❌ 웹 대시보드 빌드 실패")
            self.shutdown()
            return False
        
        # 4. 웹 서버 시작
        if not self.start_web_server():
            print("\n❌ 웹 서버 시작 실패")
            self.shutdown()
            return False
        
        # 5. 브라우저 열기
        self.open_browser()
        
        # 6. 모니터링 시작
        self.monitor_processes()
        
        return True

def main():
    """메인 함수"""
    # 시그널 핸들러 설정
    def signal_handler(sig, frame):
        print("\n🛑 종료 신호 수신")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 런처 실행
    launcher = CosmosLauncher()
    success = launcher.run()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
