#!/usr/bin/env python3
"""
Universal CSV Analyzer for COSMOS AIOps
모든 CSV 파일 유형과 양식에 대응하는 범용 분석기
"""

import pandas as pd
import numpy as np
import json
import csv
import chardet
import os
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class UniversalCSVAnalyzer:
    """모든 CSV 파일 유형을 지원하는 범용 분석기"""
    
    def __init__(self):
        self.supported_formats = {
            'web_logs': ['apache', 'nginx', 'iis', 'web', 'access', 'log'],
            'system_logs': ['syslog', 'system', 'kernel', 'audit'],
            'application_logs': ['app', 'application', 'service', 'daemon'],
            'network_logs': ['network', 'firewall', 'router', 'switch'],
            'security_logs': ['security', 'auth', 'login', 'audit'],
            'database_logs': ['database', 'db', 'sql', 'mysql', 'postgresql'],
            'financial_data': ['finance', 'trading', 'stock', 'market', 'transaction'],
            'healthcare_data': ['health', 'medical', 'patient', 'hospital'],
            'iot_data': ['iot', 'sensor', 'device', 'telemetry'],
            'social_data': ['social', 'user', 'profile', 'activity']
        }
        
        self.encoding_types = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1', 'ascii']
        self.separator_types = [',', ';', '\t', '|', ' ', ':', '#']
        
    def detect_file_type(self, file_path):
        """파일 경로와 내용으로부터 파일 유형 자동 감지"""
        file_name = Path(file_path).name.lower()
        
        # 파일명 기반 감지
        for file_type, keywords in self.supported_formats.items():
            if any(keyword in file_name for keyword in keywords):
                return file_type
        
        return 'generic_data'
    
    def detect_encoding(self, file_path, sample_size=10000):
        """파일 인코딩 자동 감지"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(sample_size)
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8')
        except Exception:
            return 'utf-8'
    
    def detect_separator(self, file_path, encoding='utf-8'):
        """CSV 구분자 자동 감지"""
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                # 첫 5줄로 구분자 감지
                sample = ''.join([f.readline() for _ in range(5)])
                
                for sep in self.separator_types:
                    if sample.count(sep) > sample.count(',') * 0.8:
                        return sep
                
                return ','  # 기본값
        except Exception:
            return ','
    
    def analyze_csv(self, file_path):
        """CSV 파일 분석"""
        try:
            # 파일 정보 수집
            file_info = {
                'file_path': str(file_path),
                'file_name': Path(file_path).name,
                'file_size': os.path.getsize(file_path),
                'file_type': self.detect_file_type(file_path),
                'timestamp': datetime.now().isoformat()
            }
            
            # 인코딩 및 구분자 감지
            encoding = self.detect_encoding(file_path)
            separator = self.detect_separator(file_path, encoding)
            
            # 데이터 로드
            df = pd.read_csv(file_path, encoding=encoding, sep=separator, low_memory=False)
            
            # 기본 통계
            basic_stats = {
                'total_records': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'data_types': df.dtypes.to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'null_counts': df.isnull().sum().to_dict(),
                'duplicate_rows': df.duplicated().sum()
            }
            
            # 데이터 품질 분석
            quality_metrics = {
                'completeness': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                'uniqueness': (1 - df.duplicated().sum() / len(df)) * 100,
                'consistency': self._analyze_consistency(df),
                'validity': self._analyze_validity(df)
            }
            
            # 이상 탐지
            anomalies = self._detect_anomalies(df, file_info['file_type'])
            
            # 패턴 분석
            patterns = self._analyze_patterns(df, file_info['file_type'])
            
            # 결과 통합
            analysis_result = {
                'file_info': file_info,
                'format_info': {
                    'encoding': encoding,
                    'separator': separator,
                    'detected_type': file_info['file_type']
                },
                'basic_stats': basic_stats,
                'quality_metrics': quality_metrics,
                'anomalies': anomalies,
                'patterns': patterns,
                'status': 'success'
            }
            
            return analysis_result
            
        except Exception as e:
            return {
                'file_info': {
                    'file_path': str(file_path),
                    'file_name': Path(file_path).name,
                    'file_size': os.path.getsize(file_path),
                    'timestamp': datetime.now().isoformat()
                },
                'error': str(e),
                'status': 'failed'
            }
    
    def _analyze_consistency(self, df):
        """데이터 일관성 분석"""
        consistency_score = 100
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # 문자열 컬럼의 일관성 검사
                unique_values = df[col].dropna().nunique()
                total_values = len(df[col].dropna())
                
                if total_values > 0:
                    consistency_ratio = unique_values / total_values
                    if consistency_ratio > 0.95:  # 너무 많은 고유값
                        consistency_score -= 10
                    elif consistency_ratio < 0.1:  # 너무 적은 고유값
                        consistency_score -= 5
        
        return max(0, consistency_score)
    
    def _analyze_validity(self, df):
        """데이터 유효성 분석"""
        validity_score = 100
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # 빈 문자열 체크
                empty_strings = (df[col] == '').sum()
                if empty_strings > 0:
                    validity_score -= (empty_strings / len(df)) * 20
                
                # 특수 문자 체크
                special_chars = df[col].str.contains(r'[^\w\s\-\.]', na=False).sum()
                if special_chars > len(df) * 0.1:
                    validity_score -= 5
        
        return max(0, validity_score)
    
    def _detect_anomalies(self, df, file_type):
        """이상 탐지"""
        anomalies = []
        
        # 기본 이상 탐지
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                # 수치형 데이터 이상 탐지
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                if len(outliers) > 0:
                    anomalies.append({
                        'type': 'numerical_outlier',
                        'column': col,
                        'count': len(outliers),
                        'percentage': (len(outliers) / len(df)) * 100
                    })
        
        # 파일 유형별 특화 이상 탐지
        if file_type == 'web_logs':
            anomalies.extend(self._detect_web_log_anomalies(df))
        elif file_type == 'financial_data':
            anomalies.extend(self._detect_financial_anomalies(df))
        
        return anomalies
    
    def _detect_web_log_anomalies(self, df):
        """웹 로그 특화 이상 탐지"""
        anomalies = []
        
        # IP 주소 이상 탐지
        if 'ip' in df.columns.str.lower() or 'client_ip' in df.columns.str.lower():
            ip_col = 'ip' if 'ip' in df.columns.str.lower() else 'client_ip'
            ip_counts = df[ip_col].value_counts()
            suspicious_ips = ip_counts[ip_counts > ip_counts.mean() + 2 * ip_counts.std()]
            
            if len(suspicious_ips) > 0:
                anomalies.append({
                    'type': 'suspicious_ip',
                    'count': len(suspicious_ips),
                    'ips': suspicious_ips.head().to_dict()
                })
        
        # 상태 코드 이상 탐지
        if 'status' in df.columns.str.lower():
            status_col = 'status'
            error_codes = df[df[status_col] >= 400]
            if len(error_codes) > 0:
                anomalies.append({
                    'type': 'high_error_rate',
                    'count': len(error_codes),
                    'percentage': (len(error_codes) / len(df)) * 100
                })
        
        return anomalies
    
    def _detect_financial_anomalies(self, df):
        """금융 데이터 특화 이상 탐지"""
        anomalies = []
        
        # 금액 관련 컬럼 이상 탐지
        amount_cols = [col for col in df.columns if any(keyword in col.lower() 
                      for keyword in ['amount', 'price', 'value', 'cost', 'fee'])]
        
        for col in amount_cols:
            if df[col].dtype in ['int64', 'float64']:
                # 음수 금액 탐지
                negative_amounts = df[df[col] < 0]
                if len(negative_amounts) > 0:
                    anomalies.append({
                        'type': 'negative_amount',
                        'column': col,
                        'count': len(negative_amounts)
                    })
                
                # 비정상적으로 큰 금액 탐지
                large_amounts = df[df[col] > df[col].quantile(0.99) * 10]
                if len(large_amounts) > 0:
                    anomalies.append({
                        'type': 'unusually_large_amount',
                        'column': col,
                        'count': len(large_amounts)
                    })
        
        return anomalies
    
    def _analyze_patterns(self, df, file_type):
        """패턴 분석"""
        patterns = {}
        
        # 시간 패턴 분석
        time_cols = [col for col in df.columns if any(keyword in col.lower() 
                   for keyword in ['time', 'date', 'timestamp', 'created', 'updated'])]
        
        if time_cols:
            patterns['temporal'] = self._analyze_temporal_patterns(df, time_cols[0])
        
        # 파일 유형별 패턴 분석
        if file_type == 'web_logs':
            patterns['web'] = self._analyze_web_patterns(df)
        elif file_type == 'financial_data':
            patterns['financial'] = self._analyze_financial_patterns(df)
        
        return patterns
    
    def _analyze_temporal_patterns(self, df, time_col):
        """시간 패턴 분석"""
        try:
            df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
            df_clean = df.dropna(subset=[time_col])
            
            if len(df_clean) == 0:
                return {}
            
            # 시간대별 분포
            hourly_dist = df_clean[time_col].dt.hour.value_counts().sort_index()
            
            # 요일별 분포
            daily_dist = df_clean[time_col].dt.dayofweek.value_counts().sort_index()
            
            return {
                'hourly_distribution': hourly_dist.to_dict(),
                'daily_distribution': daily_dist.to_dict(),
                'time_span': {
                    'start': df_clean[time_col].min().isoformat(),
                    'end': df_clean[time_col].max().isoformat()
                }
            }
        except Exception:
            return {}
    
    def _analyze_web_patterns(self, df):
        """웹 로그 패턴 분석"""
        patterns = {}
        
        # URL 패턴 분석
        if 'url' in df.columns.str.lower() or 'path' in df.columns.str.lower():
            url_col = 'url' if 'url' in df.columns.str.lower() else 'path'
            url_patterns = df[url_col].value_counts().head(10)
            patterns['top_urls'] = url_patterns.to_dict()
        
        # User-Agent 패턴 분석
        if 'user_agent' in df.columns.str.lower():
            ua_patterns = df['user_agent'].value_counts().head(10)
            patterns['top_user_agents'] = ua_patterns.to_dict()
        
        return patterns
    
    def _analyze_financial_patterns(self, df):
        """금융 데이터 패턴 분석"""
        patterns = {}
        
        # 거래 패턴 분석
        amount_cols = [col for col in df.columns if any(keyword in col.lower() 
                      for keyword in ['amount', 'price', 'value'])]
        
        if amount_cols:
            patterns['transaction_summary'] = {
                'total_transactions': len(df),
                'total_amount': df[amount_cols[0]].sum() if len(amount_cols) > 0 else 0,
                'average_amount': df[amount_cols[0]].mean() if len(amount_cols) > 0 else 0,
                'amount_range': {
                    'min': df[amount_cols[0]].min() if len(amount_cols) > 0 else 0,
                    'max': df[amount_cols[0]].max() if len(amount_cols) > 0 else 0
                }
            }
        
        return patterns
    
    def analyze_file(self, file_path):
        """파일 분석 메인 함수"""
        print(f"📊 {Path(file_path).name} 분석 시작...")
        
        result = self.analyze_csv(file_path)
        
        if result['status'] == 'success':
            print("✅ 분석 완료!")
            print(f"   📄 파일: {result['file_info']['file_name']}")
            print(f"   📊 레코드: {result['basic_stats']['total_records']:,}개")
            print(f"   📋 컬럼: {result['basic_stats']['total_columns']}개")
            print(f"   🎯 파일 유형: {result['format_info']['detected_type']}")
            print(f"   📈 데이터 품질: {result['quality_metrics']['completeness']:.1f}%")
            print(f"   ⚠️  이상 탐지: {len(result['anomalies'])}개")
            
            return result
        else:
            print(f"❌ 분석 실패: {result.get('error', 'Unknown error')}")
            return None
    
    def generate_report(self, analysis_result, output_path=None):
        """분석 결과 보고서 생성"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"analysis_report_{timestamp}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📄 분석 보고서 저장: {output_path}")
        return output_path

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Universal CSV Analyzer')
    parser.add_argument('file_path', help='분석할 CSV 파일 경로')
    parser.add_argument('--output', '-o', help='결과 저장 경로')
    
    args = parser.parse_args()
    
    analyzer = UniversalCSVAnalyzer()
    result = analyzer.analyze_file(args.file_path)
    
    if result and args.output:
        analyzer.generate_report(result, args.output)

if __name__ == "__main__":
    main()
