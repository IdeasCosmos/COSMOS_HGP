"""
COSMOS-HGP Rate Limiting Module
속도 제한 시스템 (메모리 기반)

FREE: 월 100회 제한
PRO: 무제한
"""

import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import threading

class RateLimiter:
    """
    메모리 기반 Rate Limiter
    Redis 없이 딕셔너리로 관리
    """
    
    def __init__(self):
        """
        Rate Limiter 초기화
        """
        # {api_key: {"count": int, "reset_at": timestamp}}
        self.usage: Dict[str, Dict] = defaultdict(dict)
        self._lock = threading.Lock()
        
        # 제한 설정
        self.FREE_LIMIT = 50  # 월 50회
        self.PRO_LIMIT = float('inf')  # 무제한
        
        # API 키별 플랜 (실제로는 DB에서 조회)
        self.plans = {
            "test_key_12345": "PRO",  # 테스트 키는 PRO
            "free_key_demo": "FREE"    # 데모 FREE 키
        }
    
    def _get_reset_timestamp(self) -> float:
        """
        다음 달 1일 00:00:00 timestamp 반환
        """
        now = datetime.now()
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)
        return next_month.timestamp()
    
    def _get_plan(self, api_key: str) -> str:
        """
        API 키의 플랜 조회
        
        Args:
            api_key: API 키
            
        Returns:
            str: "FREE" 또는 "PRO"
        """
        return self.plans.get(api_key, "FREE")
    
    def _get_limit(self, api_key: str) -> float:
        """
        플랜별 제한 조회
        
        Args:
            api_key: API 키
            
        Returns:
            float: 제한 횟수
        """
        plan = self._get_plan(api_key)
        return self.PRO_LIMIT if plan == "PRO" else self.FREE_LIMIT
    
    def check_limit(self, api_key: str) -> Dict[str, any]:
        """
        Rate limit 확인
        
        Args:
            api_key: 확인할 API 키
            
        Returns:
            dict: {
                "allowed": bool,
                "remaining": int,
                "limit": int,
                "reset_at": str,
                "plan": str
            }
        """
        with self._lock:
            plan = self._get_plan(api_key)
            limit = self._get_limit(api_key)
            
            # PRO는 무제한
            if plan == "PRO":
                return {
                    "allowed": True,
                    "remaining": "unlimited",
                    "limit": "unlimited",
                    "reset_at": None,
                    "plan": "PRO"
                }
            
            # FREE 사용자 처리
            now = time.time()
            
            if api_key not in self.usage:
                # 첫 사용
                self.usage[api_key] = {
                    "count": 0,
                    "reset_at": self._get_reset_timestamp()
                }
            
            user_data = self.usage[api_key]
            
            # 리셋 시간 확인
            if now >= user_data["reset_at"]:
                # 새 달 시작 - 카운터 리셋
                user_data["count"] = 0
                user_data["reset_at"] = self._get_reset_timestamp()
            
            # 제한 확인
            current_count = user_data["count"]
            remaining = max(0, limit - current_count)
            allowed = current_count < limit
            
            reset_datetime = datetime.fromtimestamp(user_data["reset_at"])
            
            return {
                "allowed": allowed,
                "remaining": int(remaining),
                "limit": int(limit),
                "reset_at": reset_datetime.isoformat(),
                "plan": plan,
                "current_usage": current_count
            }
    
    def increment(self, api_key: str) -> bool:
        """
        사용 횟수 증가
        
        Args:
            api_key: API 키
            
        Returns:
            bool: 성공 여부
        """
        with self._lock:
            plan = self._get_plan(api_key)
            
            # PRO는 카운트 안 함
            if plan == "PRO":
                return True
            
            # FREE 사용자
            if api_key not in self.usage:
                self.usage[api_key] = {
                    "count": 0,
                    "reset_at": self._get_reset_timestamp()
                }
            
            now = time.time()
            user_data = self.usage[api_key]
            
            # 리셋 확인
            if now >= user_data["reset_at"]:
                user_data["count"] = 0
                user_data["reset_at"] = self._get_reset_timestamp()
            
            # 증가
            user_data["count"] += 1
            return True
    
    def get_usage(self, api_key: str) -> Dict[str, any]:
        """
        현재 사용량 조회
        
        Args:
            api_key: API 키
            
        Returns:
            dict: 사용량 정보
        """
        with self._lock:
            if api_key not in self.usage:
                return {
                    "count": 0,
                    "limit": self._get_limit(api_key),
                    "plan": self._get_plan(api_key)
                }
            
            user_data = self.usage[api_key]
            return {
                "count": user_data["count"],
                "limit": self._get_limit(api_key),
                "reset_at": datetime.fromtimestamp(user_data["reset_at"]).isoformat(),
                "plan": self._get_plan(api_key)
            }
    
    def reset_user(self, api_key: str):
        """
        특정 사용자 사용량 리셋 (관리자용)
        
        Args:
            api_key: 리셋할 API 키
        """
        with self._lock:
            if api_key in self.usage:
                self.usage[api_key]["count"] = 0
                self.usage[api_key]["reset_at"] = self._get_reset_timestamp()
    
    def get_all_usage(self) -> Dict[str, Dict]:
        """
        전체 사용량 조회 (관리자용)
        
        Returns:
            dict: 모든 사용자의 사용량
        """
        with self._lock:
            return dict(self.usage)

# 전역 Rate Limiter 인스턴스
rate_limiter = RateLimiter()

