#!/usr/bin/env python3
"""
COSMOS-HGP Authentication & Authorization System
Tier-based access control with usage tracking
"""

import hashlib
import secrets
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class UserTier(Enum):
    """사용자 등급"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierLimits:
    """등급별 제한사항"""
    monthly_executions: int  # -1 = unlimited
    max_input_size: int      # bytes
    max_concurrent: int      # 동시 실행 수
    cascade_prediction: bool
    annotation_access: bool
    api_rate_limit: str      # "100/minute" format
    features: List[str] = field(default_factory=list)


# 등급별 제한 정의
TIER_CONFIGS = {
    UserTier.FREE: TierLimits(
        monthly_executions=50,
        max_input_size=1024,  # 1KB
        max_concurrent=1,
        cascade_prediction=False,
        annotation_access=False,
        api_rate_limit="10/minute",
        features=["basic_execution"]
    ),
    UserTier.PRO: TierLimits(
        monthly_executions=5000,
        max_input_size=1024 * 1024,  # 1MB
        max_concurrent=5,
        cascade_prediction=True,
        annotation_access=True,
        api_rate_limit="100/minute",
        features=["basic_execution", "cascade_prediction", "annotations", "export"]
    ),
    UserTier.ENTERPRISE: TierLimits(
        monthly_executions=-1,  # unlimited
        max_input_size=10 * 1024 * 1024,  # 10MB
        max_concurrent=20,
        cascade_prediction=True,
        annotation_access=True,
        api_rate_limit="1000/minute",
        features=["basic_execution", "cascade_prediction", "annotations", 
                 "export", "custom_rules", "priority_support"]
    )
}


@dataclass
class User:
    """사용자 정보"""
    api_key: str
    tier: UserTier
    created_at: datetime
    monthly_usage: int = 0
    last_reset: datetime = field(default_factory=datetime.now)
    total_usage: int = 0
    email: Optional[str] = None
    company: Optional[str] = None


class UserAuth:
    """사용자 인증 및 권한 관리"""
    
    def __init__(self, storage_path: str = "./data/users.json"):
        self.storage_path = storage_path
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, str] = {}  # session_token -> api_key
        self._load_users()
        
        logger.info(f"UserAuth initialized with {len(self.users)} users")
    
    def _load_users(self):
        """사용자 데이터 로드 (파일 기반 - 프로덕션에서는 DB 사용)"""
        try:
            import os
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for key, user_data in data.items():
                        self.users[key] = User(
                            api_key=key,
                            tier=UserTier(user_data['tier']),
                            created_at=datetime.fromisoformat(user_data['created_at']),
                            monthly_usage=user_data.get('monthly_usage', 0),
                            last_reset=datetime.fromisoformat(user_data.get('last_reset', datetime.now().isoformat())),
                            total_usage=user_data.get('total_usage', 0),
                            email=user_data.get('email'),
                            company=user_data.get('company')
                        )
        except Exception as e:
            logger.warning(f"Failed to load users: {e}. Starting with demo users.")
            self._create_demo_users()
    
    def _save_users(self):
        """사용자 데이터 저장"""
        try:
            import os
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            data = {}
            for key, user in self.users.items():
                data[key] = {
                    'tier': user.tier.value,
                    'created_at': user.created_at.isoformat(),
                    'monthly_usage': user.monthly_usage,
                    'last_reset': user.last_reset.isoformat(),
                    'total_usage': user.total_usage,
                    'email': user.email,
                    'company': user.company
                }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save users: {e}")
    
    def _create_demo_users(self):
        """데모 사용자 생성"""
        self.users = {
            "demo_free_key_123": User(
                api_key="demo_free_key_123",
                tier=UserTier.FREE,
                created_at=datetime.now(),
                email="free@demo.com"
            ),
            "demo_pro_key_456": User(
                api_key="demo_pro_key_456",
                tier=UserTier.PRO,
                created_at=datetime.now(),
                email="pro@demo.com"
            ),
            "demo_enterprise_key_789": User(
                api_key="demo_enterprise_key_789",
                tier=UserTier.ENTERPRISE,
                created_at=datetime.now(),
                email="enterprise@demo.com"
            )
        }
        self._save_users()
    
    def generate_api_key(self) -> str:
        """새 API 키 생성"""
        return f"cosmos_{secrets.token_urlsafe(32)}"
    
    def create_user(self, tier: UserTier, email: Optional[str] = None, 
                   company: Optional[str] = None) -> str:
        """새 사용자 생성"""
        api_key = self.generate_api_key()
        user = User(
            api_key=api_key,
            tier=tier,
            created_at=datetime.now(),
            email=email,
            company=company
        )
        self.users[api_key] = user
        self._save_users()
        
        logger.info(f"Created new {tier.value} user: {api_key[:20]}...")
        return api_key
    
    def verify_api_key(self, api_key: str) -> bool:
        """API 키 유효성 검증"""
        if not api_key or api_key not in self.users:
            return False
        
        user = self.users[api_key]
        self._reset_monthly_usage_if_needed(user)
        return True
    
    def get_user(self, api_key: str) -> Optional[User]:
        """사용자 정보 조회"""
        if api_key in self.users:
            user = self.users[api_key]
            self._reset_monthly_usage_if_needed(user)
            return user
        return None
    
    def get_user_tier(self, api_key: str) -> Optional[UserTier]:
        """사용자 등급 조회"""
        user = self.get_user(api_key)
        return user.tier if user else None
    
    def get_tier_limits(self, tier: UserTier) -> TierLimits:
        """등급별 제한사항 조회"""
        return TIER_CONFIGS[tier]
    
    def check_usage_limit(self, api_key: str) -> tuple[bool, str]:
        """사용량 제한 확인
        
        Returns:
            (allowed, message)
        """
        user = self.get_user(api_key)
        if not user:
            return False, "Invalid API key"
        
        limits = self.get_tier_limits(user.tier)
        
        # 무제한인 경우
        if limits.monthly_executions == -1:
            return True, "OK"
        
        # 사용량 체크
        if user.monthly_usage >= limits.monthly_executions:
            return False, f"Monthly limit reached ({limits.monthly_executions})"
        
        return True, "OK"
    
    def increment_usage(self, api_key: str) -> bool:
        """사용량 증가"""
        user = self.get_user(api_key)
        if not user:
            return False
        
        user.monthly_usage += 1
        user.total_usage += 1
        self._save_users()
        
        return True
    
    def _reset_monthly_usage_if_needed(self, user: User):
        """월간 사용량 리셋 (매월 1일)"""
        now = datetime.now()
        if now.month != user.last_reset.month or now.year != user.last_reset.year:
            user.monthly_usage = 0
            user.last_reset = now
            self._save_users()
            logger.info(f"Reset monthly usage for user {user.api_key[:20]}...")
    
    def check_feature_access(self, api_key: str, feature: str) -> bool:
        """특정 기능 접근 권한 확인"""
        user = self.get_user(api_key)
        if not user:
            return False
        
        limits = self.get_tier_limits(user.tier)
        return feature in limits.features
    
    def get_usage_stats(self, api_key: str) -> Optional[Dict]:
        """사용량 통계 조회"""
        user = self.get_user(api_key)
        if not user:
            return None
        
        limits = self.get_tier_limits(user.tier)
        
        return {
            "tier": user.tier.value,
            "monthly_usage": user.monthly_usage,
            "monthly_limit": limits.monthly_executions,
            "remaining": limits.monthly_executions - user.monthly_usage 
                        if limits.monthly_executions != -1 else -1,
            "total_usage": user.total_usage,
            "created_at": user.created_at.isoformat(),
            "last_reset": user.last_reset.isoformat()
        }
    
    def create_session(self, api_key: str) -> Optional[str]:
        """세션 토큰 생성 (웹 대시보드용)"""
        if not self.verify_api_key(api_key):
            return None
        
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = api_key
        return session_token
    
    def verify_session(self, session_token: str) -> Optional[str]:
        """세션 토큰으로 API 키 조회"""
        return self.sessions.get(session_token)
    
    def upgrade_user(self, api_key: str, new_tier: UserTier) -> bool:
        """사용자 등급 업그레이드"""
        user = self.get_user(api_key)
        if not user:
            return False
        
        old_tier = user.tier
        user.tier = new_tier
        self._save_users()
        
        logger.info(f"Upgraded user from {old_tier.value} to {new_tier.value}")
        return True


# 글로벌 인스턴스
_auth_instance = None

def get_auth() -> UserAuth:
    """싱글톤 인증 인스턴스 반환"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = UserAuth()
    return _auth_instance
