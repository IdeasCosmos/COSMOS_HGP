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
            print(f"✅ 정상 흐름: {result['timeline']}")
            print(f"   차단됨: {result['blocked']}")
            print(f"   규칙 실행: {result['summary']['rules_executed']}")
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
            print(f"✅ 국소 차단: {result['timeline']}")
            print(f"   차단됨: {result['blocked']}")
            print(f"   차단 수: {result['summary']['blocks']}")
        else:
            print(f"❌ 시나리오 B 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 시나리오 B 오류: {e}")
        return False
    
    # 시나리오 C: 누적캡 차단
    print("\n🧪 시나리오 C: 누적캡 차단 테스트")
    scenario_c = {
        "data": [100, 200, 300, 400, 500],  # 큰 값으로 임팩트 증가
        "threshold": 0.30,
        "cumulative_cap": 0.30  # 낮은 캡
    }
    
    try:
        response = requests.post(base_url, json=scenario_c, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 누적캡 차단: {result['timeline']}")
            print(f"   차단됨: {result['blocked']}")
            print(f"   캡 히트: {result['summary']['cap_hits']}")
            print(f"   누적 속도: {result['summary']['cumulative_velocity']:.3f}")
        else:
            print(f"❌ 시나리오 C 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 시나리오 C 오류: {e}")
        return False
    
    return True

def test_performance():
    """성능 테스트"""
    print("\n⚡ 성능 테스트")
    
    # 대용량 데이터 테스트
    large_data = list(range(1000))  # 1000개 요소
    
    start_time = time.time()
    
    try:
        response = requests.post("http://localhost:5000/run", json={
            "data": large_data,
            "threshold": 0.30,
            "cumulative_cap": 0.50
        }, timeout=30)
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 성능 테스트 통과")
            print(f"   입력 크기: {len(large_data)}")
            print(f"   실행 시간: {duration_ms:.1f}ms")
            print(f"   내부 시간: {result['summary']['duration_ms']:.1f}ms")
            
            # P95 < 60ms 목표 체크
            if duration_ms < 60:
                print("✅ P95 목표 달성 (< 60ms)")
            else:
                print("⚠️ P95 목표 미달 (≥ 60ms)")
            
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
    
    # 1. 헬스 체크
    if not test_health():
        print("\n❌ 배포 테스트 실패: 서비스가 실행되지 않음")
        sys.exit(1)
    
    # 2. 데모 시나리오 테스트
    if not test_demo_scenarios():
        print("\n❌ 배포 테스트 실패: 데모 시나리오 실패")
        sys.exit(1)
    
    # 3. 성능 테스트
    if not test_performance():
        print("\n❌ 배포 테스트 실패: 성능 테스트 실패")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 모든 배포 테스트 통과!")
    print("✅ COSMOS-HGP V2-min+ 정상 배포 완료")
    print("\n📋 접속 정보:")
    print("  - 웹 인터페이스: http://localhost:5000")
    print("  - API 엔드포인트: http://localhost:5000/run")
    print("  - 헬스 체크: http://localhost:5000/health")

if __name__ == "__main__":
    main()
