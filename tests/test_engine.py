import pytest
from cosmos.engine import BasicEngine

def test_basic_execution():
    engine = BasicEngine()
    rules = [{"type": "simple", "condition": "x > 0"}]
    data = [{"x": 1}]
    result = engine.run(data=data, rules=rules)
    assert result["output"] is not None

def test_blocking():
    engine = BasicEngine()
    rules = [{"type": "block", "condition": "x < 1"}]
    data = [{"x": 0.05}]
    result = engine.run(data=data, rules=rules, threshold=0.1)
    assert result["blocks"] > 0

def test_cumulative_cap():
    engine = BasicEngine()
    rules = [{"type": "cumulative", "condition": "sum > cap"}]
    data = [{"x": 0.15}, {"x": 0.15}]
    result = engine.run(data=data, rules=rules, cumulative_cap=0.2)
    assert "CAP" in result["timeline"]

def test_nested_rules():
    engine = BasicEngine()
    rules = [{"type": "nested", "conditions": [["x > 0", "y < 1"]]}]
    data = [{"x": 1, "y": 0}]
    result = engine.run(data=data, rules=rules)
    assert len(result["timeline"]) > 0

def test_empty_data():
    engine = BasicEngine()
    with pytest.raises(ValueError):
        engine.run(data=[], rules=[{"type": "simple"}])

