#!/usr/bin/env python3
"""
COSMOS 시각화 시스템 메인 실행 파일
"""

import sys
import os
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='COSMOS 시각화 시스템')
    parser.add_argument('--mode', choices=['viz', 'api', 'both'], default='both',
                       help='실행 모드: viz(시각화만), api(API만), both(둘 다)')
    parser.add_argument('--port', type=int, default=8000,
                       help='API 서버 포트 (기본값: 8000)')
    parser.add_argument('--host', default='0.0.0.0',
                       help='API 서버 호스트 (기본값: 0.0.0.0)')
    
    args = parser.parse_args()
    
    # 현재 디렉토리를 Python 경로에 추가
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    if args.mode in ['viz', 'both']:
        print("=== 시각화 생성 ===")
        try:
            from viz.log_to_map import main as generate_viz
            generate_viz()
            print("시각화 생성 완료!")
        except Exception as e:
            print(f"시각화 생성 오류: {e}")
            return 1
    
    if args.mode in ['api', 'both']:
        print(f"\n=== API 서버 시작 (http://{args.host}:{args.port}) ===")
        try:
            import uvicorn
            from api.app import app
            uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        except Exception as e:
            print(f"API 서버 시작 오류: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
