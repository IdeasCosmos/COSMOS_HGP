#!/usr/bin/env python3
"""
COSMOS AIOps 데모 시스템
로그 입력 → 경보 소음 억제 → 3WHY 설명 출력
"""

import numpy as np
import time
import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# COSMOS 컴포넌트 import (실제로는 모듈에서 가져옴)
try:
    from extended_rules import ExtendedRuleSet, DomainType, CodonType
    from core.velocity import VelocityManager
    from core.engine import UnifiedCosmosEngine
except ImportError:
    # 임시 구현
    from enum import Enum
    
    class DomainType(Enum):
        AIOPS = "aiops"
    
    class CodonType(Enum):
        AAT = ("AAT", "PARSE", "L1_QUANTUM", "파싱")
        GCC = ("GCC", "PREDICT", "L2_ATOMIC", "예측")
        CCT = ("CCT", "ALERT", "L4_COMPOUND", "알림")

logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    """로그 엔트리"""
    timestamp: str
    level: str
    component: str
    message: str
    metadata: Dict[str, Any] = None

@dataclass
class Alert:
    """경보"""
    id: str
    timestamp: str
    severity: str
    component: str
    message: str
    noise_level: float = 1.0
    confidence: float = 0.0
    root_cause: str = ""
    action_taken: str = ""

@dataclass
class WhyAnalysis:
    """3WHY 분석 결과"""
    primary_why: str
    secondary_why: str
    tertiary_why: str
    root_cause: str
    confidence: float
    suggested_actions: List[str]

class COSMOSAIOpsDemo:
    """COSMOS AIOps 데모 시스템"""
    
    def __init__(self):
        self.rule_set = ExtendedRuleSet()
        self.velocity_manager = None  # VelocityManager()
        self.engine = None  # UnifiedCosmosEngine()
        
        # 시뮬레이션 데이터
        self.log_entries: List[LogEntry] = []
        self.alerts: List[Alert] = []
        self.processed_logs: List[Dict] = []
        
        # 통계
        self.stats = {
            'logs_processed': 0,
            'alerts_generated': 0,
            'noise_reduced': 0,
            'false_positives': 0,
            'true_positives': 0
        }
    
    def generate_sample_logs(self, count: int = 100) -> List[LogEntry]:
        """샘플 로그 생성"""
        components = ['web-server', 'database', 'cache', 'api-gateway', 'load-balancer']
        levels = ['INFO', 'WARN', 'ERROR', 'DEBUG']
        
        base_time = datetime.now() - timedelta(hours=1)
        
        logs = []
        for i in range(count):
            # 실제 시스템 로그 패턴 시뮬레이션
            component = random.choice(components)
            level = random.choices(levels, weights=[60, 20, 15, 5])[0]
            
            if component == 'database' and level == 'ERROR':
                message = "Connection pool exhausted. Retrying..."
            elif component == 'web-server' and level == 'WARN':
                message = "Response time exceeded threshold: 2000ms"
            elif component == 'api-gateway' and level == 'ERROR':
                message = "Rate limit exceeded for user session"
            else:
                messages = [
                    f"Processing request {random.randint(1000, 9999)}",
                    f"Cache hit rate: {random.randint(70, 95)}%",
                    f"Memory usage: {random.randint(60, 85)}%",
                    f"CPU usage: {random.randint(40, 90)}%"
                ]
                message = random.choice(messages)
            
            log = LogEntry(
                timestamp=(base_time + timedelta(minutes=i)).isoformat(),
                level=level,
                component=component,
                message=message,
                metadata={
                    'request_id': f"req_{random.randint(10000, 99999)}",
                    'user_id': f"user_{random.randint(1000, 9999)}" if random.random() > 0.5 else None
                }
            )
            logs.append(log)
        
        return logs
    
    def parse_logs(self, logs: List[LogEntry]) -> List[Dict]:
        """1단계: 로그 파싱 및 분석"""
        print("🔍 1단계: 로그 파싱 및 분석")
        print("-" * 40)
        
        parsed_logs = []
        
        for log in logs:
            # COSMOS 규칙 적용
            parsed = self._apply_parsing_rules(log)
            parsed_logs.append(parsed)
            
            print(f"📝 {log.timestamp} [{log.level}] {log.component}: {log.message[:50]}...")
        
        self.processed_logs = parsed_logs
        self.stats['logs_processed'] = len(parsed_logs)
        
        print(f"\n✅ 총 {len(parsed_logs)}개 로그 파싱 완료")
        return parsed_logs
    
    def _apply_parsing_rules(self, log: LogEntry) -> Dict:
        """파싱 규칙 적용"""
        # 간단한 파싱 로직 (실제로는 COSMOS 규칙 사용)
        parsed = {
            'original': log,
            'timestamp': log.timestamp,
            'level': log.level,
            'component': log.component,
            'message': log.message,
            'parsed': True,
            'patterns': [],
            'anomaly_score': 0.0
        }
        
        # 패턴 추출
        if 'error' in log.message.lower():
            parsed['patterns'].append('error_pattern')
            parsed['anomaly_score'] += 0.3
        if 'timeout' in log.message.lower():
            parsed['patterns'].append('timeout_pattern')
            parsed['anomaly_score'] += 0.4
        if 'connection' in log.message.lower():
            parsed['patterns'].append('connection_pattern')
            parsed['anomaly_score'] += 0.2
        if log.level == 'ERROR':
            parsed['anomaly_score'] += 0.5
        elif log.level == 'WARN':
            parsed['anomaly_score'] += 0.2
        
        return parsed
    
    def detect_anomalies(self, parsed_logs: List[Dict]) -> List[Dict]:
        """2단계: 이상 탐지"""
        print("\n🚨 2단계: 이상 탐지")
        print("-" * 40)
        
        anomalies = []
        
        # 컴포넌트별 로그 그룹화
        component_logs = {}
        for log in parsed_logs:
            component = log['component']
            if component not in component_logs:
                component_logs[component] = []
            component_logs[component].append(log)
        
        # 각 컴포넌트별 이상 탐지
        for component, logs in component_logs.items():
            component_anomalies = self._detect_component_anomalies(component, logs)
            anomalies.extend(component_anomalies)
        
        print(f"🔍 {len(anomalies)}개 이상 패턴 탐지")
        for anomaly in anomalies:
            print(f"   • {anomaly['component']}: {anomaly['type']} (점수: {anomaly['score']:.2f})")
        
        return anomalies
    
    def _detect_component_anomalies(self, component: str, logs: List[Dict]) -> List[Dict]:
        """컴포넌트별 이상 탐지"""
        anomalies = []
        
        # 에러 빈도 분석
        error_logs = [log for log in logs if log['level'] == 'ERROR']
        if len(error_logs) > 5:  # 임계값
            anomalies.append({
                'component': component,
                'type': 'high_error_rate',
                'score': min(1.0, len(error_logs) / len(logs)),
                'details': f"{len(error_logs)}개 에러 로그 발견",
                'timestamp': logs[-1]['timestamp']
            })
        
        # 시간 간격 분석 (연속 에러)
        consecutive_errors = 0
        max_consecutive = 0
        for log in logs:
            if log['level'] == 'ERROR':
                consecutive_errors += 1
                max_consecutive = max(max_consecutive, consecutive_errors)
            else:
                consecutive_errors = 0
        
        if max_consecutive > 3:
            anomalies.append({
                'component': component,
                'type': 'consecutive_errors',
                'score': min(1.0, max_consecutive / 10),
                'details': f"연속 {max_consecutive}개 에러",
                'timestamp': logs[-1]['timestamp']
            })
        
        # 이상 점수 기반 탐지
        high_anomaly_logs = [log for log in logs if log['anomaly_score'] > 0.7]
        if len(high_anomaly_logs) > 0:
            avg_score = np.mean([log['anomaly_score'] for log in high_anomaly_logs])
            anomalies.append({
                'component': component,
                'type': 'high_anomaly_score',
                'score': avg_score,
                'details': f"평균 이상 점수: {avg_score:.2f}",
                'timestamp': logs[-1]['timestamp']
            })
        
        return anomalies
    
    def generate_alerts(self, anomalies: List[Dict]) -> List[Alert]:
        """3단계: 경보 생성"""
        print("\n📢 3단계: 경보 생성")
        print("-" * 40)
        
        alerts = []
        
        for anomaly in anomalies:
            # 경보 심각도 결정
            if anomaly['score'] > 0.8:
                severity = 'CRITICAL'
            elif anomaly['score'] > 0.6:
                severity = 'HIGH'
            elif anomaly['score'] > 0.4:
                severity = 'MEDIUM'
            else:
                severity = 'LOW'
            
            # 노이즈 레벨 계산
            noise_level = self._calculate_noise_level(anomaly)
            
            alert = Alert(
                id=f"ALERT_{len(alerts)+1:04d}",
                timestamp=anomaly['timestamp'],
                severity=severity,
                component=anomaly['component'],
                message=f"{anomaly['type']}: {anomaly['details']}",
                noise_level=noise_level,
                confidence=anomaly['score']
            )
            
            alerts.append(alert)
            print(f"🚨 {alert.id} [{alert.severity}] {alert.component}: {alert.message}")
        
        self.alerts = alerts
        self.stats['alerts_generated'] = len(alerts)
        
        print(f"\n✅ 총 {len(alerts)}개 경보 생성")
        return alerts
    
    def _calculate_noise_level(self, anomaly: Dict) -> float:
        """노이즈 레벨 계산"""
        base_noise = 1.0
        
        # 컴포넌트별 노이즈 가중치
        component_weights = {
            'database': 0.3,  # 데이터베이스는 중요하므로 낮은 노이즈
            'api-gateway': 0.4,
            'web-server': 0.5,
            'cache': 0.7,     # 캐시는 상대적으로 높은 노이즈
            'load-balancer': 0.6
        }
        
        component = anomaly['component']
        weight = component_weights.get(component, 0.5)
        
        # 이상 점수에 따른 조정
        score_factor = 1.0 - anomaly['score']  # 점수가 높을수록 노이즈 낮음
        
        return base_noise * weight * score_factor
    
    def suppress_noise(self, alerts: List[Alert]) -> List[Alert]:
        """4단계: 경보 소음 억제"""
        print("\n🔇 4단계: 경보 소음 억제")
        print("-" * 40)
        
        # 노이즈 억제 규칙 적용
        suppressed_alerts = []
        suppressed_count = 0
        
        for alert in alerts:
            should_suppress = self._should_suppress_alert(alert, alerts)
            
            if should_suppress:
                alert.action_taken = "NOISE_SUPPRESSED"
                suppressed_count += 1
                print(f"🔇 {alert.id} 소음 억제 (노이즈 레벨: {alert.noise_level:.2f})")
            else:
                suppressed_alerts.append(alert)
                print(f"✅ {alert.id} 경보 유지 (노이즈 레벨: {alert.noise_level:.2f})")
        
        self.stats['noise_reduced'] = suppressed_count
        
        print(f"\n✅ {suppressed_count}개 경보 소음 억제, {len(suppressed_alerts)}개 경보 유지")
        return suppressed_alerts
    
    def _should_suppress_alert(self, alert: Alert, all_alerts: List[Alert]) -> bool:
        """경보 억제 여부 결정"""
        # 1. 노이즈 레벨이 높은 경우
        if alert.noise_level > 0.7:
            return True
        
        # 2. 같은 컴포넌트에서 짧은 시간 내 여러 경보 발생
        recent_alerts = [
            a for a in all_alerts 
            if a.component == alert.component and a.id != alert.id
        ]
        
        if len(recent_alerts) > 3:
            return True
        
        # 3. LOW 심각도이고 노이즈 레벨이 높은 경우
        if alert.severity == 'LOW' and alert.noise_level > 0.5:
            return True
        
        return False
    
    def perform_3why_analysis(self, alert: Alert) -> WhyAnalysis:
        """5단계: 3WHY 분석"""
        print(f"\n🔍 5단계: 3WHY 분석 - {alert.id}")
        print("-" * 40)
        
        # 컴포넌트별 3WHY 분석
        if alert.component == 'database':
            analysis = self._analyze_database_issue(alert)
        elif alert.component == 'api-gateway':
            analysis = self._analyze_api_gateway_issue(alert)
        elif alert.component == 'web-server':
            analysis = self._analyze_web_server_issue(alert)
        else:
            analysis = self._analyze_generic_issue(alert)
        
        print(f"1️⃣ 왜? {analysis.primary_why}")
        print(f"2️⃣ 왜? {analysis.secondary_why}")
        print(f"3️⃣ 왜? {analysis.tertiary_why}")
        print(f"🎯 근본 원인: {analysis.root_cause}")
        print(f"📊 신뢰도: {analysis.confidence:.2f}")
        
        if analysis.suggested_actions:
            print("💡 권장 조치:")
            for action in analysis.suggested_actions:
                print(f"   • {action}")
        
        return analysis
    
    def _analyze_database_issue(self, alert: Alert) -> WhyAnalysis:
        """데이터베이스 이슈 3WHY 분석"""
        if 'connection pool' in alert.message.lower():
            return WhyAnalysis(
                primary_why="데이터베이스 연결 풀이 고갈됨",
                secondary_why="동시 연결 수가 설정된 최대값을 초과함",
                tertiary_why="연결 풀 크기가 부족하거나 연결이 제대로 해제되지 않음",
                root_cause="데이터베이스 연결 풀 설정 부족 및 연결 누수",
                confidence=0.85,
                suggested_actions=[
                    "연결 풀 크기 증가 (max_connections: 100 → 200)",
                    "연결 타임아웃 설정 최적화",
                    "연결 누수 검사 및 수정",
                    "데이터베이스 성능 모니터링 강화"
                ]
            )
        else:
            return self._analyze_generic_issue(alert)
    
    def _analyze_api_gateway_issue(self, alert: Alert) -> WhyAnalysis:
        """API 게이트웨이 이슈 3WHY 분석"""
        if 'rate limit' in alert.message.lower():
            return WhyAnalysis(
                primary_why="API 요청 한도 초과",
                secondary_why="특정 사용자가 설정된 요청 제한을 초과함",
                tertiary_why="비정상적인 트래픽 패턴 또는 봇 공격",
                root_cause="Rate limiting 설정 부족 및 비정상 트래픽 탐지 미흡",
                confidence=0.80,
                suggested_actions=[
                    "Rate limiting 정책 재검토",
                    "사용자별 요청 패턴 분석",
                    "DDoS 공격 탐지 시스템 구축",
                    "API 사용량 모니터링 대시보드 구축"
                ]
            )
        else:
            return self._analyze_generic_issue(alert)
    
    def _analyze_web_server_issue(self, alert: Alert) -> WhyAnalysis:
        """웹 서버 이슈 3WHY 분석"""
        if 'response time' in alert.message.lower():
            return WhyAnalysis(
                primary_why="웹 서버 응답 시간 초과",
                secondary_why="서버 처리 능력 부족 또는 외부 의존성 지연",
                tertiary_why="리소스 부족, 비효율적인 쿼리, 또는 네트워크 지연",
                root_cause="서버 리소스 부족 및 성능 최적화 미흡",
                confidence=0.75,
                suggested_actions=[
                    "서버 리소스 모니터링 및 스케일링",
                    "데이터베이스 쿼리 최적화",
                    "캐싱 전략 개선",
                    "로드 밸런싱 최적화"
                ]
            )
        else:
            return self._analyze_generic_issue(alert)
    
    def _analyze_generic_issue(self, alert: Alert) -> WhyAnalysis:
        """일반 이슈 3WHY 분석"""
        return WhyAnalysis(
            primary_why=f"{alert.component}에서 {alert.severity} 레벨 이슈 발생",
            secondary_why="시스템 구성 요소의 비정상적인 동작",
            tertiary_why="설정 오류, 리소스 부족, 또는 외부 의존성 문제",
            root_cause="시스템 구성 및 모니터링 부족",
            confidence=0.60,
            suggested_actions=[
                "시스템 로그 상세 분석",
                "리소스 사용량 모니터링",
                "설정 검토 및 최적화",
                "자동 복구 메커니즘 구축"
            ]
        )
    
    def generate_demo_report(self) -> Dict[str, Any]:
        """데모 보고서 생성"""
        report = {
            'demo_info': {
                'title': 'COSMOS AIOps 데모',
                'timestamp': datetime.now().isoformat(),
                'duration_minutes': 5
            },
            'statistics': self.stats,
            'logs_processed': len(self.processed_logs),
            'alerts_generated': len(self.alerts),
            'noise_suppression_rate': (
                self.stats['noise_reduced'] / self.stats['alerts_generated'] * 100
                if self.stats['alerts_generated'] > 0 else 0
            ),
            'components_affected': list(set(alert.component for alert in self.alerts)),
            'severity_distribution': {
                'CRITICAL': len([a for a in self.alerts if a.severity == 'CRITICAL']),
                'HIGH': len([a for a in self.alerts if a.severity == 'HIGH']),
                'MEDIUM': len([a for a in self.alerts if a.severity == 'MEDIUM']),
                'LOW': len([a for a in self.alerts if a.severity == 'LOW'])
            }
        }
        
        return report
    
    def run_complete_demo(self, log_count: int = 100) -> Dict[str, Any]:
        """전체 데모 실행"""
        print("🌟 COSMOS AIOps 데모 시스템 시작")
        print("=" * 60)
        print("📋 데모 시나리오: 로그 입력 → 경보 소음 억제 → 3WHY 설명 출력")
        print("=" * 60)
        
        start_time = time.time()
        
        # 1. 샘플 로그 생성
        print("\n📝 0단계: 샘플 로그 생성")
        logs = self.generate_sample_logs(log_count)
        print(f"✅ {len(logs)}개 샘플 로그 생성 완료")
        
        # 2. 로그 파싱
        parsed_logs = self.parse_logs(logs)
        
        # 3. 이상 탐지
        anomalies = self.detect_anomalies(parsed_logs)
        
        # 4. 경보 생성
        alerts = self.generate_alerts(anomalies)
        
        # 5. 소음 억제
        filtered_alerts = self.suppress_noise(alerts)
        
        # 6. 3WHY 분석 (상위 3개 경보만)
        top_alerts = sorted(filtered_alerts, key=lambda x: x.confidence, reverse=True)[:3]
        why_analyses = []
        
        for alert in top_alerts:
            analysis = self.perform_3why_analysis(alert)
            why_analyses.append(analysis)
        
        # 7. 보고서 생성
        duration = (time.time() - start_time) * 1000
        report = self.generate_demo_report()
        report['demo_info']['duration_ms'] = duration
        report['why_analyses'] = [
            {
                'alert_id': alert.id,
                'analysis': {
                    'primary_why': analysis.primary_why,
                    'secondary_why': analysis.secondary_why,
                    'tertiary_why': analysis.tertiary_why,
                    'root_cause': analysis.root_cause,
                    'confidence': analysis.confidence,
                    'suggested_actions': analysis.suggested_actions
                }
            }
            for alert, analysis in zip(top_alerts, why_analyses)
        ]
        
        # 8. 최종 결과 출력
        print("\n📊 === 데모 결과 요약 ===")
        print("=" * 40)
        print(f"⏱️ 총 소요시간: {duration:.1f}ms")
        print(f"📝 처리된 로그: {report['logs_processed']}개")
        print(f"🚨 생성된 경보: {report['alerts_generated']}개")
        print(f"🔇 소음 억제율: {report['noise_suppression_rate']:.1f}%")
        print(f"🎯 3WHY 분석: {len(why_analyses)}개")
        
        print(f"\n🏆 데모 성공! COSMOS AIOps 시스템이 정상 작동합니다.")
        
        return report

def main():
    """메인 실행 함수"""
    demo = COSMOSAIOpsDemo()
    report = demo.run_complete_demo(log_count=50)  # 작은 규모로 테스트
    
    # JSON 리포트 저장
    with open('COSMOS_Unified/aiops_demo_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📄 상세 리포트가 'aiops_demo_report.json'에 저장되었습니다.")
    
    return report

if __name__ == "__main__":
    main()
