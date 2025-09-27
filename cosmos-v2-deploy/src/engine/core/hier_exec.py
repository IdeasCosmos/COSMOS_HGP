#!/usr/bin/env python3
"""
Hierarchical Execution Engine - Core Implementation
COSMOS-HGP Open Source Version
"""

import time
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from .impact import ImpactCalculator
from .cap import CumulativeCapper
from .filters import InequalityFilter

@dataclass
class Rule:
    """Individual execution rule"""
    name: str
    function: callable
    layer: int = 1
    threshold: Optional[float] = None
    
    def execute(self, input_data: Any) -> tuple[Any, float]:
        """Execute rule and return result with impact"""
        start_time = time.time()
        
        try:
            result = self.function(input_data)
            impact = ImpactCalculator.calculate(input_data, result)
            
            duration = time.time() - start_time
            return result, impact, duration
            
        except Exception as e:
            duration = time.time() - start_time
            return input_data, 0.0, duration  # Return original data on error

@dataclass
class GroupDef:
    """Group definition for hierarchical execution"""
    name: str
    type: str  # "rule" or "group"
    threshold: Optional[float] = None
    children: Optional[List['GroupDef']] = None

@dataclass
class ExecutionResult:
    """Execution result with metadata"""
    output: Any
    impact: float
    path: str
    blocked: bool
    meta: Dict[str, Any]

class HierarchicalExecutor:
    """Core hierarchical execution engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "global_threshold": 0.30,
            "cumulative_cap": 0.50,
            "max_depth": 64,
            "epsilon": 1e-12
        }
        
        self.rules: Dict[str, Rule] = {}
        self.log_events: List[Dict] = []
        self.cumulative_velocity = 0.0
        
    def add_rule(self, rule: Rule):
        """Add a rule to the engine"""
        self.rules[rule.name] = rule
    
    def execute_group(self, group_def: GroupDef, input_data: Any, path: str = "") -> ExecutionResult:
        """Execute a group definition"""
        start_time = time.time()
        current_path = f"{path}/{group_def.name}" if path else group_def.name
        
        # Log entry event
        self._log_event("enter", group_def.name, current_path, 0.0)
        
        if group_def.type == "rule":
            # Execute single rule
            rule = self.rules.get(group_def.name)
            if not rule:
                return ExecutionResult(
                    output=input_data,
                    impact=0.0,
                    path=current_path,
                    blocked=True,
                    meta={"error": "rule_not_found"}
                )
            
            result, impact, duration = rule.execute(input_data)
            
            # Check threshold
            threshold = group_def.threshold or rule.threshold or self.config["global_threshold"]
            blocked = impact >= threshold
            
            # Update cumulative velocity
            if not blocked:
                self.cumulative_velocity = CumulativeCapper.update(
                    self.cumulative_velocity, impact
                )
            
            # Check cumulative cap
            if self.cumulative_velocity >= self.config["cumulative_cap"]:
                blocked = True
                self._log_event("cap_hit", group_def.name, current_path, impact)
            
            # Log exit event
            self._log_event("exit" if not blocked else "block", group_def.name, current_path, impact)
            
            return ExecutionResult(
                output=result if not blocked else input_data,
                impact=impact,
                path=current_path,
                blocked=blocked,
                meta={
                    "duration_ms": duration * 1000,
                    "threshold": threshold,
                    "cumulative": self.cumulative_velocity
                }
            )
        
        else:
            # Execute group (process children sequentially)
            current_data = input_data
            group_blocked = False
            
            if group_def.children:
                for child in group_def.children:
                    result = self.execute_group(child, current_data, current_path)
                    
                    if result.blocked:
                        group_blocked = True
                        break
                    
                    current_data = result.output
            
            duration = time.time() - start_time
            self._log_event("exit" if not group_blocked else "block", group_def.name, current_path, 0.0)
            
            return ExecutionResult(
                output=current_data,
                impact=0.0,
                path=current_path,
                blocked=group_blocked,
                meta={"duration_ms": duration * 1000}
            )
    
    def generate_timeline(self) -> str:
        """Generate ASCII timeline from log events"""
        timeline_parts = []
        
        for event in self.log_events:
            if event["type"] == "rule" and event["event"] == "exit":
                if event.get("blocked", False):
                    timeline_parts.append(f"[{event['node']} blocked: impact={event['impact']:.2f}]")
                else:
                    timeline_parts.append(event['node'])
            elif event["event"] == "cap_hit":
                timeline_parts.append("(subtree stop by cap)")
        
        return " → ".join(timeline_parts) if timeline_parts else "no_execution"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary"""
        rules_executed = len([e for e in self.log_events if e["type"] == "rule" and e["event"] == "exit"])
        blocks = len([e for e in self.log_events if e.get("blocked", False)])
        cap_hits = len([e for e in self.log_events if e["event"] == "cap_hit"])
        max_depth = max(len(e["path"].split("/")) for e in self.log_events) if self.log_events else 0
        total_duration = sum(e.get("duration_ms", 0) for e in self.log_events)
        
        return {
            "rules_executed": rules_executed,
            "blocks": blocks,
            "cap_hits": cap_hits,
            "max_depth": max_depth,
            "duration_ms": total_duration,
            "cumulative_velocity": self.cumulative_velocity
        }
    
    def _log_event(self, event_type: str, node: str, path: str, impact: float, blocked: bool = False):
        """Log execution event"""
        event = {
            "ts": time.time(),
            "path": path,
            "node": node,
            "type": "rule" if node in self.rules else "group",
            "event": event_type,
            "impact": impact,
            "blocked": blocked,
            "cumulative": self.cumulative_velocity
        }
        self.log_events.append(event)
        
        # Save to file
        self._save_log(event)
    
    def _save_log(self, event: Dict):
        """Save log event to file"""
        try:
            with open("/app/log/annotations.jsonl", "a") as f:
                f.write(json.dumps(event) + "\n")
        except:
            pass  # Ignore file write errors in demo
