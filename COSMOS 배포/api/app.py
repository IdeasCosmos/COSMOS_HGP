# /api/app.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json, pathlib, time, os
from typing import List, Dict, Any, Optional
import uvicorn

app = FastAPI(
    title="COSMOS Visualization API",
    description="COSMOS 시스템의 실시간 지표 및 시각화 데이터를 제공하는 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG = pathlib.Path("./log/annotations.jsonl")
VIZ = pathlib.Path("./viz_out")

@app.get("/")
async def root():
    """대시보드로 리다이렉트"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard")
async def dashboard():
    """시각화 대시보드"""
    dashboard_path = pathlib.Path("./dashboard.html")
    if dashboard_path.exists():
        return FileResponse(str(dashboard_path), media_type="text/html")
    else:
        return JSONResponse({
            "message": "COSMOS Visualization API",
            "version": "1.0.0",
            "endpoints": {
                "metrics": "/metrics/live",
                "events": "/events",
                "visualizations": "/viz/{name}",
                "health": "/health"
            }
        })

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "log_exists": LOG.exists(),
        "viz_dir_exists": VIZ.exists()
    }

@app.get("/metrics/live")
async def metrics_live():
    """실시간 지표를 반환합니다 (최근 1분 내 이벤트 기준)"""
    now = time.time()
    blocks = caps = 0
    p = []
    running = set()
    last_ts = 0
    total_events = 0
    
    if LOG.exists():
        try:
            with LOG.open(encoding='utf-8') as f:
                for line in f:
                    try:
                        e = json.loads(line.strip())
                        total_events += 1
                        ts = e.get("ts", 0) / 1000  # 밀리초를 초로 변환
                        last_ts = max(last_ts, ts)
                        
                        # 최근 1분 내 이벤트만 처리
                        if now - ts > 60:
                            continue
                            
                        k = e.get("kind", "")
                        if k == "block": 
                            blocks += 1
                        if k == "cap": 
                            caps += 1
                        if k in ("enter", "exit"): 
                            p.append(e.get("dur_ms", 0.0))
                        if k == "enter": 
                            running.add(e.get("path", ""))
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        print(f"이벤트 파싱 오류: {e}")
                        continue
        except Exception as e:
            print(f"로그 파일 읽기 오류: {e}")
            return JSONResponse(
                {"error": "로그 파일을 읽을 수 없습니다"}, 
                status_code=500
            )
    
    p95 = sorted(p)[int(0.95 * len(p))] if p else 0.0
    
    return {
        "p95_ms": round(p95, 2),
        "blocks": blocks,
        "caps": caps,
        "running_groups": len(running),
        "last_event_ts": last_ts,
        "total_events": total_events,
        "recent_events": len(p)
    }

@app.get("/events")
async def events(after: int = Query(0, description="시작 인덱스"), 
                limit: int = Query(200, description="최대 이벤트 수")):
    """이벤트 목록을 반환합니다 (페이지네이션 지원)"""
    out = []
    
    if not LOG.exists():
        return {"events": [], "next": 0, "total": 0}
    
    try:
        with LOG.open(encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i < after: 
                    continue
                try: 
                    out.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
                if len(out) >= limit: 
                    break
    except Exception as e:
        print(f"이벤트 로드 오류: {e}")
        return JSONResponse(
            {"error": "이벤트를 로드할 수 없습니다"}, 
            status_code=500
        )
    
    next_cursor = after + len(out)
    return {
        "events": out, 
        "next": next_cursor,
        "total": len(out),
        "has_more": len(out) == limit
    }

@app.get("/events/stats")
async def events_stats():
    """이벤트 통계를 반환합니다"""
    if not LOG.exists():
        return {"error": "로그 파일이 없습니다"}
    
    stats = {
        "total_events": 0,
        "by_kind": {},
        "by_layer": {},
        "impact_stats": {"min": 0, "max": 0, "avg": 0},
        "duration_stats": {"min": 0, "max": 0, "avg": 0}
    }
    
    impacts = []
    durations = []
    
    try:
        with LOG.open(encoding='utf-8') as f:
            for line in f:
                try:
                    e = json.loads(line.strip())
                    stats["total_events"] += 1
                    
                    # 종류별 통계
                    kind = e.get("kind", "unknown")
                    stats["by_kind"][kind] = stats["by_kind"].get(kind, 0) + 1
                    
                    # 레이어별 통계
                    layer = e.get("layer", 0)
                    if layer > 0:
                        stats["by_layer"][layer] = stats["by_layer"].get(layer, 0) + 1
                    
                    # 임팩트 통계
                    impact = e.get("impact")
                    if impact is not None:
                        impacts.append(impact)
                    
                    # 지속시간 통계
                    dur = e.get("dur_ms")
                    if dur is not None:
                        durations.append(dur)
                        
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        return JSONResponse(
            {"error": f"통계 생성 오류: {e}"}, 
            status_code=500
        )
    
    if impacts:
        stats["impact_stats"] = {
            "min": min(impacts),
            "max": max(impacts),
            "avg": sum(impacts) / len(impacts)
        }
    
    if durations:
        stats["duration_stats"] = {
            "min": min(durations),
            "max": max(durations),
            "avg": sum(durations) / len(durations)
        }
    
    return stats

@app.get("/viz/{name}")
async def viz(name: str):
    """시각화 파일을 반환합니다"""
    # 보안을 위해 파일명 검증
    if not name or ".." in name or "/" in name or "\\" in name:
        raise HTTPException(status_code=400, detail="잘못된 파일명입니다")
    
    p = VIZ / name
    if not p.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    
    # 파일 확장자에 따른 MIME 타입 설정
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.json': 'application/json',
        '.txt': 'text/plain'
    }
    
    suffix = p.suffix.lower()
    media_type = mime_types.get(suffix, 'application/octet-stream')
    
    return FileResponse(str(p), media_type=media_type)

@app.get("/viz")
async def list_viz():
    """사용 가능한 시각화 파일 목록을 반환합니다"""
    if not VIZ.exists():
        return {"files": []}
    
    files = []
    for file_path in VIZ.iterdir():
        if file_path.is_file():
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
    
    return {"files": sorted(files, key=lambda x: x["modified"], reverse=True)}

@app.get("/events/stats")
async def events_stats():
    """이벤트 통계를 반환합니다"""
    if not LOG.exists():
        return {"error": "로그 파일이 없습니다"}
    
    stats = {
        "total_events": 0,
        "by_kind": {},
        "by_layer": {},
        "impact_stats": {"min": 0, "max": 0, "avg": 0},
        "duration_stats": {"min": 0, "max": 0, "avg": 0}
    }
    
    impacts = []
    durations = []
    
    try:
        with LOG.open(encoding='utf-8') as f:
            for line in f:
                try:
                    e = json.loads(line.strip())
                    stats["total_events"] += 1
                    
                    # 종류별 통계
                    kind = e.get("kind", "unknown")
                    stats["by_kind"][kind] = stats["by_kind"].get(kind, 0) + 1
                    
                    # 레이어별 통계
                    layer = e.get("layer", 0)
                    if layer > 0:
                        stats["by_layer"][layer] = stats["by_layer"].get(layer, 0) + 1
                    
                    # 임팩트 통계
                    impact = e.get("impact")
                    if impact is not None:
                        impacts.append(impact)
                    
                    # 지속시간 통계
                    dur = e.get("dur_ms")
                    if dur is not None:
                        durations.append(dur)
                        
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        return JSONResponse(
            {"error": f"통계 생성 오류: {e}"}, 
            status_code=500
        )
    
    if impacts:
        stats["impact_stats"] = {
            "min": min(impacts),
            "max": max(impacts),
            "avg": sum(impacts) / len(impacts)
        }
    
    if durations:
        stats["duration_stats"] = {
            "min": min(durations),
            "max": max(durations),
            "avg": sum(durations) / len(durations)
        }
    
    return stats

@app.get("/en")
async def dashboard_en():
    """영문 대시보드를 반환합니다"""
    dashboard_path = Path("./dashboard_en.html")
    if dashboard_path.exists():
        return FileResponse(str(dashboard_path), media_type="text/html")
    else:
        return JSONResponse(
            {"error": "영문 대시보드 파일을 찾을 수 없습니다"}, 
            status_code=404
        )

@app.get("/benchmark-viewer")
async def benchmark_viewer():
    """벤치마크 결과 뷰어 페이지"""
    viewer_path = Path("./benchmark_viewer.html")
    if viewer_path.exists():
        return FileResponse(str(viewer_path), media_type="text/html")
    else:
        return JSONResponse(
            {"error": "벤치마크 뷰어 파일을 찾을 수 없습니다"}, 
            status_code=404
        )

@app.post("/run-benchmark/{benchmark_type}")
async def run_benchmark(benchmark_type: str):
    """벤치마크 실행"""
    try:
        import subprocess
        import asyncio
        
        if benchmark_type == "enhanced":
            result = subprocess.run(
                ["python", "enhanced_benchmark.py"], 
                capture_output=True, text=True, timeout=300
            )
        else:
            result = subprocess.run(
                ["python", "benchmark.py"], 
                capture_output=True, text=True, timeout=300
            )
        
        if result.returncode == 0:
            return {"success": True, "message": f"{benchmark_type} 벤치마크 완료"}
        else:
            return {"success": False, "error": result.stderr}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "벤치마크 시간 초과"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/benchmark-results/{filename}")
async def get_benchmark_result(filename: str):
    """벤치마크 결과 파일 반환"""
    file_path = Path(f"./{filename}")
    
    if filename.endswith('.png'):
        if file_path.exists():
            return FileResponse(str(file_path), media_type="image/png")
        else:
            return JSONResponse({"error": "파일을 찾을 수 없습니다"}, status_code=404)
    
    elif filename.endswith('.json'):
        if file_path.exists():
            return FileResponse(str(file_path), media_type="application/json")
        else:
            return JSONResponse({"error": "파일을 찾을 수 없습니다"}, status_code=404)
    
    else:
        return JSONResponse({"error": "지원하지 않는 파일 형식"}, status_code=400)

@app.get("/benchmark-files")
async def get_benchmark_files():
    """벤치마크 파일 목록 반환"""
    files = [
        {"name": "benchmark_report.png", "description": "기본 성능 리포트"},
        {"name": "enhanced_benchmark_report.png", "description": "향상된 성능 리포트"},
        {"name": "benchmark_results.json", "description": "기본 벤치마크 데이터"},
        {"name": "enhanced_benchmark_results.json", "description": "향상된 벤치마크 데이터"}
    ]
    
    # 실제 파일 존재 여부 확인
    existing_files = []
    for file_info in files:
        file_path = Path(f"./{file_info['name']}")
        if file_path.exists():
            file_info["exists"] = True
            file_info["size"] = file_path.stat().st_size
            file_info["modified"] = file_path.stat().st_mtime
        else:
            file_info["exists"] = False
        
        existing_files.append(file_info)
    
    return {"files": existing_files}

@app.post("/generate")
async def generate_visualizations():
    """시각화를 새로 생성합니다"""
    try:
        # viz 모듈을 동적으로 임포트하여 실행
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        from viz.log_to_map import main as generate_viz
        generate_viz()
        
        return {"message": "시각화가 성공적으로 생성되었습니다"}
    except Exception as e:
        return JSONResponse(
            {"error": f"시각화 생성 오류: {str(e)}"}, 
            status_code=500
        )

if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
