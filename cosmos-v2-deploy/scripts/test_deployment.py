#!/usr/bin/env python3
"""
COSMOS-HGP V2-min+ 배포 테스트 스크립트
"""
import requests
import json
import time
import sys

def test_health():
    """헬스 체크 테스트"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 헬스 체크 통과")
            return True
        else:
            print(f"❌ 헬스 체크 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 헬스 체크 오류: {e}")
        return False

def test_demo_scenarios():
    """데모 시나리오 테스트"""
    base_url = "http://localhost:5000/run"
    
    # 시나리오 A: 정상 흐름
    print("\n🧪 시나리오 A: 정상 흐름 테스트")
    scenario_a = {
        "data": [1, 2, 3, 4, 5],
        "threshold": 0.30,
        "cumulative_cap": 0.50
    }
    
    try:
        response = requests.post(base_url, json=scenario_a, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 시나리오 A 성공: {result['summary']['rules_executed']}개 규칙 실행")
            print(f"   타임라인: {result['timeline']}")
        else:
            print(f"❌ 시나리오 A 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 시나리오 A 오류: {e}")
        return False
    
    # 시나리오 B: 국소 차단
    print("\n🧪 시나리오 B: 국소 차단 테스트")
    scenario_b = {
        "data": [1, 2, 3, 4, 5],
        "threshold": 0.70,
        "cumulative_cap": 0.50
    }
    
    try:
        response = requests.post(base_url, json=scenario_b, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 시나리오 B 성공: {result['summary']['blocks']}개 차단")
            print(f"   타임라인: {result['timeline']}")
        else:
            print(f"❌ 시나리오 B 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 시나리오 B 오류: {e}")
        return False
    
    # 시나리오 C: 누적캡 차단
    print("\n🧪 시나리오 C: 누적캡 차단 테스트")
    scenario_c = {
        "data": [10, 20, 30, 40, 50],
        "threshold": 0.30,
        "cumulative_cap": 0.50
    }
    
    try:
        response = requests.post(base_url, json=scenario_c, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 시나리오 C 성공: {result['summary']['cap_hits']}개 캡 히트")
            print(f"   타임라인: {result['timeline']}")
        else:
            print(f"❌ 시나리오 C 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 시나리오 C 오류: {e}")
        return False
    
    # 시나리오 D: 극단값 처리
    print("\n🧪 시나리오 D: 극단값 처리 테스트")
    scenario_d = {
        "data": [1e6, 1e-6, float('nan'), float('inf'), float('-inf')],
        "threshold": 0.30,
        "cumulative_cap": 0.50
    }
    
    try:
        response = requests.post(base_url, json=scenario_d, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 시나리오 D 성공: 극단값 정규화 완료")
            print(f"   타임라인: {result['timeline']}")
        else:
            print(f"❌ 시나리오 D 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 시나리오 D 오류: {e}")
        return False
    
    return True

def test_deterministic_replay():
    """결정적 재실행 테스트"""
    print("\n🔄 결정적 재실행 테스트")
    
    base_url = "http://localhost:5000/run"
    test_data = {
        "data": [1, 2, 3, 4, 5],
        "threshold": 0.30,
        "cumulative_cap": 0.50,
        "seed": 42
    }
    
    try:
        # 첫 번째 실행
        response1 = requests.post(base_url, json=test_data, timeout=10)
        if response1.status_code != 200:
            print(f"❌ 첫 번째 실행 실패: {response1.status_code}")
            return False
        
        result1 = response1.json()
        
        # 두 번째 실행 (동일한 시드)
        response2 = requests.post(base_url, json=test_data, timeout=10)
        if response2.status_code != 200:
            print(f"❌ 두 번째 실행 실패: {response2.status_code}")
            return False
        
        result2 = response2.json()
        
        # 결과 비교
        if (result1['timeline'] == result2['timeline'] and 
            result1['summary']['rules_executed'] == result2['summary']['rules_executed']):
            print("✅ 결정적 재실행 성공: 동일한 결과 재현")
            return True
        else:
            print("❌ 결정적 재실행 실패: 다른 결과 생성")
            print(f"   첫 번째: {result1['timeline']}")
            print(f"   두 번째: {result2['timeline']}")
            return False
            
    except Exception as e:
        print(f"❌ 결정적 재실행 오류: {e}")
        return False

def test_performance():
    """성능 테스트"""
    print("\n⚡ 성능 테스트")
    
    base_url = "http://localhost:5000/run"
    large_data = list(range(1000))  # 1000개 요소
    
    test_data = {
        "data": large_data,
        "threshold": 0.30,
        "cumulative_cap": 0.50,
        "seed": 42
    }
    
    try:
        start_time = time.time()
        response = requests.post(base_url, json=test_data, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            duration_ms = (end_time - start_time) * 1000
            result = response.json()
            
            print(f"✅ 성능 테스트 성공: {duration_ms:.1f}ms")
            print(f"   처리된 요소: {len(large_data)}개")
            print(f"   실행된 규칙: {result['summary']['rules_executed']}개")
            
            # P95 목표: 60ms
            if duration_ms < 60:
                print("✅ P95 목표 달성 (< 60ms)")
            else:
                print(f"⚠️ P95 목표 미달성: {duration_ms:.1f}ms > 60ms")
            
            return True
        else:
            print(f"❌ 성능 테스트 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 성능 테스트 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🌌 COSMOS-HGP V2-min+ 배포 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("헬스 체크", test_health),
        ("데모 시나리오", test_demo_scenarios),
        ("결정적 재실행", test_deterministic_replay),
        ("성능 테스트", test_performance)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 테스트 중...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 통과")
        else:
            print(f"❌ {test_name} 실패")
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! 배포 준비 완료")
        return 0
    else:
        print("⚠️ 일부 테스트 실패. 배포 전 수정 필요")
        return 1

if __name__ == "__main__":
    sys.exit(main())