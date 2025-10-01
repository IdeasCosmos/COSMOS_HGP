#!/usr/bin/env python3
"""
COSMOS-HGP MVP 메인 실행 파일
"""

import sys
import os
import argparse
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def run_dashboard():
    """대시보드 실행"""
    print("🌐 COSMOS-HGP MVP 대시보드 시작...")
    
    try:
        from app import app
        print("✅ Flask 앱 로드 성공")
        print("📊 대시보드: http://localhost:5000")
        print("🔍 API 상태: http://localhost:5000/api/status")
        print("📄 결과: http://localhost:5000/results")
        print("🧪 테스트: http://localhost:5000/test")
        print("=" * 50)
        
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ 대시보드 실행 실패: {e}")
        return False

def run_csv_analyzer(file_path=None):
    """CSV 분석기 실행"""
    print("📊 CSV 분석기 실행...")
    
    try:
        from universal_csv_analyzer import UniversalCSVAnalyzer
        
        analyzer = UniversalCSVAnalyzer()
        
        if file_path:
            result = analyzer.analyze_file(file_path)
            if result:
                print("✅ 파일 분석 완료")
                return True
            else:
                print("❌ 파일 분석 실패")
                return False
        else:
            # 현재 디렉토리의 CSV 파일들 분석
            csv_files = list(Path('.').glob("*.csv"))
            
            if not csv_files:
                print("❌ CSV 파일을 찾을 수 없습니다.")
                return False
            
            print(f"📊 발견된 CSV 파일: {len(csv_files)}개")
            
            for csv_file in csv_files:
                print(f"\n{'='*60}")
                result = analyzer.analyze_file(csv_file)
                if result:
                    print(f"✅ {csv_file} 분석 완료")
                else:
                    print(f"❌ {csv_file} 분석 실패")
            
            return True
        
    except Exception as e:
        print(f"❌ CSV 분석기 실행 실패: {e}")
        return False

def run_self_test():
    """자가 테스트 실행"""
    print("🧪 COSMOS 자가 테스트 실행...")
    
    try:
        from cosmos_selftest import run_cosmos_self_test
        
        report = run_cosmos_self_test()
        
        if report['success_rate'] >= 80:
            print("🎉 자가 테스트 성공!")
            return True
        else:
            print("❌ 자가 테스트 실패!")
            return False
        
    except Exception as e:
        print(f"❌ 자가 테스트 실행 실패: {e}")
        return False

def run_profiler():
    """프로파일러 실행"""
    print("📈 COSMOS 프로파일러 실행...")
    
    try:
        from tests.test_profiler_fixed import main as profiler_main
        
        success = profiler_main()
        
        if success:
            print("🎉 프로파일러 테스트 성공!")
            return True
        else:
            print("❌ 프로파일러 테스트 실패!")
            return False
        
    except Exception as e:
        print(f"❌ 프로파일러 실행 실패: {e}")
        return False

def download_data():
    """데이터 다운로드"""
    print("📥 데이터 다운로드...")
    
    try:
        from scripts.download_data import main as download_main
        
        success = download_main()
        
        if success:
            print("🎉 데이터 다운로드 성공!")
            return True
        else:
            print("❌ 데이터 다운로드 실패!")
            return False
        
    except Exception as e:
        print(f"❌ 데이터 다운로드 실패: {e}")
        return False

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='COSMOS-HGP MVP 메인 실행기')
    parser.add_argument('command', 
                       choices=['dashboard', 'analyze', 'test', 'profiler', 'download'],
                       help='실행할 명령어')
    parser.add_argument('--file', '-f', 
                       help='분석할 파일 경로 (analyze 명령어 사용시)')
    
    args = parser.parse_args()
    
    print("🚀 COSMOS-HGP MVP")
    print("=" * 50)
    
    if args.command == 'dashboard':
        return run_dashboard()
    elif args.command == 'analyze':
        return run_csv_analyzer(args.file)
    elif args.command == 'test':
        return run_self_test()
    elif args.command == 'profiler':
        return run_profiler()
    elif args.command == 'download':
        return download_data()
    else:
        print("❌ 알 수 없는 명령어입니다.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
