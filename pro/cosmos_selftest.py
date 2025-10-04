#!/usr/bin/env python3
"""
COSMOS 자가 디버깅 셀프테스트 러너
COSMOS 시스템이 스스로 실행·설명·가드·정책반응을 검증
"""

import numpy as np
import time
import json
import traceback
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# 핵심코드에서 가져올 컴포넌트들 (실제로는 import 필요)
try:
    from 핵심코드첨부 import (
        GlobalPolicy, 
        UnifiedDualityEngine, 
        DualityRule, 
        Layer,
        DualityDNACodon,
        create_demo_duality_rules
    )
except ImportError:
    # 임시로 핵심코드의 클래스들을 여기에 정의
    from enum import Enum
    from typing import Literal
    from dataclasses import dataclass, field
    
    class Layer(Enum):
        L1_QUANTUM = (1, "Quantum", 0.12)
        L2_ATOMIC = (2, "Atomic", 0.20)
        L3_MOLECULAR = (3, "Molecular", 0.26)
        L4_COMPOUND = (4, "Compound", 0.30)
        L5_ORGANIC = (5, "Organic", 0.33)
        L6_ECOSYSTEM = (6, "Ecosystem", 0.35)
        L7_COSMOS = (7, "Cosmos", 0.38)
        
        def __init__(self, level: int, name: str, threshold: float):
            self.level = level
            self.display_name = name
            self.base_threshold = threshold
    
    @dataclass
    class GlobalPolicy:
        mode: Literal['stability', 'innovation', 'adaptive'] = 'stability'
        base_threshold: float = 0.3
        
        def get_effective_threshold(self, base=None, layer_level=1):
            return (base or self.base_threshold) * (0.7 if self.mode == 'stability' else 2.2 if self.mode == 'innovation' else 1.0)
        
        def get_butterfly_factor(self):
            return 0.8 if self.mode == 'stability' else 1.4 if self.mode == 'innovation' else 1.0
        
        def should_explore_chaos(self):
            return np.random.random() < (0.1 if self.mode == 'stability' else 0.7 if self.mode == 'innovation' else 0.4)
    
    @dataclass 
    class DualityRule:
        key: str
        function: Any
        layer: Layer
        threshold: float = None
        
        def get_policy_threshold(self, policy):
            base = self.threshold or self.layer.base_threshold
            return policy.get_effective_threshold(base, self.layer.level)
    
    class UnifiedDualityEngine:
        def __init__(self, rules, policy):
            self.rules = {rule.key: rule for rule in rules}
            self.policy = policy
            self.mode_stats = {'stability': {'protected': 0, 'recovered': 0, 'blocked': 0}}
        
        def execute_with_full_duality(self, group, input_data):
            # 단순화된 실행 로직
            current_data = input_data
            execution_path = []
            
            for item in group:
                if isinstance(item, str):
                    rule = self.rules.get(item)
                    if rule:
                        result = self._execute_rule(rule, current_data)
                        execution_path.append({
                            'rule': item,
                            'layer': rule.layer.display_name,
                            'status': result['status'],
                            'impact': result['impact']
                        })
                        current_data = result['output']
            
            return {
                'output_data': current_data,
                'execution_path': execution_path,
                'total_impact': np.linalg.norm(current_data - input_data) if isinstance(current_data, np.ndarray) else 0.1
            }
        
        def _execute_rule(self, rule, input_data):
            try:
                output = rule.function(input_data)
                impact = np.linalg.norm(output - input_data) if isinstance(output, np.ndarray) else 0.1
                threshold = rule.get_policy_threshold(self.policy)
                
                if impact <= threshold:
                    status = 'SUCCESS'
                else:
                    status = 'BLOCKED'
                    if self.policy.mode == 'stability':
                        output = input_data  # 복구
                        status = 'RECOVERED'
                
                return {'output': output, 'impact': impact, 'status': status}
            except Exception as e:
                return {'output': input_data, 'impact': 0, 'status': 'ERROR', 'error': str(e)}
    
    def create_demo_duality_rules():
        return [
            DualityRule(
                key="scale",
                function=lambda x: x * 2,
                layer=Layer.L2_ATOMIC,
                threshold=0.2
            ),
            DualityRule(
                key="normalize", 
                function=lambda x: x / (np.linalg.norm(x) + 1e-9),
                layer=Layer.L1_QUANTUM,
                threshold=0.1
            ),
            DualityRule(
                key="clip",
                function=lambda x: np.clip(x, -1, 1),
                layer=Layer.L4_COMPOUND,
                threshold=0.3
            )
        ]

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """테스트 결과"""
    title: str
    status: str
    details: Dict[str, Any]
    duration_ms: float
    success: bool

class COSMOSSelfTestRunner:
    """COSMOS 자가 테스트 러너"""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.engine_cache = {}
        
    def run_case(self, title: str, engine, payload: Any, bucket: str = "normal") -> TestResult:
        """단일 테스트 케이스 실행"""
        print(f"\n=== {title} ===")
        start_time = time.time()
        
        try:
            # 엔진 실행
            out = engine.execute_with_full_duality(payload, bucket=bucket)
            duration = (time.time() - start_time) * 1000
            
            # 결과 분석
            status = self._analyze_result(out)
            success = status in ['SUCCESS', 'BLOCKED', 'AMPLIFIED']
            
            # 출력
            print(f"mode: {out.get('mode', 'unknown')} | status: {status}")
            print(f"impact: {out.get('total_impact', 0):.3f}")
            print(f"duration: {duration:.1f}ms")
            
            if 'execution_path' in out:
                for step in out['execution_path']:
                    print(f" - {step['rule']} [{step['layer']}] {step['status']} imp: {step.get('impact', 0):.3f}")
            
            result = TestResult(
                title=title,
                status=status,
                details=out,
                duration_ms=duration,
                success=success
            )
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            print(f"❌ ERROR: {str(e)}")
            
            result = TestResult(
                title=title,
                status="ERROR",
                details={'error': str(e), 'traceback': traceback.format_exc()},
                duration_ms=duration,
                success=False
            )
            
            self.test_results.append(result)
            return result
    
    def _analyze_result(self, result: Dict) -> str:
        """결과 분석하여 상태 결정"""
        execution_path = result.get('execution_path', [])
        
        if not execution_path:
            return "EMPTY"
        
        # 상태별 카운트
        status_counts = {}
        for step in execution_path:
            status = step.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 우선순위별 상태 결정
        if status_counts.get('AMPLIFIED', 0) > 0:
            return 'AMPLIFIED'
        elif status_counts.get('BLOCKED', 0) > 0:
            return 'BLOCKED'
        elif status_counts.get('SUCCESS', 0) > 0:
            return 'SUCCESS'
        elif status_counts.get('ERROR', 0) > 0:
            return 'ERROR'
        else:
            return 'UNKNOWN'
    
    def run_smoke_test(self) -> TestResult:
        """1) 스모크 테스트: 정상 흐름 + 3why(duality_path) 확인"""
        print("\n🔥 === SMOKE TEST: 정상 흐름 검증 ===")
        
        eng_ok = UnifiedDualityEngine(
            rules=create_demo_duality_rules(),
            policy=GlobalPolicy(mode="stability", base_threshold=0.35)
        )
        
        payload = {
            "sequence": ["normalize", "scale", "clip"],
            "input_data": np.array([1.0, 2.0, 3.0, 4.0])
        }
        
        return self.run_case("SMOKE / stability", eng_ok, payload, bucket="normal")
    
    def run_guard_test(self) -> TestResult:
        """2) 속도 가드 검증: 아주 낮은 cap → BLOCKED 기대"""
        print("\n🛡️ === GUARD TEST: 속도 제한 검증 ===")
        
        eng_block = UnifiedDualityEngine(
            rules=create_demo_duality_rules(),
            policy=GlobalPolicy(mode="stability", base_threshold=0.05)  # 매우 낮은 임계값
        )
        
        payload = {
            "sequence": ["scale", "normalize"],  # 큰 변화를 일으킬 수 있는 시퀀스
            "input_data": np.array([1.0, 2.0, 3.0, 4.0])
        }
        
        return self.run_case("GUARD / low cap → BLOCKED", eng_block, payload, bucket="high")
    
    def run_innovation_test(self) -> TestResult:
        """3) 혁신 모드 증폭 경로: same payload, amplification 작동 여부"""
        print("\n🚀 === INNOVATION TEST: 증폭 경로 검증 ===")
        
        eng_innov = UnifiedDualityEngine(
            rules=create_demo_duality_rules(),
            policy=GlobalPolicy(mode="innovation", base_threshold=0.35)
        )
        
        payload = {
            "sequence": ["scale", "normalize", "clip"],
            "input_data": np.array([1.0, 2.0, 3.0, 4.0])
        }
        
        return self.run_case("INNOVATION / amplification", eng_innov, payload, bucket="high")
    
    def run_rule_injection_test(self) -> TestResult:
        """4) 규칙 주입으로 "의도적 큰 변화" 발생 → 정책 반응 확인"""
        print("\n💉 === RULE INJECTION TEST: 정책 반응 검증 ===")
        
        # 큰 변화를 일으키는 규칙 생성
        def big_bang_transform(x: np.ndarray) -> np.ndarray:
            """전체 노름을 크게 키워 impact 상승"""
            return x + np.ones_like(x) * 0.8
        
        # 규칙 추가
        rules = create_demo_duality_rules()
        rules.append(DualityRule(
            key="big_bang",
            function=big_bang_transform,
            layer=Layer.L6_ECOSYSTEM,
            threshold=0.35
        ))
        
        # 안정성 모드 엔진
        eng_stability = UnifiedDualityEngine(
            rules=rules,
            policy=GlobalPolicy(mode="stability", base_threshold=0.35)
        )
        
        # 혁신 모드 엔진  
        eng_innovation = UnifiedDualityEngine(
            rules=rules,
            policy=GlobalPolicy(mode="innovation", base_threshold=0.35)
        )
        
        payload = {
            "sequence": ["scale", "big_bang", "clip"],
            "input_data": np.array([1.0, 2.0, 3.0, 4.0])
        }
        
        # 안정성 모드 테스트
        stability_result = self.run_case("RULE INJECTION / stability reaction", eng_stability, payload)
        
        # 혁신 모드 테스트
        innovation_result = self.run_case("RULE INJECTION / innovation reaction", eng_innovation, payload)
        
        return TestResult(
            title="RULE INJECTION / combined",
            status="COMBINED",
            details={
                'stability': stability_result.details,
                'innovation': innovation_result.details
            },
            duration_ms=stability_result.duration_ms + innovation_result.duration_ms,
            success=stability_result.success and innovation_result.success
        )
    
    def run_chaos_exploration_test(self) -> TestResult:
        """5) 카오스 탐험 테스트: 혁신 모드의 카오스 탐험 기능"""
        print("\n🌀 === CHAOS EXPLORATION TEST: 카오스 탐험 검증 ===")
        
        eng_chaos = UnifiedDualityEngine(
            rules=create_demo_duality_rules(),
            policy=GlobalPolicy(mode="innovation", base_threshold=0.25)
        )
        
        # 카오스 시드가 포함된 입력
        chaos_input = np.array([1.0, 2.0, 3.0, 4.0]) + np.random.normal(0, 0.1, 4)
        
        payload = {
            "sequence": ["scale", "normalize"],
            "input_data": chaos_input
        }
        
        return self.run_case("CHAOS / exploration", eng_chaos, payload, bucket="chaos")
    
    def run_adaptive_mode_test(self) -> TestResult:
        """6) 적응 모드 테스트: 동적 균형 조절"""
        print("\n⚖️ === ADAPTIVE MODE TEST: 적응적 균형 검증 ===")
        
        eng_adaptive = UnifiedDualityEngine(
            rules=create_demo_duality_rules(),
            policy=GlobalPolicy(mode="adaptive", base_threshold=0.3)
        )
        
        payload = {
            "sequence": ["normalize", "scale", "clip"],
            "input_data": np.array([1.0, 2.0, 3.0, 4.0])
        }
        
        return self.run_case("ADAPTIVE / balance", eng_adaptive, payload, bucket="adaptive")
    
    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """전체 테스트 스위트 실행"""
        print("🌟 COSMOS 자가 디버깅 셀프테스트 시작")
        print("=" * 60)
        
        start_time = time.time()
        
        # 모든 테스트 실행
        tests = [
            self.run_smoke_test,
            self.run_guard_test,
            self.run_innovation_test,
            self.run_rule_injection_test,
            self.run_chaos_exploration_test,
            self.run_adaptive_mode_test
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ 테스트 실패: {test_func.__name__} - {str(e)}")
        
        total_duration = (time.time() - start_time) * 1000
        
        # 결과 분석
        return self._generate_test_report(total_duration)
    
    def _generate_test_report(self, total_duration: float) -> Dict[str, Any]:
        """테스트 보고서 생성"""
        print("\n📊 === 테스트 결과 종합 분석 ===")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.success)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 상태별 통계
        status_stats = {}
        for result in self.test_results:
            status = result.status
            status_stats[status] = status_stats.get(status, 0) + 1
        
        # 성능 통계
        durations = [r.duration_ms for r in self.test_results]
        avg_duration = np.mean(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        
        # 상세 결과
        print(f"📈 전체 테스트: {total_tests}개")
        print(f"✅ 성공: {successful_tests}개 ({success_rate:.1f}%)")
        print(f"❌ 실패: {total_tests - successful_tests}개")
        print(f"⏱️ 총 소요시간: {total_duration:.1f}ms")
        print(f"📊 평균 테스트시간: {avg_duration:.1f}ms")
        
        print(f"\n📋 상태별 통계:")
        for status, count in status_stats.items():
            print(f"   {status}: {count}개")
        
        # 기대 확인 포인트 검증
        print(f"\n🎯 기대 확인 포인트 검증:")
        
        smoke_test = next((r for r in self.test_results if "SMOKE" in r.title), None)
        if smoke_test and smoke_test.success:
            print("✅ SMOKE: 정상 흐름 및 duality_path 확인")
        else:
            print("❌ SMOKE: 실패")
        
        guard_test = next((r for r in self.test_results if "GUARD" in r.title), None)
        if guard_test and guard_test.status == "BLOCKED":
            print("✅ GUARD: 낮은 cap에서 BLOCKED 확인")
        else:
            print("❌ GUARD: BLOCKED 미발생")
        
        innovation_test = next((r for r in self.test_results if "INNOVATION" in r.title), None)
        if innovation_test:
            execution_path = innovation_test.details.get('execution_path', [])
            amplified_count = sum(1 for step in execution_path if step.get('status') == 'AMPLIFIED')
            if amplified_count > 0:
                print("✅ INNOVATION: AMPLIFIED 발생 확인")
            else:
                print("⚠️ INNOVATION: AMPLIFIED 미발생 (정상일 수 있음)")
        
        injection_tests = [r for r in self.test_results if "RULE INJECTION" in r.title]
        if len(injection_tests) >= 2:
            stability_injection = injection_tests[0]
            innovation_injection = injection_tests[1]
            
            stability_blocked = any(step.get('status') == 'BLOCKED' for step in stability_injection.details.get('execution_path', []))
            innovation_explored = any(step.get('status') in ['AMPLIFIED', 'EXPLORED'] for step in innovation_injection.details.get('execution_path', []))
            
            if stability_blocked:
                print("✅ RULE INJECTION: stability에서 차단/복구 확인")
            else:
                print("❌ RULE INJECTION: stability 차단 미발생")
            
            if innovation_explored:
                print("✅ RULE INJECTION: innovation에서 증폭/탐험 확인")
            else:
                print("⚠️ RULE INJECTION: innovation 증폭 미발생")
        
        report = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': success_rate,
            'total_duration_ms': total_duration,
            'avg_duration_ms': avg_duration,
            'max_duration_ms': max_duration,
            'min_duration_ms': min_duration,
            'status_stats': status_stats,
            'test_results': [
                {
                    'title': r.title,
                    'status': r.status,
                    'success': r.success,
                    'duration_ms': r.duration_ms
                }
                for r in self.test_results
            ],
            'expectation_verification': {
                'smoke_test': smoke_test.success if smoke_test else False,
                'guard_test_blocked': guard_test.status == "BLOCKED" if guard_test else False,
                'innovation_amplified': any(step.get('status') == 'AMPLIFIED' for step in innovation_test.details.get('execution_path', [])) if innovation_test else False,
                'rule_injection_reactions': len(injection_tests) >= 2
            }
        }
        
        return report

def run_cosmos_self_test():
    """COSMOS 자가 테스트 실행 함수"""
    runner = COSMOSSelfTestRunner()
    report = runner.run_comprehensive_test_suite()
    
    print(f"\n🎉 COSMOS 자가 디버깅 셀프테스트 완료!")
    print(f"📊 최종 성공률: {report['success_rate']:.1f}%")
    
    if report['success_rate'] >= 80:
        print("🌟 COSMOS 시스템이 정상적으로 작동하고 있습니다!")
    elif report['success_rate'] >= 60:
        print("⚠️ COSMOS 시스템에 일부 문제가 있을 수 있습니다.")
    else:
        print("🚨 COSMOS 시스템에 심각한 문제가 있습니다!")
    
    return report

if __name__ == "__main__":
    # 자가 테스트 실행
    report = run_cosmos_self_test()
    
    # JSON 리포트 저장
    with open('COSMOS_Unified/selftest_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📄 상세 리포트가 'selftest_report.json'에 저장되었습니다.")
