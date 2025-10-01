#!/usr/bin/env python3
"""COSMOS-HGP Local Test Script"""

import sys

def test_basic_engine():
    """BasicEngine 기본 테스트"""
    print("=" * 50)
    print("COSMOS-HGP Local Test")
    print("=" * 50)
    
    try:
        # 1. Import cosmos package
        print("\n[1/4] Importing cosmos...")
        from cosmos import BasicEngine
        print("✅ Import successful")
        
        # 2. Create BasicEngine
        print("\n[2/4] Creating engine...")
        engine = BasicEngine()
        print("✅ Engine created")
        
        # 3. Execute with 3 simple rules
        print("\n[3/4] Executing with 3 rules...")
        data = [{"x": 1}, {"x": 2}, {"x": 3}]
        rules = [
            {"name": "rule1", "type": "normalize"},
            {"name": "rule2", "type": "scale"},
            {"name": "rule3", "type": "validate"}
        ]
        result = engine.run(data=data, rules=rules)
        print("✅ Execution completed")
        
        # 4. Display results
        print("\n[4/4] Results:")
        print(f"  Timeline: {result.get('timeline', [])}")
        print(f"  Blocks: {result.get('blocks', 0)}")
        print(f"  Output: {result.get('output', 'N/A')}")
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if test_basic_engine() else 1)
