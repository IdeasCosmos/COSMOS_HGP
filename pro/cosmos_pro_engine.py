#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Literal, Optional, Protocol, Tuple, Union
from time import perf_counter
from datetime import datetime
from hashlib import sha256
import json, math, os
try:
    import numpy as np
except Exception:
    # 최소 폴백
    class _NP:
        def array(self, x, dtype=float): return list(map(float, x)) if isinstance(x,(list,tuple)) else [float(x)]
    np=_NP()  # type: ignore

# ========= 외부 모듈 연동(있으면 사용) =========
try:
    from core_modules.velocity import calculate_layer_threshold as _ext_threshold
    from core_modules.velocity import calc_velocity as _ext_velocity
    from core_modules.velocity import calc_cumulative as _ext_cumulative
except Exception:
    _ext_threshold=_ext_velocity=_ext_cumulative=None

try:
    from core_modules.codon import (
        analyze_python_code as _ext_analyze,
        encode_instruction as _ext_encode,
        decode_codon as _ext_decode,
        codon_to_layer as _ext_codon2layer,
    )
except Exception:
    _ext_analyze=_ext_encode=_ext_decode=_ext_codon2layer=None

# ========= 기본 타입 =========
class Layer(Enum):
    L1_QUANTUM =(1,"Quantum", 0.12,"subatomic")
    L2_ATOMIC  =(2,"Atomic",  0.20,"atomic")
    L3_MOLECULAR=(3,"Molecular",0.26,"molecular")
    L4_COMPOUND=(4,"Compound",0.30,"compound")
    L5_ORGANIC =(5,"Organic", 0.33,"organic")
    L6_ECOSYSTEM=(6,"Ecosystem",0.35,"ecosystem")
    L7_COSMOS  =(7,"Cosmos",  0.38,"cosmos")
    def __init__(self, lv, name, th, desc):
        self.level=lv; self.display_name=name; self.base_threshold=th; self.description=desc

class DualityMode(Enum):
    STABILITY=auto(); INNOVATION=auto(); ADAPTIVE=auto()

class FlowDirection(Enum):
    TOP_DOWN=auto(); BOTTOM_UP=auto(); BIDIRECTIONAL=auto()

class ExecutionStatus(Enum):
    PENDING="pending"; RUNNING="running"; SUCCESS="success"; BLOCKED="blocked"; FAILED="failed"

@dataclass
class VelocityConfig:
    mode: DualityMode = DualityMode.STABILITY
    base_threshold: float = 0.30
    cumulative_cap: float = 0.50
    butterfly_factor: float = 1.0
    layer_multipliers: Dict[Layer,float]=field(default_factory=dict)

@dataclass
class CodonAnalysisResult:
    codons: List[str]; instruction_types: List[str]
    layer_distribution: Dict[Layer,int]; complexity_score: float
    macro_sequences: List[Dict[str,Any]]; metadata: Dict[str,Any]=field(default_factory=dict)

@dataclass
class PredictionResult:
    cascade_probability: float; risk_level: Literal["LOW","MODERATE","HIGH","CRITICAL"]
    recommendations: List[str]; confidence: float; should_block: bool
    alternative_path: Optional[str]=None

@dataclass
class ExecutionMetrics:
    rule_key: str; layer: Layer; start_time: float; end_time: float; duration_ms: float
    velocity: float; threshold: float; status: ExecutionStatus; input_hash: str; output_hash: str
    error: Optional[str]=None

@dataclass
class AnnotationEvent:
    timestamp: datetime; event_type: str
    level: Literal["DEBUG","INFO","WARNING","ERROR","CRITICAL"]
    rule_key: str; layer: Layer; message: str; metadata: Dict[str,Any]=field(default_factory=dict)

class VelocityCalculator(Protocol):
    def calculate_impact(self,before:np.ndarray,after:np.ndarray)->float: ...
    def check_threshold(self,layer:Layer,velocity:float)->Tuple[bool,float]: ...
    def calculate_cumulative(self,velocities:List[float])->float: ...

class CodonAnalyzer(Protocol):
    def analyze_code(self,code:str)->CodonAnalysisResult: ...
    def encode_instruction(self,instruction:str)->str: ...
    def decode_codon(self,codon:str)->str: ...

class CascadePredictor(Protocol):
    def predict_cascade(self,input_data:np.ndarray,group:str)->PredictionResult: ...
    def record_execution(self,input_data:np.ndarray,result:Dict)->None: ...
    def get_risk_assessment(self,input_data:np.ndarray)->Dict[str,Any]: ...

class ExecutionMonitor(Protocol):
    def record_event(self,event:AnnotationEvent)->None: ...
    def get_statistics(self)->Dict[str,Any]: ...
    def flush_buffer(self)->None: ...

@dataclass
class Rule:
    key:str; function:Callable[[Any],Any]; layer:Layer
    threshold: Optional[float]=None; dependencies: List[str]=field(default_factory=list)
    fallback_rule: Optional[str]=None; is_critical: bool=False; metadata: Dict[str,Any]=field(default_factory=dict)

@dataclass
class RuleGroup:
    name:str; structure:List[Union[str,List]]; metadata:Dict[str,Any]=field(default_factory=dict)

# ========= 유틸 =========
_CODONS=[a+b+c for a in "ATGC" for b in "ATGC" for c in "ATGC"]
def _sh(obj:Any)->str: 
    try: return sha256(repr(obj).encode("utf-8")).hexdigest()[:16]
    except Exception: return sha256(str(obj).encode("utf-8")).hexdigest()[:16]
def _to_np(x:Any)->np.ndarray:
    try:
        if isinstance(x,(list,tuple)): return np.array(x,dtype=float)
        if hasattr(x,"__iter__") and not isinstance(x,(str,bytes)): return np.array(list(x),dtype=float)
        return np.array([x],dtype=float)
    except Exception: return np.array([0.0],dtype=float)

def _mode_mult(mode:DualityMode,bf:float)->float:
    if mode is DualityMode.STABILITY: return 0.7
    if mode is DualityMode.INNOVATION: return 2.2
    return max(0.6,min(1.6,1.0 + 0.5*(bf-1.0)))

def _simple_velocity(before:np.ndarray,after:np.ndarray)->float:
    try:
        b=before.astype(float); a=after.astype(float)
        if len(b)!=len(a): 
            m=min(len(b),len(a)); b=b[:m]; a=a[:m]
        num=float(np.linalg.norm(a-b)); den=float(np.linalg.norm(b)+1e-9)
        v=1.0-math.exp(-num/(den+1e-9))
        return max(0.0,min(1.0,v))
    except Exception: return 0.0

def _cumulative(vs:List[float])->float:
    p=1.0
    for v in vs: p*= (1.0 - max(0.0,min(1.0,v)))
    return max(0.0,min(1.0,1.0-p))

def _risk_level(p:float)->str:
    return "CRITICAL" if p>=0.8 else "HIGH" if p>=0.6 else "MODERATE" if p>=0.3 else "LOW"

# ========= 기본 모니터/예측 폴백 =========
class _LocalMonitor:
    def __init__(self): self.buf:List[AnnotationEvent]=[]
    def record_event(self,event:AnnotationEvent)->None: self.buf.append(event)
    def get_statistics(self)->Dict[str,Any]:
        by_level={k:0 for k in ["DEBUG","INFO","WARNING","ERROR","CRITICAL"]}
        for e in self.buf: by_level[e.level]+=1
        return {"count":len(self.buf),"by_level":by_level}
    def flush_buffer(self)->None: self.buf.clear()

class _HeuristicPredictor:
    def predict_cascade(self,input_data:np.ndarray,group:str)->PredictionResult:
        x=_to_np(input_data); var=float(np.var(x)); mean=float(np.mean(x) if len(x)>0 else 0.0)
        p=max(0.0,min(1.0,0.5*math.tanh(var)+0.3*abs(mean)/(abs(mean)+1.0)))
        rl=_risk_level(p)
        rec=["bypass group" if p>0.6 else "proceed","lower threshold" if p>0.6 else "monitor"]
        return PredictionResult(p, rl, rec, confidence=0.65, should_block=p>0.6, alternative_path=None)
    def record_execution(self,input_data:np.ndarray,result:Dict)->None: return
    def get_risk_assessment(self,input_data:np.ndarray)->Dict[str,Any]:
        pr=self.predict_cascade(input_data,"_")
        return {"p":pr.cascade_probability,"risk":pr.risk_level}

# ========= 메인 엔진 구현 =========
class CosmosPROEngine:
    def __init__(
        self,
        rules: List[Rule],
        groups: Dict[str,RuleGroup],
        config: VelocityConfig,
        velocity_calculator: Optional[VelocityCalculator]=None,
        codon_analyzer: Optional[CodonAnalyzer]=None,
        cascade_predictor: Optional[CascadePredictor]=None,
        execution_monitor: Optional[ExecutionMonitor]=None,
    ):
        self.rules={r.key:r for r in rules}
        self.groups=groups
        self.config=config
        self.current_mode=config.mode
        self.current_direction=FlowDirection.TOP_DOWN
        self.velocity_calculator=velocity_calculator
        self.codon_analyzer=codon_analyzer
        self.cascade_predictor=cascade_predictor or _HeuristicPredictor()
        self.execution_monitor=execution_monitor or _LocalMonitor()
        self.execution_history:List[Dict[str,Any]]=[]
        self._events:List[AnnotationEvent]=[]

    # ---- 1. 속도 ----
    def calculate_velocity(self, layer:Layer, before:np.ndarray, after:np.ndarray)->float:
        if self.velocity_calculator: 
            return max(0.0,min(1.0,self.velocity_calculator.calculate_impact(before,after)))
        if _ext_velocity: 
            try: return max(0.0,min(1.0,_ext_velocity(before,after)))
            except Exception: pass
        return _simple_velocity(before,after)

    def check_velocity_threshold(self, layer:Layer, velocity:float)->Tuple[bool,float]:
        th=self.get_effective_threshold(layer)
        return (velocity>=th, th)

    def calculate_cumulative_velocity(self, velocities:List[float])->float:
        if self.velocity_calculator: return self.velocity_calculator.calculate_cumulative(velocities)
        if _ext_cumulative:
            try: return max(0.0,min(1.0,_ext_cumulative(velocities)))
            except Exception: pass
        return _cumulative(velocities)

    def get_effective_threshold(self, layer:Layer, mode:Optional[DualityMode]=None)->float:
        m=mode or self.current_mode
        base=_ext_threshold(layer) if _ext_threshold else layer.base_threshold
        mult=_mode_mult(m,self.config.butterfly_factor)*self.config.layer_multipliers.get(layer,1.0)
        eff=max(0.0,min(1.0, base*mult))
        return max(0.0,min(1.0, eff if eff>0 else self.config.base_threshold))

    # ---- 2. 코돈 ----
    def analyze_codon(self, code:str, include_macros:bool=True)->CodonAnalysisResult:
        if self.codon_analyzer: return self.codon_analyzer.analyze_code(code)
        if _ext_analyze:
            try: return _ext_analyze(code)
            except Exception: pass
        # 폴백 간이 분석
        toks=[t for t in ["def","for","if","return","class","import"] if t in code]
        cods=[_CODONS[hash(t)%64] for t in toks] or ["AAA"]
        dist={l:0 for l in Layer}; dist[Layer.L1_QUANTUM]=len(cods)
        return CodonAnalysisResult(cods, toks, dist, complexity_score=min(1.0,len(toks)/10.0),
                                   macro_sequences=[], metadata={"fallback":True})

    def encode_rule_to_codon(self, rule:Rule)->str:
        if _ext_encode:
            try: return _ext_encode(rule.key)
            except Exception: pass
        return _CODONS[hash(rule.key)%64]

    def decode_codon_to_instruction(self, codon:str)->str:
        if _ext_decode:
            try: return _ext_decode(codon)
            except Exception: pass
        return {"AAA":"FUNC_DEF","TAA":"ASSIGN"}.get(codon,"INSTR")

    def get_layer_from_codon(self, codon:str)->Layer:
        if _ext_codon2layer:
            try: return _ext_codon2layer(codon)
            except Exception: pass
        head=codon[0] if codon else "A"
        return { "A":Layer.L1_QUANTUM,"T":Layer.L3_MOLECULAR,"G":Layer.L5_ORGANIC,"C":Layer.L7_COSMOS }.get(head,Layer.L1_QUANTUM)

    # ---- 3. 예측 ----
    def predict_cascade(self, input_data:np.ndarray, group_name:str)->PredictionResult:
        return self.cascade_predictor.predict_cascade(_to_np(input_data), group_name)

    def predict_and_block(self, input_data:np.ndarray, group_name:str, auto_block:bool=True)->Tuple[bool,PredictionResult]:
        pr=self.predict_cascade(input_data, group_name)
        if auto_block and pr.should_block:
            self._note("_predict","WARNING",f"blocked by predictor p={pr.cascade_probability:.2f}", rule_key=group_name, layer=Layer.L7_COSMOS)
            return True, pr
        return False, pr

    def update_prediction_model(self, execution_result:Dict[str,Any])->None:
        try:
            self.cascade_predictor.record_execution(_to_np(execution_result.get("input",[0])), execution_result)
        except Exception: pass

    # ---- 4. 모니터 ----
    def monitor_execution(self, rule_key:str, event_type:str, level:Literal["DEBUG","INFO","WARNING","ERROR","CRITICAL"], message:str, **metadata)->None:
        evt=AnnotationEvent(datetime.utcnow(), event_type, level, rule_key, metadata.get("layer",Layer.L1_QUANTUM), message, metadata)
        self.execution_monitor.record_event(evt); self._events.append(evt)

    def get_monitoring_statistics(self)->Dict[str,Any]: return self.execution_monitor.get_statistics()
    def flush_monitoring_buffer(self)->None: self.execution_monitor.flush_buffer()

    # ---- 5. 모드 ----
    def switch_duality_mode(self, mode:DualityMode, reason:str="")->None:
        old=self.current_mode; self.current_mode=mode
        self._note("mode_switch","INFO",f"{old.name} -> {mode.name} {('('+reason+')') if reason else ''}", rule_key="_system", layer=Layer.L7_COSMOS)

    def get_mode_philosophy(self, mode:Optional[DualityMode]=None)->Dict[str,Any]:
        m=mode or self.current_mode
        mult=_mode_mult(m,self.config.butterfly_factor)
        return {"mode":m.name,"threshold_multiplier":mult,"butterfly_factor":self.config.butterfly_factor}

    # ---- 6. 흐름 ----
    def enable_bidirectional(self, direction:FlowDirection)->None:
        self.current_direction=direction
        self._note("direction","INFO",direction.name, rule_key="_system", layer=Layer.L7_COSMOS)

    def execute_top_down(self, group_name:str, input_data:Any)->Dict[str,Any]:
        grp=self._get_group(group_name); data=input_data; metrics=[]
        executed=set(); blocked_any=False; velocities=[]
        for key in self._flatten(grp.structure):
            rule=self._get_rule(key)
            if not self._deps_ok(rule, executed): continue
            before=_to_np(data); t0=perf_counter(); status=ExecutionStatus.RUNNING; err=None
            try:
                out=rule.function(data)
                after=_to_np(out); v=self.calculate_velocity(rule.layer,before,after)
                blocked,th=self.check_velocity_threshold(rule.layer,v)
                velocities.append(v)
                status=ExecutionStatus.BLOCKED if blocked else ExecutionStatus.SUCCESS
                if blocked and rule.is_critical: blocked_any=True
                data = data if (blocked and rule.is_critical) else out
            except Exception as e:
                status=ExecutionStatus.FAILED; err=str(e)
                if rule.fallback_rule and rule.fallback_rule in self.rules:
                    try: data=self.rules[rule.fallback_rule].function(data); status=ExecutionStatus.SUCCESS
                    except Exception as e2: err=f"{err}; fallback:{e2}"
            t1=perf_counter()
            met=ExecutionMetrics(rule.key, rule.layer, t0, t1, (t1-t0)*1000.0, locals().get('v',0.0),
                                 locals().get('th',self.get_effective_threshold(rule.layer)),
                                 status, _sh(before.tolist() if hasattr(before,"tolist") else before),
                                 _sh(_to_np(data).tolist() if hasattr(np,"array") else data), err)
            metrics.append(met); executed.add(rule.key)
            self._note("rule", "INFO" if status==ExecutionStatus.SUCCESS else "WARNING", status.value, rule_key=rule.key, layer=rule.layer, v=locals().get('v',0.0))
            if blocked_any: break
        agg=self.calculate_cumulative_velocity(velocities) if velocities else 0.0
        return {"success": not blocked_any, "output": data, "metrics":[m.__dict__ for m in metrics], "cumulative_velocity":agg}

    def execute_bottom_up(self, signal_data:Any, start_layer:Layer=Layer.L1_QUANTUM)->Dict[str,Any]:
        # 단순: 낮은 레이어 우선
        order=sorted(self.rules.values(), key=lambda r:r.layer.level)
        data=signal_data; metrics=[]; velocities=[]
        for rule in order:
            before=_to_np(data); t0=perf_counter(); err=None
            try:
                out=rule.function(data); after=_to_np(out)
                v=self.calculate_velocity(rule.layer,before,after); blocked,th=self.check_velocity_threshold(rule.layer,v)
                velocities.append(v); status=ExecutionStatus.BLOCKED if blocked else ExecutionStatus.SUCCESS
                data = data if blocked else out
            except Exception as e:
                status=ExecutionStatus.FAILED; err=str(e)
            t1=perf_counter()
            metrics.append(ExecutionMetrics(rule.key, rule.layer, t0,t1,(t1-t0)*1000.0, locals().get('v',0.0),
                                            locals().get('th',self.get_effective_threshold(rule.layer)), status, _sh(before), _sh(_to_np(data)), err).__dict__)
        return {"success":True, "output":data, "metrics":metrics, "cumulative_velocity":self.calculate_cumulative_velocity(velocities) if velocities else 0.0}

    def execute_bidirectional(self, group_name:str, input_data:Any)->Dict[str,Any]:
        top=self.execute_top_down(group_name,input_data)
        bot=self.execute_bottom_up(top["output"])
        merged={"success": top["success"] and bot["success"], "output": bot["output"],
                "top_down": top, "bottom_up": bot}
        return merged

    # ---- 7. 통합 ----
    def execute_with_full_integration(self, group_name:str, input_data:Any, enable_prediction:bool=True, enable_monitoring:bool=True)->Dict[str,Any]:
        codon=None
        try:
            codon=self.analyze_codon(json.dumps(input_data))  # 간단 표본화
        except Exception: pass
        if enable_prediction:
            blk, pr=self.predict_and_block(_to_np(input_data), group_name, auto_block=True)
            if blk:
                out={"success":False,"blocked_by_predictor":True,"prediction":pr.__dict__,"codon_analysis":codon.__dict__ if codon else None}
                self.execution_history.append(out); return out
        if self.current_direction==FlowDirection.BOTTOM_UP:
            res=self.execute_bottom_up(input_data)
        elif self.current_direction==FlowDirection.BIDIRECTIONAL:
            res=self.execute_bidirectional(group_name,input_data)
        else:
            res=self.execute_top_down(group_name,input_data)
        if enable_monitoring:
            self._note("exec","INFO","completed", rule_key=group_name, layer=Layer.L7_COSMOS, success=res.get("success"))
        if codon: res["codon_analysis"]=codon.__dict__
        self.execution_history.append(res); return res

    # ---- 8. 상태/관리 ----
    def get_comprehensive_status(self)->Dict[str,Any]:
        return {
            "mode": self.current_mode.name,
            "direction": self.current_direction.name,
            "history_count": len(self.execution_history),
            "monitoring": self.get_monitoring_statistics(),
        }

    def reset_statistics(self)->None:
        self.execution_history.clear(); self.flush_monitoring_buffer(); self._events.clear()

    def export_execution_report(self, filepath:str, format:Literal["json","yaml","csv"]="json")->None:
        data=self.execution_history
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        if format=="json":
            with open(filepath,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
        elif format=="yaml":
            try:
                import yaml
                with open(filepath,"w",encoding="utf-8") as f: yaml.safe_dump(data,f,sort_keys=False,allow_unicode=True)
            except Exception: 
                with open(filepath,"w",encoding="utf-8") as f: json.dump({"warning":"yaml_unavailable","data":data},f,ensure_ascii=False,indent=2)
        elif format=="csv":
            import csv
            with open(filepath,"w",newline="",encoding="utf-8") as f:
                w=csv.writer(f); w.writerow(["index","success","keys"])
                for i,it in enumerate(data): w.writerow([i, it.get("success"), ";".join(it.keys())])
        else:
            raise ValueError("unsupported format")

    # ========= 내부 헬퍼 =========
    def _get_group(self,name:str)->RuleGroup:
        if name not in self.groups: raise KeyError(f"group not found: {name}")
        return self.groups[name]
    def _get_rule(self,key:str)->Rule:
        if key not in self.rules: raise KeyError(f"rule not found: {key}")
        return self.rules[key]
    def _flatten(self,struct:List[Union[str,List]])->List[str]:
        out:List[str]=[]
        for x in struct:
            if isinstance(x,list): out.extend(self._flatten(x))
            else: out.append(str(x))
        return out
    def _deps_ok(self,rule:Rule, done:set)->bool:
        return all(d in done for d in rule.dependencies)
    def _note(self,etype:str, lvl:str, msg:str, *, rule_key:str, layer:Layer, **meta):
        try: self.monitor_execution(rule_key, etype, lvl, msg, layer=layer, **meta)
        except Exception: pass

# ======= 간단 사용 예시(주석 처리) =======
# if __name__ == "__main__":
#     def r1(x): return [v*2 for v in x]
#     def r2(x): return [v+1 for v in x]
#     rules=[Rule("double", r1, Layer.L2_ATOMIC), Rule("add", r2, Layer.L3_MOLECULAR)]
#     group=RuleGroup("main", ["double","add"])
#     eng=CosmosPROEngine(rules, {"main":group}, VelocityConfig())
#     print(eng.execute_with_full_integration("main",[1,2,3]))
