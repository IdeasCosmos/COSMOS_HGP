#!/usr/bin/env python3
"""
COSMOS-HGP PRO API Server (완전 통합 버전)
모든 PRO 기능 + 신규 4대 기능

기본 PRO 기능 (11개):
- DNA 코돈, 7계층 속도, 이중성 모드, 양방향, 예측, 자가치유, 병렬, 텔레메트리

신규 고급 기능 (4개):
- 자가 디버깅: COSMOS 스스로 테스트
- CSV 분석: 모든 CSV 유형 자동 분석
- 웹로그 분석: 공격 패턴 탐지
- 도메인 컨설팅: AIOps/Finance/Healthcare 전문 분석
"""

import sys
import numpy as np
import pandas as pd
import json
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, status, Depends, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# === 내부 모듈 임포트 ===
try:
    from auth import verify_api_key, API_KEY
    from rate_limit import rate_limiter
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    API_KEY = "test_key_12345"
    print("⚠️  Warning: auth.py not available")

try:
    from advanced_features import (
        run_selftest, analyze_csv_universal, 
        analyze_weblog, domain_consulting
    )
    ADVANCED_FEATURES_AVAILABLE = True
    print("✅ Advanced Features loaded")
except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False
    print("⚠️  Warning: advanced_features.py not available")

try:
    from cosmos_pro_engine import (
        CosmosPROEngine, Rule, RuleGroup, VelocityConfig,
        Layer, DualityMode, FlowDirection
    )
    ENGINE_AVAILABLE = True
except ImportError:
    ENGINE_AVAILABLE = False
    print("⚠️  Warning: cosmos_pro_engine.py not available")

try:
    sys.path.append('..')
    from core_modules.velocity import VelocityPolicyManager
    from core_modules.codon import CodonRegistry
    from core_modules.prediction import CascadePredictor
    from core_modules.annotation import AnnotationSystem
    CORE_MODULES_AVAILABLE = True
except ImportError:
    CORE_MODULES_AVAILABLE = False
    print("⚠️  Warning: core_modules not available")

# === FastAPI 앱 설정 ===
app = FastAPI(
    title="COSMOS-HGP PRO API",
    version="2.0",
    description="통합 PRO API 서버 - 10가지 PRO 기능 제공"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Pydantic 모델 ===
class CodonInput(BaseModel):
    code: str = Field(..., description="Python 소스 코드")

class VelocityInput(BaseModel):
    layer: int = Field(..., ge=1, le=7, description="계층 (1-7)")
    impact: float = Field(..., description="영향도")

class ProcessInput(BaseModel):
    data: List[float] = Field(..., description="처리할 데이터")
    direction: Optional[str] = Field("TOP_DOWN", description="흐름 방향")

class DualityModeInput(BaseModel):
    mode: str = Field(..., description="stability/innovation/adaptive")

class ThresholdAdjustInput(BaseModel):
    layer: int = Field(..., ge=1, le=7)
    value: float = Field(..., ge=0.0, le=1.0)

class PredictionInput(BaseModel):
    sequence: List[float] = Field(..., description="예측할 시계열 데이터")

# === 전역 인스턴스 초기화 ===
velocity_manager = None
codon_registry = None
predictor = None
annotation_system = None
pro_engine = None

if CORE_MODULES_AVAILABLE:
    velocity_manager = VelocityPolicyManager()
    codon_registry = CodonRegistry()
    predictor = CascadePredictor()
    annotation_system = AnnotationSystem()

if ENGINE_AVAILABLE:
    # PRO 엔진 초기화 (간단한 예제)
    def sample_rule1(x): return [v * 2 for v in x] if isinstance(x, list) else x * 2
    def sample_rule2(x): return [v + 1 for v in x] if isinstance(x, list) else x + 1
    
    rules = [
        Rule("double", sample_rule1, Layer.L2_ATOMIC),
        Rule("increment", sample_rule2, Layer.L3_MOLECULAR)
    ]
    groups = {"main": RuleGroup("main", ["double", "increment"])}
    config = VelocityConfig()
    
    try:
        pro_engine = CosmosPROEngine(rules, groups, config)
        print("✅ PRO Engine initialized")
    except Exception as e:
        print(f"⚠️  PRO Engine init failed: {e}")

# === Rate Limit Middleware ===
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limit 체크 미들웨어"""
    # 공개 엔드포인트는 제외
    if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/pro/features"]:
        return await call_next(request)
    
    # Authorization 헤더 확인
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        api_key = auth_header.split(" ")[1]
        
        # Rate limit 확인
        status = rate_limiter.check_limit(api_key)
        
        if not status["allowed"]:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "limit": status["limit"],
                    "reset_at": status["reset_at"],
                    "plan": status["plan"],
                    "upgrade": "https://cosmos-hgp.com/pricing"
                }
            )
        
        # 사용 횟수 증가
        rate_limiter.increment(api_key)
        
        # 응답 헤더에 사용량 정보 추가
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(status["limit"])
        response.headers["X-RateLimit-Remaining"] = str(status["remaining"])
        response.headers["X-RateLimit-Reset"] = status["reset_at"]
        return response
    
    return await call_next(request)

# === 기본 엔드포인트 ===
@app.get("/")
async def root():
    """API 루트"""
    return {
        "service": "COSMOS-HGP PRO API",
        "version": "2.0",
        "status": "operational",
        "modules": {
            "auth": AUTH_AVAILABLE,
            "engine": ENGINE_AVAILABLE,
            "core_modules": CORE_MODULES_AVAILABLE
        }
    }

@app.get("/health")
async def health():
    """헬스 체크"""
    return {
        "healthy": True,
        "engine_status": "nominal" if pro_engine else "unavailable",
        "modules": {
            "auth": AUTH_AVAILABLE,
            "rate_limiter": True,
            "velocity": velocity_manager is not None,
            "codon": codon_registry is not None,
            "predictor": predictor is not None,
            "annotation": annotation_system is not None
        }
    }

# === PRO 기능 엔드포인트 ===
@app.post("/codon/analyze")
async def analyze_codon(
    payload: CodonInput,
    api_key: str = Depends(verify_api_key) if AUTH_AVAILABLE else None
):
    """
    PRO: DNA 코돈 분석 (64개 무제한)
    FREE: 월 50회 제한
    """
    if not codon_registry:
        raise HTTPException(503, "Codon analyzer not available")
    
    result = codon_registry.analyze_code(payload.code)
    return result

@app.post("/velocity/calculate")
async def calculate_velocity(
    payload: VelocityInput,
    api_key: str = Depends(verify_api_key) if AUTH_AVAILABLE else None
):
    """PRO: 7계층 속도 계산"""
    if not velocity_manager:
        raise HTTPException(503, "Velocity manager not available")
    
    try:
        layer = list(Layer)[payload.layer - 1]
        threshold = velocity_manager.get_threshold(layer)
        blocked = payload.impact >= threshold
        
        return {
            "layer": layer.display_name,
            "threshold": threshold,
            "impact": payload.impact,
            "blocked": blocked,
            "recommendation": "block" if blocked else "pass"
        }
    except IndexError:
        raise HTTPException(400, "Invalid layer number (1-7)")

@app.post("/pro/process")
async def process_with_prediction(
    payload: ProcessInput,
    api_key: str = Depends(verify_api_key) if AUTH_AVAILABLE else None
):
    """PRO: 예측 기반 처리 (양방향 + 자가 치유)"""
    if not predictor:
        raise HTTPException(503, "Predictor not available")
    
    data = np.array(payload.data)
    
    # 예측 차단
    should_prevent = predictor.should_block(data)
    
    if should_prevent:
        # 자가 치유
        from core_modules.annotation import RecoveryStrategy
        recovered_data = RecoveryStrategy.bypass(data)
        
        if annotation_system:
            annotation_system.annotate("CASCADE_PREVENTED", "High risk detected")
        
        return {
            "status": "cascade_prevented",
            "data": recovered_data.tolist() if isinstance(recovered_data, np.ndarray) else recovered_data,
            "prediction": "high_risk"
        }
    
    # 정상 처리
    return {
        "status": "processed",
        "data": data.tolist(),
        "prediction": "low_risk"
    }

@app.post("/pro/batch")
async def process_batch(
    payload: Dict[str, List[List[float]]],
    api_key: str = Depends(verify_api_key) if AUTH_AVAILABLE else None
):
    """PRO: 병렬 배치 처리"""
    data_list = payload.get("data_list", [])
    results = []
    
    for data in data_list:
        arr = np.array(data)
        result = {
            "data": arr.tolist(),
            "norm": float(np.linalg.norm(arr))
        }
        results.append(result)
    
    return {"results": results, "count": len(results)}

@app.post("/pro/duality/switch")
async def switch_mode(
    payload: DualityModeInput,
    api_key: str = Depends(verify_api_key) if AUTH_AVAILABLE else None
):
    """PRO: 이중성 모드 전환 (Stability/Innovation/Adaptive)"""
    if not pro_engine:
        raise HTTPException(503, "PRO Engine not available")
    
    mode_map = {
        "stability": DualityMode.STABILITY,
        "innovation": DualityMode.INNOVATION,
        "adaptive": DualityMode.ADAPTIVE
    }
    
    if payload.mode not in mode_map:
        raise HTTPException(400, f"Invalid mode. Use: {list(mode_map.keys())}")
    
    try:
        pro_engine.switch_duality_mode(mode_map[payload.mode])
        return {
            "status": "success",
            "new_mode": payload.mode,
            "philosophy": pro_engine.get_mode_philosophy()
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/pro/threshold/adjust")
async def adjust_threshold(
    payload: ThresholdAdjustInput,
    api_key: str = Depends(verify_api_key) if AUTH_AVAILABLE else None
):
    """PRO: 임계값 조정 (쓰기 권한)"""
    if not velocity_manager:
        raise HTTPException(503, "Velocity manager not available")
    
    layer = list(Layer)[payload.layer - 1]
    velocity_manager.set_threshold(layer, payload.value)
    
    return {
        "status": "success",
        "layer": layer.display_name,
        "new_threshold": payload.value
    }

@app.get("/pro/telemetry")
async def get_telemetry(
    api_key: str = Depends(verify_api_key) if AUTH_AVAILABLE else None
):
    """PRO: 실시간 텔레메트리"""
    telemetry = {
        "velocity_stats": velocity_manager.get_breach_statistics() if velocity_manager else {},
        "annotation_stats": annotation_system.get_statistics() if annotation_system else {},
        "predictor_trained": predictor.is_trained if predictor else False
    }
    
    if pro_engine:
        telemetry["engine_status"] = pro_engine.get_comprehensive_status()
    
    return telemetry

@app.get("/pro/stats")
async def get_stats(
    api_key: str = Depends(verify_api_key) if AUTH_AVAILABLE else None
):
    """PRO: 전체 통계"""
    return {
        "rate_limit": rate_limiter.get_all_usage(),
        "engine": pro_engine.get_comprehensive_status() if pro_engine else {},
        "modules": {
            "velocity": velocity_manager.get_breach_statistics() if velocity_manager else {},
            "annotation": annotation_system.get_statistics() if annotation_system else {}
        }
    }

@app.get("/pro/features")
async def list_features():
    """PRO 기능 목록 (인증 불필요)"""
    return {
        "features": [
            {"name": "DNA 코돈", "endpoint": "/codon/analyze", "free": "50회/월"},
            {"name": "7계층 속도", "endpoint": "/velocity/calculate", "pro": True},
            {"name": "이중성 모드", "endpoint": "/pro/duality/switch", "pro": True},
            {"name": "양방향 처리", "endpoint": "/pro/process", "pro": True},
            {"name": "예측 차단", "endpoint": "/pro/process", "pro": True},
            {"name": "자가 치유", "endpoint": "/pro/process", "pro": True},
            {"name": "병렬 처리", "endpoint": "/pro/batch", "pro": True},
            {"name": "텔레메트리", "endpoint": "/pro/telemetry", "pro": True},
            {"name": "자가 디버깅", "endpoint": "/selftest", "pro": True, "new": True},
            {"name": "CSV 분석", "endpoint": "/analyze/csv", "pro": True, "new": True},
            {"name": "웹로그 분석", "endpoint": "/analyze/weblog", "pro": True, "new": True},
            {"name": "도메인 컨설팅", "endpoint": "/consult/{domain}", "pro": True, "new": True}
        ],
        "pricing": {"free": "$0 (50회/월)", "pro": "$5/월 (무제한)"}
    }

# ===============================
# 신규 고급 기능 엔드포인트 (4개)
# ===============================

class CSVAnalyzeInput(BaseModel):
    file_content: str = Field(..., description="CSV 파일 내용")
    file_name: Optional[str] = "data.csv"

class WeblogInput(BaseModel):
    logs: List[Dict[str, Any]] = Field(..., description="웹 로그 배열")

class ConsultInput(BaseModel):
    data: Dict[str, Any] = Field(..., description="분석할 데이터")

@app.post("/selftest")
async def selftest_endpoint(
    api_key: str = Depends(verify_api_key) if AUTH_AVAILABLE else None
):
    """자가 디버깅: COSMOS 스스로 6가지 테스트 실행"""
    if not ADVANCED_FEATURES_AVAILABLE:
        raise HTTPException(503, "Advanced features not available")
    
    try:
        return run_selftest()
    except Exception as e:
        raise HTTPException(500, f"Selftest failed: {str(e)}")

@app.post("/analyze/csv")
async def csv_analyze_endpoint(
    payload: CSVAnalyzeInput,
    api_key: str = Depends(verify_api_key) if AUTH_AVAILABLE else None
):
    """CSV 분석: 모든 유형 자동 감지 및 분석"""
    if not ADVANCED_FEATURES_AVAILABLE:
        raise HTTPException(503, "Advanced features not available")
    
    try:
        return analyze_csv_universal(payload.file_content, payload.file_name)
    except Exception as e:
        raise HTTPException(500, f"CSV 분석 실패: {str(e)}")

@app.post("/analyze/weblog")
async def weblog_analyze_endpoint(
    payload: WeblogInput,
    api_key: str = Depends(verify_api_key) if AUTH_AVAILABLE else None
):
    """웹로그 분석: 공격 패턴 탐지 + IP/URL 분석"""
    if not ADVANCED_FEATURES_AVAILABLE:
        raise HTTPException(503, "Advanced features not available")
    
    try:
        return analyze_weblog(payload.logs)
    except Exception as e:
        raise HTTPException(500, f"웹로그 분석 실패: {str(e)}")

@app.post("/consult/{domain}")
async def consult_endpoint(
    domain: str,
    payload: ConsultInput,
    api_key: str = Depends(verify_api_key) if AUTH_AVAILABLE else None
):
    """
    도메인 컨설팅: AIOps/Finance/Healthcare
    3WHY 설명 + 전문 분석 + 구체적 권고사항
    """
    if not ADVANCED_FEATURES_AVAILABLE:
        raise HTTPException(503, "Advanced features not available")
    
    try:
        return domain_consulting(domain, payload.data)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"컨설팅 실패: {str(e)}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  COSMOS-HGP PRO API Server Starting...")
    print("="*60)
    print(f"  Auth: {'✅' if AUTH_AVAILABLE else '⚠️ '}")
    print(f"  Engine: {'✅' if ENGINE_AVAILABLE else '⚠️ '}")
    print(f"  Core Modules: {'✅' if CORE_MODULES_AVAILABLE else '⚠️ '}")
    print(f"  Advanced Features: {'✅' if ADVANCED_FEATURES_AVAILABLE else '⚠️ '}")
    print(f"  Rate Limiter: ✅ (FREE: 50회/월, PRO: 무제한)")
    print("="*60)
    print(f"\n  📡 API 서버: http://localhost:7860")
    print(f"  📖 API 문서: http://localhost:7860/docs")
    print(f"  🔑 테스트 키: {API_KEY}")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=7860, reload=False)
