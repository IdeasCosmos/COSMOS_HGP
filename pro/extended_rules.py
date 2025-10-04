#!/usr/bin/env python3
"""
Extended Rules and Codons for COSMOS Unified
확장된 규칙과 코돈 시스템 - 실용화를 위한 도메인별 규칙
"""

import numpy as np
import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

from core.velocity import Layer
from core.engine import RuleDefinition

logger = logging.getLogger(__name__)

class DomainType(Enum):
    """도메인 타입"""
    AIOPS = "aiops"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    GENERAL = "general"

class CodonType(Enum):
    """코돈 타입 - 64개 DNA 코돈 매핑"""
    # L1_QUANTUM 코돈들 (12개)
    ATG = ("ATG", "INIT", Layer.L1_QUANTUM, "초기화")
    ATC = ("ATC", "VALIDATE", Layer.L1_QUANTUM, "검증")
    ATT = ("ATT", "NORMALIZE", Layer.L1_QUANTUM, "정규화")
    ATA = ("ATA", "SCALE", Layer.L1_QUANTUM, "스케일링")
    ACT = ("ACT", "FILTER", Layer.L1_QUANTUM, "필터링")
    ACC = ("ACC", "TRANSFORM", Layer.L1_QUANTUM, "변환")
    ACA = ("ACA", "ENCODE", Layer.L1_QUANTUM, "인코딩")
    ACG = ("ACG", "DECODE", Layer.L1_QUANTUM, "디코딩")
    AAT = ("AAT", "PARSE", Layer.L1_QUANTUM, "파싱")
    AAC = ("AAC", "SERIALIZE", Layer.L1_QUANTUM, "직렬화")
    AAA = ("AAA", "DESERIALIZE", Layer.L1_QUANTUM, "역직렬화")
    AAG = ("AAG", "HASH", Layer.L1_QUANTUM, "해싱")
    
    # L2_ATOMIC 코돈들 (12개)
    GTT = ("GTT", "COMPUTE", Layer.L2_ATOMIC, "계산")
    GTC = ("GTC", "AGGREGATE", Layer.L2_ATOMIC, "집계")
    GTA = ("GTA", "CORRELATE", Layer.L2_ATOMIC, "상관분석")
    GTG = ("GTG", "CLASSIFY", Layer.L2_ATOMIC, "분류")
    GCT = ("GCT", "CLUSTER", Layer.L2_ATOMIC, "클러스터링")
    GCC = ("GCC", "PREDICT", Layer.L2_ATOMIC, "예측")
    GCA = ("GCA", "OPTIMIZE", Layer.L2_ATOMIC, "최적화")
    GCG = ("GCG", "ANALYZE", Layer.L2_ATOMIC, "분석")
    GAT = ("GAT", "EXTRACT", Layer.L2_ATOMIC, "추출")
    GAC = ("GAC", "REDUCE", Layer.L2_ATOMIC, "축소")
    GAA = ("GAA", "MAP", Layer.L2_ATOMIC, "매핑")
    GAG = ("GAG", "FOLD", Layer.L2_ATOMIC, "폴드")
    
    # L3_MOLECULAR 코돈들 (12개)
    TTT = ("TTT", "PROCESS", Layer.L3_MOLECULAR, "처리")
    TTC = ("TTC", "EXECUTE", Layer.L3_MOLECULAR, "실행")
    TTA = ("TTA", "SCHEDULE", Layer.L3_MOLECULAR, "스케줄링")
    TTG = ("TTG", "QUEUE", Layer.L3_MOLECULAR, "큐잉")
    TCT = ("TCT", "ROUTE", Layer.L3_MOLECULAR, "라우팅")
    TCC = ("TCC", "LOAD_BALANCE", Layer.L3_MOLECULAR, "로드밸런싱")
    TCA = ("TCA", "CACHE", Layer.L3_MOLECULAR, "캐싱")
    TCG = ("TCG", "REPLICATE", Layer.L3_MOLECULAR, "복제")
    TAT = ("TAT", "SYNC", Layer.L3_MOLECULAR, "동기화")
    TAC = ("TAC", "MERGE", Layer.L3_MOLECULAR, "병합")
    TAA = ("TAA", "SPLIT", Layer.L3_MOLECULAR, "분할")
    TAG = ("TAG", "COORDINATE", Layer.L3_MOLECULAR, "조정")
    
    # L4_COMPOUND 코돈들 (12개)
    CTT = ("CTT", "ORCHESTRATE", Layer.L4_COMPOUND, "오케스트레이션")
    CTC = ("CTC", "MANAGE", Layer.L4_COMPOUND, "관리")
    CTA = ("CTA", "CONTROL", Layer.L4_COMPOUND, "제어")
    CTG = ("CTG", "MONITOR", Layer.L4_COMPOUND, "모니터링")
    CCT = ("CCT", "ALERT", Layer.L4_COMPOUND, "알림")
    CCC = ("CCC", "LOG", Layer.L4_COMPOUND, "로깅")
    CCA = ("CCA", "AUDIT", Layer.L4_COMPOUND, "감사")
    CCG = ("CCG", "BACKUP", Layer.L4_COMPOUND, "백업")
    CAT = ("CAT", "RECOVER", Layer.L4_COMPOUND, "복구")
    CAC = ("CAC", "RESTORE", Layer.L4_COMPOUND, "복원")
    CAA = ("CAA", "MIGRATE", Layer.L4_COMPOUND, "마이그레이션")
    CAG = ("CAG", "DEPLOY", Layer.L4_COMPOUND, "배포")
    
    # L5_ORGANIC 코돈들 (8개)
    TGT = ("TGT", "EVOLVE", Layer.L5_ORGANIC, "진화")
    TGC = ("TGC", "ADAPT", Layer.L5_ORGANIC, "적응")
    TGA = ("TGA", "LEARN", Layer.L5_ORGANIC, "학습")
    TGG = ("TGG", "IMPROVE", Layer.L5_ORGANIC, "개선")
    CGT = ("CGT", "INNOVATE", Layer.L5_ORGANIC, "혁신")
    CGC = ("CGC", "OPTIMIZE", Layer.L5_ORGANIC, "최적화")
    CGA = ("CGA", "SCALE", Layer.L5_ORGANIC, "확장")
    CGG = ("CGG", "INTEGRATE", Layer.L5_ORGANIC, "통합")
    
    # L6_ECOSYSTEM 코돈들 (4개)
    AGT = ("AGT", "COORDINATE", Layer.L6_ECOSYSTEM, "조율")
    AGC = ("AGC", "BALANCE", Layer.L6_ECOSYSTEM, "균형")
    AGA = ("AGA", "HARMONIZE", Layer.L6_ECOSYSTEM, "조화")
    AGG = ("AGG", "SYNCHRONIZE", Layer.L6_ECOSYSTEM, "동기화")
    
    # L7_COSMOS 코돈들 (4개)
    GGT = ("GGT", "TRANSCEND", Layer.L7_COSMOS, "초월")
    GGC = ("GGC", "UNIFY", Layer.L7_COSMOS, "통합")
    GGA = ("GGA", "EMERGE", Layer.L7_COSMOS, "출현")
    GGG = ("GGG", "TRANSFORM", Layer.L7_COSMOS, "변환")
    
    def __init__(self, codon_seq: str, instruction: str, layer: Layer, description: str):
        self._value_ = codon_seq
        self.codon_seq = codon_seq
        self.instruction = instruction
        self.layer = layer
        self.description = description

@dataclass
class ExtendedRule:
    """확장된 규칙 정의"""
    key: str
    function: Callable
    layer: Layer
    threshold: float
    domain: DomainType
    codon_type: CodonType
    description: str
    dependencies: List[str] = field(default_factory=list)
    is_critical: bool = False
    fallback_rule: Optional[str] = None
    cache_ttl: int = 0
    timeout_seconds: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class ExtendedRuleSet:
    """확장된 규칙 세트 관리자"""
    
    def __init__(self):
        self.rules: Dict[str, ExtendedRule] = {}
        self.domain_rules: Dict[DomainType, List[str]] = {
            domain: [] for domain in DomainType
        }
        self.codon_mapping: Dict[str, CodonType] = {}
        
        # 기본 규칙들 초기화
        self._initialize_basic_rules()
        self._initialize_domain_rules()
    
    def _initialize_basic_rules(self):
        """기본 규칙들 초기화"""
        
        # L1_QUANTUM 규칙들
        self.add_rule(ExtendedRule(
            key="validate_input",
            function=self._validate_input,
            layer=Layer.L1_QUANTUM,
            threshold=0.1,
            domain=DomainType.GENERAL,
            codon_type=CodonType.ATC,
            description="입력 데이터 검증"
        ))
        
        self.add_rule(ExtendedRule(
            key="normalize_data",
            function=self._normalize_data,
            layer=Layer.L1_QUANTUM,
            threshold=0.15,
            domain=DomainType.GENERAL,
            codon_type=CodonType.ATT,
            description="데이터 정규화"
        ))
        
        self.add_rule(ExtendedRule(
            key="scale_features",
            function=self._scale_features,
            layer=Layer.L1_QUANTUM,
            threshold=0.12,
            domain=DomainType.GENERAL,
            codon_type=CodonType.ATA,
            description="특성 스케일링"
        ))
        
        # L2_ATOMIC 규칙들
        self.add_rule(ExtendedRule(
            key="compute_statistics",
            function=self._compute_statistics,
            layer=Layer.L2_ATOMIC,
            threshold=0.2,
            domain=DomainType.GENERAL,
            codon_type=CodonType.GTT,
            description="통계 계산"
        ))
        
        self.add_rule(ExtendedRule(
            key="aggregate_metrics",
            function=self._aggregate_metrics,
            layer=Layer.L2_ATOMIC,
            threshold=0.18,
            domain=DomainType.GENERAL,
            codon_type=CodonType.GTC,
            description="메트릭 집계"
        ))
        
        # L3_MOLECULAR 규칙들
        self.add_rule(ExtendedRule(
            key="process_workflow",
            function=self._process_workflow,
            layer=Layer.L3_MOLECULAR,
            threshold=0.25,
            domain=DomainType.GENERAL,
            codon_type=CodonType.TTT,
            description="워크플로우 처리"
        ))
        
        # L4_COMPOUND 규칙들
        self.add_rule(ExtendedRule(
            key="orchestrate_tasks",
            function=self._orchestrate_tasks,
            layer=Layer.L4_COMPOUND,
            threshold=0.3,
            domain=DomainType.GENERAL,
            codon_type=CodonType.CTT,
            description="태스크 오케스트레이션"
        ))
    
    def _initialize_domain_rules(self):
        """도메인별 규칙들 초기화"""
        
        # AIOps 규칙들
        self._add_aiops_rules()
        
        # 금융 규칙들
        self._add_finance_rules()
        
        # 헬스케어 규칙들
        self._add_healthcare_rules()
    
    def _add_aiops_rules(self):
        """AIOps 도메인 규칙들"""
        
        # 로그 분석 규칙들
        self.add_rule(ExtendedRule(
            key="parse_log_entries",
            function=self._parse_log_entries,
            layer=Layer.L1_QUANTUM,
            threshold=0.1,
            domain=DomainType.AIOPS,
            codon_type=CodonType.AAT,
            description="로그 엔트리 파싱"
        ))
        
        self.add_rule(ExtendedRule(
            key="extract_log_patterns",
            function=self._extract_log_patterns,
            layer=Layer.L2_ATOMIC,
            threshold=0.2,
            domain=DomainType.AIOPS,
            codon_type=CodonType.GAT,
            description="로그 패턴 추출"
        ))
        
        self.add_rule(ExtendedRule(
            key="detect_anomalies",
            function=self._detect_anomalies,
            layer=Layer.L2_ATOMIC,
            threshold=0.22,
            domain=DomainType.AIOPS,
            codon_type=CodonType.GCC,
            description="이상 탐지"
        ))
        
        # 시스템 모니터링 규칙들
        self.add_rule(ExtendedRule(
            key="monitor_system_health",
            function=self._monitor_system_health,
            layer=Layer.L4_COMPOUND,
            threshold=0.28,
            domain=DomainType.AIOPS,
            codon_type=CodonType.CTG,
            description="시스템 건강도 모니터링"
        ))
        
        self.add_rule(ExtendedRule(
            key="generate_alerts",
            function=self._generate_alerts,
            layer=Layer.L4_COMPOUND,
            threshold=0.25,
            domain=DomainType.AIOPS,
            codon_type=CodonType.CCT,
            description="알림 생성"
        ))
        
        # 자동 복구 규칙들
        self.add_rule(ExtendedRule(
            key="auto_recovery",
            function=self._auto_recovery,
            layer=Layer.L5_ORGANIC,
            threshold=0.32,
            domain=DomainType.AIOPS,
            codon_type=CodonType.TGT,
            description="자동 복구"
        ))
    
    def _add_finance_rules(self):
        """금융 도메인 규칙들"""
        
        # 리스크 관리 규칙들
        self.add_rule(ExtendedRule(
            key="calculate_var",
            function=self._calculate_var,
            layer=Layer.L2_ATOMIC,
            threshold=0.18,
            domain=DomainType.FINANCE,
            codon_type=CodonType.GTC,
            description="VaR 계산"
        ))
        
        self.add_rule(ExtendedRule(
            key="detect_fraud",
            function=self._detect_fraud,
            layer=Layer.L3_MOLECULAR,
            threshold=0.24,
            domain=DomainType.FINANCE,
            codon_type=CodonType.TTT,
            description="사기 탐지"
        ))
        
        self.add_rule(ExtendedRule(
            key="portfolio_optimization",
            function=self._portfolio_optimization,
            layer=Layer.L4_COMPOUND,
            threshold=0.3,
            domain=DomainType.FINANCE,
            codon_type=CodonType.CTT,
            description="포트폴리오 최적화"
        ))
        
        # 거래 규칙들
        self.add_rule(ExtendedRule(
            key="execute_trade",
            function=self._execute_trade,
            layer=Layer.L3_MOLECULAR,
            threshold=0.26,
            domain=DomainType.FINANCE,
            codon_type=CodonType.TTC,
            description="거래 실행"
        ))
        
        self.add_rule(ExtendedRule(
            key="risk_assessment",
            function=self._risk_assessment,
            layer=Layer.L4_COMPOUND,
            threshold=0.28,
            domain=DomainType.FINANCE,
            codon_type=CodonType.CTC,
            description="리스크 평가"
        ))
    
    def _add_healthcare_rules(self):
        """헬스케어 도메인 규칙들"""
        
        # 진단 규칙들
        self.add_rule(ExtendedRule(
            key="analyze_symptoms",
            function=self._analyze_symptoms,
            layer=Layer.L2_ATOMIC,
            threshold=0.2,
            domain=DomainType.HEALTHCARE,
            codon_type=CodonType.GCA,
            description="증상 분석"
        ))
        
        self.add_rule(ExtendedRule(
            key="diagnose_condition",
            function=self._diagnose_condition,
            layer=Layer.L3_MOLECULAR,
            threshold=0.25,
            domain=DomainType.HEALTHCARE,
            codon_type=CodonType.TTT,
            description="질환 진단"
        ))
        
        self.add_rule(ExtendedRule(
            key="predict_outcome",
            function=self._predict_outcome,
            layer=Layer.L2_ATOMIC,
            threshold=0.22,
            domain=DomainType.HEALTHCARE,
            codon_type=CodonType.GCC,
            description="결과 예측"
        ))
        
        # 치료 규칙들
        self.add_rule(ExtendedRule(
            key="recommend_treatment",
            function=self._recommend_treatment,
            layer=Layer.L4_COMPOUND,
            threshold=0.3,
            domain=DomainType.HEALTHCARE,
            codon_type=CodonType.CTT,
            description="치료 권고"
        ))
        
        self.add_rule(ExtendedRule(
            key="monitor_vitals",
            function=self._monitor_vitals,
            layer=Layer.L3_MOLECULAR,
            threshold=0.24,
            domain=DomainType.HEALTHCARE,
            codon_type=CodonType.TCT,
            description="생체 신호 모니터링"
        ))
    
    def add_rule(self, rule: ExtendedRule):
        """규칙 추가"""
        self.rules[rule.key] = rule
        self.domain_rules[rule.domain].append(rule.key)
        self.codon_mapping[rule.codon_type.codon_seq] = rule.codon_type
    
    def get_rules_by_domain(self, domain: DomainType) -> List[ExtendedRule]:
        """도메인별 규칙 조회"""
        rule_keys = self.domain_rules.get(domain, [])
        return [self.rules[key] for key in rule_keys if key in self.rules]
    
    def get_rule_by_codon(self, codon_seq: str) -> Optional[ExtendedRule]:
        """코돈으로 규칙 조회"""
        codon_type = self.codon_mapping.get(codon_seq)
        if not codon_type:
            return None
        
        # 해당 코돈 타입을 가진 규칙 찾기
        for rule in self.rules.values():
            if rule.codon_type == codon_type:
                return rule
        
        return None
    
    def get_all_rules(self) -> Dict[str, ExtendedRule]:
        """모든 규칙 조회"""
        return self.rules.copy()
    
    # ===============================
    # 기본 규칙 함수들
    # ===============================
    
    def _validate_input(self, data: Any) -> Any:
        """입력 데이터 검증"""
        if data is None:
            raise ValueError("Input data cannot be None")
        
        if isinstance(data, (list, np.ndarray)):
            if len(data) == 0:
                raise ValueError("Input data cannot be empty")
            
            # NaN 값 검사
            if isinstance(data, np.ndarray):
                if np.any(np.isnan(data)):
                    data = np.nan_to_num(data, nan=0.0)
        
        return data
    
    def _normalize_data(self, data: Any) -> Any:
        """데이터 정규화"""
        if isinstance(data, (list, np.ndarray)):
            data = np.array(data)
            norm = np.linalg.norm(data)
            if norm > 0:
                return data / norm
            return data
        return data
    
    def _scale_features(self, data: Any) -> Any:
        """특성 스케일링"""
        if isinstance(data, (list, np.ndarray)):
            data = np.array(data)
            if len(data) > 0:
                min_val, max_val = np.min(data), np.max(data)
                if max_val > min_val:
                    return (data - min_val) / (max_val - min_val)
            return data
        return data
    
    def _compute_statistics(self, data: Any) -> Any:
        """통계 계산"""
        if isinstance(data, (list, np.ndarray)):
            data = np.array(data)
            stats = {
                'mean': np.mean(data),
                'std': np.std(data),
                'min': np.min(data),
                'max': np.max(data),
                'count': len(data)
            }
            return stats
        return data
    
    def _aggregate_metrics(self, data: Any) -> Any:
        """메트릭 집계"""
        if isinstance(data, dict) and 'metrics' in data:
            metrics = data['metrics']
            if isinstance(metrics, list):
                aggregated = {
                    'total_count': len(metrics),
                    'avg_value': np.mean([m.get('value', 0) for m in metrics]),
                    'sum_value': np.sum([m.get('value', 0) for m in metrics])
                }
                return aggregated
        return data
    
    def _process_workflow(self, data: Any) -> Any:
        """워크플로우 처리"""
        if isinstance(data, dict) and 'steps' in data:
            steps = data['steps']
            processed_steps = []
            
            for step in steps:
                if isinstance(step, dict):
                    processed_step = step.copy()
                    processed_step['processed'] = True
                    processed_step['timestamp'] = time.time()
                    processed_steps.append(processed_step)
            
            return {'steps': processed_steps, 'status': 'completed'}
        return data
    
    def _orchestrate_tasks(self, data: Any) -> Any:
        """태스크 오케스트레이션"""
        if isinstance(data, dict) and 'tasks' in data:
            tasks = data['tasks']
            orchestrated = {
                'total_tasks': len(tasks),
                'completed_tasks': 0,
                'failed_tasks': 0,
                'status': 'running'
            }
            
            for task in tasks:
                if isinstance(task, dict):
                    if task.get('status') == 'completed':
                        orchestrated['completed_tasks'] += 1
                    elif task.get('status') == 'failed':
                        orchestrated['failed_tasks'] += 1
            
            if orchestrated['completed_tasks'] + orchestrated['failed_tasks'] == orchestrated['total_tasks']:
                orchestrated['status'] = 'completed'
            
            return orchestrated
        return data
    
    # ===============================
    # AIOps 규칙 함수들
    # ===============================
    
    def _parse_log_entries(self, data: Any) -> Any:
        """로그 엔트리 파싱"""
        if isinstance(data, str):
            # 간단한 로그 파싱 (실제로는 더 복잡한 파싱 로직 필요)
            parts = data.split(' ')
            if len(parts) >= 4:
                return {
                    'timestamp': parts[0],
                    'level': parts[1],
                    'component': parts[2],
                    'message': ' '.join(parts[3:]),
                    'parsed': True
                }
        return data
    
    def _extract_log_patterns(self, data: Any) -> Any:
        """로그 패턴 추출"""
        if isinstance(data, list):
            patterns = {}
            for entry in data:
                if isinstance(entry, dict) and 'message' in entry:
                    message = entry['message']
                    # 간단한 패턴 추출
                    if 'error' in message.lower():
                        patterns['error_pattern'] = patterns.get('error_pattern', 0) + 1
                    elif 'warning' in message.lower():
                        patterns['warning_pattern'] = patterns.get('warning_pattern', 0) + 1
            
            return patterns
        return data
    
    def _detect_anomalies(self, data: Any) -> Any:
        """이상 탐지"""
        if isinstance(data, (list, np.ndarray)):
            data = np.array(data)
            if len(data) > 1:
                mean_val = np.mean(data)
                std_val = np.std(data)
                
                anomalies = []
                for i, value in enumerate(data):
                    if abs(value - mean_val) > 2 * std_val:
                        anomalies.append({
                            'index': i,
                            'value': value,
                            'severity': 'high' if abs(value - mean_val) > 3 * std_val else 'medium'
                        })
                
                return {
                    'anomalies': anomalies,
                    'anomaly_count': len(anomalies),
                    'anomaly_rate': len(anomalies) / len(data)
                }
        return data
    
    def _monitor_system_health(self, data: Any) -> Any:
        """시스템 건강도 모니터링"""
        if isinstance(data, dict):
            health_score = 1.0
            
            # CPU 사용률 체크
            cpu_usage = data.get('cpu_usage', 0)
            if cpu_usage > 0.8:
                health_score -= 0.3
            elif cpu_usage > 0.6:
                health_score -= 0.1
            
            # 메모리 사용률 체크
            memory_usage = data.get('memory_usage', 0)
            if memory_usage > 0.9:
                health_score -= 0.4
            elif memory_usage > 0.7:
                health_score -= 0.2
            
            # 디스크 사용률 체크
            disk_usage = data.get('disk_usage', 0)
            if disk_usage > 0.95:
                health_score -= 0.3
            elif disk_usage > 0.8:
                health_score -= 0.1
            
            health_score = max(0.0, health_score)
            
            return {
                'health_score': health_score,
                'status': 'healthy' if health_score > 0.7 else 'warning' if health_score > 0.4 else 'critical',
                'timestamp': time.time()
            }
        return data
    
    def _generate_alerts(self, data: Any) -> Any:
        """알림 생성"""
        if isinstance(data, dict):
            alerts = []
            
            health_score = data.get('health_score', 1.0)
            if health_score < 0.4:
                alerts.append({
                    'type': 'critical',
                    'message': 'System health critical',
                    'severity': 'high'
                })
            elif health_score < 0.7:
                alerts.append({
                    'type': 'warning',
                    'message': 'System health degraded',
                    'severity': 'medium'
                })
            
            anomaly_count = data.get('anomaly_count', 0)
            if anomaly_count > 10:
                alerts.append({
                    'type': 'anomaly',
                    'message': f'High anomaly count: {anomaly_count}',
                    'severity': 'high'
                })
            
            return {
                'alerts': alerts,
                'alert_count': len(alerts),
                'timestamp': time.time()
            }
        return data
    
    def _auto_recovery(self, data: Any) -> Any:
        """자동 복구"""
        if isinstance(data, dict):
            recovery_actions = []
            
            health_score = data.get('health_score', 1.0)
            if health_score < 0.4:
                recovery_actions.append({
                    'action': 'restart_service',
                    'description': 'Restart critical services'
                })
                recovery_actions.append({
                    'action': 'clear_cache',
                    'description': 'Clear system cache'
                })
            
            anomaly_rate = data.get('anomaly_rate', 0)
            if anomaly_rate > 0.1:
                recovery_actions.append({
                    'action': 'adjust_thresholds',
                    'description': 'Adjust anomaly detection thresholds'
                })
            
            return {
                'recovery_actions': recovery_actions,
                'actions_taken': len(recovery_actions),
                'timestamp': time.time()
            }
        return data
    
    # ===============================
    # 금융 규칙 함수들
    # ===============================
    
    def _calculate_var(self, data: Any) -> Any:
        """VaR (Value at Risk) 계산"""
        if isinstance(data, (list, np.ndarray)):
            returns = np.array(data)
            if len(returns) > 1:
                # 95% VaR 계산
                var_95 = np.percentile(returns, 5)
                # 99% VaR 계산
                var_99 = np.percentile(returns, 1)
                
                return {
                    'var_95': var_95,
                    'var_99': var_99,
                    'mean_return': np.mean(returns),
                    'volatility': np.std(returns)
                }
        return data
    
    def _detect_fraud(self, data: Any) -> Any:
        """사기 탐지"""
        if isinstance(data, dict):
            fraud_score = 0.0
            fraud_indicators = []
            
            # 거래 금액 체크
            amount = data.get('amount', 0)
            if amount > 100000:  # 10만 이상
                fraud_score += 0.3
                fraud_indicators.append('high_amount')
            
            # 시간 체크 (새벽 거래)
            hour = data.get('hour', 12)
            if hour < 6 or hour > 22:
                fraud_score += 0.2
                fraud_indicators.append('unusual_time')
            
            # 위치 체크
            location = data.get('location', '')
            if 'overseas' in location.lower():
                fraud_score += 0.2
                fraud_indicators.append('overseas_transaction')
            
            # 빈도 체크
            frequency = data.get('frequency', 0)
            if frequency > 10:  # 하루 10회 이상
                fraud_score += 0.3
                fraud_indicators.append('high_frequency')
            
            return {
                'fraud_score': min(1.0, fraud_score),
                'fraud_indicators': fraud_indicators,
                'is_fraud': fraud_score > 0.5
            }
        return data
    
    def _portfolio_optimization(self, data: Any) -> Any:
        """포트폴리오 최적화"""
        if isinstance(data, dict) and 'assets' in data:
            assets = data['assets']
            if isinstance(assets, list) and len(assets) > 0:
                # 간단한 최적화 (실제로는 더 복잡한 알고리즘 필요)
                weights = np.random.dirichlet(np.ones(len(assets)))
                
                optimized_portfolio = []
                for i, asset in enumerate(assets):
                    optimized_portfolio.append({
                        'asset': asset,
                        'weight': weights[i],
                        'expected_return': np.random.normal(0.05, 0.1)
                    })
                
                return {
                    'portfolio': optimized_portfolio,
                    'total_weight': np.sum(weights),
                    'diversification': len(assets)
                }
        return data
    
    def _execute_trade(self, data: Any) -> Any:
        """거래 실행"""
        if isinstance(data, dict):
            symbol = data.get('symbol', '')
            quantity = data.get('quantity', 0)
            price = data.get('price', 0)
            
            # 간단한 거래 실행 시뮬레이션
            trade_id = f"TRD_{int(time.time())}"
            execution_price = price * (1 + np.random.normal(0, 0.001))  # 약간의 슬리피지
            
            return {
                'trade_id': trade_id,
                'symbol': symbol,
                'quantity': quantity,
                'execution_price': execution_price,
                'total_value': quantity * execution_price,
                'status': 'executed',
                'timestamp': time.time()
            }
        return data
    
    def _risk_assessment(self, data: Any) -> Any:
        """리스크 평가"""
        if isinstance(data, dict):
            risk_score = 0.0
            risk_factors = []
            
            # 시장 변동성
            volatility = data.get('volatility', 0)
            if volatility > 0.3:
                risk_score += 0.4
                risk_factors.append('high_volatility')
            
            # 레버리지
            leverage = data.get('leverage', 1)
            if leverage > 3:
                risk_score += 0.3
                risk_factors.append('high_leverage')
            
            # 집중도
            concentration = data.get('concentration', 0)
            if concentration > 0.7:
                risk_score += 0.3
                risk_factors.append('high_concentration')
            
            return {
                'risk_score': min(1.0, risk_score),
                'risk_level': 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.4 else 'low',
                'risk_factors': risk_factors
            }
        return data
    
    # ===============================
    # 헬스케어 규칙 함수들
    # ===============================
    
    def _analyze_symptoms(self, data: Any) -> Any:
        """증상 분석"""
        if isinstance(data, list):
            symptoms = data
            symptom_scores = {}
            
            # 증상별 점수 계산
            for symptom in symptoms:
                if isinstance(symptom, dict):
                    name = symptom.get('name', '')
                    severity = symptom.get('severity', 0)
                    
                    # 간단한 증상 분석
                    if 'fever' in name.lower():
                        symptom_scores['fever'] = severity * 0.8
                    elif 'pain' in name.lower():
                        symptom_scores['pain'] = severity * 0.6
                    elif 'fatigue' in name.lower():
                        symptom_scores['fatigue'] = severity * 0.4
            
            return {
                'symptoms': symptoms,
                'symptom_scores': symptom_scores,
                'total_score': sum(symptom_scores.values())
            }
        return data
    
    def _diagnose_condition(self, data: Any) -> Any:
        """질환 진단"""
        if isinstance(data, dict):
            symptom_scores = data.get('symptom_scores', {})
            total_score = data.get('total_score', 0)
            
            # 간단한 진단 로직
            diagnosis = "unknown"
            confidence = 0.0
            
            if symptom_scores.get('fever', 0) > 0.7:
                diagnosis = "infection"
                confidence = 0.8
            elif symptom_scores.get('pain', 0) > 0.6:
                diagnosis = "injury"
                confidence = 0.7
            elif total_score > 0.5:
                diagnosis = "general_illness"
                confidence = 0.6
            
            return {
                'diagnosis': diagnosis,
                'confidence': confidence,
                'symptom_analysis': symptom_scores,
                'timestamp': time.time()
            }
        return data
    
    def _predict_outcome(self, data: Any) -> Any:
        """결과 예측"""
        if isinstance(data, dict):
            diagnosis = data.get('diagnosis', 'unknown')
            confidence = data.get('confidence', 0)
            
            # 간단한 예측 로직
            outcome_probability = 0.8  # 기본 회복 확률
            
            if diagnosis == 'infection':
                outcome_probability = 0.9
            elif diagnosis == 'injury':
                outcome_probability = 0.85
            elif diagnosis == 'general_illness':
                outcome_probability = 0.75
            
            # 신뢰도에 따른 조정
            outcome_probability *= confidence
            
            return {
                'outcome': 'recovery' if outcome_probability > 0.7 else 'monitoring_needed',
                'probability': outcome_probability,
                'recommended_action': 'treatment' if outcome_probability > 0.8 else 'observation'
            }
        return data
    
    def _recommend_treatment(self, data: Any) -> Any:
        """치료 권고"""
        if isinstance(data, dict):
            diagnosis = data.get('diagnosis', 'unknown')
            outcome = data.get('outcome', 'unknown')
            
            treatments = []
            
            if diagnosis == 'infection':
                treatments.append({
                    'treatment': 'antibiotics',
                    'priority': 'high',
                    'duration': '7-10 days'
                })
            elif diagnosis == 'injury':
                treatments.append({
                    'treatment': 'pain_management',
                    'priority': 'medium',
                    'duration': '3-5 days'
                })
            
            if outcome == 'monitoring_needed':
                treatments.append({
                    'treatment': 'regular_checkup',
                    'priority': 'medium',
                    'duration': 'ongoing'
                })
            
            return {
                'treatments': treatments,
                'treatment_count': len(treatments),
                'follow_up_needed': outcome == 'monitoring_needed'
            }
        return data
    
    def _monitor_vitals(self, data: Any) -> Any:
        """생체 신호 모니터링"""
        if isinstance(data, dict):
            vitals = {}
            
            # 심박수
            heart_rate = data.get('heart_rate', 70)
            if heart_rate > 100:
                vitals['heart_rate_status'] = 'elevated'
            elif heart_rate < 60:
                vitals['heart_rate_status'] = 'low'
            else:
                vitals['heart_rate_status'] = 'normal'
            
            # 혈압
            blood_pressure = data.get('blood_pressure', [120, 80])
            if isinstance(blood_pressure, list) and len(blood_pressure) >= 2:
                systolic, diastolic = blood_pressure[0], blood_pressure[1]
                if systolic > 140 or diastolic > 90:
                    vitals['blood_pressure_status'] = 'high'
                elif systolic < 90 or diastolic < 60:
                    vitals['blood_pressure_status'] = 'low'
                else:
                    vitals['blood_pressure_status'] = 'normal'
            
            # 체온
            temperature = data.get('temperature', 36.5)
            if temperature > 37.5:
                vitals['temperature_status'] = 'fever'
            elif temperature < 36.0:
                vitals['temperature_status'] = 'low'
            else:
                vitals['temperature_status'] = 'normal'
            
            return {
                'vitals': vitals,
                'overall_status': 'normal' if all('normal' in str(v) for v in vitals.values()) else 'abnormal',
                'timestamp': time.time()
            }
        return data
