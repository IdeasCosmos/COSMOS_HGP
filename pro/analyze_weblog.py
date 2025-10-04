#!/usr/bin/env python3
"""
웹 로그 데이터 분석 스크립트
실제 weblog.csv 데이터를 분석하여 COSMOS AIOps 시스템 테스트
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from collections import Counter
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_weblog_structure():
    """웹 로그 데이터 구조 분석"""
    print("📊 웹 로그 데이터 구조 분석")
    print("=" * 50)
    
    try:
        # CSV 파일 읽기
        df = pd.read_csv('weblog.csv')
        
        print(f"📈 기본 정보:")
        print(f"   총 레코드 수: {len(df):,}개")
        print(f"   컬럼 수: {len(df.columns)}개")
        print(f"   컬럼명: {list(df.columns)}")
        
        print(f"\n📋 데이터 샘플 (처음 5개):")
        print(df.head())
        
        print(f"\n📊 데이터 타입:")
        print(df.dtypes)
        
        print(f"\n🔍 결측값 정보:")
        print(df.isnull().sum())
        
        return df
        
    except Exception as e:
        print(f"❌ 데이터 읽기 실패: {e}")
        return None

def analyze_ip_patterns(df):
    """IP 패턴 분석"""
    print(f"\n🌐 IP 패턴 분석")
    print("-" * 30)
    
    # IP 주소별 요청 수
    ip_counts = df['IP'].value_counts()
    
    print(f"📊 IP 통계:")
    print(f"   고유 IP 수: {len(ip_counts)}개")
    print(f"   상위 5개 IP:")
    for ip, count in ip_counts.head().items():
        print(f"     {ip}: {count:,}회 요청")
    
    # IP 범위 분석
    ip_ranges = df['IP'].str.extract(r'(\d+\.\d+\.\d+)\.\d+')[0].value_counts()
    print(f"\n📈 IP 대역별 요청:")
    for ip_range, count in ip_ranges.head().items():
        print(f"     {ip_range}.x: {count:,}회 요청")
    
    return ip_counts

def analyze_url_patterns(df):
    """URL 패턴 분석"""
    print(f"\n🔗 URL 패턴 분석")
    print("-" * 30)
    
    # URL별 요청 수
    url_counts = df['URL'].value_counts()
    
    print(f"📊 URL 통계:")
    print(f"   고유 URL 수: {len(url_counts)}개")
    print(f"   상위 10개 URL:")
    for url, count in url_counts.head(10).items():
        # URL이 너무 길면 잘라서 표시
        display_url = url[:80] + "..." if len(url) > 80 else url
        print(f"     {display_url}: {count:,}회")
    
    # HTTP 메서드 분석
    http_methods = df['URL'].str.extract(r'^([A-Z]+)')[0].value_counts()
    print(f"\n📈 HTTP 메서드 분포:")
    for method, count in http_methods.items():
        print(f"     {method}: {count:,}회")
    
    # 파일 확장자 분석
    extensions = df['URL'].str.extract(r'\.([a-zA-Z0-9]+)')[0].value_counts()
    print(f"\n📁 파일 확장자 분포:")
    for ext, count in extensions.head(10).items():
        if pd.notna(ext):
            print(f"     .{ext}: {count:,}회")
    
    return url_counts

def analyze_status_codes(df):
    """상태 코드 분석"""
    print(f"\n📊 HTTP 상태 코드 분석")
    print("-" * 30)
    
    status_counts = df['Staus'].value_counts().sort_index()
    
    print(f"📈 상태 코드 분포:")
    for status, count in status_counts.items():
        percentage = (count / len(df)) * 100
        print(f"     {status}: {count:,}회 ({percentage:.1f}%)")
    
    # 에러 상태 코드 분석
    error_codes = [400, 401, 403, 404, 500, 502, 503]
    error_count = 0
    for code in error_codes:
        if code in status_counts:
            error_count += status_counts[code]
    
    error_percentage = (error_count / len(df)) * 100
    print(f"\n⚠️ 에러 상태 코드 총합: {error_count:,}회 ({error_percentage:.1f}%)")
    
    return status_counts

def analyze_time_patterns(df):
    """시간 패턴 분석"""
    print(f"\n⏰ 시간 패턴 분석")
    print("-" * 30)
    
    # 시간 파싱 (간단한 예시)
    time_data = df['Time'].str.extract(r'\[(\d+/\w+/\d+):(\d+:\d+:\d+)')
    
    if not time_data.empty:
        time_data.columns = ['date', 'time']
        
        # 시간대별 분석
        time_data['hour'] = time_data['time'].str.extract(r'(\d+):').astype(int)
        hourly_counts = time_data['hour'].value_counts().sort_index()
        
        print(f"📈 시간대별 요청 분포:")
        for hour, count in hourly_counts.items():
            print(f"     {hour:02d}시: {count:,}회")
        
        # 날짜별 분석
        date_counts = time_data['date'].value_counts().sort_index()
        print(f"\n📅 날짜별 요청 분포:")
        for date, count in date_counts.head(10).items():
            print(f"     {date}: {count:,}회")
    
    return time_data

def detect_anomalies(df):
    """이상 패턴 탐지"""
    print(f"\n🚨 이상 패턴 탐지")
    print("-" * 30)
    
    anomalies = []
    
    # 1. 과도한 요청 IP 탐지
    ip_counts = df['IP'].value_counts()
    ip_threshold = ip_counts.quantile(0.95)  # 상위 5% IP
    high_request_ips = ip_counts[ip_counts > ip_threshold]
    
    if len(high_request_ips) > 0:
        anomalies.append({
            'type': 'high_request_ip',
            'count': len(high_request_ips),
            'description': f'{ip_threshold:.0f}회 이상 요청한 IP {len(high_request_ips)}개 발견'
        })
        print(f"⚠️ 과도한 요청 IP: {len(high_request_ips)}개")
        for ip, count in high_request_ips.head(5).items():
            print(f"     {ip}: {count:,}회")
    
    # 2. 에러 상태 코드 탐지
    error_codes = [400, 401, 403, 404, 500, 502, 503]
    error_requests = df[df['Staus'].isin(error_codes)]
    error_rate = len(error_requests) / len(df) * 100
    
    if error_rate > 5:  # 에러율 5% 이상
        anomalies.append({
            'type': 'high_error_rate',
            'count': len(error_requests),
            'description': f'에러율 {error_rate:.1f}% ({len(error_requests):,}개 에러)'
        })
        print(f"⚠️ 높은 에러율: {error_rate:.1f}%")
    
    # 3. 비정상적인 URL 패턴 탐지
    url_counts = df['URL'].value_counts()
    suspicious_urls = url_counts[url_counts > 1000]  # 1000회 이상 요청된 URL
    
    if len(suspicious_urls) > 0:
        anomalies.append({
            'type': 'suspicious_url',
            'count': len(suspicious_urls),
            'description': f'1000회 이상 요청된 URL {len(suspicious_urls)}개'
        })
        print(f"⚠️ 의심스러운 URL: {len(suspicious_urls)}개")
    
    print(f"\n📊 탐지된 이상 패턴: {len(anomalies)}개")
    for anomaly in anomalies:
        print(f"   • {anomaly['description']}")
    
    return anomalies

def test_cosmos_aiops_with_real_data(df):
    """COSMOS AIOps 시스템으로 실제 데이터 테스트"""
    print(f"\n🤖 COSMOS AIOps 시스템 테스트")
    print("-" * 40)
    
    try:
        from unified_cosmos import COSMOSFactory, DomainType
        
        # AIOps 엔진 생성
        aiops_engine = COSMOSFactory.create_aiops_system()
        print("✅ AIOps 엔진 생성 완료")
        
        # 실제 로그 데이터 준비
        sample_logs = df.head(100).to_dict('records')
        
        # COSMOS 시스템으로 처리
        test_data = {
            'logs': sample_logs,
            'component': 'web-server',
            'total_requests': len(df),
            'error_rate': len(df[df['Staus'].isin([400, 401, 403, 404, 500, 502, 503])]) / len(df)
        }
        
        print(f"📊 테스트 데이터 준비:")
        print(f"   로그 샘플: {len(sample_logs)}개")
        print(f"   전체 요청: {test_data['total_requests']:,}개")
        print(f"   에러율: {test_data['error_rate']:.2%}")
        
        # COSMOS 실행
        result = aiops_engine.execute_with_unified_duality(
            rule_sequence=['validate_input', 'parse_log_entries', 'detect_anomalies', 'generate_alerts'],
            input_data=test_data,
            domain_context=DomainType.AIOPS
        )
        
        print(f"\n🎯 COSMOS 실행 결과:")
        print(f"   모드: {result['mode']}")
        print(f"   도메인: {result['domain']}")
        print(f"   영향도: {result['total_impact']:.3f}")
        print(f"   실행 시간: {result['total_duration_ms']:.1f}ms")
        print(f"   실행 경로: {len(result['execution_path'])}단계")
        
        print(f"\n📋 실행 경로 상세:")
        for i, step in enumerate(result['execution_path'], 1):
            print(f"   {i}. {step['rule']} [{step['layer']}] - {step['status']} (영향도: {step['impact']:.3f})")
        
        return result
        
    except Exception as e:
        print(f"❌ COSMOS 테스트 실패: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return None

def generate_report(df, anomalies, cosmos_result):
    """분석 보고서 생성"""
    print(f"\n📄 분석 보고서 생성")
    print("-" * 30)
    
    report = {
        'analysis_date': datetime.now().isoformat(),
        'dataset_info': {
            'total_records': len(df),
            'columns': list(df.columns),
            'date_range': '2017-11-29',
            'data_source': 'weblog.csv'
        },
        'statistics': {
            'unique_ips': len(df['IP'].unique()),
            'unique_urls': len(df['URL'].unique()),
            'error_rate': len(df[df['Staus'].isin([400, 401, 403, 404, 500, 502, 503])]) / len(df),
            'top_ip': df['IP'].value_counts().index[0],
            'most_common_status': df['Staus'].value_counts().index[0]
        },
        'anomalies_detected': len(anomalies),
        'anomaly_details': anomalies,
        'cosmos_test': {
            'success': cosmos_result is not None,
            'impact': cosmos_result['total_impact'] if cosmos_result else None,
            'execution_time_ms': cosmos_result['total_duration_ms'] if cosmos_result else None
        }
    }
    
    # JSON 파일로 저장
    with open('weblog_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ 분석 보고서 저장: weblog_analysis_report.json")
    
    return report

def main():
    """메인 실행 함수"""
    print("🚀 웹 로그 데이터 분석 및 COSMOS AIOps 테스트")
    print("=" * 60)
    
    # 1. 데이터 구조 분석
    df = analyze_weblog_structure()
    if df is None:
        return False
    
    # 2. IP 패턴 분석
    ip_analysis = analyze_ip_patterns(df)
    
    # 3. URL 패턴 분석
    url_analysis = analyze_url_patterns(df)
    
    # 4. 상태 코드 분석
    status_analysis = analyze_status_codes(df)
    
    # 5. 시간 패턴 분석
    time_analysis = analyze_time_patterns(df)
    
    # 6. 이상 패턴 탐지
    anomalies = detect_anomalies(df)
    
    # 7. COSMOS AIOps 시스템 테스트
    cosmos_result = test_cosmos_aiops_with_real_data(df)
    
    # 8. 보고서 생성
    report = generate_report(df, anomalies, cosmos_result)
    
    print(f"\n🎉 분석 완료!")
    print(f"📊 총 {len(df):,}개 로그 레코드 분석")
    print(f"🚨 {len(anomalies)}개 이상 패턴 탐지")
    print(f"🤖 COSMOS AIOps 시스템 테스트 {'성공' if cosmos_result else '실패'}")
    
    return True

if __name__ == "__main__":
    main()
