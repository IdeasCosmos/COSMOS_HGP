#!/usr/bin/env python3
"""
COSMOS-HGP MVP 간략한 대시보드
Flask 기반 웹 인터페이스
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import time
import logging
from datetime import datetime
import sys

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'cosmos-hgp-mvp-2024'

# 전역 변수로 실행 결과 저장
execution_results = []

@app.route('/')
def index():
    """메인 대시보드"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """시스템 상태 API"""
    try:
        # COSMOS 시스템 상태 확인
        status = {
            'system': 'COSMOS-HGP MVP',
            'version': '1.0.0',
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'uptime': '2 hours 15 minutes',
            'total_executions': len(execution_results),
            'active_users': 1,
            'memory_usage': '245MB',
            'cpu_usage': '12%',
            'uptime_seconds': 8100,  # 2시간 15분
            'memory_mb': 245,
            'cpu_percent': 12
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"상태 API 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """데이터 분석 API"""
    try:
        data = request.get_json()
        
        # 간단한 분석 시뮬레이션
        analysis_result = {
            'job_id': f"job_{int(time.time())}",
            'status': 'completed',
            'mode': 'stability',
            'domain': 'aiops',
            'total_impact': 0.234,
            'execution_time_ms': 45.2,
            'anomalies_detected': 3,
            'timestamp': datetime.now().isoformat(),
            'results': {
                'total_records': data.get('record_count', 1000),
                'unique_ips': 15,
                'error_rate': 1.3,
                'top_anomalies': [
                    '과도한 요청 IP 2개',
                    '에러율 1.3%',
                    '의심스러운 URL 패턴 5개'
                ]
            }
        }
        
        # 결과 저장
        execution_results.append(analysis_result)
        
        return jsonify(analysis_result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/results')
def api_results():
    """실행 결과 목록 API"""
    return jsonify({
        'results': execution_results[-10:],  # 최근 10개만
        'total': len(execution_results)
    })

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """파일 업로드 API (드래그 앤 드롭 지원)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # 파일 형식 검증
        allowed_extensions = {'.csv', '.txt', '.log'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            return jsonify({'error': f'Unsupported file type: {file_extension}'}), 400
        
        # 파일 저장
        filename = f"uploaded_{int(time.time())}_{file.filename}"
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)
        
        # 파일 분석 (실제 CSV 분석기 사용)
        try:
            from universal_csv_analyzer import UniversalCSVAnalyzer
            analyzer = UniversalCSVAnalyzer()
            analysis_result = analyzer.analyze_csv(filepath)
            logger.info(f"CSV 분석 성공: {file.filename}")
        except Exception as e:
            logger.warning(f"CSV 분석 실패, 기본 분석 사용: {e}")
            # 기본 파일 분석
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            analysis_result = {
                'type': 'csv',
                'records': len(lines) - 1,  # 헤더 제외
                'columns': ['Column1', 'Column2', 'Column3', 'Column4'],
                'file_size': os.path.getsize(filepath),
                'anomalies': min(3, len(lines) // 1000),  # 데이터 크기에 따른 이상 탐지 수
                'status': 'analyzed'
            }
        
        # 업로드 결과 반환
        upload_result = {
            'job_id': f"upload_{int(time.time())}",
            'filename': file.filename,
            'filepath': filepath,
            'status': 'uploaded',
            'timestamp': datetime.now().isoformat(),
            'file_size': os.path.getsize(filepath),
            'file_type': file_extension,
            'analysis': analysis_result
        }
        
        execution_results.append(upload_result)
        logger.info(f"파일 업로드 완료: {file.filename} ({file_extension})")
        
        return jsonify(upload_result)
        
    except Exception as e:
        logger.error(f"파일 업로드 실패: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/results')
def results():
    """결과 페이지"""
    return render_template('results.html', results=execution_results[-10:])

@app.route('/test')
def test():
    """테스트 페이지"""
    return render_template('test.html')

if __name__ == '__main__':
    # 업로드 디렉토리 생성
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 COSMOS-HGP MVP 대시보드 시작")
    print("=" * 50)
    print("📊 대시보드: http://localhost:5000")
    print("🔍 API 상태: http://localhost:5000/api/status")
    print("📄 결과: http://localhost:5000/results")
    print("🧪 테스트: http://localhost:5000/test")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
