# /viz/log_to_map.py
import json, math, os, pathlib
from typing import List, Dict, Any, Tuple
import numpy as np
import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 비활성화
import matplotlib.pyplot as plt

LOG = pathlib.Path("./log/annotations.jsonl")
OUT = pathlib.Path("./viz_out"); OUT.mkdir(parents=True, exist_ok=True)

LAYER_NAMES = {1:"L1_QUANTUM",2:"L2_ATOMIC",3:"L3_MOLECULAR",4:"L4_COMPOUND",5:"L5_ORGANIC",6:"L6_ECOSYSTEM",7:"L7_COSMOS"}

def load_events() -> List[Dict[str,Any]]:
    """JSONL 로그 파일에서 이벤트를 로드하고 정렬합니다."""
    if not LOG.exists(): 
        print(f"로그 파일이 없습니다: {LOG}")
        return []
    
    ev = []
    with LOG.open(encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue
            try: 
                ev.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 오류: {e}")
                continue
    
    # 시간순 정렬
    ev.sort(key=lambda e: (e.get("ts", 0), e.get("path", "")))
    # 인덱스 부여
    for i, e in enumerate(ev): 
        e["_idx"] = i
    
    print(f"로드된 이벤트 수: {len(ev)}")
    return ev

def norm01(x: float) -> float:
    """값을 0-1 범위로 정규화합니다."""
    if x is None or math.isnan(x): 
        return 0.0
    return float(max(0.0, min(1.0, x)))

def make_heatmap(ev: List[Dict[str,Any]]):
    """레이어×시간 히트맵을 생성합니다."""
    if not ev: 
        print("이벤트가 없어 히트맵을 생성할 수 없습니다.")
        return None
    
    # 축: time index × layer
    T = ev[-1]["_idx"] + 1
    H = np.zeros((7, T), dtype=float)
    marks = []  # (idx, layer, symbol)
    
    for e in ev:
        k = e.get("kind", "")
        if k not in ("exit", "block", "cap", "error"): 
            continue
        
        idx = e["_idx"]
        layer = int(e.get("layer", 0) or 0)
        if layer < 1 or layer > 7: 
            continue
        
        imp = norm01(e.get("impact", 0.0))
        H[layer-1, idx] = imp
        
        if k == "block":   
            marks.append((idx, layer-1, "X"))
        elif k == "cap":   
            marks.append((idx, layer-1, "▮"))
        elif k == "error": 
            marks.append((idx, layer-1, "!"))

    plt.figure(figsize=(12, 3.5))
    plt.imshow(H, aspect="auto", interpolation="nearest", vmin=0, vmax=1, cmap='Reds')
    plt.yticks(range(7), [LAYER_NAMES[i] for i in range(1,8)], fontsize=8)
    plt.xticks([])
    cbar = plt.colorbar()
    cbar.set_label("impact (0..1)")
    
    for idx, ly, sym in marks:
        plt.text(idx, ly, sym, ha="center", va="center", fontsize=7, color="white")
    
    plt.title("Layer×Time Heatmap")
    out = OUT / "heatmap.png"
    plt.tight_layout()
    plt.savefig(out, dpi=160, bbox_inches='tight')
    plt.close()
    print(f"히트맵 생성: {out}")
    return str(out)

def make_strip_timeline(ev: List[Dict[str,Any]]):
    """스트립 타임라인을 생성합니다."""
    if not ev: 
        print("이벤트가 없어 타임라인을 생성할 수 없습니다.")
        return None
    
    # 각 이벤트를 점으로: x=순서, y=layer, color=impact, marker=kind
    kind_map = {"exit":"o", "block":"x", "cap":"s", "error":"^", "enter":"."}
    xs, ys, cs, ms = [], [], [], []
    
    for e in ev:
        idx = e["_idx"]
        layer = int(e.get("layer", 0) or 0)
        if layer < 1 or layer > 7: 
            continue
        
        xs.append(idx)
        ys.append(layer)
        cs.append(norm01(e.get("impact", 0.0)))
        ms.append(kind_map.get(e.get("kind", "exit"), "o"))

    plt.figure(figsize=(12, 2.8))
    for x, y, c, m in zip(xs, ys, cs, ms):
        plt.scatter([x], [y], c=[[c, 0, 0]], marker=m, s=15, alpha=0.7)
    
    plt.yticks(range(1, 8), [LAYER_NAMES[i] for i in range(1, 8)], fontsize=8)
    plt.xticks([])
    plt.title("Genome Strip Timeline (red=intense)")
    plt.xlabel("Event Index")
    plt.ylabel("Layer")
    
    out = OUT / "timeline.png"
    plt.tight_layout()
    plt.savefig(out, dpi=160, bbox_inches='tight')
    plt.close()
    print(f"타임라인 생성: {out}")
    return str(out)

def make_codon_bar(ev: List[Dict[str,Any]]):
    """코돈 빈도 막대그래프를 생성합니다."""
    codon_cnt = {}
    for e in ev:
        c = e.get("codon")
        if not c: 
            continue
        if len(c) == 3: 
            codon_cnt[c] = codon_cnt.get(c, 0) + 1
    
    if not codon_cnt: 
        print("코돈 데이터가 없어 막대그래프를 생성할 수 없습니다.")
        return None
    
    items = sorted(codon_cnt.items(), key=lambda x: x[1], reverse=True)[:20]
    labels, vals = zip(*items)
    
    plt.figure(figsize=(12, 3))
    bars = plt.bar(labels, vals, color='skyblue', alpha=0.7)
    plt.xticks(rotation=45, fontsize=8)
    plt.title("Top Codon Patterns")
    plt.xlabel("Codon")
    plt.ylabel("Frequency")
    
    # 값 표시
    for bar, val in zip(bars, vals):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                str(val), ha='center', va='bottom', fontsize=6)
    
    out = OUT / "codon_bar.png"
    plt.tight_layout()
    plt.savefig(out, dpi=160, bbox_inches='tight')
    plt.close()
    print(f"코돈 막대그래프 생성: {out}")
    return str(out)

def make_summary_stats(ev: List[Dict[str,Any]]):
    """요약 통계를 생성합니다."""
    if not ev:
        return None
    
    stats = {
        "total_events": len(ev),
        "layers": {},
        "kinds": {},
        "avg_impact": 0.0,
        "max_impact": 0.0,
        "duration_range": (0, 0)
    }
    
    impacts = []
    durations = []
    
    for e in ev:
        # 레이어별 카운트
        layer = e.get("layer", 0)
        if layer > 0:
            stats["layers"][layer] = stats["layers"].get(layer, 0) + 1
        
        # 종류별 카운트
        kind = e.get("kind", "unknown")
        stats["kinds"][kind] = stats["kinds"].get(kind, 0) + 1
        
        # 임팩트 통계
        impact = e.get("impact", 0.0)
        if impact is not None:
            impacts.append(impact)
            stats["max_impact"] = max(stats["max_impact"], impact)
        
        # 지속시간 통계
        dur = e.get("dur_ms", 0.0)
        if dur is not None:
            durations.append(dur)
    
    if impacts:
        stats["avg_impact"] = sum(impacts) / len(impacts)
    
    if durations:
        stats["duration_range"] = (min(durations), max(durations))
    
    # 통계를 파일로 저장
    out = OUT / "summary_stats.json"
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"요약 통계 생성: {out}")
    return str(out)

def main():
    """메인 실행 함수"""
    print("=== COSMOS 시각화 도구 시작 ===")
    
    # 이벤트 로드
    ev = load_events()
    if not ev:
        print("이벤트가 없습니다. 샘플 데이터를 생성합니다...")
        # 샘플 데이터 생성
        ev = create_sample_events()
        if not ev:
            print("샘플 데이터 생성에 실패했습니다.")
            return
    
    # 시각화 생성
    print("\n시각화 생성 중...")
    a = make_heatmap(ev)
    b = make_strip_timeline(ev)
    c = make_codon_bar(ev)
    d = make_summary_stats(ev)
    
    print(f"\n생성 완료:")
    print(f"  - 히트맵: {a}")
    print(f"  - 타임라인: {b}")
    print(f"  - 코돈 막대그래프: {c}")
    print(f"  - 요약 통계: {d}")

def create_sample_events():
    """테스트용 샘플 이벤트를 생성합니다."""
    import time
    import random
    
    sample_events = []
    base_time = time.time() * 1000  # 밀리초
    
    for i in range(100):
        event = {
            "ts": base_time + i * 100,
            "path": f"A/B/C{i%10}",
            "node": f"C{i%10}",
            "kind": random.choice(["enter", "exit", "block", "cap", "error"]),
            "impact": random.uniform(0.1, 0.9),
            "threshold": 0.3,
            "cum": random.uniform(0.2, 0.8),
            "layer": random.randint(1, 7),
            "dur_ms": random.uniform(0.5, 5.0),
            "reason": f"sample_reason_{i}",
            "codon": random.choice(["ATG", "TAA", "TAG", "TGA", "GCT", "GCC", "GCA", "GCG"]) if random.random() > 0.7 else None
        }
        sample_events.append(event)
    
    # 샘플 데이터를 로그 파일에 저장
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, 'w', encoding='utf-8') as f:
        for event in sample_events:
            f.write(json.dumps(event) + '\n')
    
    print(f"샘플 데이터 생성: {LOG}")
    return sample_events

if __name__ == "__main__":
    main()
